import base64,copy,json,unittest
from types import SimpleNamespace
from fixture.apply import PipelineFailureScenario
from investigator.process_tape import bytes_of

class PipelineScenarios(unittest.TestCase):
 def definition(self):
  value={'properties':{'activities':[{'name':'Copy','type':'Copy','dependsOn':[]},{'name':'Audit','type':'Script','dependsOn':[{'activity':'Copy','dependencyConditions':['Succeeded']}],'linkedService':{'connection':'existing-connection'},'typeProperties':{'database':'existing-audit','scripts':[{'type':'NonQuery','text':'existing writer SQL'}]}}]}}
  return {'definition':{'parts':[{'path':'pipeline-content.json','payloadType':'InlineBase64','payload':base64.b64encode(bytes_of(value)).decode()},{'path':'.platform','payloadType':'InlineBase64','payload':base64.b64encode(b'{"metadata":"unchanged"}').decode()}]}}
 def control(self,original):
  calls=[];state=[copy.deepcopy(original)]
  def call(endpoint,method,body=None,**kwargs):
   calls.append((endpoint,method,copy.deepcopy(body),kwargs))
   if endpoint.endswith('/updateDefinition'):state[0]=copy.deepcopy(body);return {'status_code':200,'text':{}}
   return {'status_code':200,'text':copy.deepcopy(state[0])}
  return SimpleNamespace(workspace='11111111-1111-1111-1111-111111111111',call=call,resolve=lambda response,**kwargs:response['text']),calls,state
 def test_fixed_failure_prevents_original_work_and_preserves_connection_and_input(self):
  before=self.definition();original=copy.deepcopy(before);after=PipelineFailureScenario.failure(before);content=PipelineFailureScenario.content(after);acts=content['properties']['activities']
  self.assertEqual(before,original);self.assertEqual(after['definition']['parts'][1],before['definition']['parts'][1]);self.assertEqual(acts[0]['typeProperties']['scripts'],[{'type':'NonQuery','text':PipelineFailureScenario.THROW}]);self.assertEqual(acts[0]['linkedService'],{'connection':'existing-connection'});self.assertEqual(acts[1]['dependsOn'][0]['activity'],PipelineFailureScenario.MARKER)
  self.assertEqual(acts[2]['dependsOn'][0]['activity'],'Copy')
 def test_apply_and_restore_read_back_original_with_same_scope_and_journal_keys(self):
  before=self.definition();control,calls,state=self.control(before);scenario=PipelineFailureScenario(control,'22222222-2222-2222-2222-222222222222');applied=scenario.apply(before,key='apply-one');restored=scenario.restore(before,applied['injected_hash'],key='restore-one')
  self.assertEqual(restored['status'],'RESTORED_DEFINITION');self.assertEqual(state[0],before);writes=[c for c in calls if c[0].endswith('/updateDefinition')];self.assertEqual([c[3]['key']for c in writes],['apply-one','restore-one']);self.assertTrue(all(c[0].startswith('workspaces/'+control.workspace+'/dataPipelines/')for c in calls))
  self.assertEqual(scenario.restore(before,applied['injected_hash'],key='restore-again')['mutations'],0)
 def test_changed_before_or_concurrent_restore_never_writes(self):
  before=self.definition();control,calls,state=self.control(before);scenario=PipelineFailureScenario(control,'22222222-2222-2222-2222-222222222222');state[0]=PipelineFailureScenario.failure(before)
  with self.assertRaisesRegex(ValueError,'BEFORE_DEFINITION_CHANGED'):scenario.apply(before,key='no-write')
  with self.assertRaisesRegex(ValueError,'CONCURRENT_CHANGE'):scenario.restore(before,'not-current',key='no-write')
  self.assertFalse(any(c[0].endswith('/updateDefinition')for c in calls))
 def test_no_existing_connection_template_means_refusal_not_invented_connection(self):
  before=self.definition();d=PipelineFailureScenario.content(before);d['properties']['activities']=d['properties']['activities'][:1];before['definition']['parts'][0]['payload']=base64.b64encode(bytes_of(d)).decode()
  with self.assertRaisesRegex(ValueError,'EXISTING_SCRIPT_CONNECTION'):PipelineFailureScenario.failure(before)

 def test_job_submission_is_durable_and_location_bound_to_the_same_pipeline(self):
  before=self.definition();control,calls,state=self.control(before);scenario=PipelineFailureScenario(control,'22222222-2222-2222-2222-222222222222');run='33333333-3333-3333-3333-333333333333'
  endpoint='workspaces/'+control.workspace+'/items/'+scenario.item_id+'/jobs/instances/'+run
  def call(path,method='GET',body=None,**kwargs):
   calls.append((path,method,body,kwargs))
   return {'status_code':202,'headers':{'Location':'https://api.fabric.microsoft.com/v1/'+endpoint},'text':{}}if method=='POST'else {'status_code':200,'text':{'id':run,'status':'Failed'}}
  control.call=call
  submitted=scenario.start_failure(key='one-real-run');self.assertEqual(submitted['endpoint'],endpoint);self.assertEqual(calls[-1][3]['key'],'one-real-run');self.assertEqual(scenario.job(endpoint)['status'],'Failed')
  with self.assertRaisesRegex(ValueError,'OUTSIDE_PIPELINE'):scenario.job(endpoint.replace(scenario.item_id,run))
  control.call=lambda *args,**kwargs:{'status_code':202,'headers':{'location':'https://example.org/elsewhere'},'text':{}}
  with self.assertRaisesRegex(ValueError,'OUTSIDE_WORKSPACE'):scenario.start_failure(key='refused-location')

if __name__=='__main__':unittest.main()

import base64,copy,json,unittest
from types import SimpleNamespace
from fixture.apply import PipelineFailureScenario,PipelineWaitScenario
from investigator.process_tape import bytes_of
from fixture.apply import SourceHistoryScenario
import hashlib

class SourceHistoryPlans(unittest.TestCase):
 def baseline(self):
  rows=[{'movement_id':'1','warehouse_id':'1','product_id':'8','units':'16','event_day':'2026-09-11','movement_type':'RECEIPT','source_modified_at_utc':'2026-10-03T00:00:00Z','source_row_version':'28001'}]
  v={'status':'READ_ONLY_BASELINE_COMPLETE','table':'[app].[stock_movements_round_two_20261003]','row_count':1,'source_units':16,'rows_sha256':hashlib.sha256(bytes_of(rows)).hexdigest(),'result':{'body':{'sets':[[{}],rows,[]]}}};v['seal']=hashlib.sha256(bytes_of(v)).hexdigest();return v
 def added(self):return {'movement_id':900101,'warehouse_id':1,'product_id':8,'units':7,'event_day':'2026-09-11','movement_type':'RECEIPT'}
 def test_reader_observes_only_new_control_ids_with_parameters_and_binary_version_conversion(self):
  plan=SourceHistoryScenario(self.baseline());rows=[self.added(),{**self.added(),'movement_id':900102}]
  request=plan.observation(rows)
  self.assertEqual(request['read_only_objects'],['[app].[stock_movements_round_two_20261003]'])
  self.assertEqual(request['max_rows'],3)
  self.assertEqual(request['parameters'],[{'name':'@case_id_0','value':900101},{'name':'@case_id_1','value':900102}])
  self.assertNotIn('900101',request['query']);self.assertTrue(request['query'].startswith('SELECT '))
  self.assertIn('CONVERT(bigint,source_row_version)',request['query']);self.assertIn('source_row_version',request['result_columns'])
  for invalid in ([],[self.added()]*4,[self.added(),self.added()],[{**self.added(),'movement_id':1}]):
   with self.assertRaises(ValueError):plan.observation(invalid)
 def test_corrupt_or_incomplete_preimage_refuses_before_producing_mutation(self):
  v=self.baseline();v['source_units']=17
  with self.assertRaisesRegex(ValueError,'SEAL_DIFFERS'):SourceHistoryScenario(v)
  v=self.baseline();v['rows_sha256']='0'*64;v.pop('seal');v['seal']=hashlib.sha256(bytes_of(v)).hexdigest()
  with self.assertRaisesRegex(ValueError,'ROWS_DIFFER'):SourceHistoryScenario(v)
 def test_insertion_is_new_ids_only_and_guards_full_preimage_inside_transaction(self):
  builder=SourceHistoryScenario(self.baseline());sql=builder.insert([self.added()])['query']
  self.assertLess(sql.index('BEGIN TRANSACTION'),sql.index('IF (SELECT COUNT_BIG'))
  self.assertLess(sql.index('Source preimage changed'),sql.index('INSERT INTO'))
  self.assertIn('UPDLOCK,HOLDLOCK',sql);self.assertIn('MAX(CONVERT(bigint,source_row_version))',sql)
  self.assertNotIn('source_row_version) VALUES',sql);self.assertNotIn('UPDATE ',sql);self.assertNotIn('DELETE ',sql)
  with self.assertRaisesRegex(ValueError,'ID_NOT_NEW'):builder.insert([{**self.added(),'movement_id':1}])
  with self.assertRaisesRegex(ValueError,'ID_NOT_NEW'):builder.insert([self.added(),self.added()])
 def test_literals_cannot_escape_the_closed_source_plan(self):
  builder=SourceHistoryScenario(self.baseline())
  for changed in ({'units':True},{'movement_id':'900101; DROP TABLE x'},{'event_day':"2026-09-11');DELETE FROM x;--"},{'movement_type':"RECEIPT');DELETE FROM x;--"},{'source_row_version':9}):
   with self.subTest(changed=changed),self.assertRaises((ValueError,TypeError)):builder.insert([{**self.added(),**changed}])
 def test_restoration_needs_native_versions_and_refuses_changed_payload(self):
  builder=SourceHistoryScenario(self.baseline());r=self.added()
  with self.assertRaisesRegex(ValueError,'NATIVE_INSERT_RECEIPT'):builder.restore([r],[])
  with self.assertRaisesRegex(ValueError,'INTEGER_REQUIRED'):builder.restore([r],[r])
  with self.assertRaisesRegex(ValueError,'VALUES_DIFFER'):builder.restore([r],[{**r,'units':99,'source_row_version':28002}])
  with self.assertRaisesRegex(ValueError,'INTEGER_BOUND'):builder.restore([r],[{**r,'source_row_version':28001}])
  sql=builder.restore([r],[{**r,'source_row_version':28002}]);self.assertIn('movement_id NOT IN (900101)',sql);self.assertIn('movement_id=900101 AND CONVERT(bigint,source_row_version)=28002',sql)
  self.assertLess(sql.index('Inserted rows changed'),sql.index('DELETE FROM'));self.assertIn('DELETE FROM [app].[stock_movements_round_two_20261003] WHERE movement_id IN (900101)',sql)

class PipelineScenarios(unittest.TestCase):
 def test_wait_control_contains_no_original_work_even_on_skip_paths(self):
  before=self.definition();preserved=copy.deepcopy(before);content=PipelineFailureScenario.content(before)
  content['properties']['activities'][1]['dependsOn']=[{'activity':'Copy','dependencyConditions':['Skipped']}]
  before['definition']['parts'][0]['payload']=base64.b64encode(bytes_of(content)).decode();original=copy.deepcopy(before)
  after=PipelineWaitScenario.waiting(before,seconds=300);activities=PipelineWaitScenario.content(after)['properties']['activities']
  self.assertEqual(activities,[{'name':PipelineWaitScenario.WAIT_MARKER,'type':'Wait','dependsOn':[],'typeProperties':{'waitTimeInSeconds':300}}])
  self.assertEqual(before,original);self.assertEqual(after['definition']['parts'][1],preserved['definition']['parts'][1])
  self.assertNotIn('Copy',json.dumps(activities));self.assertNotIn('existing writer SQL',json.dumps(activities))
 def test_wait_bound_and_restoration_use_existing_concurrency_checks(self):
  before=self.definition();control,calls,state=self.control(before);item='22222222-2222-2222-2222-222222222222'
  for seconds in (True,59,601,'300'):
   with self.subTest(seconds=seconds),self.assertRaisesRegex(ValueError,'WAIT_BOUND'):PipelineWaitScenario(control,item,seconds=seconds)
  scenario=PipelineWaitScenario(control,item,seconds=60);applied=scenario.apply(before,key='wait-apply')
  self.assertEqual(PipelineWaitScenario.content(state[0])['properties']['activities'][0]['type'],'Wait')
  restored=scenario.restore(before,applied['injected_hash'],key='wait-restore');self.assertEqual(restored['status'],'RESTORED_DEFINITION');self.assertEqual(state[0],before)
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

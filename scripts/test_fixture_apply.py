import base64,copy,json,unittest
from unittest.mock import Mock
from uuid import uuid4
from fixture.apply import Executor,inputs,verify_source
from fixture.rebuild import templates
from fixture.seed import load

W='d028fa2b-0d1b-4dd8-b423-37dd161cd5d0'
P={'workspace_id':W,'workspace_name':'empty-fixture','capacity_id':'ec15bc07-8e88-436e-8dbe-485b9a7f4533',
   'prefix':'rehearsal','source_table':'stock_movements_rehearsal','source_object_id':100,
   'source_connection':str(uuid4()),'invoke_connection':str(uuid4()),'approval_reference':'Explicit fixture test approval'}

class Control:
 def __init__(self):self.workspace=W;self.record={};self.created={};self.requests=[];self.existing=[]
 def save(self):pass
 def create(self,key,collection,body):
  item={'id':str(uuid4()),'displayName':body['displayName'],'workspaceId':W}
  self.created[item['id']]={'collection':collection,'body':copy.deepcopy(body),'item':item};return item
 def resolve(self,response):return response['text']
 def call(self,endpoint,method='GET',body=None,**kw):
  self.requests.append((endpoint,method,body));parts=endpoint.split('/')
  if endpoint=='workspaces/'+W:return {'text':{'displayName':P['workspace_name'],'capacityId':P['capacity_id']}}
  if endpoint.endswith('/items'):return {'text':{'value':self.existing}}
  if endpoint.endswith('/getDefinition'):return {'text':{'definition':self.created[parts[-2]]['body']['definition']}}
  if endpoint.endswith('/connectionString'):return {'text':{'connectionString':'fixture.datawarehouse.fabric.microsoft.com'}}
  if '/jobs/instances?' in endpoint or '/jobs/execute/instances?' in endpoint:return {'headers':{'location':'https://api.fabric.microsoft.com/v1/workspaces/'+W+'/dataPipelines/x/jobs/instances/'+str(uuid4())}}
  if '/jobs/instances/' in endpoint:return {'text':{'id':parts[-1],'status':'Completed'}}
  item=copy.deepcopy(self.created[parts[-1]]['item']);item['properties']={'sqlEndpointProperties':{'id':str(uuid4()),'provisioningStatus':'Success','connectionString':'fixture.datawarehouse.fabric.microsoft.com'}}
  return {'text':item}

class ApplyTests(unittest.TestCase):
 def test_nonempty_workspace_refuses_before_any_create(self):
  ctl=Control();ctl.existing=[{'id':str(uuid4())}]
  with self.assertRaisesRegex(ValueError,'empty'):Executor(ctl,P,templates(),sleep=lambda _:None).provision()
  self.assertFalse(ctl.created)
 def test_served_notebook_must_preserve_every_statement_before_execution(self):
  ctl=Control();original=ctl.call
  def lost(endpoint,*args,**kw):
   if endpoint.endswith('/getDefinition'):
    return {'text':{'definition':{'parts':[{'path':'notebook-content.py','payload':base64.b64encode(b'pass').decode()}]}}}
   return original(endpoint,*args,**kw)
  ctl.call=lost
  with self.assertRaisesRegex(ValueError,'Served notebook lost'):Executor(ctl,P,templates(),sleep=lambda _:None).provision()
  self.assertFalse(any('/jobs/' in r[0] for r in ctl.requests))
 def test_all_retained_templates_bind_to_new_objects_without_refresh(self):
  ctl=Control();executor=Executor(ctl,P,templates(),sleep=lambda _:None);result=executor.provision()
  self.assertEqual(len(result['items']),14)
  self.assertEqual(set(result['jobs']),{'notebook','audit-ddl','pipeline'})
  for record in ctl.created.values():self.assertNotIn('${',json.dumps(record['body']))
  script=next(x['body'] for x in ctl.created.values() if x['item']['displayName'].endswith('_application_load'))
  content=json.loads(base64.b64decode(script['definition']['parts'][0]['payload']))
  text=content['properties']['activities'][1]['typeProperties']['scripts'][0]['text']
  self.assertIn('rowsRead',text);self.assertIn('rowsCopied',text);self.assertNotIn('COUNT(',text.upper())
  self.assertFalse(any('refresh' in r[0].lower() for r in ctl.requests))
  execution=next(r[2] for r in ctl.requests if '/jobs/execute/instances?' in r[0])
  self.assertEqual(execution['executionData']['computeConfiguration']['defaultLakehouse']['itemId'],result['items']['bronze']['id'])
 def test_prepared_source_is_compared_rowwise_as_guarded_reader(self):
  table=next(t for t in load()['tables'] if t['name'].startswith('stock_movements_'));cols=[x[0] for x in table['columns']]
  rows=[{'fixture_source_object_id':'100',**{c:str(v) for c,v in zip(cols,row)}} for row in sorted(table['rows'],key=lambda x:x[0])]
  read=Mock(return_value={'read_only_verified':True,'rows':rows})
  self.assertEqual(verify_source(P,{},read)['row_count'],360)
  self.assertEqual(read.call_args.args[1]['read_only_objects'],['[app].[stock_movements_rehearsal]'])
  rows[0]['units']='999999'
  with self.assertRaisesRegex(ValueError,'differs'):verify_source(P,{},read)
 def test_identical_rows_on_wrong_object_cannot_publish_a_wrong_binding(self):
  table=next(t for t in load()['tables'] if t['name'].startswith('stock_movements_'));cols=[x[0] for x in table['columns']]
  rows=[{'fixture_source_object_id':'101',**{c:str(v) for c,v in zip(cols,row)}} for row in table['rows']]
  with self.assertRaisesRegex(ValueError,'object identity differs'):
   verify_source(P,{},Mock(return_value={'read_only_verified':True,'rows':rows}))
 def test_scope_and_extra_input_cannot_be_smuggled(self):
  with self.assertRaisesRegex(ValueError,'contract'):inputs({**P,'workspace_role':'Admin'})

if __name__=='__main__':unittest.main()

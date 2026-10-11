import base64,io,json,sqlite3,sys,tempfile,unittest
from pathlib import Path
from contextlib import closing
from urllib.error import HTTPError
sys.path[:0]=[str(Path.cwd()/'scripts'),str(Path(__file__).parent)]
from metadata_capture import Capture,CapturedHttp,safe
from investigator.process_tape import Tape,active,bounded_call,validate_event
from investigator.planner_recording import RecordingError
class Tests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  self.db=self.root/'source.sqlite'
  with closing(sqlite3.connect(self.db)) as db:
   with db:db.execute('CREATE TABLE fixture(value TEXT)');db.execute('INSERT INTO fixture VALUES(?)',('{"name":"synthetic"}',))
 def capture(self,manifest=None):
  return Capture(self.root/'capture',manifest or {'environment':'synthetic'},{},None,self.db,self.root/'absent.sqlite','a'*64)
 def test_exact_metadata_response_replays_without_producer(self):
  c=self.capture();request={'endpoint':'workspaces/fixture/items','method':'get','audience':'fabric'};response={'status_code':200,'headers':{'RequestId':'synthetic-id'},'text':{'value':[{'name':'synthetic-report'}]}}
  self.assertEqual(c.call('metadata_http',request,lambda:response),response)
  artifact=c.finish({'status':'COLLECTED_NOT_APPROVED','context_id':'synthetic-context'})
  t=Tape(artifact['path'])
  with active(t):
   self.assertEqual(bounded_call('metadata_http',request,lambda:self.fail('must not read')),response)
  final=json.loads(t.take('FINAL'));self.assertEqual(final['context_id'],'synthetic-context');self.assertTrue((self.root/'capture/catalog-after.sqlite').is_file())
 def test_authentication_header_never_enters_boundary_and_http_error_body_survives(self):
  class Tokens:
   def get_token(self,scope):return 'SECRET_TOKEN_ONLY_IN_MEMORY'
  class Opener:
   def open(self,request,timeout):
    self.last=request
    raise HTTPError(request.full_url,403,'Forbidden',{'RequestId':'synthetic-error'},io.BytesIO(b'{"error":{"code":"Forbidden"}}'))
  opener=Opener();client=CapturedHttp(Tokens(),opener)
  c=self.capture();response=c.call('metadata_http',{'endpoint':'workspaces/fixture/items'},lambda:client('workspaces/fixture/items'))
  self.assertEqual(response['status_code'],403);self.assertEqual(response['text']['error']['code'],'Forbidden')
  c.finish({'status':'PARTIAL'});self.assertNotIn(b'SECRET_TOKEN_ONLY_IN_MEMORY',(self.root/'capture/tape.json').read_bytes());self.assertIn('Bearer ',opener.last.headers['Authorization'])
 def test_encoded_secret_and_sensitive_response_headers_are_refused_before_recording(self):
  with self.assertRaises(RecordingError):safe({'parts':[{'payload':base64.b64encode(b'{"password":"SYNTHETIC_SECRET_VALUE"}').decode()}]})
  c=self.capture()
  with self.assertRaisesRegex(RuntimeError,'METADATA_READ_FAILED:RecordingError'):
   c.call('metadata_http',{'endpoint':'fixture'},lambda:{'headers':{'Set-Cookie':'SYNTHETIC_SECRET_VALUE'}})
  c.finish({'status':'BLOCKED'});self.assertNotIn(b'SYNTHETIC_SECRET_VALUE',(self.root/'capture/tape.json').read_bytes())
 def test_projected_installation_never_falls_back_to_exact_discovery(self):
  policy={'tape_class':'PRIVACY_PROJECTED','version':'estate-privacy-projection-v1','estate_id':'synthetic','key_reference':'secret-store-only','columns':['private']}
  with self.assertRaisesRegex(RecordingError,'PROJECTED_DISCOVERY_CAPTURE_UNIMPLEMENTED'):self.capture({'environment':'synthetic','recording':policy})
  self.assertFalse((self.root/'capture').exists())
class GovernedDiscoveryTests(unittest.TestCase):
 def test_actual_policy_discovery_collector_replays_context_and_budget_without_network(self):
  import copy,shutil,time
  from types import SimpleNamespace
  from test_enterprise_discovery import DiscoveryTests
  from investigator.onboarding import ModelStore
  from investigator.enterprise_discovery import Discovery
  from investigator.discovery_collect import Collector
  from investigator.usage_governance import UsageGovernor
  from investigator.budget_checkpoint import prepare
  from metadata_capture import deterministic_metadata
  fixture=DiscoveryTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
  environment=fixture.store.environment
  manifest={'environment':environment,'recording':{'tape_class':'EXACT'}}
  actual_policy={'environment':environment,'daily_limits':{'planner_calls':50,'cloud_calls':100,'input_characters':1000000,'output_tokens':100000},'max_inflight_planners':1,'no_progress_limit':3}
  gov=UsageGovernor(SimpleNamespace(store=fixture.store,db=fixture.store.connect,config={}),actual_policy,time.time)
  root=fixture.root/'capture';session='governed-metadata';sequence=0
  from investigator.runtime import fingerprint
  capture=Capture(root,manifest,fixture.config,actual_policy,fixture.store.database,fixture.store.inventory,fingerprint())
  gov.clock=lambda:__import__('investigator.process_tape',fromlist=['clock']).clock('billing_budget')
  def http(endpoint,method='get',audience='fabric'):
   nonlocal sequence
   sequence+=1
   return gov.metered_read(session,'http-'+str(sequence),lambda:capture.call('billing_metadata_http',{'endpoint':endpoint,'method':method,'audience':audience,'identity':'investigator-code-reader'},lambda:fixture.transport(endpoint,method,audience)))
  def sql(*args):
   nonlocal sequence
   sequence+=1
   return gov.metered_read(session,'sql-'+str(sequence),lambda:capture.call('billing_source_catalog',{'server':args[0],'database':args[1],'schema':args[2]},lambda:fixture.sql(*args)))
  from investigator import process_tape as journal
  collected=Discovery(fixture.store,fixture.config).run(Collector(fixture.config,http,sql,clock=lambda:journal.clock('collection_deadline',time.monotonic)).run,session)
  models=fixture.store.list();self.assertTrue(models);context=models[0]['context'];self.assertTrue(context['id'])
  artifact=capture.finish({'status':'COLLECTED_NOT_APPROVED','result':collected,'session':session,'metadata_physical_admissions':sequence,'auth_control_admissions':0})
  from replay_metadata import replay
  portable=replay(root,fixture.root/'portable-replay')
  self.assertEqual(portable['metadata_requests'],sequence);self.assertTrue(portable['context_result_byte_identical'])
  tape=Tape(artifact['path']);clone=fixture.root/'replay';clone.mkdir()
  shutil.copyfile(root/'catalog.sqlite',clone/'catalog.sqlite')
  if (root/'inventory.sqlite').exists():shutil.copyfile(root/'inventory.sqlite',clone/'inventory.sqlite')
  store=ModelStore(clone/'catalog.sqlite',clone/'inventory.sqlite',environment)
  replaygov=UsageGovernor(SimpleNamespace(store=store,db=store.connect,config={}),actual_policy,time.time)
  prepare(tape,root/'catalog.sqlite',environment);sequence=0
  def replay_http(endpoint,method='get',audience='fabric'):
   nonlocal sequence
   sequence+=1
   return replaygov.metered_read(session,'http-'+str(sequence),lambda:bounded_call('billing_metadata_http',{'endpoint':endpoint,'method':method,'audience':audience,'identity':'investigator-code-reader'},lambda:self.fail('network forbidden')))
  def replay_sql(*args):
   nonlocal sequence
   sequence+=1
   return replaygov.metered_read(session,'sql-'+str(sequence),lambda:bounded_call('billing_source_catalog',{'server':args[0],'database':args[1],'schema':args[2]},lambda:self.fail('SQL/network forbidden')))
  with active(tape),deterministic_metadata():
   replaygov.clock=lambda:journal.clock('billing_budget')
   replayed=Discovery(store,fixture.config).run(Collector(fixture.config,replay_http,replay_sql,clock=lambda:journal.clock('collection_deadline',time.monotonic)).run,session)
  final=json.loads(tape.take('FINAL'))
  self.assertEqual(final['result'],replayed)
  self.assertEqual(context,store.list()[0]['context'])
  self.assertEqual(tape.index,len(tape.events))
  with store.connect() as db:self.assertEqual(db.execute("SELECT count(*) FROM adaptive_usage WHERE environment=? AND kind='cloud'",(environment,)).fetchone()[0],sequence)
if __name__=='__main__':unittest.main()

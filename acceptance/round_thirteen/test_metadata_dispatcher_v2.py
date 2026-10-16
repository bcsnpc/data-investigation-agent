import hashlib,json,subprocess,sys,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path.cwd();sys.path[:0]=[str(ROOT/'scripts'),str(Path(__file__).parent)]
from metadata_revision_v2 import replay_metadata_v2_revision
from test_metadata_worker_v2 import WORKER
class Tests(unittest.TestCase):
 def test_real_discovery_nested_sql_protocol_archived_replay(self):
  from test_enterprise_discovery import DiscoveryTests
  from metadata_capture import Capture
  from investigator import process_tape as journal
  from investigator.physical_reads import run
  from investigator.runtime import fingerprint
  from investigator.enterprise_discovery import Discovery
  from investigator.discovery_collect import Collector
  from investigator.usage_governance import UsageGovernor
  f=DiscoveryTests();f.setUp();self.addCleanup(f.doCleanups)
  credential=str(f.root/'absent-credential.xml');f.config['sql']['auth']={'credential_file':credential}
  manifest={'environment':f.store.environment,'recording':{'tape_class':'EXACT'}}
  governed={'environment':f.store.environment,'daily_limits':{'planner_calls':50,'cloud_calls':100,'input_characters':1000000,'output_tokens':100000},'max_inflight_planners':1,'no_progress_limit':3}
  class Governor(UsageGovernor):
   def __init__(self,*a):self.physical=0;super().__init__(*a)
   def reserve(self,db,session,key,kind,*a,**kw):
    value=super().reserve(db,session,key,kind,*a,**kw)
    if kind=='cloud':self.physical+=1
    return value
  gov=Governor(SimpleNamespace(store=f.store,db=f.store.connect,config={}),governed,time.time)
  capture=Capture(f.root/'capture',manifest,f.config,governed,f.store.database,f.store.inventory,fingerprint());gov.clock=lambda:journal.clock('billing_budget');sequence=0;session='synthetic-v2-dispatcher'
  program=f.root/'worker.py';program.write_text(WORKER);actual_popen=subprocess.Popen
  def fake(command,**kw):return actual_popen([sys.executable,str(program)],**kw)
  def http(endpoint,method='get',audience='fabric'):
   nonlocal sequence
   sequence+=1
   return gov.metered_read(session,'http-'+str(sequence),lambda:capture.call('billing_metadata_http',{'endpoint':endpoint,'method':method,'audience':audience,'identity':'investigator-code-reader'},lambda:f.transport(endpoint,method,audience)))
  def sql(*args):
   nonlocal sequence
   sequence+=1
   def execute():
    command=['powershell','-NoProfile','-File',str(ROOT/'infra/scripts/Get-SqlMetadata.ps1'),'-Server',args[0],'-Database',args[1],'-VisibilitySchema',args[2],'-CredentialPath',credential,'-OutputPath',str(f.root/'never-created.json')]
    result=run(command,input='{}',timeout=240,capture_output=True,text=True,encoding='utf-8')
    if result.returncode:raise RuntimeError('synthetic worker failed')
    return f.sql(*args)
   return gov.metered_read(session,'sql-'+str(sequence),lambda:capture.call('billing_source_catalog',{'server':args[0],'database':args[1],'schema':args[2]},execute))
  with patch.object(subprocess,'Popen',side_effect=fake):
   result=Discovery(f.store,f.config).run(Collector(f.config,http,sql,clock=lambda:journal.clock('collection_deadline',time.monotonic)).run,session)
  captured=capture.finish({'status':'COLLECTED_NOT_APPROVED','result':result,'session':session,'metadata_physical_admissions':gov.physical,'auth_control_admissions':0})
  path=Path(captured['path']);before=path.read_bytes();helpers={n:hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in ('metadata_worker_v2.py','replay_metadata_v2.py')}
  revision=capture.tape.bootstrap['state']['engine_revision']
  replayed=replay_metadata_v2_revision(path,f.root/'replayed',revision,repository=ROOT,consumer_hashes=helpers)
  self.assertTrue(replayed['matched']);self.assertTrue(replayed['context_result_byte_identical']);self.assertEqual(replayed['metadata_physical_admissions'],gov.physical);self.assertGreater(gov.physical,sequence);self.assertEqual(before,path.read_bytes());self.assertFalse(Path(credential).exists());self.assertFalse((f.root/'never-created.json').exists())
  with self.assertRaisesRegex(ValueError,'CONSUMER_PINS_REQUIRED'):replay_metadata_v2_revision(path,f.root/'pinless',revision,repository=ROOT)
  changed=dict(helpers);changed['metadata_worker_v2.py']='0'*64
  with self.assertRaisesRegex(ValueError,'CONSUMER_HASH_CHANGED'):replay_metadata_v2_revision(path,f.root/'changed',revision,repository=ROOT,consumer_hashes=changed)
if __name__=='__main__':unittest.main()

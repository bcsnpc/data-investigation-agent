import base64,copy,hashlib,importlib.util,json,runpy,shutil,subprocess,sys,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
ROOT=Path.cwd();sys.path[:0]=[str(ROOT/'scripts'),str(Path(__file__).parent)]
H=runpy.run_path(str(Path(__file__).with_name('metadata_revision.py')))
class Tests(unittest.TestCase):
 def test_real_discovery_inventory_fake_source_in_recorded_revision(self):
  from test_enterprise_discovery import DiscoveryTests
  from metadata_capture import Capture
  from investigator import process_tape as journal
  from investigator.runtime import fingerprint
  from investigator.enterprise_discovery import Discovery
  from investigator.discovery_collect import Collector
  from investigator.usage_governance import UsageGovernor
  f=DiscoveryTests();f.setUp();self.addCleanup(f.doCleanups)
  manifest={'environment':f.store.environment,'recording':{'tape_class':'EXACT'}}
  governed={'environment':f.store.environment,'daily_limits':{'planner_calls':50,'cloud_calls':100,'input_characters':1000000,'output_tokens':100000},'max_inflight_planners':1,'no_progress_limit':3};gov=UsageGovernor(SimpleNamespace(store=f.store,db=f.store.connect,config={}),governed,time.time)
  capture=Capture(f.root/'capture',manifest,f.config,governed,f.store.database,f.store.inventory,fingerprint());gov.clock=lambda:journal.clock('billing_budget');sequence=0;session='synthetic-dispatcher'
  def http(endpoint,method='get',audience='fabric'):
   nonlocal sequence
   sequence+=1
   return gov.metered_read(session,'http-'+str(sequence),lambda:capture.call('billing_metadata_http',{'endpoint':endpoint,'method':method,'audience':audience,'identity':'investigator-code-reader'},lambda:f.transport(endpoint,method,audience)))
  def sql(*args):
   nonlocal sequence
   sequence+=1
   return gov.metered_read(session,'sql-'+str(sequence),lambda:capture.call('billing_source_catalog',{'server':args[0],'database':args[1],'schema':args[2]},lambda:f.sql(*args)))
  result=Discovery(f.store,f.config).run(Collector(f.config,http,sql,clock=lambda:journal.clock('collection_deadline',time.monotonic)).run,session)
  captured=capture.finish({'status':'COLLECTED_NOT_APPROVED','result':result,'session':session,'metadata_physical_admissions':sequence,'auth_control_admissions':0})
  tape_path=Path(captured['path']);before=tape_path.read_bytes();revision=capture.tape.bootstrap['state']['engine_revision']
  replayed=H['replay_metadata_revision'](tape_path,f.root/'isolated-replay',revision,repository=ROOT)
  self.assertTrue(replayed['matched']);self.assertTrue(replayed['context_result_byte_identical']);self.assertEqual(replayed['metadata_requests'],sequence);self.assertEqual(before,tape_path.read_bytes())
  (tape_path.parent/'metadata_capture.py').write_bytes((tape_path.parent/'metadata_capture.py').read_bytes()+b'\n# changed\n')
  with self.assertRaisesRegex(ValueError,'SUPPORT_CHANGED'):H['replay_metadata_revision'](tape_path,f.root/'tamper-replay',revision,repository=ROOT)
  with self.assertRaisesRegex(ValueError,'SEALED_PRODUCER_REVISION_MISMATCH'):H['replay_metadata_revision'](tape_path,f.root/'wrong-revision',subprocess.check_output(['git','rev-parse',revision+'^'],text=True).strip(),repository=ROOT)
 def test_live_socket_attempt_from_sealed_synthetic_helper_is_denied(self):
  from investigator import process_tape as journal
  from investigator.runtime import fingerprint
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);support={'metadata_capture.py':b'# synthetic helper\n','replay_metadata.py':b'import socket\ndef replay(root,destination): socket.create_connection(("localhost",1))\n'}
   for name,body in support.items():(p/name).write_bytes(body)
   revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
   b={'entry_point':'billing_metadata_collection','context_identity':'synthetic','config':{},'profile':{},'usage_policy':None,'engine_hash':fingerprint(),'state':{'engine_revision':revision,'capture_support':{n:hashlib.sha256(v).hexdigest() for n,v in support.items()}}}
   t=journal.Tape(p/'tape.json',b);t.finish({})
   with self.assertRaisesRegex(ValueError,'NETWORK_FORBIDDEN'):H['replay_metadata_revision'](p/'tape.json',p/'out',revision,repository=ROOT)
if __name__=='__main__':unittest.main()

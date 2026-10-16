"""Private recorded-revision replay handler. Network/authentication forbidden."""
import argparse,hashlib,json,shutil,sys,time
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,'scripts')
from investigator import process_tape as journal
from investigator.runtime import fingerprint
from investigator.onboarding import ModelStore
from investigator.enterprise_discovery import Discovery
from investigator.discovery_collect import Collector
from investigator.usage_governance import UsageGovernor
from investigator.budget_checkpoint import prepare
from metadata_capture import deterministic_metadata
from metadata_worker_v2 import owned_bounded,sql_file_catalog
import sqlite3
from contextlib import closing

def replay(root,destination):
 root=Path(root);destination=Path(destination)
 tape=journal.Tape(root/'tape.json');bootstrap=tape.bootstrap
 if bootstrap['entry_point']!='billing_metadata_collection':raise RuntimeError('Metadata replay entry point differs')
 if bootstrap['engine_hash']!=fingerprint():raise RuntimeError('Run metadata replay in its recorded engine revision')
 for name,expected in bootstrap['state']['capture_support'].items():
  if hashlib.sha256((root/name).read_bytes()).hexdigest()!=expected:raise RuntimeError('Capture helper hash differs')
 for name,expected in bootstrap['state']['artifacts'].items():
  if expected is not None and hashlib.sha256((root/name).read_bytes()).hexdigest()!=expected:raise RuntimeError('Before artifact hash differs')
 final=json.loads(journal.validate_event(tape.events[-1],len(tape.events)))
 for name,expected in final['artifacts'].items():
  if expected is not None and hashlib.sha256((root/name).read_bytes()).hexdigest()!=expected:raise RuntimeError('After artifact hash differs')
 destination.mkdir(exist_ok=False)
 for name in ('catalog.sqlite','inventory.sqlite'):
  if (root/name).exists():shutil.copyfile(root/name,destination/name)
 config=bootstrap['config'];environment=bootstrap['state']['environment']
 store=ModelStore(destination/'catalog.sqlite',destination/'inventory.sqlite',environment)
 class RecordedMetadataGovernor(UsageGovernor):
  # Counts actual admitted physical slots; the private native caller cap is
  # explicitly outside this narrower replay contract. No cap is backfilled.
  def __init__(self,*a):self.metadata_admissions=0;super().__init__(*a)
  def reserve(self,db,session,key,kind,*a,**kw):
   answer=super().reserve(db,session,key,kind,*a,**kw)
   if kind=='cloud':self.metadata_admissions+=1
   return answer
 gov=RecordedMetadataGovernor(SimpleNamespace(store=store,db=store.connect,config=config),bootstrap['usage_policy'],time.time)
 prepare(tape,root/'catalog.sqlite',environment);sequence=0;session=final['session']
 def forbidden():raise AssertionError('Metadata replay must not invoke network, auth, or SQL')
 def http(endpoint,method='get',audience='fabric'):
  nonlocal sequence
  sequence+=1
  request={'endpoint':endpoint,'method':method,'audience':audience,'identity':'investigator-code-reader'}
  return gov.metered_read(session,'http-'+str(sequence),lambda:journal.bounded_call('billing_metadata_http',request,forbidden))
 def sql(*args):
  nonlocal sequence
  sequence+=1
  request={'server':args[0],'database':args[1],'schema':args[2]}
  return gov.metered_read(session,'sql-'+str(sequence),lambda:owned_bounded('billing_source_catalog',request,lambda:sql_file_catalog(*args,script=Path.cwd()/'infra/scripts/Get-SqlMetadata.ps1',credential_file=config['sql']['auth']['credential_file'])))
 with journal.active(tape),deterministic_metadata():
  gov.clock=lambda:journal.clock('billing_budget')
  result=Discovery(store,config).run(Collector(config,http,sql,clock=lambda:journal.clock('collection_deadline',time.monotonic)).run,session)
 if journal.bytes_of(result)!=journal.bytes_of(final['result']) or gov.metadata_admissions!=final['metadata_physical_admissions']:raise RuntimeError('Metadata/context/physical-count replay differs')
 def context_rows(database):
  with closing(sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro',uri=True)) as db:return db.execute('SELECT id,model_id,scan_id,body,hash,created FROM model_contexts ORDER BY id').fetchall()
 if context_rows(destination/'catalog.sqlite')!=context_rows(root/'catalog-after.sqlite'):raise RuntimeError('Metadata model-context bytes differ')
 tape.take('FINAL')
 if tape.index!=len(tape.events):raise RuntimeError('Replay left unconsumed events')
 return {'status':'REPLAYED','dispatcher':'RECORDED_METADATA_SQL_PROTOCOL_V2','claim':'Archived Collector/Discovery plus SQL worker protocol and recorded bounded JSON file-result; native private caller cap enforcement and pre-tape authentication controls are outside replay. No native temporary file bytes are claimed.','metadata_logical_calls':sequence,'metadata_physical_admissions':gov.metadata_admissions,'auth_controls_retained_outside_replay':final['auth_control_admissions'],'metadata_requests':sequence,'estate_reads':0,'model_calls':0,'authentication_calls':0,'context_result_byte_identical':True,'tape_sha256':hashlib.sha256((root/'tape.json').read_bytes()).hexdigest()}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--capture',type=Path,required=True);parser.add_argument('--destination',type=Path,required=True);args=parser.parse_args()
 print(json.dumps(replay(args.capture,args.destination),sort_keys=True))

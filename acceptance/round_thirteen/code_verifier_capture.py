"""Private next-producer exact verifier capture. No legacy evidence backfill."""
import hashlib,importlib.util,json,shutil,sqlite3,subprocess
from contextlib import closing
from pathlib import Path
from investigator import process_tape as journal
from investigator.planner_recording import _safe

CONTRACT='code-verifier-dependencies-v1'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def name(n):
 if not isinstance(n,str) or not n or Path(n).name!=n or n in ('.','..') or ':' in n or '\\' in n or '/' in n:raise ValueError('VERIFIER_UNSAFE_MEMBER')
 return n
def audit(p):
 _safe(Path(p).read_bytes())
def snapshot(source,destination):
 with closing(sqlite3.connect(Path(source).resolve().as_uri()+'?mode=ro',uri=True)) as db:
  db.execute('BEGIN')
  for table, in db.execute("SELECT name FROM sqlite_master WHERE type='table'"):
   for row in db.execute('SELECT * FROM "'+table.replace('"','""')+'"'):
    for value in row:
     if isinstance(value,str):_safe(value.encode())
     elif isinstance(value,bytes):_safe(value)
  with closing(sqlite3.connect(destination)) as out:db.backup(out)
  db.rollback()
 return sha(destination)
def load_program(path):
 spec=importlib.util.spec_from_file_location('sealed_verification_program',path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
class Capture:
 def __init__(self,folder,*,inputs,config,policy,engine_hash,program,files,databases,environment,context_identity,profile_member=None):
  journal.bytes_of(inputs);_safe(journal.bytes_of(inputs));_safe(journal.bytes_of(config));_safe(journal.bytes_of(policy))
  if config.get('_estate',{}).get('recording',{}).get('tape_class','EXACT')!='EXACT':raise ValueError('PROJECTED_VERIFIER_CAPTURE_UNIMPLEMENTED')
  self.root=Path(folder);self.root.mkdir(parents=True,exist_ok=False);self.work=self.root/'working';self.work.mkdir()
  self.originals={};members={};identities={}
  for n,source in {**files,**databases}.items():
   name(n);source=Path(source);identities[n]=str(source.resolve());self.originals[n]=source
   if n in databases:members[n]=snapshot(source,self.root/n)
   else:audit(source);shutil.copyfile(source,self.root/n);members[n]=sha(self.root/n)
   shutil.copyfile(self.root/n,self.work/n)
  if 'catalog.sqlite' not in databases:raise ValueError('VERIFIER_CATALOG_BASELINE_REQUIRED')
  session=inputs['session_id']
  if not isinstance(session,str) or not session:raise ValueError('VERIFIER_FRESH_SESSION_REQUIRED')
  with closing(sqlite3.connect(self.root/'catalog.sqlite')) as baseline:
   if baseline.execute('SELECT count(*) FROM adaptive_usage WHERE environment=? AND session_id IN (?,?)',(environment,session,session+':prewarm-controls')).fetchone()[0]:raise ValueError('VERIFIER_SESSION_ALREADY_USED')
  audit(program);shutil.copyfile(program,self.root/'verification_program.py');members['verification_program.py']=sha(self.root/'verification_program.py')
  shutil.copyfile(Path(__file__),self.root/'code_verifier_capture.py');members['code_verifier_capture.py']=sha(self.root/'code_verifier_capture.py')
  revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
  if profile_member is not None and profile_member not in files:raise ValueError('VERIFIER_PROFILE_BASELINE_REQUIRED')
  state={'profile_member':profile_member,'capture_contract':CONTRACT,'engine_revision':revision,'environment':environment,'inputs':inputs,'members':members,'database_members':sorted(databases),'native_path_identities':identities,'budget_checkpoint':'DELTA_V2','snapshot_clock':'ONE_CLOCK_V1'}
  # Execute exactly the serialized representation replay will consume. Mapping
  # insertion order must not become an unsealed catalog-column list order.
  bootstrap=json.loads(journal.bytes_of({'entry_point':'code_verifier','context_identity':context_identity,'config':config,'profile':{},'usage_policy':policy,'engine_hash':engine_hash,'state':state}))
  self.tape=journal.Tape(self.root/'tape.json',bootstrap=bootstrap)
  if self.tape.engine_revision!=revision:raise ValueError('VERIFIER_PRODUCER_REVISION_CHANGED_DURING_CAPTURE')
  from investigator.budget_checkpoint import prepare
  prepare(self.tape,self.root/'catalog.sqlite',environment)
 def execute(self,live=None):
  program=load_program(self.root/'verification_program.py')
  with journal.active(self.tape):
   result,error,status=perform(program,self.tape.bootstrap,self.work,self.originals['catalog.sqlite'],live)
   after=self.root/'catalog-after.sqlite';snapshot(self.originals['catalog.sqlite'],after);shutil.copyfile(after,self.work/'catalog.sqlite')
   final=finalize(self.tape.bootstrap,self.work,result,error,status,self.tape)
   _safe(journal.bytes_of(final));self.tape.finish(final)
  summary={'status':status,'control':'APPROVAL_VERIFICATION_CAPTURE','physical_requests':final['accounting']['physical_requests'],'control_requests':final['accounting']['control_requests'],'verification_physical_requests':final['accounting']['verification_physical_requests'],'verification_reads':final['accounting']['verification_reads'],'verification_cap':final['accounting']['verification_cap'],'diagnostic_reads':0,'model_calls':0,'error_type':error['error_type'] if error else None,'capture_sha256':sha(self.tape.path),'capture_contract':CONTRACT}
  (self.root/'capture-summary.json').write_bytes(journal.bytes_of(summary))
  return final

def accounting(b,work):
 identity=b['state']['inputs']['session_id'];environment=b['state']['environment']
 with closing(sqlite3.connect(Path(work,'catalog.sqlite').resolve().as_uri()+'?mode=ro',uri=True)) as db:
  db.execute('BEGIN')
  rows=db.execute('SELECT session_id,kind,reserved,status FROM adaptive_usage WHERE environment=? AND session_id IN (?,?)',(environment,identity,identity+':prewarm-controls')).fetchall()
 controls=sum(json.loads(r[2]).get('cloud_calls',0) for r in rows if r[0]==identity+':prewarm-controls')
 verification=sum(json.loads(r[2]).get('cloud_calls',0) for r in rows if r[0]==identity)
 if any(r[1]!='cloud' for r in rows):raise ValueError('VERIFIER_OWNED_NONREAD_USAGE')
 return {'physical_requests':controls+verification,'control_requests':controls,'verification_physical_requests':verification,'pending_reservations':sum(r[3]=='RESERVED' for r in rows),'diagnostic_reads':0,'model_calls':0,'ownership':'EXACT_SESSION_AND_PREWARM_CONTROL_SESSION'}
def perform(program,b,work,catalog,live):
 try:return program.perform(b,work,catalog,live),None,'COMPLETED'
 except Exception as exc:
  error={'error_type':type(exc).__name__,'message':str(exc),'errno':getattr(exc,'errno',None)}
  try:_safe(journal.bytes_of(error))
  except Exception:error={'error_type':type(exc).__name__,'message_retention':'REFUSED_SECRET_CONTENT','errno':getattr(exc,'errno',None)}
  from investigator.usage_governance import UsageHold
  return None,error,'HELD' if isinstance(exc,UsageHold) else 'FAILED'
def finalize(b,work,result,error,status,tape):
 work=Path(work);n=b['state']['profile_member'];owned=accounting(b,work)
 decisions=[]
 for index,event in enumerate(tape.events[:-1] if tape.replaying else tape.events):
  if event['kind']=='BOUNDED_REQUEST':
   request=json.loads(__import__('base64').b64decode(event['body']))
   if request.get('name')=='binding_verification_admission':
    value=request['request'];decisions.append(value)
 admitted=[v for v in decisions if v.get('decision')=='ADMITTED']
 count=max((v['count'] for v in admitted),default=0);cap=b['state']['inputs'].get('verification_cap')
 if cap is not None and (count>cap or any(v.get('cap')!=cap for v in decisions)):raise ValueError('VERIFIER_RETAINED_PROBE_CAP_DIFFERS')
 if owned['physical_requests']>b['usage_policy']['daily_limits']['cloud_calls']:raise ValueError('VERIFIER_OWNED_PHYSICAL_ALLOWANCE_EXCEEDED')
 owned.update(verification_reads=count,verification_cap=cap,physical_allowance=b['usage_policy']['daily_limits']['cloud_calls'],admission_enforcement='EVERY_PHYSICAL_REQUEST_BY_SHARED_GOVERNOR')
 return {'status':status,'result':result,'error':error,'accounting':owned,'working_members':{p.name:sha(p) for p in sorted(work.iterdir()) if p.is_file()},'profile_identity':{'native_path':b['state']['native_path_identities'].get(n),'sha256':sha(work/n) if n else None}}

def replay(folder,output):
 folder=Path(folder);output=Path(output);tape=journal.Tape(folder/'tape.json');b=tape.bootstrap;s=b['state']
 if b['entry_point']!='code_verifier' or s.get('capture_contract')!=CONTRACT:raise ValueError('VERIFIER_DEPENDENCY_CONTRACT_MISSING')
 for n,h in s['members'].items():
  name(n)
  if sha(folder/n)!=h:raise ValueError('VERIFIER_MEMBER_CHANGED:'+n)
 if set(s['native_path_identities'])!=set(s['members'])-{'verification_program.py','code_verifier_capture.py'}:raise ValueError('VERIFIER_NATIVE_PATH_IDENTITY_SET')
 output.mkdir(parents=True,exist_ok=False)
 for n in s['native_path_identities']:shutil.copyfile(folder/n,output/n)
 from investigator.budget_checkpoint import prepare
 prepare(tape,folder/'catalog.sqlite',s['environment'])
 def forbidden(*a,**k):raise RuntimeError('VERIFIER_LIVE_PRODUCER_FORBIDDEN')
 with journal.active(tape):
  result,error,status=perform(load_program(folder/'verification_program.py'),b,output,output/'catalog.sqlite',forbidden)
  after=output.parent/(output.name+'-catalog-after.sqlite');snapshot(output/'catalog.sqlite',after);shutil.copyfile(after,output/'catalog.sqlite')
  final=finalize(b,output,result,error,status,tape)
  (output.parent/(output.name+'-recomputed-final.json')).write_bytes(journal.bytes_of(final))
  tape.finish(final)
 return {'matched':True,'status':status,'matched_failure':status!='COMPLETED','result':result,'error':error,'accounting':final['accounting'],'profile_identity':final['profile_identity'],'estate_reads':0,'model_calls':0}

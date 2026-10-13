"""Fixed two-phase cloud approval/demo job; no shell or arbitrary program input."""
import hashlib,io,json,os,re,shutil,stat,time,zipfile
from pathlib import Path
from contextlib import contextmanager
from investigator.onboarding import digest
from investigator.planner_recording import _safe


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2),encoding='utf8')
@contextmanager
def offline():
 old=os.environ.pop('INVESTIGATOR_STATE_BACKEND',None)
 try:yield
 finally:
  if old is not None:os.environ['INVESTIGATOR_STATE_BACKEND']=old


def extract(raw,root,*,expected,expanded_limit):
 if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('INPUT_ZIP_HASH_DIFFERS')
 root=Path(root)
 if root.exists() and any(root.iterdir()):raise ValueError('INPUT_DIRECTORY_NOT_EMPTY')
 root.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(io.BytesIO(raw)) as archive:
  rows=archive.infolist()
  if len(rows)>20000 or sum(r.file_size for r in rows)>expanded_limit:raise ValueError('INPUT_ZIP_BOUND')
  if len({r.filename for r in rows})!=len(rows):raise ValueError('INPUT_ZIP_DUPLICATE')
  for row in rows:
   p=Path(row.filename)
   if p.is_absolute() or '..' in p.parts or '\\' in row.filename or ':' in row.filename or stat.S_ISLNK(row.external_attr>>16):raise ValueError('INPUT_ZIP_PATH')
   target=root/p
   if row.is_dir():target.mkdir(parents=True,exist_ok=True);continue
   target.parent.mkdir(parents=True,exist_ok=True)
   with target.open('xb') as dst,archive.open(row) as src:shutil.copyfileobj(src,dst)
   target.chmod(0o444)
 for directory in sorted((p for p in root.rglob('*') if p.is_dir()),reverse=True):directory.chmod(0o555)
 root.chmod(0o555)


def audit_database(path):
 import sqlite3
 from contextlib import closing
 with closing(sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True)) as db:
  for (table,) in db.execute("SELECT name FROM sqlite_master WHERE type='table'"):
   query='SELECT * FROM '+chr(34)+table.replace(chr(34),chr(34)*2)+chr(34)
   for row in db.execute(query):
    for value in row:
     if isinstance(value,str):
      try:parsed=json.loads(value)
      except json.JSONDecodeError:parsed=value
      _safe(json.dumps(parsed,ensure_ascii=False).encode())
     elif isinstance(value,bytes):_safe(value)


def package(inputs,work,output):
 # Public result artifacts and existing audited input only. Credential caches
 # are memory-only and no home/tmp/environment directories are admitted here.
 allowed={'verification','verification-capture','readiness','one-attempt'}
 paths=[(p,p.relative_to(inputs).as_posix())for p in inputs.rglob('*')if p.is_file() and p.parts[len(inputs.parts)] not in {'verification','stage-result.json','platform-controls.jsonl','gateway-audit.jsonl','form-bundle.json'}]
 for name in allowed:
  folder=work/name
  if folder.exists():paths +=[(p,p.relative_to(work).as_posix())for p in folder.rglob('*') if p.is_file()]
 for name in ('stage-result.json','platform-controls.jsonl','gateway-audit.jsonl','form-bundle.json'):
  if (work/name).is_file():paths.append((work/name,name))
 if len(paths)>20000 or sum(p.stat().st_size for p,_ in paths)>5_500_000_000:raise ValueError('OUTPUT_BOUND')
 from cloud_verification_capture import audit
 # Inputs were audited before their explicitly approved archive hash. New or
 # changed SQLite snapshots are inspected as rows, never uploaded unchecked.
 approved_databases={sha(p) for p in inputs.rglob('*') if p.is_file() and p.suffix in ('.sqlite','.db')}
 for p,_ in paths:
  if p.suffix in ('.sqlite','.db'):
   identity=sha(p)
   if identity not in approved_databases:
    audit_database(p);approved_databases.add(identity)
  else:audit(p)
 with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=4) as archive:
  for p,name in paths:archive.write(p,name)
 return {'sha256':sha(output),'bytes':output.stat().st_size,'expanded_bytes':sum(p.stat().st_size for p,_ in paths),'members':len(paths)}


def prepare_phase(inputs,work):
 from cloud_context_prepare import prepare
 plan=read(inputs/'operator-plan.json')
 decision=plan.get('decision','Round Eighteen cloud migration: preserved definitions, fresh verification, one original A demo')
 if not isinstance(decision,str) or not decision.strip() or len(decision)>2000:
  raise ValueError('OWNER_DECISION_REQUIRED')
 with offline():
  value=prepare(inputs/'estate.json',inputs/'catalog.sqlite',inputs/'inventory.sqlite',work/'verification',
   model_id=plan['model_id'],context_id=plan['source_context'],context_hash=plan['source_context_hash'],
   actor='owner',decision=decision)
 shutil.copyfile(inputs/'endpoints.json',work/'verification/endpoints.json')
 return {'status':'PREPARED_NOT_PUBLISHED_NOT_READY','candidate_sha256':sha(work/'verification/publication-candidate.json'),'approval':value['approval'],'estate_reads':0,'model_calls':0}


def verify_phase(inputs,work,config):
 from cloud_context_prepare import publish
 from investigator.shared_state import configured_state
 from cloud_verification_run import execute
 from cloud_readiness_build import build
 from cloud_form_worker import main as form_main
 shutil.copytree(inputs/'verification',work/'verification')
 (work/'verification').chmod(0o700)
 for p in (work/'verification').rglob('*'):
  p.chmod(0o700 if p.is_dir() else 0o600)
 prepared=work/'verification';candidate=prepared/'publication-candidate.json'
 if sha(candidate)!=config['candidate_sha256']:raise ValueError('OWNER_REVIEWED_CANDIDATE_DIFFERS')
 state=configured_state()
 if state is None or state.backend!='postgresql':raise ValueError('CLOUD_POSTGRES_REQUIRED')
 publication=publish(state,read(candidate));write(prepared/'publication.json',publication)
 plan=read(inputs/'operator-plan.json')
 result=execute(inputs/'estate.json',prepared,inputs/'verification-spec.json',spec_sha256=plan['verification_spec_sha256'],session=config['session'],deadline=config['deadline'],capture=work/'verification-capture')
 write(prepared/'verification-result.json',result)
 if result['status']!='COMPLETED':return {'status':'VERIFICATION_STOPPED','verification':result}
 ready=build(inputs/'estate.json',prepared,inputs/'retained-facts.json',work/'verification-capture',work/'readiness')
 if ready['status']!='READY':return {'status':'READINESS_BLOCKED','readiness':ready}
 for name in ('estate.json','form.json'):shutil.copyfile(inputs/name,work/name)
 def reference(path):return {'path':path.relative_to(work).as_posix(),'sha256':sha(path)}
 model=read(prepared/'model.json')
 bundle={'version':'cloud-form-attempt-v1','manifest':reference(work/'estate.json'),'approval':reference(prepared/'approval.json'),
  'index':reference(work/'readiness/index.json'),'scope':reference(work/'readiness/scope.json'),'form':reference(work/'form.json'),
  'snapshots':{'catalog':reference(prepared/'catalog.sqlite'),'inventory':reference(prepared/'inventory.sqlite')},
  'model_pin':{'model_id':model['id'],'context_id':model['context_id'],'context_hash':digest(model['context'])}}
 write(work/'form-bundle.json',bundle)
 form_main(['--bundle',str(work/'form-bundle.json'),'--sha256',sha(work/'form-bundle.json'),'--job-root',str(work/'one-attempt')])
 return {'status':'DEMO_FINISHED','verification':result,'readiness':ready,'demo':read(work/'one-attempt/result.json')}


def run(config,*,download,upload,inputs=Path('/inputs'),work=Path('/work'),prepare_fn=prepare_phase,verify_fn=verify_phase):
 inputs=Path(inputs);work=Path(work);work.mkdir(parents=True,exist_ok=True)
 if config.get('phase') not in ('prepare','verify'):raise ValueError('CLOUD_STAGE_UNKNOWN')
 if not 1<=config['compressed_limit']<=300_000_000 or not 1<=config['expanded_limit']<=1_500_000_000:raise ValueError('CLOUD_STAGE_BOUNDS')
 result={'status':'STARTED','phase':config['phase']}
 try:
  raw=download(config['input_url'],config['compressed_limit'])
  if len(raw)>config['compressed_limit']:raise ValueError('INPUT_COMPRESSED_BOUND')
  extract(raw,inputs,expected=config['input_sha256'],expanded_limit=config['expanded_limit']);del raw
  if config['phase']=='prepare':result=prepare_fn(inputs,work)
  elif config['phase']=='verify':result=verify_fn(inputs,work,config)
  else:raise ValueError('CLOUD_STAGE_UNKNOWN')
 except Exception as exc:
  message=str(exc)
  try:_safe(message.encode())
  except Exception:message='REDACTED_ERROR_CONTENT'
  result={'status':'FAILED','phase':config['phase'],'error_type':type(exc).__name__,'message':message}
 finally:
  write(work/'stage-result.json',result)
  archive=work/'stage-output.zip';metadata=package(inputs,work,archive)
  upload(config['output_url'],archive.read_bytes())
 return {'status':result['status'],'phase':config['phase'],'output':metadata}


def transport(config):
 from urllib.request import Request,build_opener,HTTPRedirectHandler
 from investigator.adapters.managed_identity import Tokens
 from investigator.live_gateway import current,open_http
 class NoRedirect(HTTPRedirectHandler):
  def redirect_request(self,*args,**kwargs):raise ValueError('PLATFORM_REDIRECT_REFUSED')
 tokens=Tokens(config['identity']);opener=build_opener(NoRedirect());channel=config['channel']
 def request(url,method,raw=None,limit=300_000_000):
  if not re.fullmatch(r'https://[a-z0-9]+\.blob\.core\.windows\.net/captures/[A-Za-z0-9_./-]+',url):raise ValueError('PLATFORM_ARTIFACT_URL')
  current().http(channel,method,url)
  token=tokens.get_token('https://storage.azure.com/.default')
  headers={'Authorization':'Bearer '+token,'x-ms-version':'2023-11-03'}
  if method=='PUT':headers.update({'x-ms-blob-type':'BlockBlob','If-None-Match':'*'})
  req=Request(url,data=raw,method=method,headers=headers)
  status=None
  try:
   with open_http(opener,req,timeout=120,identity=channel) as response:
    status=response.status;body=response.read(limit+1)
    if len(body)>limit:raise ValueError('PLATFORM_RESPONSE_BOUND')
    if response.status!=(201 if method=='PUT' else 200):raise ValueError('PLATFORM_ARTIFACT_RESPONSE')
    return body
  finally:
   log=Path(os.environ['DIA_PLATFORM_CONTROL_RECEIPTS']);log.parent.mkdir(parents=True,exist_ok=True)
   with log.open('a',encoding='utf8') as stream:stream.write(json.dumps({'kind':'PLATFORM_ARTIFACT_CONTROL','method':method,'url':url,'http_status':status,'principal_id':config['identity']['principal_id'],'body_bytes':len(raw) if raw else 0})+'\n')
 return lambda url,limit:request(url,'GET',limit=limit),lambda url,raw:request(url,'PUT',raw)


def main():
 from investigator.source_revision import committed_revision
 committed_revision()
 from cloud_stage_environment import install
 install()
 config=json.loads(os.environ['DIA_CLOUD_STAGE']);download,upload=transport(config)
 print(json.dumps(run(config,download=download,upload=upload)))
if __name__=='__main__':main()

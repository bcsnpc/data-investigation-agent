"""Serial, manifest-pinned captured-operation replay; never a live fallback."""
import argparse,base64,hashlib,json,os,re,socket,subprocess,sys,traceback
from pathlib import Path,PurePosixPath
from contextlib import contextmanager

VERSION='round-thirteen-captured-replay-suite-v1'
HEX64=re.compile(r'[0-9a-f]{64}')
HEX40=re.compile(r'[0-9a-f]{40}')
METADATA_DISPATCHER='RECORDED_METADATA_DISCOVERY_V1'
METADATA_V2_DISPATCHER='RECORDED_METADATA_SQL_PROTOCOL_V2'
METADATA_V2_CONSUMERS={'acceptance/round_thirteen/'+n for n in ('metadata_revision_v2.py','metadata_worker_v2.py','replay_metadata_v2.py')}
VERIFIER_DISPATCHER='RECORDED_CODE_VERIFIER_DEPENDENCIES_V1'
BOUNDED_CONSUMER='acceptance/round_thirteen/bounded_replay_lifecycle.py'
CONSUMERS=frozenset(('acceptance/unknown_domain/recorded_engine.py','acceptance/unknown_domain/process_replay.py','acceptance/unknown_domain/lineage_replay.py','acceptance/unknown_domain/catalog_replay.py','acceptance/known_domain/private_bundle.py','scripts/investigator/budget_tape_contract.py','scripts/investigator/provider_tape_contract.py','scripts/investigator/process_tape.py','scripts/investigator/privacy_tape.py'))

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def relative(name):
 if not isinstance(name,str) or not name or '\\' in name or ':' in name:raise ValueError('SUITE_UNSAFE_PATH')
 p=PurePosixPath(name)
 if p.is_absolute() or any(x in ('..','.') for x in p.parts) or str(p)!=name:raise ValueError('SUITE_UNSAFE_PATH')
 return name
def validate(suite):
 if suite.get('version')!=VERSION:raise ValueError('SUITE_VERSION')
 if suite.get('consumer_hash_mode')!='GIT_BLOB_WITH_DECLARED_TEXT_MATERIALIZATION_V1':raise ValueError('SUITE_CONSUMER_HASH_MODE')
 if not HEX40.fullmatch(suite.get('consumer_revision','')):raise ValueError('SUITE_CONSUMER_REVISION')
 hashes=suite.get('consumer_hashes',{})
 required_consumers=CONSUMERS | ({'acceptance/round_thirteen/metadata_revision.py'} if any(o.get('dispatcher')==METADATA_DISPATCHER for o in suite.get('operations',[])) else set())
 if any(o.get('dispatcher')==METADATA_V2_DISPATCHER for o in suite.get('operations',[])):required_consumers=required_consumers|METADATA_V2_CONSUMERS
 if any(o.get('dispatcher')==VERIFIER_DISPATCHER for o in suite.get('operations',[])):required_consumers=required_consumers|{'acceptance/round_thirteen/code_verifier_revision.py'}
 if suite.get('scratch_lifecycle') is not None:
  if suite['scratch_lifecycle']!='EXCLUSIVE_SERIAL_SHARDS_V1':raise ValueError('SUITE_SCRATCH_LIFECYCLE')
  required_consumers=required_consumers|{BOUNDED_CONSUMER}
 if set(hashes)!=required_consumers or any(not isinstance(h,dict) or set(h)!={'git_blob_sha256','checkout_sha256'} or set(h['checkout_sha256'])!={'LF','CRLF'} or not HEX64.fullmatch(h['git_blob_sha256']) or any(not HEX64.fullmatch(v) for v in h['checkout_sha256'].values()) for h in hashes.values()):raise ValueError('SUITE_CANONICAL_CONSUMER_SET')
 assets=suite.get('assets');ops=suite.get('operations')
 if not isinstance(assets,list) or not isinstance(ops,list):raise ValueError('SUITE_ASSETS_OR_OPERATIONS')
 ids=set();locations=set()
 for a in assets:
  if not re.fullmatch(r'[a-zA-Z0-9_-]+',a.get('id','')) or a['id'] in ids:raise ValueError('SUITE_ASSET_ID_COLLISION')
  ids.add(a['id'])
  if not HEX64.fullmatch(a.get('ciphertext_sha256','')) or not a.get('inventory'):raise ValueError('SUITE_ASSET_HASH_OR_INVENTORY')
  if not re.fullmatch(r'https://github\.com/[^/]+/[^/]+/releases/download/[^/]+/[^/]+',a.get('url','')):raise ValueError('SUITE_RELEASE_ASSET_URL')
  for member,h in a['inventory'].items():
   relative(member)
   if not HEX64.fullmatch(h):raise ValueError('SUITE_MEMBER_HASH')
 for op in ops:
  metadata=op.get('dispatcher') in (METADATA_DISPATCHER,METADATA_V2_DISPATCHER)
  verifier=op.get('dispatcher')==VERIFIER_DISPATCHER
  if op.get('dispatcher','RECORDED_WORKSPACE') not in ('RECORDED_WORKSPACE',METADATA_DISPATCHER,METADATA_V2_DISPATCHER,VERIFIER_DISPATCHER):raise ValueError('SUITE_DISPATCHER_UNSUPPORTED')
  if not re.fullmatch(r'[a-zA-Z0-9_-]+',op.get('id','')) or op['id'] in locations:raise ValueError('SUITE_OPERATION_ID_COLLISION')
  locations.add(op['id'])
  if not op.get('run_id') or not op.get('operation') or not HEX40.fullmatch(op.get('producer_revision','')):raise ValueError('SUITE_OPERATION_IDENTITY')
  if op.get('tape_class')!='EXACT':raise ValueError('SUITE_TAPE_CLASS_UNSUPPORTED')
  if op.get('expected_status') not in ('MATCHED_CAPTURED_OPERATION','REPLAY_BLOCKED','MISSING_CAPTURE'):raise ValueError('SUITE_ROSTER_STATUS')
  if op['expected_status']=='REPLAY_BLOCKED' and not op.get('expected_blocker'):raise ValueError('SUITE_BLOCKER_CLASS_REQUIRED')
  references=[(key,op.get(key)) for key in ('tape','catalog','inventory','estate_manifest')]
  if metadata:
   if set(op.get('capture_support',{}))!={'metadata_capture.py','replay_metadata.py'} or set(op.get('after_artifacts',{}))!={'catalog-after.sqlite','inventory-after.sqlite'}:raise ValueError('SUITE_METADATA_SUPPORT_OR_AFTER_SET')
   references+=list(op['capture_support'].items())+list(op['after_artifacts'].items())
  if verifier:
   if op.get('operation')!='code_verifier' or not isinstance(op.get('dependencies'),dict) or not {'code_verifier_capture.py','verification_program.py','catalog.sqlite','inventory.sqlite'}<=set(op['dependencies']):raise ValueError('SUITE_VERIFIER_DEPENDENCIES')
   for n in op['dependencies']:
    if PurePosixPath(relative(n)).name!=n:raise ValueError('SUITE_VERIFIER_DEPENDENCY_BASENAME')
   references+=list(op['dependencies'].items())
  for key,ref in references:
   if ref is None:
    if key in ('tape','catalog','inventory') and op['expected_status']!='MISSING_CAPTURE' and not (metadata and key=='inventory'):raise ValueError('SUITE_REQUIRED_MEMBER:'+key)
    continue
   if set(ref)!={'asset','member','sha256'} or ref['asset'] not in ids:raise ValueError('SUITE_MEMBER_REFERENCE')
   relative(ref['member']);a=next(a for a in assets if a['id']==ref['asset'])
   if a['inventory'].get(ref['member'])!=ref['sha256']:raise ValueError('SUITE_MEMBER_NOT_HASH_PINNED')
 return suite
def git_revision(root,revision):
 try:actual=subprocess.check_output(['git','rev-parse',revision+'^{commit}'],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
 except subprocess.CalledProcessError as exc:raise ValueError('SUITE_GIT_REVISION_MISSING:'+revision) from exc
 if actual!=revision:raise ValueError('SUITE_GIT_REVISION_DIFFERS')
def consumers(root,suite):
 git_revision(root,suite['consumer_revision'])
 for name,h in suite['consumer_hashes'].items():
  if not (root/name).is_file() or sha(root/name) not in h['checkout_sha256'].values():raise ValueError('CANONICAL_CONSUMER_CHECKOUT_HASH_MISMATCH:'+name)
  try:data=subprocess.check_output(['git','show',suite['consumer_revision']+':'+name],cwd=root,stderr=subprocess.DEVNULL)
  except subprocess.CalledProcessError as exc:raise ValueError('CANONICAL_CONSUMER_REVISION_MEMBER_MISSING:'+name) from exc
  if hashlib.sha256(data).hexdigest()!=h['git_blob_sha256']:raise ValueError('CANONICAL_CONSUMER_REVISION_HASH_MISMATCH:'+name)
  # Exact materializations are separately pinned, never normalized on read.
  # Existing CR bytes remain content; LF->CRLF adds only the checkout newline.
  materialized={'LF':hashlib.sha256(data).hexdigest(),'CRLF':hashlib.sha256(data.replace(b'\n',b'\r\n')).hexdigest()}
  if materialized!=h['checkout_sha256']:raise ValueError('CANONICAL_CONSUMER_MATERIALIZATION_HASH_MISMATCH:'+name)
def member(root,ref):
 path=(root/ref['asset']/relative(ref['member'])).resolve()
 if not path.is_relative_to(root.resolve()):raise ValueError('SUITE_MEMBER_ESCAPES_ROOT')
 if not path.is_file():raise ValueError('SUITE_MEMBER_MISSING:'+ref['member'])
 if sha(path)!=ref['sha256']:raise ValueError('SUITE_MEMBER_CHANGED:'+ref['member'])
 return path
@contextmanager
def offline():
 def denied(*args,**kwargs):raise RuntimeError('NETWORK_FORBIDDEN')
 old=(socket.create_connection,socket.socket.connect)
 socket.create_connection=denied;socket.socket.connect=denied
 try:yield
 finally:socket.create_connection,socket.socket.connect=old
def hydrate(root,suite,output):
 sys.path.insert(0,str(root/'acceptance/known_domain'))
 from private_bundle import hydrate as decrypt
 secret=os.environ.get('KNOWN_DOMAIN_REPLAY_KEY')
 if not secret:raise ValueError('SUITE_REPLAY_KEY_MISSING')
 key=base64.b64decode(secret,validate=True)
 output.mkdir(parents=True,exist_ok=False)
 for asset in suite['assets']:
  encrypted=output/(asset['id']+'.encrypted')
  match=re.fullmatch(r'https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/releases/download/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)',asset['url'])
  if not match:raise ValueError('SUITE_RELEASE_ASSET_REFERENCE')
  owner,repo,tag,name=match.groups()
  # Existing GitHub CLI authentication supports private immutable assets.
  # No shell, wildcard, fallback source, estate auth or decryption key argument.
  subprocess.run(['gh','release','download',tag,'--repo',owner+'/'+repo,'--pattern',name,'--output',str(encrypted)],cwd=root,check=True,capture_output=True)
  if encrypted.stat().st_size>4_000_000_000:raise ValueError('SUITE_CIPHERTEXT_SIZE_BOUND')
  if asset.get('ciphertext_bytes') is not None and encrypted.stat().st_size!=asset['ciphertext_bytes']:raise ValueError('SUITE_CIPHERTEXT_SIZE_PIN_DIFFERS')
  # Existing decryptor verifies ciphertext first and every exact member before extraction.
  decrypt(encrypted,asset['ciphertext_sha256'],key,output/asset['id'],expected_members=len(asset['inventory']),inventory=asset['inventory'],expected_uncompressed_bytes=asset.get('uncompressed_bytes'))
def materialize_capture(root,op,output):
 """Assemble verified shard members into one fresh logical capture directory."""
 target=output/'materialized-captures'/op['id']/Path(op['tape']['member']).parent.name;target.mkdir(parents=True,exist_ok=False)
 references={'tape.json':op['tape'],'catalog.sqlite':op['catalog']}
 if op.get('inventory'):references['inventory.sqlite']=op['inventory']
 if op.get('estate_manifest'):references[Path(op['estate_manifest']['member']).name]=op['estate_manifest']
 for group in ('capture_support','after_artifacts','dependencies'):
  for name,ref in op.get(group,{}).items():
   if ref is not None:
    relative(name)
    if name in references and references[name]!=ref:raise ValueError('SUITE_CAPTURE_MEMBER_COLLISION')
    references[name]=ref
 for name,ref in references.items():
  source=member(root,ref)
  # The declared native basename is semantic; shards supply storage only.
  if source.name!=Path(name).name:raise ValueError('SUITE_CAPTURE_MEMBER_BASENAME')
  dest=target/relative(name);dest.parent.mkdir(parents=True,exist_ok=True)
  # Same-volume scratch hardlinks avoid a third catalog copy. They are never
  # modified by replay; recorded_engine owns its separate mutable clone.
  os.link(source,dest)
  if sha(dest)!=ref['sha256']:raise ValueError('SUITE_MATERIALIZED_MEMBER_HASH_DIFFERS')
 return target

def run(suite,member_root,output,repo,*,replay=None,load_tape=None,revision_check=None,consumer_check=None,operation_ids=None):
 validate(suite)
 if operation_ids is not None and (not isinstance(operation_ids,set) or not operation_ids or not operation_ids<=set(o['id'] for o in suite['operations'])):raise ValueError('SUITE_SELECTED_OPERATION_UNKNOWN')
 output.mkdir(parents=True,exist_ok=False)
 receipts=[]
 try:(consumer_check or consumers)(repo,suite)
 except Exception as exc:
  failure={'status':'SUITE_PREFLIGHT_BLOCKED','error_type':type(exc).__name__,'error_message':str(exc),'estate_reads':0,'model_calls':0}
  (output/'final-map.json').write_text(json.dumps(failure,indent=2));return failure
 if replay is None:
  sys.path[:0]=[str(repo/'acceptance/unknown_domain'),str(repo/'scripts')]
  from recorded_engine import replay_revision
  from investigator.process_tape import Tape
  replay=replay_revision;load_tape=Tape
 for op in suite['operations']:
  if operation_ids is not None and op['id'] not in operation_ids:continue
  receipt={'id':op['id'],'run_id':op['run_id'],'case':op.get('case'),'operation':op['operation'],'producer_revision':op['producer_revision'],'tape_class':op['tape_class'],'expected_status':op['expected_status'],'expected_blocker':op.get('expected_blocker'),'estate_reads':0,'model_calls':0}
  path=None;capture=None;capture_hashes={}
  try:
   (revision_check or git_revision)(repo,op['producer_revision'])
   if op.get('tape') is None:
    receipt['status']='MISSING_CAPTURE'
   else:
    metadata=op.get('dispatcher') in (METADATA_DISPATCHER,METADATA_V2_DISPATCHER)
    verifier=op.get('dispatcher')==VERIFIER_DISPATCHER
    path=member(member_root,op['tape']);cat=member(member_root,op['catalog']);inv=member(member_root,op['inventory']) if op.get('inventory') else None
    capture=materialize_capture(member_root,op,output)
    capture_hashes={str(p.relative_to(capture)):sha(p) for p in capture.rglob('*') if p.is_file()}
    path=capture/'tape.json';cat=capture/'catalog.sqlite';inv=capture/'inventory.sqlite' if inv is not None else None
    if cat!=path.parent/'catalog.sqlite' or inv is not None and inv!=path.parent/'inventory.sqlite':raise ValueError('SUITE_BOOTSTRAP_ARTIFACT_LOCATION')
    if metadata:
     for name,ref in {**op['capture_support'],**op['after_artifacts']}.items():
      if ref is not None and sha(path.parent/name)!=ref['sha256']:raise ValueError('SUITE_METADATA_SUPPORT_LOCATION')
    if verifier:
     if path.stat().st_size>64*1024*1024:raise ValueError('VERIFIER_SEPARATE_LARGE_TAPE_CLASS_REQUIRED')
     for name,ref in op['dependencies'].items():
      if sha(path.parent/name)!=ref['sha256']:raise ValueError('SUITE_VERIFIER_DEPENDENCY_LOCATION')
    tape=load_tape(path)
    if verifier and (tape.bootstrap['entry_point']!='code_verifier' or tape.bootstrap['state'].get('capture_contract')!='code-verifier-dependencies-v1'):raise ValueError('SUITE_VERIFIER_CAPTURE_CONTRACT')
    if verifier and {n:ref['sha256'] for n,ref in op['dependencies'].items()}!=tape.bootstrap['state']['members']:raise ValueError('SUITE_VERIFIER_SEALED_DEPENDENCIES_DIFFER')
    producer=tape.bootstrap['state']['engine_revision'] if metadata else tape.engine_revision
    if producer!=op['producer_revision']:raise ValueError('SUITE_PRODUCER_REVISION_DIFFERS_FROM_TAPE')
    if metadata and (tape.bootstrap['entry_point']!='billing_metadata_collection' or op['operation']!='billing_metadata_collection'):raise ValueError('SUITE_METADATA_OPERATION_IDENTITY')
    if hasattr(tape,'events') and not metadata and not verifier:
     import base64
     starts=[json.loads(base64.b64decode(e['body'])) for e in tape.events if e['kind']=='OPERATION_START']
     if len(starts)!=1 or starts[0]['name']!=op['operation']:raise ValueError('SUITE_CAPTURE_OPERATION_IDENTITY_DIFFERS')
     receipt['recorded_body_seals']=[{'ordinal':e['ordinal'],'kind':e['kind'],'sha256':e['sha256']} for e in tape.events if e['kind'] in ('PROVIDER_REQUEST','PROVIDER_RESPONSE','PROVIDER_FAILURE','WORKER_START','WORKER_SEND','WORKER_READ','WORKER_END','WORKER_FAILURE','BOUNDED_REQUEST','BOUNDED_RESPONSE','BOUNDED_FAILURE')]
    estate=tape.bootstrap['config'].get('_estate',{})
    enabled=any(r.get('may_infer_from_code') for r in estate.get('lineage',{}).get('code_locations',[]))
    manifest=member(member_root,op['estate_manifest']) if op.get('estate_manifest') else None
    if enabled and manifest is None:raise ValueError('SUITE_SEALED_ESTATE_MANIFEST_MISSING')
    if manifest is not None:
     from hashlib import sha256
     obj=json.loads(manifest.read_text(encoding='utf-8-sig'))
     # Same canonical JSON digest as onboarding.digest, no native assumptions.
     from investigator.onboarding import digest
     if digest(obj)!=estate.get('manifest_hash'):raise ValueError('SUITE_SEALED_ESTATE_MANIFEST_DIGEST_DIFFERS')
    if metadata:
     import importlib.util
     v2=op.get('dispatcher')==METADATA_V2_DISPATCHER
     handler_path=Path(__file__).with_name('metadata_revision_v2.py' if v2 else 'metadata_revision.py');spec=importlib.util.spec_from_file_location('metadata_revision_v2' if v2 else 'metadata_revision',handler_path);handler=importlib.util.module_from_spec(spec);spec.loader.exec_module(handler)
     with offline():
      if v2:result=handler.replay_metadata_v2_revision(path,output/op['id'],op['producer_revision'],repository=repo,consumer_hashes={n:sha(Path(__file__).with_name(n)) for n in ('metadata_worker_v2.py','replay_metadata_v2.py')})
      else:result=handler.replay_metadata_revision(path,output/op['id'],op['producer_revision'],repository=repo)
    elif verifier:
     import importlib.util
     handler_path=Path(__file__).with_name('code_verifier_revision.py');spec=importlib.util.spec_from_file_location('code_verifier_revision',handler_path);handler=importlib.util.module_from_spec(spec);spec.loader.exec_module(handler)
     with offline():result=handler.replay_code_verifier_revision(path,output/op['id'],op['producer_revision'],repository=repo)
    else:
     with offline():result=replay(path,output/op['id'],op['producer_revision'],estate_manifest=manifest)
    receipt.update(status='MATCHED_CAPTURED_OPERATION' if result.get('matched') else 'REPLAY_DIFFERED',result=result)
  except Exception as exc:receipt.update(status='REPLAY_BLOCKED',blocker=str(exc),error_type=type(exc).__name__,error_message=str(exc),traceback=traceback.format_exc())
  if path is not None:
   try:receipt['tape_sha256_after']=sha(path)
   except OSError:receipt['tape_sha256_after']=None
   receipt['sealed_tape_unchanged']=receipt['tape_sha256_after']==op['tape']['sha256']
   if not receipt['sealed_tape_unchanged']:receipt.update(status='CAPTURE_CHANGED_DURING_REPLAY',blocker='SEALED_TAPE_BYTES_CHANGED')
  if capture is not None and capture_hashes:
   changed=[]
   for name,expected in capture_hashes.items():
    try:valid=sha(capture/name)==expected
    except OSError:valid=False
    if not valid:changed.append(name)
   receipt['sealed_capture_members_unchanged']=not changed
   if changed:receipt.update(status='CAPTURE_CHANGED_DURING_REPLAY',blocker='SEALED_CAPTURE_MEMBER_BYTES_CHANGED',changed_members=changed)
  receipt['roster_match']=receipt['status']==op['expected_status'] and (receipt['status']!='REPLAY_BLOCKED' or receipt.get('blocker')==op.get('expected_blocker'))
  (output/(op['id']+'.receipt.json')).write_text(json.dumps(receipt,sort_keys=True,indent=2));receipts.append(receipt)
  (output/'partial-map.json').write_text(json.dumps({'operations':receipts,'estate_reads':0,'model_calls':0},sort_keys=True,indent=2))
 result={'operations':receipts,'counts':{k:sum(r['status']==k for r in receipts) for k in ('MATCHED_CAPTURED_OPERATION','REPLAY_BLOCKED','MISSING_CAPTURE','REPLAY_DIFFERED','CAPTURE_CHANGED_DURING_REPLAY')},'roster_matched':all(r['roster_match'] for r in receipts),'estate_reads':0,'model_calls':0,'scope':'Captured operation roster, not successful investigations or live accuracy.'}
 (output/'final-map.json').write_text(json.dumps(result,sort_keys=True,indent=2));return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--suite',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--members',type=Path);p.add_argument('--hydrate',action='store_true');p.add_argument('--scratch-parent',type=Path);p.add_argument('--repo',type=Path,default=Path.cwd());a=p.parse_args()
 suite=validate(json.loads(a.suite.read_text()));consumers(a.repo,suite)
 if a.hydrate and a.members is not None:p.error('Choose hydrate or explicit member root')
 members=a.output.with_name(a.output.name+'-members') if a.hydrate else a.members
 if members is None:p.error('Declared member root or hydrate required; no fallback')
 if a.hydrate:
  if suite.get('scratch_lifecycle')!='EXCLUSIVE_SERIAL_SHARDS_V1':p.error('Bounded scratch lifecycle contract required for hydration')
  from bounded_replay_lifecycle import run_bounded
  result=run_bounded(suite,a.output,a.scratch_parent or a.output.parent,a.repo,validate=validate,consumers=consumers,hydrate=hydrate,run=run)
 else:result=run(suite,members,a.output,a.repo)
 print(json.dumps({k:v for k,v in result.items() if k!='operations'}));raise SystemExit(0 if result.get('roster_matched') else 1)
if __name__=='__main__':main()

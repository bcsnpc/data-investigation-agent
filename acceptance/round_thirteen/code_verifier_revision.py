"""Sealed metadata helper dispatched in exact archived producer code, offline."""
import io,json,re,subprocess,sys,tarfile,tempfile
from pathlib import Path
def replay_code_verifier_revision(path,output,revision,*,estate_manifest=None,repository=None):
 root=Path(repository or Path.cwd())
 if Path(path).stat().st_size>64*1024*1024:raise ValueError('VERIFIER_SEPARATE_LARGE_TAPE_CLASS_REQUIRED')
 if not re.fullmatch('[0-9a-f]{40}',revision):raise ValueError('VERIFIER_IMMUTABLE_PRODUCER_REVISION_REQUIRED')
 actual=subprocess.check_output(['git','rev-parse',revision+'^{commit}'],cwd=root,text=True).strip()
 if actual!=revision:raise ValueError('VERIFIER_PRODUCER_REVISION_DIFFERS')
 archive=subprocess.check_output(['git','archive','--format=tar',revision],cwd=root)
 with tempfile.TemporaryDirectory(prefix='dia-verifier-producer-') as td:
  isolated=Path(td)
  with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
   for member in bundle.getmembers():
    if member.issym() or member.islnk() or not (isolated/member.name).resolve().is_relative_to(isolated.resolve()):raise ValueError('VERIFIER_UNSAFE_PRODUCER_ARCHIVE')
   bundle.extractall(isolated,filter='data')
  driver=isolated/'verifier-replay-driver.py';answer=isolated/'answer.json'
  driver.write_text('''import base64,hashlib,importlib.util,json,socket,sys,traceback
from pathlib import Path
root=Path(__file__).parent;capture=Path(sys.argv[1]).resolve();output=Path(sys.argv[2]).resolve();revision=sys.argv[3];answer=Path(sys.argv[4])
def denied(*a,**k):raise RuntimeError('NETWORK_FORBIDDEN')
socket.create_connection=denied;socket.socket.connect=denied
sys.path[:0]=[str(root/'scripts'),str(capture)]
try:
 from investigator import process_tape as journal
 from investigator.runtime import fingerprint
 tape=journal.Tape(capture/'tape.json');b=tape.bootstrap
 if b['entry_point']!='code_verifier' or b['state'].get('capture_contract')!='code-verifier-dependencies-v1':raise ValueError('VERIFIER_DEPENDENCY_CONTRACT_MISSING')
 if tape.engine_revision!=revision or b['state']['engine_revision']!=revision:raise ValueError('VERIFIER_SEALED_PRODUCER_REVISION_MISMATCH')
 actual_materialized_fingerprint=fingerprint()
 for name,expected in {n:h for n,h in b['state']['members'].items() if n in ('code_verifier_capture.py','verification_program.py')}.items():
  if name not in ('code_verifier_capture.py','verification_program.py') or hashlib.sha256((capture/name).read_bytes()).hexdigest()!=expected:raise ValueError('VERIFIER_CAPTURE_SUPPORT_CHANGED')
 if set({n:h for n,h in b['state']['members'].items() if n in ('code_verifier_capture.py','verification_program.py')})!={'code_verifier_capture.py','verification_program.py'}:raise ValueError('VERIFIER_CAPTURE_SUPPORT_SET')
 if (root/'.local').exists():raise ValueError('VERIFIER_PRIVATE_FALLBACK_FORBIDDEN')
 spec=importlib.util.spec_from_file_location('sealed_verifier_capture',capture/'code_verifier_capture.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
 # Match recorded_engine: engine identity is a sealed environmental input,
 # distinct from executing the exact producer revision's archived code.
 # Runtime identities used by this program are sealed inputs; its source is exact.
 import investigator.runtime as runtime_identity
 runtime_identity.fingerprint=lambda:b['engine_hash']
 sys.path[:]=[p for p in sys.path if '.local/round-thirteen/replay-promotion' not in p]
 result=helper.replay(capture,output)
 result.update(matched=True,replay_engine_revision=revision,recorded_engine_hash=b['engine_hash'],materialized_engine_hash=actual_materialized_fingerprint,recorded_runtime_identity_bound=True,claim='Exact producer revision and sealed verifier program replayed; native filesystem identities are preserved separately from isolated mutable clones.')
 answer.write_text(json.dumps({'result':result}))
except Exception as exc:
 answer.write_text(json.dumps({'error_type':type(exc).__name__,'reason':str(exc),'traceback':traceback.format_exc()}));raise SystemExit(1)
''',encoding='utf8')
  done=subprocess.run([sys.executable,str(driver),str(Path(path).parent.resolve()),str(Path(output).resolve()),revision,str(answer)],cwd=isolated,capture_output=True,text=True,timeout=900)
  if not answer.is_file():raise ValueError('VERIFIER_REPLAY_WORKER_FAILED_WITHOUT_RECEIPT:'+str(done.returncode))
  result=json.loads(answer.read_text())
  if 'result' not in result:raise ValueError(result.get('reason','VERIFIER_REPLAY_FAILED'))
  value=result['result'];value['capture_sha256']=__import__('hashlib').sha256(Path(path).read_bytes()).hexdigest()
  (Path(output)/'portable-replay-summary.json').write_text(json.dumps(value,sort_keys=True,indent=2),encoding='utf8')
  return value

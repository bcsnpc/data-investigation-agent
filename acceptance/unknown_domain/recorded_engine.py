"""Isolated, zero-network replay using an explicitly pinned Git engine revision.

Tape format and replay-engine revision are separate contracts. Legacy bindings
are hash-bound annotations, not modifications to the sealed evidence.
"""
import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replay_revision(path, output, revision, *, estate_manifest=None):
    if not isinstance(revision, str) or not re.fullmatch('[0-9a-f]{40}', revision):
        raise ValueError('Replay revision must be an immutable Git commit')
    accounting_version=2 if subprocess.run(['git','merge-base','--is-ancestor','7abaabf37812b58cc74b684de9cafc172212c1ad',revision],cwd=ROOT,capture_output=True).returncode==0 else 1
    actual = subprocess.check_output(['git', 'rev-parse', revision + '^{commit}'], cwd=ROOT, text=True).strip()
    if actual != revision:raise ValueError('Replay revision differs')
    archive = subprocess.check_output(['git', 'archive', '--format=tar', revision], cwd=ROOT)
    with tempfile.TemporaryDirectory(prefix='dia-recorded-engine-') as folder:
        root = Path(folder)
        with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
            for member in bundle.getmembers():
                target = (root / member.name).resolve()
                if not target.is_relative_to(root.resolve()) or member.issym() or member.islnk():
                    raise ValueError('Unsafe replay archive member')
            bundle.extractall(root, filter='data')
        driver = root / 'replay-pinned-driver.py'
        driver.write_text("""import sys,json,socket,traceback,importlib.util
from pathlib import Path
root=Path(__file__).parent
sys.path[:0]=[str(root/'scripts'),str(root/'acceptance/unknown_domain')]
def refused(*a,**k):raise RuntimeError('NETWORK_FORBIDDEN')
socket.create_connection=refused;socket.socket.connect=refused
try:
 from investigator import process_tape as journal
 spec=importlib.util.spec_from_file_location('budget_tape_contract',sys.argv[5])
 contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
 provider_spec=importlib.util.spec_from_file_location('provider_tape_contract',sys.argv[6])
 provider_contract=importlib.util.module_from_spec(provider_spec);provider_spec.loader.exec_module(provider_contract)
 contract.install(journal,provider_equal=provider_contract.equal)
 import process_replay
 lineage_spec=importlib.util.spec_from_file_location('lineage_replay',sys.argv[7])
 lineage=importlib.util.module_from_spec(lineage_spec);lineage_spec.loader.exec_module(lineage)
 tape=journal.Tape(sys.argv[1])
 with lineage.install(process_replay,tape,sys.argv[8] or None):
  result=process_replay.replay(sys.argv[1],sys.argv[2],allow_engine_drift=True)
 result['replay_engine_revision']=sys.argv[3]
 Path(sys.argv[4]).write_text(json.dumps({'result':result}))
except Exception as exc:
 Path(sys.argv[4]).write_text(json.dumps({'error_type':type(exc).__name__,'reason':str(exc)}))
 raise SystemExit(1)
""", encoding='utf-8')
        answer = root / 'answer.json'
        done = subprocess.run([sys.executable, str(driver), str(Path(path).resolve()),
            str(Path(output).resolve()), revision, str(answer), str(ROOT/'scripts/investigator/budget_tape_contract.py'), str(ROOT/'scripts/investigator/provider_tape_contract.py'),
            str(ROOT/'acceptance/unknown_domain/lineage_replay.py'),str(Path(estate_manifest).resolve()) if estate_manifest is not None else ''], cwd=ROOT, capture_output=True, text=True, timeout=900)
        if not answer.exists():raise ValueError('Pinned replay worker failed without response: ' + str(done.returncode))
        value = json.loads(answer.read_text())
        if 'result' not in value:
            from investigator.process_tape import TapeError
            raise TapeError(value.get('reason', 'PINNED_REPLAY_FAILED'))
        value['result']['replay_accounting_version']=accounting_version
        return value['result']

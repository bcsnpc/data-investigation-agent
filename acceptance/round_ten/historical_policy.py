"""Exact archived checker for explicitly sealed cohorts; current audit stays separate."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
POLICY = Path(__file__).with_name('historical-policy.json')


def select(roster_path, selected):
    policy = json.loads(POLICY.read_text())
    seal = hashlib.sha256(Path(roster_path).read_bytes()).hexdigest()
    cohort = next((c for c in policy['cohorts'] if c['roster_sha256'] == seal), None)
    if cohort is None:
        return None  # New/unpinned captures never inherit archived policy.
    if selected not in cohort['entries']:
        raise ValueError('HISTORICAL_COHORT_ENTRY_DIFFERS')
    return policy


def grade(policy, case, column, run):
    """Run the real pinned checker and dependencies in an isolated, offline process."""
    revision = policy['revision']
    archive = subprocess.check_output(['git', '-c', 'core.autocrlf=false',
        '-c', 'core.eol=lf', 'archive', '--format=tar', revision], cwd=ROOT)
    if hashlib.sha256(archive).hexdigest() != policy['archive_sha256']:
        raise ValueError('HISTORICAL_POLICY_ARCHIVE_DIFFERS')
    with tempfile.TemporaryDirectory(prefix='dia-historical-policy-') as folder:
        root = Path(folder)
        with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
            for member in bundle.getmembers():
                target = (root / member.name).resolve()
                if not target.is_relative_to(root.resolve()) or member.issym() or member.islnk():
                    raise ValueError('Unsafe historical policy archive member')
            bundle.extractall(root, filter='data')
        checker = root / 'acceptance/round_ten/check.py'
        if hashlib.sha256(checker.read_bytes()).hexdigest() != policy['checker_sha256']:
            raise ValueError('HISTORICAL_POLICY_CHECKER_DIFFERS')
        for name, expected in policy['module_sha256'].items():
            if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
                raise ValueError('HISTORICAL_POLICY_MODULE_DIFFERS:' + name)
        request = root / 'grade-input.json'
        request.write_text(json.dumps({'case': case, 'column': column, 'run': run}))
        driver = root / 'grade-driver.py'
        driver.write_text('''import importlib.util,json,socket,sys
from pathlib import Path
def denied(*args,**kwargs):raise RuntimeError('NETWORK_FORBIDDEN')
socket.create_connection=denied;socket.socket.connect=denied
root=Path(__file__).parent
spec=importlib.util.spec_from_file_location('exact_historical_checker',root/'acceptance/round_ten/check.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
request=json.loads((root/'grade-input.json').read_text())
print(json.dumps(checker.grade(request['case'],request['column'],request['run'])))
''')
        result = subprocess.run([sys.executable, str(driver)], cwd=root,
                                capture_output=True, text=True, timeout=90, check=True)
        return json.loads(result.stdout)

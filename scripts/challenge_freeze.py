"""Operator-only engine freeze manifest. Never imported by investigation runtime."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def create(policy_paths):
    if git('status', '--porcelain', '--untracked-files=no').strip():
        raise ValueError('Commit changes before freezing')
    # Broad snapshot includes prompts, adapters, validators, dependencies and UI.
    # Publisher/evaluator additions after freeze cannot change these existing files.
    paths = git('ls-files', 'scripts', 'infra', 'apps/investigator-workspace').decode().splitlines()
    files = {p: sha((ROOT / p).read_bytes()) for p in paths}
    return {'version': 1, 'created': datetime.now(timezone.utc).isoformat(),
            'commit': git('rev-parse', 'HEAD').decode().strip(), 'files': files,
            'policy_files': {str(Path(p).resolve()): sha(Path(p).read_bytes()) for p in policy_paths},
            'rule': 'No engine changes or evaluator answers in runtime context; a correction requires a fresh freeze and variant.'}


def verify(manifest):
    if manifest['version'] != 1:
        raise ValueError('Unknown freeze version')
    for name, expected in manifest['files'].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or sha(path.read_bytes()) != expected:
            raise ValueError('Frozen engine file changed: ' + name)
    for name, expected in manifest['policy_files'].items():
        if sha(Path(name).read_bytes()) != expected:
            raise ValueError('Frozen connection or usage policy changed')
    return {'status': 'UNCHANGED', 'commit': manifest['commit'], 'files': len(manifest['files'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['create', 'verify'])
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--policy', type=Path, action='append', default=[])
    args = parser.parse_args()
    if args.action == 'create':
        value = create(args.policy)
        with args.manifest.open('x', encoding='utf-8') as handle:
            json.dump(value, handle, indent=2)
    else:
        value = json.loads(args.manifest.read_text(encoding='utf-8'))
    print(json.dumps(dict(verify(value), manifest_sha256=sha(args.manifest.read_bytes()))))


if __name__ == '__main__':
    main()

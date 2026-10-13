"""Stage only tracked executable source and requirements for a public image.

Never copy the repository wholesale. No data JSON, databases, captures, receipts,
secrets, acceptance answers, .git or .local files enter this context.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess

PUBLIC_CODE_POLICIES = frozenset({'infra/scripts/WorkerResponseBounds.json',
    'acceptance/model_steps/intake-resolution-policy.json'})


def admitted(name):
    path = PurePosixPath(name)
    if any(part.startswith('.') or part in {'__pycache__', 'node_modules'} for part in path.parts):
        return False
    return (name in PUBLIC_CODE_POLICIES or name == 'scripts/investigator/windows_ocr.ps1'
            or (path.parts[0] in {'scripts', 'acceptance'} and path.suffix == '.py')
            or (path.parent == PurePosixPath('scripts') and path.name.startswith('requirements-') and path.suffix == '.txt')
            or (path.parent == PurePosixPath('infra/scripts') and path.suffix == '.ps1')
            or name == 'infra/cloud-worker/Dockerfile')


def stage(repo, destination):
    repo = Path(repo).resolve(); destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError('BUILD_CONTEXT_MUST_BE_NEW')
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=repo).decode().split('\0')
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=all'],cwd=repo,text=True)
    if dirty.strip():raise ValueError('BUILD_REQUIRES_CLEAN_COMMITTED_SOURCE')
    entries = []
    for name in names:
        if not name or not admitted(name): continue
        source = repo / name
        if source.is_symlink() or not source.resolve().is_relative_to(repo):
            raise ValueError('BUILD_CONTEXT_SYMLINK')
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        entries.append({'path': name, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    if not (destination / 'infra/cloud-worker/Dockerfile').is_file():
        raise ValueError('TRACKED_DOCKERFILE_REQUIRED')
    (destination / 'image-source-manifest.json').write_text(json.dumps({'version': 2, 'engine_revision':revision, 'files': entries}, indent=2) + '\n')
    print(json.dumps({'files': len(entries), 'context': str(destination), 'private_artifacts': 0}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); stage(args.repo, args.output)

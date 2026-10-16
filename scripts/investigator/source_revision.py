"""Commit provenance from Git or a hash-verified code-only image manifest."""
import hashlib,json,re,subprocess
from pathlib import Path


def committed_revision(root=None):
    root=Path(root or Path(__file__).resolve().parents[2]).resolve()
    from .runtime import FINGERPRINT_TRANSPORTS,fingerprint_files
    from .worker_launch import options
    if (root/'.git').exists():
        launch=options({'cwd':root,'text':True})
        dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','scripts/investigator',*FINGERPRINT_TRANSPORTS],**launch)
        if dirty.strip():raise ValueError('TAPE_UNCOMMITTED_ENGINE')
        return subprocess.check_output(['git','rev-parse','HEAD'],**launch).strip()
    manifest=json.loads((root/'image-source-manifest.json').read_bytes())
    if set(manifest)!={'version','engine_revision','files'} or manifest['version']!=2 or not re.fullmatch('[0-9a-f]{40}',manifest['engine_revision']):
        raise ValueError('IMAGE_SOURCE_PROVENANCE_REQUIRED')
    entries=manifest['files'];mapping={e['path']:e['sha256'] for e in entries}
    if len(entries)!=len(mapping):raise ValueError('IMAGE_SOURCE_DUPLICATE')
    _,required=fingerprint_files(root)
    if not {p.relative_to(root).as_posix()for p in required}<=set(mapping):raise ValueError('IMAGE_ENGINE_FILE_MISSING')
    # Dockerfile is build input, not copied into the runtime filesystem.
    for name,expected in mapping.items():
        path=Path(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name:raise ValueError('IMAGE_SOURCE_PATH')
        if name=='infra/cloud-worker/Dockerfile':continue
        file=root/path
        if file.is_symlink() or not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=expected:
            raise ValueError('IMAGE_SOURCE_CHANGED:'+name)
    actual={p.relative_to(root).as_posix() for folder in ('scripts','acceptance') for p in (root/folder).rglob('*.py') if '__pycache__' not in p.parts}
    if not actual<=set(mapping):raise ValueError('IMAGE_UNDECLARED_EXECUTABLE')
    return manifest['engine_revision']

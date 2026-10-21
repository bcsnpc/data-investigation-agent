"""Ephemeral successful-audit reuse for sealed files in one runner instance."""
from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
import json
from pathlib import Path

ACTIVE=ContextVar('run_database_audits',default=None)
STAGE='sqlite-normalized-cells-raw-blob-v1'


def environment_identity():
    from .planner_recording import secret_environment
    return hashlib.sha256(json.dumps(sorted(secret_environment()),ensure_ascii=False).encode()).hexdigest()


def detector_identity(detector):
    # The callable itself is held in the in-memory key, so Python cannot recycle
    # its identity while the successful result is live. Nothing is serialized.
    return (detector,environment_identity())


def identity(path):
    path=Path(path)
    if path.is_symlink() or getattr(path.lstat(),'st_file_attributes',0)&0x400:
        raise ValueError('AUDIT_SEALED_FILE_LINK')
    for suffix in ('-wal','-shm','-journal'):
        if Path(str(path)+suffix).exists():raise ValueError('AUDIT_SQLITE_SIDECAR_PRESENT')
    whole=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):whole.update(block)
    for suffix in ('-wal','-shm','-journal'):
        if Path(str(path)+suffix).exists():raise ValueError('AUDIT_SQLITE_SIDECAR_PRESENT')
    return whole.hexdigest()


@contextmanager
def scope():
    token=ACTIVE.set(set())
    try:yield
    finally:ACTIVE.reset(token)


def invalidate():
    state=ACTIVE.get()
    if state is not None:state.clear()


def checked(path,profile,detector,perform):
    """Hash every byte even on reuse; a failed/unstable audit registers nothing."""
    state=ACTIVE.get();before=identity(path);guard=detector_identity(detector)
    key=(before,profile,guard)
    if state is not None and key in state:return before
    perform()
    if detector_identity(detector)!=guard:raise ValueError('AUDIT_ENVIRONMENT_CHANGED')
    if identity(path)!=before:raise ValueError('AUDIT_FILE_CHANGED_DURING_CHECK')
    if state is not None:state.add(key)
    return before


def certify_snapshot(path,detector,guard,expected):
    """Only a successfully audited, written destination earns stage trust.

    Caller audited schema, normalized strings and BOTH raw/normalized BLOBs.
    Source main-file bytes are never certified from an SQLite backup.
    """
    if detector_identity(detector)!=guard:raise ValueError('AUDIT_ENVIRONMENT_CHANGED')
    actual=identity(path)
    if actual!=expected:raise ValueError('AUDIT_SNAPSHOT_CHANGED')
    state=ACTIVE.get()
    if state is not None:state.add((actual,STAGE,guard))

"""Versioned storage envelope; sealed original tape bytes remain untouched."""
import hashlib
import json
from pathlib import Path
import tempfile
from contextlib import contextmanager
from .artifact_store import ArtifactError, Files, canonical, digest, hash_id

VERSION = 'snapshot-referenced-tape-v1'
CLASSES = frozenset({'EXACT', 'PRIVACY_PROJECTED'})


def pack(directory, files, *, tape_class, final_files=None):
    root = Path(directory)
    if tape_class not in CLASSES:
        raise ArtifactError('TAPE_CLASS_REQUIRED')
    if tape_class == 'PRIVACY_PROJECTED':
        # Privacy capture owns projection BEFORE disk. Never guess that an
        # arbitrary legacy tape is projected because an operator says so.
        raise ArtifactError('PROJECTED_BUNDLE_REQUIRES_INSTALLATION_CAPTURE_ADAPTER')
    tape = root / 'tape.json'
    source = json.loads(tape.read_bytes())
    from .process_tape import Tape
    sealed = Tape(tape)  # original seal, event conservation and snapshot hashes
    entries = {}
    for name in ('catalog.sqlite', 'inventory.sqlite', 'tape.json', 'tape.events.jsonl'):
        path = root / name
        if path.exists():
            entries[name] = files.capture(path)
    expected = sealed.bootstrap.get('state', {}).get('artifacts', {})
    for name, identity in expected.items():
        if entries.get(name, {}).get('sha256') != identity:
            raise ArtifactError('BOOTSTRAP_REFERENCE_DIFFERS')
    final = {}
    for name, path in (final_files or {}).items():
        if name not in expected:
            raise ArtifactError('UNKNOWN_FINAL_STATE')
        final[name] = files.capture(path)
    value = {'version': VERSION, 'tape_class': tape_class,
             'source_tape_version': source['version'], 'source_seal': source['seal'],
             'files': entries, 'final_state': final,
             'write_capture': 'NATIVE_FINAL_SNAPSHOT' if final else 'LEGACY_WRITES_REPLAYED_FROM_OPERATIONS'}
    value['seal'] = digest(canonical(value))
    return value


def validate(value):
    fields = {'version', 'tape_class', 'source_tape_version', 'source_seal',
              'files', 'final_state', 'write_capture', 'seal'}
    if not isinstance(value, dict) or set(value) != fields or value['version'] != VERSION:
        raise ArtifactError('BUNDLE_SCHEMA')
    if value['tape_class'] != 'EXACT':
        raise ArtifactError('BUNDLE_CLASS_UNSUPPORTED')
    if digest(canonical({k: v for k, v in value.items() if k != 'seal'})) != value['seal']:
        raise ArtifactError('BUNDLE_SEAL')
    if not {'catalog.sqlite', 'inventory.sqlite', 'tape.json'} <= value['files'].keys():
        raise ArtifactError('BUNDLE_STARTING_STATE_MISSING')
    if not set(value['files']) <= {'catalog.sqlite', 'inventory.sqlite', 'tape.json', 'tape.events.jsonl'}:
        raise ArtifactError('BUNDLE_FILE_NOT_ALLOWED')
    if not set(value['final_state']) <= {'catalog.sqlite', 'inventory.sqlite'}:
        raise ArtifactError('BUNDLE_FINAL_NOT_ALLOWED')
    expected = 'NATIVE_FINAL_SNAPSHOT' if value['final_state'] else 'LEGACY_WRITES_REPLAYED_FROM_OPERATIONS'
    if value['write_capture'] != expected:
        raise ArtifactError('BUNDLE_WRITE_PROVENANCE')
    for entry in [*value['files'].values(), *value['final_state'].values()]:
        if set(entry) != {'sha256', 'bytes'} or type(entry['bytes']) is not int or entry['bytes'] < 0:
            raise ArtifactError('BUNDLE_REFERENCE')
        hash_id(entry['sha256'])
    return value


@contextmanager
def materialize(bundle, files, *, temporary_parent=None):
    value = validate(bundle)
    with tempfile.TemporaryDirectory(prefix='tape-replay-', dir=temporary_parent) as temporary:
        root = Path(temporary)
        for name, reference in value['files'].items():
            path = files.restore(reference['sha256'], root / name)
            if path.stat().st_size != reference['bytes']:
                raise ArtifactError('BUNDLE_SIZE_DIFFERS')
        source = json.loads((root / 'tape.json').read_bytes())
        if source['seal'] != value['source_seal'] or source['version'] != value['source_tape_version']:
            raise ArtifactError('BUNDLE_SOURCE_DIFFERS')
        from .process_tape import Tape
        Tape(root / 'tape.json')
        yield root / 'tape.json'

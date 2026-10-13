"""Immutable content-addressed artifact storage; no credentials in manifests.

Files are keyed by their full SHA-256 and represented by reusable compressed
chunks. A small change to a catalog therefore does not duplicate its unchanged
pages. Hashes are verified on both publication and restoration.
"""
from contextlib import contextmanager
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tempfile

VERSION = 'content-addressed-file-v1'
CHUNK_SIZE = 1024 * 1024
HASH = re.compile(r'^[0-9a-f]{64}$')


class ArtifactError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf8')


def hash_id(value):
    if not isinstance(value, str) or not HASH.fullmatch(value):
        raise ArtifactError('INVALID_CONTENT_ADDRESS')
    return value


class LocalObjects:
    """Offline/cache backend. Remote persistence uses the identical object keys."""
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key):
        if not re.fullmatch(r'(chunks|files)/[0-9a-f]{64}', key):
            raise ArtifactError('INVALID_OBJECT_KEY')
        return self.root / key

    def put(self, key, data):
        destination = self._path(key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Atomic publication, safe for parallel recorders. Never overwrite.
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as f:
            temporary = Path(f.name)
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        try:
            try:
                os.link(temporary, destination)
            except FileExistsError:
                if destination.read_bytes() != data:
                    raise ArtifactError('IMMUTABLE_OBJECT_CONFLICT')
        finally:
            temporary.unlink(missing_ok=True)

    def get(self, key):
        return self._path(key).read_bytes()


class Files:
    def __init__(self, objects):
        self.objects = objects

    def capture(self, source):
        """Caller supplies a consistent sealed/projected file, never a live DB."""
        chunks = []
        total = 0
        whole = hashlib.sha256()
        with Path(source).open('rb') as stream:
            while block := stream.read(CHUNK_SIZE):
                identity = digest(block)
                self.objects.put('chunks/' + identity, gzip.compress(block, compresslevel=6, mtime=0))
                whole.update(block)
                total += len(block)
                chunks.append({'sha256': identity, 'bytes': len(block)})
        identity = whole.hexdigest()
        manifest = {'version': VERSION, 'sha256': identity, 'bytes': total,
                    'chunk_bytes': CHUNK_SIZE, 'chunks': chunks}
        self.objects.put('files/' + identity, canonical(manifest))
        return {'sha256': identity, 'bytes': total}

    def describe(self, identity):
        hash_id(identity)
        value = json.loads(self.objects.get('files/' + identity))
        if set(value) != {'version', 'sha256', 'bytes', 'chunk_bytes', 'chunks'}:
            raise ArtifactError('FILE_MANIFEST_FIELDS')
        if value['version'] != VERSION or value['sha256'] != identity or value['chunk_bytes'] != CHUNK_SIZE:
            raise ArtifactError('FILE_MANIFEST_IDENTITY')
        if type(value['bytes']) is not int or value['bytes'] < 0 or not isinstance(value['chunks'], list):
            raise ArtifactError('FILE_MANIFEST_SIZE')
        total = 0
        for index, chunk in enumerate(value['chunks']):
            if set(chunk) != {'sha256', 'bytes'}:
                raise ArtifactError('CHUNK_FIELDS')
            hash_id(chunk['sha256'])
            size = chunk['bytes']
            if type(size) is not int or not 0 < size <= CHUNK_SIZE:
                raise ArtifactError('CHUNK_SIZE')
            if index < len(value['chunks']) - 1 and size != CHUNK_SIZE:
                raise ArtifactError('NONFINAL_SHORT_CHUNK')
            total += size
        if total != value['bytes']:
            raise ArtifactError('FILE_MANIFEST_SIZE')
        return value

    def restore(self, identity, destination):
        value = self.describe(identity)
        target = Path(destination)
        if target.exists():
            raise ArtifactError('RESTORE_WOULD_OVERWRITE')
        target.parent.mkdir(parents=True, exist_ok=True)
        whole = hashlib.sha256()
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as output:
            temporary = Path(output.name)
            try:
                for chunk in value['chunks']:
                    encoded = self.objects.get('chunks/' + chunk['sha256'])
                    with gzip.GzipFile(fileobj=io.BytesIO(encoded)) as zipped:
                        block = zipped.read(chunk['bytes'] + 1)
                    if len(block) != chunk['bytes'] or digest(block) != chunk['sha256']:
                        raise ArtifactError('CHUNK_INTEGRITY')
                    whole.update(block)
                    output.write(block)
                if whole.hexdigest() != identity:
                    raise ArtifactError('FILE_INTEGRITY')
                output.flush()
                os.fsync(output.fileno())
            except BaseException:
                output.close()
                temporary.unlink(missing_ok=True)
                raise
        try:
            os.link(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
        return target

    def verify(self, identity):
        with tempfile.TemporaryDirectory(prefix='artifact-verify-') as folder:
            self.restore(identity, Path(folder) / 'verified')
        return True

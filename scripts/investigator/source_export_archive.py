"""Lossless deduplicated container for an explicitly approved legacy export set.

The original path manifest and every unique byte stream are members. Original
files never move or change. Whole-bundle download verification proves the same
member bytes; only then can individual-file cleanup receipts be derived.
"""
import io
import gzip
import json
from pathlib import Path
import tarfile
from .artifact_store import ArtifactError, canonical, digest
from .archive_migration import sha_file, verify_local, privacy_approved, eligible, encoded_chunks
from .resumable_archive import publish_resumable


def build(manifest, manifest_sha, destination, *, compression='identity', max_staging_bytes=512*1024*1024):
    if digest(canonical(manifest)) != manifest_sha or (not manifest.get('source_export_roots') and
            not all(eligible(entry['path']) for entry in manifest.get('entries',[]))):
        raise ArtifactError('SOURCE_EXPORT_MANIFEST_REQUIRED')
    paths = [(entry, verify_local(manifest, entry)) for entry in manifest['entries']]
    destination = Path(destination)
    import shutil
    unique={entry['sha256']:entry['bytes'] for entry in manifest['entries']}
    upper=sum(unique.values())+len(unique)*2048+len(canonical(manifest))+10240
    if compression not in ('identity','gzip') or type(max_staging_bytes) is not int or max_staging_bytes<1:
        raise ArtifactError('ARCHIVE_STAGING_BOUND')
    needed=upper if compression=='identity' else max_staging_bytes
    if shutil.disk_usage(destination.parent).free-needed < 10*1024**3:
        raise ArtifactError('ARCHIVE_STAGING_DISK_FLOOR')
    class BoundedWriter:
        def __init__(self,stream):self.stream=stream;self.count=0
        def write(self,data):
            if self.count+len(data)>max_staging_bytes:raise ArtifactError('ARCHIVE_STAGING_BOUND')
            self.count+=len(data);return self.stream.write(data)
        def flush(self):self.stream.flush()
    with destination.open('xb') as stream:
        from contextlib import nullcontext
        compressed=(gzip.GzipFile(filename='',fileobj=BoundedWriter(stream),mode='wb',mtime=0)
                    if compression=='gzip' else nullcontext(BoundedWriter(stream)))
        with compressed as output, tarfile.open(fileobj=output, mode='w|', format=tarfile.PAX_FORMAT) as archive:
            metadata = canonical(manifest)
            info = tarfile.TarInfo('manifest.json')
            info.size = len(metadata)
            archive.addfile(info, io.BytesIO(metadata))
            seen = set()
            for entry, path in paths:
                if entry['sha256'] in seen:
                    continue
                seen.add(entry['sha256'])
                info = tarfile.TarInfo('objects/' + entry['sha256'])
                info.size = entry['bytes']
                with path.open('rb') as source:
                    archive.addfile(info, source)
    return verify_bundle(destination, manifest, manifest_sha)


def verify_bundle(path, manifest, manifest_sha):
    import hashlib
    if digest(canonical(manifest)) != manifest_sha:
        raise ArtifactError('SOURCE_EXPORT_MANIFEST_SHA')
    expected = {entry['sha256']: entry['bytes'] for entry in manifest['entries']}
    seen = set()
    names = set()
    metadata_seen = False
    end = 0
    with Path(path).open('rb') as source:compressed=source.read(2)==b'\x1f\x8b'
    opener=gzip.open if compressed else open
    with opener(path,'rb') as stream, tarfile.open(fileobj=stream, mode='r|') as archive:
        for member in archive:
            if not member.isfile() or member.name in names:
                raise ArtifactError('SOURCE_EXPORT_BUNDLE_MEMBER')
            names.add(member.name)
            end = member.offset_data + ((member.size + 511) // 512) * 512
            source = archive.extractfile(member)
            if member.name == 'manifest.json':
                if member.size != len(canonical(manifest)) or source.read() != canonical(manifest):
                    raise ArtifactError('SOURCE_EXPORT_BUNDLE_MANIFEST')
                metadata_seen = True
                continue
            identity = member.name.removeprefix('objects/')
            if member.name != 'objects/' + identity or identity not in expected or member.size != expected[identity]:
                raise ArtifactError('SOURCE_EXPORT_BUNDLE_MEMBER')
            whole = hashlib.sha256()
            for chunk in iter(lambda: source.read(1024 * 1024), b''):
                whole.update(chunk)
            if whole.hexdigest() != identity:
                raise ArtifactError('SOURCE_EXPORT_BUNDLE_MEMBER_SHA')
            seen.add(identity)
    if not metadata_seen or seen != set(expected):
        raise ArtifactError('SOURCE_EXPORT_BUNDLE_CONSERVATION')
    with opener(path,'rb') as stream:
        stream.seek(end)
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            if block.strip(b'\x00'):
                raise ArtifactError('SOURCE_EXPORT_BUNDLE_TRAILING_DATA')
    return {'source_manifest_sha256': manifest_sha, 'bundle_sha256': sha_file(path),
            'bundle_bytes': Path(path).stat().st_size, 'original_paths': len(manifest['entries']),
            'unique_objects': len(expected), 'unique_original_bytes': sum(expected.values()),
            **({'bundle_compression':'gzip'} if compressed else {})}


def bundle_manifest(path, source_manifest, source_sha, proof):
    path = Path(path).resolve(strict=True)
    if verify_bundle(path, source_manifest, source_sha) != proof:
        raise ArtifactError('SOURCE_EXPORT_BUNDLE_PROOF_CHANGED')
    return {'version': 'source-export-bundle-v1', 'workspace': str(path.parent),
            'storage_encoding': 'gzip', 'protected_paths': [],
            'source_manifest_sha256': source_sha, 'member_proof': proof,
            'entries': [{'path': path.name, 'sha256': proof['bundle_sha256'], 'bytes': proof['bundle_bytes']}]}


def publish_bundle(bundle, bundle_sha, source_manifest, source_sha, review, client, journal, *, max_stored_bytes=None):
    privacy_approved(review, source_sha)
    # Validate source seals and runtime dependencies before any remote mutation,
    # then repeat after publication before deriving per-original receipts.
    for entry in source_manifest['entries']:
        verify_local(source_manifest, entry)
    proof = bundle['member_proof']
    if bundle.get('source_manifest_sha256') != source_sha or len(bundle['entries']) != 1:
        raise ArtifactError('SOURCE_EXPORT_BUNDLE_SCOPE')
    def verified_source(current, entry):
        path = Path(current['workspace']) / entry['path']
        if path.name != entry['path'] or path.is_symlink():
            raise ArtifactError('SOURCE_EXPORT_BUNDLE_PATH')
        if verify_bundle(path, source_manifest, source_sha) != proof or entry != {
                'path': path.name, 'sha256': proof['bundle_sha256'], 'bytes': proof['bundle_bytes']}:
            raise ArtifactError('SOURCE_EXPORT_BUNDLE_PROOF_CHANGED')
        return path
    if max_stored_bytes is not None:
        if type(max_stored_bytes) is not int or max_stored_bytes < 1:
            raise ArtifactError('ARCHIVE_TRANSFER_BYTE_CAP')
        path = verified_source(bundle,bundle['entries'][0])
        measured = {}
        for _ in encoded_chunks(path,'gzip',measured): pass
        if measured['stored_bytes'] > max_stored_bytes:
            raise ArtifactError('ARCHIVE_TRANSFER_BYTE_CAP')
    # The derivation records which separately reviewed manifest supplied bytes.
    bundle_review = {**review, 'manifest_sha256': bundle_sha, 'source_manifest_sha256': source_sha}
    result = publish_resumable(bundle, bundle_sha, bundle_review, client, journal, source_verifier=verified_source)
    archived = result['objects'][0]
    objects = []
    for entry in source_manifest['entries']:
        verify_local(source_manifest, entry)
        objects.append({**entry, 'blob': archived['blob'], 'etag': archived['etag'], 'tier': 'Archive',
                        'download_verified_sha256': entry['sha256'], 'original_bytes': entry['bytes'],
                        'storage_encoding': 'gzip', 'stored_sha256': archived['stored_sha256'],
                        'stored_bytes': archived['stored_bytes'], 'stored_bytes_scope': 'WHOLE_BUNDLE_NOT_MEMBER',
                        'member': 'objects/' + entry['sha256'], 'bundle_sha256': proof['bundle_sha256'],
                        'verified_at': archived['verified_at']})
    return {'version': 'verified-archive-receipt-v1', 'manifest_sha256': source_sha, 'privacy_review': review,
            'objects': objects, 'bundle_receipt': result, 'member_proof': proof,
            'original_bytes': sum(e['bytes'] for e in source_manifest['entries']),
            'stored_bytes': archived['stored_bytes'], 'max_stored_bytes': max_stored_bytes,
            'local_deletion_performed': False}

"""Streaming archive migration. No local deletion, credential fallback or overwrite."""
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

from .archive_migration import encoded_chunks, privacy_approved, verify_download, verify_local
from .artifact_store import ArtifactError, canonical, digest
from .adapters.platform_archive import BLOCK_BYTES


class Journal:
    """Append-only, fsynced, hash-chained checkpoint scoped to one manifest/remote."""
    def __init__(self, path, manifest_sha, account_url):
        self.path = Path(path)
        self.scope = {'manifest_sha256': manifest_sha, 'account_url': account_url, 'container': 'archive'}
        self.rows = []
        self.tail = '0' * 64
        if self.path.exists():
            for line in self.path.read_bytes().splitlines():
                row = json.loads(line)
                identity = row.pop('record_sha256')
                if row.get('scope') != self.scope or row.get('previous_sha256') != self.tail or digest(canonical(row)) != identity:
                    raise ArtifactError('ARCHIVE_JOURNAL_INTEGRITY')
                self.tail = identity
                self.rows.append(row['event'])

    def append(self, event):
        row = {'scope': self.scope, 'previous_sha256': self.tail, 'event': event}
        identity = digest(canonical(row))
        with self.path.open('ab') as stream:
            stream.write(canonical({**row, 'record_sha256': identity}) + b'\n')
            stream.flush()
            os.fsync(stream.fileno())
        self.tail = identity
        self.rows.append(event)

    def last(self, key, phase):
        return next((row for row in reversed(self.rows) if row.get('blob') == key and row.get('phase') == phase), None)


def fixed_blocks(chunks):
    pending = bytearray()
    for chunk in chunks:
        pending.extend(chunk)
        while len(pending) >= BLOCK_BYTES:
            yield bytes(pending[:BLOCK_BYTES])
            del pending[:BLOCK_BYTES]
    if pending:
        yield bytes(pending)


def block_id(index, data):
    # The content-block contract uses equal-length base64 IDs. Its 64-byte identity
    # includes position and bytes, so a resumed block cannot silently change.
    return base64.b64encode(hashlib.sha256(index.to_bytes(8, 'big') + data).hexdigest().encode()).decode()


def publish_resumable(manifest, manifest_sha, review, client, journal, *, source_verifier=verify_local,
                      max_stored_bytes=None, source_encoder=None):
    privacy_approved(review, manifest_sha)
    if digest(canonical(manifest)) != manifest_sha:
        raise ArtifactError('ARCHIVE_MANIFEST_SHA_DIFFERS')
    if journal.scope != {'manifest_sha256': manifest_sha, 'account_url': client.account_url, 'container': 'archive'}:
        raise ArtifactError('ARCHIVE_JOURNAL_SCOPE')
    # The full approved set is checked before any control request is dispatched.
    paths = [source_verifier(manifest, entry) for entry in manifest['entries']]
    encoding = manifest.get('storage_encoding', 'identity')
    source_encoder=source_encoder or encoded_chunks
    if max_stored_bytes is not None:
        if type(max_stored_bytes) is not int or max_stored_bytes < 1:
            raise ArtifactError('ARCHIVE_TRANSFER_BYTE_CAP')
        measured={}
        for entry,path in zip(manifest['entries'],paths):
            identity=(entry['sha256'],entry['bytes'])
            if identity in measured:continue
            stats={}
            for _ in source_encoder(path,encoding,stats):pass
            measured[identity]=stats['stored_bytes']
            if sum(measured.values())>max_stored_bytes:
                raise ArtifactError('ARCHIVE_TRANSFER_BYTE_CAP')
    receipts = []
    first_path = {}
    for entry, path in zip(manifest['entries'], paths):
        original_path = first_path.setdefault((entry['sha256'], entry['bytes']), entry['path'])
        key = 'originals/' + entry['sha256'] + '/' + digest(original_path.encode()) + ('.gz' if encoding == 'gzip' else '')
        before = client.properties(key)
        if before and before['tier'] == 'Archive':
            prior = journal.last(key, 'ARCHIVED') or journal.last(key, 'VERIFIED')
            if (not prior or prior['etag'] != before['etag'] or prior.get('download_verified_sha256') != entry['sha256']
                    or prior.get('bytes') != entry['bytes']):
                raise ArtifactError('ARCHIVE_COLD_OBJECT_WITHOUT_MATCHING_VERIFICATION')
            receipt = {**prior, **entry, 'tier': 'Archive', 'phase': 'ARCHIVED'}
        else:
            if before and before['tier'] != 'Hot':
                raise ArtifactError('ARCHIVE_HOT_VERIFICATION_REQUIRED')
            if before is None:
                existing = client.blocks(key)
                stats = {}
                ids = []
                streamed_bytes=0
                for index, data in enumerate(fixed_blocks(source_encoder(path, encoding, stats))):
                    streamed_bytes+=len(data)
                    if max_stored_bytes is not None and streamed_bytes>measured[(entry['sha256'],entry['bytes'])]:
                        raise ArtifactError('ARCHIVE_TRANSFER_BYTE_CAP')
                    if index >= 30000:
                        raise ArtifactError('ARCHIVE_BLOCK_COUNT_BOUND')
                    identity = block_id(index, data)
                    ids.append(identity)
                    if existing.get(identity) != len(data):
                        client.stage(key, identity, data)
                        journal.append({'phase': 'BLOCK_STAGED', 'blob': key, 'block_id': identity,
                                        'index': index, 'bytes': len(data), 'sha256': digest(data)})
                client.commit(key, ids)
                before = client.properties(key)
            if not before or before['tier'] != 'Hot' or not before.get('etag'):
                raise ArtifactError('ARCHIVE_HOT_VERIFICATION_REQUIRED')
            verified = verify_download(client.download_chunks(key), encoding, entry)
            after = client.properties(key)
            if after != before:
                raise ArtifactError('ARCHIVE_OBJECT_CHANGED_DURING_VERIFICATION')
            # Persist proof BEFORE tiering. A crash cannot turn an unverified
            # object into a valid deletion receipt.
            receipt = {**entry, **verified, 'blob': key, 'etag': before['etag'], 'phase': 'VERIFIED',
                       'verified_at': datetime.now(timezone.utc).isoformat()}
            journal.append(receipt)
            client.archive(key, before['etag'])
            final = client.properties(key)
            if not final or final['tier'] != 'Archive' or not final.get('etag'):
                raise ArtifactError('ARCHIVE_TIER_NOT_CONFIRMED')
            receipt = {**receipt, 'etag': final['etag'], 'tier': 'Archive', 'phase': 'ARCHIVED'}
        if max_stored_bytes is not None and sum({row['blob']:row['stored_bytes'] for row in receipts+[receipt]}.values())>max_stored_bytes:
            raise ArtifactError('ARCHIVE_TRANSFER_BYTE_CAP')
        journal.append(receipt)
        receipts.append(receipt)
    return {'version': 'verified-archive-receipt-v1', 'manifest_sha256': manifest_sha, 'privacy_review': review,
            'objects': receipts, 'local_deletion_performed': False,
            'original_bytes': sum(row['bytes'] for row in receipts),
            'stored_bytes': sum({row['blob']:row['stored_bytes'] for row in receipts}.values())}


# Backward-compatible public import; transport decisions live in the adapter.
from .adapters.platform_archive_client import IdentityArchiveClient

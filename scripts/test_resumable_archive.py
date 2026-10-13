import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from investigator import archive_migration as old
from investigator.artifact_store import ArtifactError, canonical, digest
from investigator.resumable_archive import Journal, publish_resumable, block_id, IdentityArchiveClient
from investigator.adapters.platform_archive import bind
from investigator.live_gateway import Gateway, GatewayDenied

URL = 'https://fixture.blob.core.windows.net'
KEY = 'originals/' + 'a' * 64 + '/' + 'b' * 64


def gateway():
    return Gateway({'version': 1, 'live_enabled': True, 'identities': {'archive': {
        'role': 'platform', 'platform_archive': [{'account_url': URL, 'container': 'archive'}]}}})


class Remote:
    account_url = URL
    def __init__(self):
        self.parts, self.objects, self.tiers, self.calls = {}, {}, {}, []
        self.fail_stage = None
        self.corrupt = False
    def properties(self, key):
        return {'tier': self.tiers[key], 'etag': 'immutable'} if key in self.objects else None
    def blocks(self, key):
        return {name: len(data) for name, data in self.parts.get(key, {}).items()}
    def stage(self, key, identity, data):
        self.calls.append(('stage', identity))
        if len(self.calls) == self.fail_stage:
            raise OSError('interrupted')
        self.parts.setdefault(key, {})[identity] = data
    def commit(self, key, identities):
        assert key not in self.objects
        self.objects[key] = b''.join(self.parts.get(key, {})[i] for i in identities)
        self.tiers[key] = 'Hot'
    def download_chunks(self, key):
        yield self.objects[key] + (b'corrupt' if self.corrupt else b'')
    def archive(self, key, etag):
        assert etag == 'immutable'
        self.tiers[key] = 'Archive'


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
    def prepare(self, bodies=(b'0123456789' * 20,)):
        paths = []
        for i, body in enumerate(bodies):
            path = self.root / f'.local/round-seventeen/file-{i}.json'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
            paths.append(path.relative_to(self.root).as_posix())
        manifest = old.plan(self.root, paths, protected=[], finished_statement='Owner approved, finished')
        sha = digest(canonical(manifest))
        review = {'status': 'APPROVED', 'manifest_sha256': sha, 'reviewer': 'test', 'basis': 'synthetic'}
        journal = Journal(self.root / 'journal.jsonl', sha, URL)
        return manifest, sha, review, journal
    def test_interrupted_block_upload_resumes_without_resending_verified_blocks(self):
        manifest, sha, review, journal = self.prepare()
        remote = Remote()
        remote.fail_stage = 2
        with patch('investigator.resumable_archive.BLOCK_BYTES', 80):
            with self.assertRaises(OSError):
                publish_resumable(manifest, sha, review, remote, journal)
            remote.fail_stage = None
            reopened = Journal(journal.path, sha, URL)
            result = publish_resumable(manifest, sha, review, remote, reopened)
        first_id = remote.calls[0][1]
        self.assertEqual(sum(identity == first_id for _, identity in remote.calls), 1)
        self.assertEqual(result['objects'][0]['download_verified_sha256'], manifest['entries'][0]['sha256'])
        self.assertFalse(result['local_deletion_performed'])
        self.assertIn('Remove-Item', old.cleanup_script(manifest, sha, result))
    def test_cold_resume_needs_durable_proof_and_deduplicates_exact_copies(self):
        manifest, sha, review, journal = self.prepare((b'one', b'one', b'different metadata'))
        remote = Remote()
        result = publish_resumable(manifest, sha, review, remote, journal)
        self.assertEqual(len(remote.objects), 2)
        self.assertEqual(len(result['objects']), 3)
        self.assertEqual(result['objects'][0]['blob'], result['objects'][1]['blob'])
        reopened = Journal(journal.path, sha, URL)
        self.assertEqual(len(publish_resumable(manifest, sha, review, remote, reopened)['objects']), 3)
        with self.assertRaisesRegex(ArtifactError, 'WITHOUT_MATCHING_VERIFICATION'):
            publish_resumable(manifest, sha, review, remote, Journal(self.root / 'empty.jsonl', sha, URL))
    def test_corrupt_remote_never_archived_or_cleanup_eligible(self):
        manifest, sha, review, journal = self.prepare()
        remote = Remote()
        remote.corrupt = True
        with self.assertRaisesRegex(ArtifactError, 'REMOTE_HASH_DIFFERS'):
            publish_resumable(manifest, sha, review, remote, journal)
        self.assertEqual(set(remote.tiers.values()), {'Hot'})
        self.assertFalse(any(row['phase'] == 'VERIFIED' for row in journal.rows))
    def test_changed_source_refuses_before_remote(self):
        manifest, sha, review, journal = self.prepare()
        (self.root / manifest['entries'][0]['path']).write_bytes(b'changed')
        remote = Remote()
        with self.assertRaisesRegex(ArtifactError, 'LOCAL_HASH_DIFFERS'):
            publish_resumable(manifest, sha, review, remote, journal)
        self.assertEqual(remote.calls, [])
    def test_journal_other_remote_or_tampering_refused(self):
        manifest, sha, review, journal = self.prepare()
        journal.append({'phase': 'TEST'})
        with self.assertRaisesRegex(ArtifactError, 'JOURNAL_INTEGRITY'):
            Journal(journal.path, sha, 'https://other.blob.core.windows.net')
        journal.path.write_bytes(journal.path.read_bytes().replace(b'TEST', b'FAKE'))
        with self.assertRaisesRegex(ArtifactError, 'JOURNAL_INTEGRITY'):
            Journal(journal.path, sha, URL)
    def test_source_exports_require_explicit_scope_and_keep_both_metadata(self):
        root = '.local/source-snapshots/12345678-1234-1234-1234-123456789012'
        path = self.root / root / 'manifest.json'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'fixture metadata')
        args = dict(protected=[], finished_statement='Owner explicit duplicate export archive')
        self.assertEqual(old.plan(self.root, [root + '/manifest.json'], **args)['entries'], [])
        manifest = old.plan(self.root, [root + '/manifest.json'], source_export_roots=[root], **args)
        file = self.root / 'plan.json'
        file.write_bytes(canonical(manifest))
        self.assertEqual(len(old.load_pinned(file, digest(file.read_bytes()))['entries']), 1)
    def test_gateway_requires_request_binding_exact_bytes_and_conditional_archive(self):
        g = gateway()
        with self.assertRaises(GatewayDenied):
            g.http('archive', 'GET', URL + '/archive/' + KEY)
        with bind(g, 'archive', URL, KEY, 'STAGE', body=b'value', block_id=block_id(0, b'value')) as (method, url, headers):
            self.assertEqual(g.http('archive', method, url, body=b'value', headers=headers)['purpose'], 'platform_archive')
            with self.assertRaises(GatewayDenied):
                g.http('archive', method, url, body=b'changed', headers=headers)
            with self.assertRaises(GatewayDenied):
                g.http('archive', method, url.replace('/archive/', '/snapshots/'), body=b'value', headers=headers)
        with bind(g, 'archive', URL, KEY, 'ARCHIVE', etag='pinned') as (method, url, headers):
            with self.assertRaises(GatewayDenied):
                g.http('archive', method, url, body=b'', headers={})
            g.http('archive', method, url, body=b'', headers=headers)
    def test_raw_key_never_accepted(self):
        with self.assertRaisesRegex(ArtifactError, 'TOKEN_CREDENTIAL_REQUIRED'):
            IdentityArchiveClient(URL, 'secret-key', gateway(), 'archive', max_requests=1, receipts='unused')

    def test_real_transport_request_shape_retries_transient_but_not_auth(self):
        from investigator.adapters.guarded_transport import GuardedTransport
        class Response:
            def __init__(self, status):
                self.status_code = status
                self.headers = {'x-ms-access-tier': 'Hot', 'etag': 'pinned'}
                self.internal_response = SimpleNamespace(close=lambda: None)
        class Wire:
            def __init__(self, statuses): self.statuses, self.calls = list(statuses), []
            def send(self, request, **kwargs):
                self.calls.append(request)
                result = self.statuses.pop(0)
                if isinstance(result, Exception): raise result
                return Response(result)
        for statuses, cap, expected in [([429, 200], 2, None), ([403], 3, 'HTTP_403'),
                                        ([429, 200], 1, 'CONTROL_CAP_REACHED')]:
            g = gateway()
            wire = Wire(statuses)
            log = self.root / ('controls-' + str(statuses[0]) + '-' + str(cap))
            transport = GuardedTransport(g, 'archive', receipts=log, inner=wire)
            credential = SimpleNamespace(get_token=lambda audience: SimpleNamespace(token='synthetic-token'))
            client = IdentityArchiveClient(URL, credential, g, 'archive', max_requests=cap,
                      receipts=log, transport=transport, sleep=lambda _: None)
            if expected:
                with self.assertRaisesRegex(ArtifactError, expected): client.properties(KEY)
            else:
                self.assertEqual(client.properties(KEY), {'tier': 'Hot', 'etag': 'pinned'})
            self.assertNotIn('synthetic-token', log.read_text())
            dispatched = [json.loads(line) for line in log.read_text().splitlines() if json.loads(line)['phase'] == 'DISPATCHED']
            self.assertEqual(len(dispatched), len(wire.calls))
            self.assertLessEqual(len(wire.calls), cap)
        from azure.core.exceptions import ServiceResponseError
        log = self.root / 'network-controls'
        wire = Wire([ServiceResponseError('connection reset'), 200])
        g = gateway()
        client = IdentityArchiveClient(URL, credential, g, 'archive', max_requests=2, receipts=log,
                 transport=GuardedTransport(g, 'archive', receipts=log, inner=wire), sleep=lambda _: None)
        self.assertEqual(client.properties(KEY)['etag'], 'pinned')
        resumed = IdentityArchiveClient(URL, credential, g, 'archive', max_requests=2, receipts=log,
                  transport=GuardedTransport(g, 'archive', receipts=log, inner=wire))
        with self.assertRaisesRegex(ArtifactError, 'CONTROL_CAP_REACHED'): resumed.properties(KEY)

    def test_gzip_stored_and_original_hashes_are_both_recorded(self):
        manifest, _, _, _ = self.prepare()
        manifest['storage_encoding'] = 'gzip'
        sha = digest(canonical(manifest))
        review = {'status': 'APPROVED', 'manifest_sha256': sha, 'reviewer': 'test', 'basis': 'synthetic'}
        result = publish_resumable(manifest, sha, review, Remote(), Journal(self.root / 'gzip.jsonl', sha, URL))
        row = result['objects'][0]
        self.assertEqual(row['download_verified_sha256'], row['sha256'])
        self.assertNotEqual(row['stored_sha256'], row['sha256'])
        self.assertLess(row['stored_bytes'], row['original_bytes'])


if __name__ == '__main__':
    unittest.main()

from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
import json
import sys
import time
from unittest.mock import patch
from investigator.artifact_store import ArtifactError, digest
from platform_blob_transfer import transfer


class Tests(unittest.TestCase):
    def test_explicit_cli_uses_only_storage_scope_and_never_lists_keys(self):
        from investigator.adapters.platform_credentials import OwnerCliCredential
        credential = OwnerCliCredential(sys.executable, 'tenant', 'subscription')
        value = {'accessToken': 'synthetic-token', 'expires_on': int(time.time()) + 600,
                 'tenant': 'tenant', 'subscription': 'subscription'}
        with patch('subprocess.run', return_value=SimpleNamespace(returncode=0,stdout=json.dumps(value))) as run:
            self.assertEqual(credential.get_token('https://storage.azure.com/.default').token, 'synthetic-token')
            credential.get_token('https://storage.azure.com/.default')
            self.assertEqual(run.call_count, 1)
            self.assertIn('get-access-token', run.call_args.args[0])
            self.assertNotIn('keys', run.call_args.args[0])
            self.assertNotIn('--tenant', run.call_args.args[0])
            self.assertIn('--subscription', run.call_args.args[0])
            with self.assertRaisesRegex(ValueError, 'STORAGE_SCOPE_ONLY'):
                credential.get_token('https://database.windows.net/.default')

    def test_token_credential_only_and_verified_download_preserves_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'result'
            args = dict(gateway=SimpleNamespace(http=lambda *a: None), channel='owner', controls='unused')
            with self.assertRaisesRegex(ArtifactError, 'TOKEN_CREDENTIAL_REQUIRED'):
                transfer('get', 'https://fixture.blob.core.windows.net/captures/result', path, digest(b'ok'), credential='raw-key', **args)
            credential = SimpleNamespace(get_token=lambda _: None)
            fake = SimpleNamespace(download_blob=lambda **kw: SimpleNamespace(chunks=lambda: iter([b'wrong'])))
            with patch('azure.storage.blob.BlobClient.from_blob_url', return_value=fake):
                with self.assertRaisesRegex(ArtifactError, 'DOWNLOAD_SHA_DIFFERS'):
                    transfer('get', 'https://fixture.blob.core.windows.net/captures/result', path, digest(b'ok'), credential=credential, **args)
            self.assertFalse(path.exists())
            self.assertEqual(path.with_name('result.partial').read_bytes(), b'wrong')

    def test_upload_is_hash_pinned_and_immutable(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'input'
            path.write_bytes(b'fixture')
            calls = []
            fake = SimpleNamespace(upload_blob=lambda stream, **kw: calls.append((stream.read(), kw)))
            args = dict(credential=SimpleNamespace(get_token=lambda _: None), gateway=SimpleNamespace(http=lambda *a: None),
                        channel='owner', controls='unused')
            with patch('azure.storage.blob.BlobClient.from_blob_url', return_value=fake):
                with self.assertRaisesRegex(ArtifactError, 'UPLOAD_INPUT_HASH'):
                    transfer('put', 'https://fixture.blob.core.windows.net/captures/input', path, '0' * 64, **args)
                transfer('put', 'https://fixture.blob.core.windows.net/captures/input', path, digest(b'fixture'), **args)
            self.assertEqual(calls, [(b'fixture', {'length': 7, 'overwrite': False, 'max_concurrency': 1})])


if __name__ == '__main__': unittest.main()

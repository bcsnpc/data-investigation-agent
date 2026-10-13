import hashlib
import io
import json
import os
import subprocess
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import cloud_replay_bootstrap as bootstrap


def archive(path, extras=()):
    with tarfile.open(path, 'w:gz') as tape:
        for name, data, kind in [('engine.bundle', b'git', None), ('replay-manifest.json', b'{}', None), *extras]:
            info = tarfile.TarInfo(name); info.size = len(data)
            if kind is not None:
                info.type = kind; info.linkname = '/outside'
            tape.addfile(info, io.BytesIO(data))


class BootstrapTests(unittest.TestCase):
    def test_bounded_download_matches_exact_hash(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'download'
            value = b'complete sealed bytes'
            self.assertEqual(bootstrap.download(io.BytesIO(value), path, hashlib.sha256(value).hexdigest(), len(value)), len(value))
            self.assertEqual(path.read_bytes(), value)

    def test_download_hash_and_size_fail_closed(self):
        for digest, maximum, error in [('0' * 64, 100, 'HASH_MISMATCH'), ('0' * 64, 1, 'OVERSIZE')]:
            with self.subTest(error=error), tempfile.TemporaryDirectory() as root:
                with self.assertRaisesRegex(ValueError, error):
                    bootstrap.download(io.BytesIO(b'abc'), Path(root) / 'input', digest, maximum)

    def test_regular_bounded_package_extracts(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / 'a.tar.gz'
            archive(source, [('evidence/case/tape.json', b'sealed', None)])
            self.assertEqual(bootstrap.extract(source, root / 'output', 100), 11)
            self.assertEqual((root / 'output/evidence/case/tape.json').read_bytes(), b'sealed')

    def test_escape_symlink_hardlink_git_and_live_roots_refused(self):
        for name, kind in [('../outside', None), ('/outside', None), ('evidence/../../outside', None),
                           ('evidence/link', tarfile.SYMTYPE), ('evidence/hard', tarfile.LNKTYPE),
                           ('.git/config', None), ('.local/model-spend.sqlite', None),
                           ('evidence/.git/hooks/a', None), ('D:/estate/config.json', None),
                           ('evidence\\escape', None)]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); source = root / 'a.tar.gz'
                archive(source, [(name, b'x', kind)])
                with self.assertRaisesRegex(ValueError, 'UNSAFE'):
                    bootstrap.extract(source, root / 'output', 100)

    def test_expansion_bound_precedes_file_write(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / 'a.tar.gz'
            archive(source, [('evidence/big', b'x' * 10000, None)])
            with self.assertRaisesRegex(ValueError, 'EXPANDED_OVERSIZE'):
                bootstrap.extract(source, root / 'output', 100)
            self.assertFalse((root / 'output/evidence/big').exists())

    def test_exact_platform_endpoints_only(self):
        from investigator.adapters.cloud_replay_transport import endpoint
        self.assertEqual(endpoint('https://demostore.blob.core.windows.net/tapes/pinned.tar.gz'),
                         'https://demostore.blob.core.windows.net/tapes/pinned.tar.gz')
        for value in ('https://estate.example/query.json', 'https://demostore.blob.core.windows.net/tapes/a.json?sig=secret',
                      'https://demostore.blob.core.windows.net/tapes/../a.json'):
            with self.assertRaises(ValueError):
                endpoint(value)

    def test_pinned_local_git_bundle_restores_revision_without_checkout_or_hooks(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); original = root / 'original'; original.mkdir()
            def git(*args, cwd=original):
                return subprocess.check_output(['git', *args], cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()
            git('init', '--quiet')
            (original / 'engine.py').write_text('excluded earlier engine')
            git('add', 'engine.py')
            git('-c', 'user.name=OfflineTest', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'earlier')
            (original / 'engine.py').write_text('sealed historical engine')
            git('add', 'engine.py')
            git('-c', 'user.name=OfflineTest', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'sealed')
            revision = git('rev-parse', 'HEAD')
            package = root / 'package'; package.mkdir(); evidence = package / 'evidence'; evidence.mkdir()
            tape = evidence / 'tape.json'; tape.write_bytes(b'sealed tape')
            shallow = root / 'shallow.git'
            git('init', '--bare', '--quiet', str(shallow))
            git('-c', 'protocol.file.allow=always', 'fetch', '--depth=1', original.as_uri(),
                'HEAD:refs/heads/replay', cwd=shallow)
            git('bundle', 'create', str(package / 'engine.bundle'), 'refs/heads/replay', cwd=shallow)
            (package / 'replay-manifest.json').write_text(json.dumps({'version': 1, 'entries': [{
                'id': 'test', 'tape_path': 'tape.json', 'tape_sha256': hashlib.sha256(tape.read_bytes()).hexdigest(),
                'engine_revision': revision}]}))
            repo = root / 'restored'
            env = {key: os.environ[key] for key in ('PATH', 'SYSTEMROOT', 'TEMP', 'TMP') if key in os.environ}
            env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT='0')
            bootstrap.prepare_repo(package, repo, env)
            self.assertEqual(git('show', revision + ':engine.py', cwd=repo), 'sealed historical engine')
            self.assertFalse((repo / 'engine.py').exists())
            self.assertTrue((repo / bootstrap.HELPERS[0]).is_file())
            self.assertTrue((repo / '.git/shallow').is_file())

    def test_fixed_replay_child_scrubs_live_environment_and_uploads_counts_only(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'a.tar.gz'; archive(source)
            data = source.read_bytes(); uploads = []
            class FakeTransport:
                def request(self, url, body=None):
                    if body is None:
                        return io.BytesIO(data)
                    uploads.append(json.loads(body)); return io.BytesIO(b'')
            config = {'version': 1, 'input_url': 'https://demostore.blob.core.windows.net/tapes/a.tar.gz',
                      'result_url': 'https://demostore.blob.core.windows.net/captures/result.json',
                      'input_sha256': hashlib.sha256(data).hexdigest(), 'channel': 'worker-artifact',
                      'identity': {'mode': 'managed_identity', 'client_id': '11111111-1111-4111-8111-111111111111',
                                   'tenant_id': '22222222-2222-4222-8222-222222222222',
                                   'principal_id': '33333333-3333-4333-8333-333333333333'},
                      'max_download_bytes': 10000, 'max_expanded_bytes': 10000, 'shard': 0, 'shards': 8}
            def worker(command, **kwargs):
                self.assertEqual(kwargs['env']['DIA_LIVE_ACCESS_DISABLED'], '1')
                self.assertNotIn('AZURE_CLIENT_SECRET', kwargs['env'])
                self.assertNotIn('DIA_ESTATE_CONFIG', kwargs['env'])
                self.assertIn('--mode', command); self.assertIn('replay', command)
                output = Path(command[command.index('--output') + 1]); output.mkdir()
                (output / 'shard-0.json').write_text(json.dumps({'mode': 'SEALED_REPLAY', 'shard': 0,
                    'shards': 8, 'count': 1, 'matched': 1, 'network_requests': 0, 'physical_requests': 0,
                    'rows': [{'secret': 'never-upload-this'}]}))
                return type('Done', (), {'returncode': 0})()
            with patch.dict(os.environ, {'AZURE_CLIENT_SECRET': 'secret', 'DIA_ESTATE_CONFIG': '/live'}), \
                    patch.object(bootstrap, 'prepare_repo'), patch.object(bootstrap.subprocess, 'run', worker):
                self.assertEqual(bootstrap.execute(config, transport=FakeTransport()), 0)
            self.assertNotIn('never-upload-this', json.dumps(uploads))
            self.assertEqual(uploads[0]['matched'], 1)


if __name__ == '__main__':
    unittest.main()

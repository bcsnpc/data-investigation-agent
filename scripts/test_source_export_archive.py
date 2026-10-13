import io
from pathlib import Path
import tempfile
import tarfile
import unittest
from unittest.mock import patch
from investigator.archive_migration import plan, cleanup_script
from investigator.artifact_store import canonical, digest, ArtifactError
from investigator.source_export_archive import build, verify_bundle, bundle_manifest, publish_bundle
from investigator.resumable_archive import Journal
from test_resumable_archive import Remote, URL


class Tests(unittest.TestCase):
    def test_conservation_unique_metadata_and_duplicate_content_remote_proof(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            roots = ['.local/source-snapshots/' + character * 8 + '-1234-1234-1234-123456789012' for character in 'ab']
            paths = []
            for i, folder in enumerate(roots):
                target = root / folder
                target.mkdir(parents=True)
                for name, body in [('rows.jsonl', b'same synthetic rows'), ('manifest.json', str(i).encode())]:
                    (target / name).write_bytes(body)
                    paths.append(folder + '/' + name)
            source = plan(root, paths, protected=[], finished_statement='explicit test', source_export_roots=roots, storage_encoding='gzip')
            sha = digest(canonical(source))
            bundle = root / 'bundle.tar'
            with patch('shutil.disk_usage',return_value=type('Usage',(),{'free':20*1024**3})()):
                proof = build(source, sha, bundle)
                compressed=root/'compressed.tar.gz'
                gzip_proof=build(source,sha,compressed,compression='gzip',max_staging_bytes=1024*1024)
                self.assertEqual(gzip_proof['unique_objects'],3)
                self.assertEqual(gzip_proof['bundle_compression'],'gzip')
                with self.assertRaisesRegex(ArtifactError,'STAGING_BOUND'):
                    build(source,sha,root/'too-large.tar.gz',compression='gzip',max_staging_bytes=1)
                with self.assertRaisesRegex(ArtifactError,'STAGING_BOUND'):
                    build(source,sha,root/'too-large.tar',compression='identity',max_staging_bytes=1)
            self.assertEqual(proof['original_paths'], 4)
            self.assertEqual(proof['unique_objects'], 3)
            prepared = bundle_manifest(bundle, source, sha, proof)
            prepared_sha = digest(canonical(prepared))
            review = {'status': 'APPROVED', 'manifest_sha256': sha, 'reviewer': 'test', 'basis': 'synthetic'}
            refused_remote=Remote()
            with self.assertRaisesRegex(ArtifactError,'TRANSFER_BYTE_CAP'):
                publish_bundle(prepared,prepared_sha,source,sha,review,refused_remote,
                               Journal(root/'too-small',prepared_sha,URL),max_stored_bytes=1)
            self.assertEqual(refused_remote.calls,[])
            receipt = publish_bundle(prepared, prepared_sha, source, sha, review, Remote(), Journal(root / 'journal', prepared_sha, URL))
            self.assertEqual(len(receipt['objects']), 4)
            self.assertEqual(len({row['blob'] for row in receipt['objects']}), 1)
            self.assertIn('Remove-Item', cleanup_script(source, sha, receipt))
            self.assertTrue(all((root / path).exists() for path in paths))
            bad = root / 'bad.tar'
            with tarfile.open(bad, 'w') as archive:
                data = canonical(source)
                member = tarfile.TarInfo('manifest.json')
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
            with self.assertRaisesRegex(ArtifactError, 'CONSERVATION'):
                verify_bundle(bad, source, sha)
            changed = bytearray(bundle.read_bytes())
            offset = changed.find(b'same synthetic rows')
            changed[offset] ^= 1
            bad.write_bytes(changed)
            with self.assertRaisesRegex(ArtifactError, 'MEMBER_SHA'):
                verify_bundle(bad, source, sha)
            bad.write_bytes(bundle.read_bytes() + b'undeclared trailing material')
            with self.assertRaisesRegex(ArtifactError, 'TRAILING_DATA'):
                verify_bundle(bad, source, sha)


if __name__ == '__main__': unittest.main()

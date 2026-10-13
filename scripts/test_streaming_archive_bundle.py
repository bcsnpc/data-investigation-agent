from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from investigator.archive_migration import plan
from investigator.artifact_store import canonical,digest,ArtifactError
from investigator.source_export_archive import build
from investigator.streaming_archive_bundle import prepare,publish
from investigator.resumable_archive import Journal
from test_resumable_archive import Remote,URL


class Tests(unittest.TestCase):
    def test_streamed_tar_matches_standard_tar_and_resumes_without_staging(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);folder=root/'.local/round-five/capture';folder.mkdir(parents=True)
            paths=[]
            for index,body in enumerate([b'one'*10000,b'one'*10000,b'two']):
                path=folder/f'{index}.json';path.write_bytes(body);paths.append(path.relative_to(root).as_posix())
            manifest=plan(root,paths,protected=[],finished_statement='synthetic test',storage_encoding='gzip')
            sha=digest(canonical(manifest));prepared,source=prepare(manifest,sha)
            before={p.relative_to(root) for p in root.rglob('*')}
            streamed=b''.join(source.chunks())
            self.assertEqual({p.relative_to(root) for p in root.rglob('*')},before)
            with patch('shutil.disk_usage',return_value=type('Usage',(),{'free':20*1024**3})()):
                build(manifest,sha,root/'reference.tar')
            self.assertEqual(streamed,(root/'reference.tar').read_bytes())
            self.assertEqual(prepared['entries'][0]['sha256'],digest(streamed))
            with source.open('rb') as reader:
                with self.assertRaisesRegex(ArtifactError,'UNBOUNDED_READ'):reader.read()
            prepared_sha=digest(canonical(prepared))
            journal=Journal(root/'journal',prepared_sha,URL)
            review={'status':'APPROVED','manifest_sha256':sha,'reviewer':'test','basis':'synthetic'}
            remote=Remote();remote.fail_stage=2
            with patch('investigator.resumable_archive.BLOCK_BYTES',80):
                with self.assertRaises(OSError):
                    publish(prepared,prepared_sha,manifest,sha,review,remote,journal,max_stored_bytes=1024*1024)
                first=remote.calls[0][1];remote.fail_stage=None
                receipt=publish(prepared,prepared_sha,manifest,sha,review,remote,
                                Journal(root/'journal',prepared_sha,URL),max_stored_bytes=1024*1024)
            self.assertEqual(sum(identity==first for _,identity in remote.calls),1)
            self.assertEqual(len(receipt['objects']),3)
            self.assertEqual(len(remote.objects),1)
            self.assertEqual(receipt['mode'],'STREAMED_BUNDLE_NO_BODY_STAGING')
            self.assertFalse(receipt['local_deletion_performed'])
            self.assertEqual(receipt['member_proof']['unique_objects'],2)
            self.assertTrue(all((root/p).exists() for p in paths))
            new_remote=Remote()
            with self.assertRaisesRegex(ArtifactError,'TRANSFER_BYTE_CAP'):
                publish(prepared,prepared_sha,manifest,sha,review,new_remote,
                        Journal(root/'tiny',prepared_sha,URL),max_stored_bytes=1)
            self.assertEqual(new_remote.calls,[])
            (root/paths[0]).write_bytes(b'changed')
            with self.assertRaisesRegex(ArtifactError,'LOCAL_HASH_DIFFERS'):
                publish(prepared,prepared_sha,manifest,sha,review,new_remote,
                        Journal(root/'changed',prepared_sha,URL),max_stored_bytes=1024*1024)
            self.assertEqual(new_remote.calls,[])


if __name__=='__main__':unittest.main()

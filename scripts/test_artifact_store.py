import concurrent.futures
import json
from pathlib import Path
import tempfile
import unittest
from investigator.artifact_store import ArtifactError, CHUNK_SIZE, Files, LocalObjects


class ArtifactStoreTests(unittest.TestCase):
    def test_snapshot_dedup_and_exact_restore(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); objects = LocalObjects(root/'objects'); files = Files(objects)
            a=root/'a'; b=root/'b'
            a.write_bytes(b'a'*CHUNK_SIZE + b'b'*CHUNK_SIZE)
            b.write_bytes(b'a'*CHUNK_SIZE + b'c'*CHUNK_SIZE)
            first=files.capture(a); second=files.capture(b)
            self.assertEqual(files.capture(a),first)
            self.assertEqual(len(list((objects.root/'chunks').iterdir())),3)
            self.assertEqual(files.restore(first['sha256'],root/'restored-a').read_bytes(),a.read_bytes())
            self.assertEqual(files.restore(second['sha256'],root/'restored-b').read_bytes(),b.read_bytes())

    def test_parallel_publication_same_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); source=root/'source';source.write_bytes(b'fixture'*30000)
            files=Files(LocalObjects(root/'objects'))
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                refs=list(pool.map(files.capture,[source]*16))
            self.assertTrue(all(r==refs[0]for r in refs))
            self.assertTrue(files.verify(refs[0]['sha256']))

    def test_corruption_refuses_without_publishing_partial_restore(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'source';source.write_bytes(b'original')
            objects=LocalObjects(root/'objects');files=Files(objects);ref=files.capture(source)
            manifest=files.describe(ref['sha256']);chunk=manifest['chunks'][0]['sha256']
            import gzip
            (objects.root/'chunks'/chunk).write_bytes(gzip.compress(b'changed!'))
            with self.assertRaisesRegex(ArtifactError,'CHUNK_INTEGRITY'):
                files.restore(ref['sha256'],root/'restored')
            self.assertFalse((root/'restored').exists())

    def test_path_escape_and_overwrite_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);objects=LocalObjects(root/'objects');files=Files(objects)
            with self.assertRaises(ArtifactError):objects.get('../outside')
            source=root/'source';source.write_bytes(b'')
            ref=files.capture(source)
            with self.assertRaisesRegex(ArtifactError,'OVERWRITE'):files.restore(ref['sha256'],source)

    def test_immutable_publication_refuses_conflict(self):
        with tempfile.TemporaryDirectory() as folder:
            objects=LocalObjects(folder);key='files/'+'a'*64
            objects.put(key,b'first')
            with self.assertRaisesRegex(ArtifactError,'IMMUTABLE_OBJECT_CONFLICT'):objects.put(key,b'second')


if __name__=='__main__':unittest.main()

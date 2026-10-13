from pathlib import Path
import json
import tempfile
import time
import unittest
from plan_archive_batches import sample,batch


class Tests(unittest.TestCase):
    def test_sample_never_exceeds_bound_or_emits_raw_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);folder=root/'.local/round-five/capture';folder.mkdir(parents=True)
            (folder/'tape.json').write_text(json.dumps({'events':[],'private_fixture':'do-not-emit-this-value'}))
            (folder/'large.json').write_bytes(b'private-data'*1000)
            value=sample(root,time.time()+1,max_sample_bytes=32)
            self.assertLessEqual(value['sample_bytes'],32)
            self.assertNotIn('do-not-emit-this-value',json.dumps(value))
            self.assertNotIn('private-data',json.dumps(value))
    def test_batch_excludes_whole_capture_when_one_file_is_quarantined(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ['good','quarantined']:
                folder=root/'.local/round-five'/name;folder.mkdir(parents=True)
                (folder/'tape.json').write_text(json.dumps({'events':[]}))
                (folder/'receipt.json').write_text('safe')
            (root/'.local/round-five/quarantined/secret.json').write_text('not to copy')
            value=batch(root,time.time()+1,max_original_bytes=1024,max_files=20,protected=[])
            self.assertEqual(len(value['entries']),2)
            self.assertTrue(all('/good/' in row['path'] for row in value['entries']))
            self.assertEqual(len(value['excluded']),3)


if __name__=='__main__':unittest.main()

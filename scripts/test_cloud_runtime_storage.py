"""Exercise the actual non-root image's normal recording directory."""
import os
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


@unittest.skipUnless(ROOT.as_posix()=='/app' and (ROOT/'image-source-manifest.json').is_file(),
                     'actual code-only container filesystem check')
class RuntimeRecordingStorageTests(unittest.TestCase):
    def test_nonroot_normal_recording_path_is_writable_but_engine_is_not(self):
        self.assertNotEqual(os.geteuid(),0)
        self.assertFalse(os.access(ROOT/'scripts',os.W_OK))
        with tempfile.TemporaryDirectory(dir=ROOT/'.local',prefix='recording-contract-')as folder:
            path=Path(folder)/'tape.events.jsonl'
            with path.open('xb')as stream:stream.write(b'{"synthetic":true}\n')
            self.assertEqual(path.read_bytes(),b'{"synthetic":true}\n')

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from investigator.artifact_store import Files, LocalObjects, ArtifactError, canonical, digest
from investigator import tape_bundle
from investigator.process_tape import Tape, bytes_of


class BundleTests(unittest.TestCase):
    def test_snapshot_bundle_replays_original_events_without_rewriting_tape(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); original = root/'original'; original.mkdir()
            for name in ('catalog.sqlite','inventory.sqlite'):
                (original/name).write_bytes(b'synthetic offline snapshot'+name.encode())
            bootstrap = {'entry_point':'synthetic','context_identity':'test','config':{},'profile':{},
                         'usage_policy':{},'engine_hash':'test','state':{}}
            tape = Tape(original/'tape.json',bootstrap)
            tape.event('BOUNDED_REQUEST',bytes_of({'a':1}))
            tape.event('BOUNDED_RESPONSE',bytes_of({'result':2}))
            tape.finish({'status':'COMPLETED'})
            before = {p.name:p.read_bytes() for p in original.iterdir()}
            files = Files(LocalObjects(root/'objects'))
            bundle = tape_bundle.pack(original,files,tape_class='EXACT')
            with tape_bundle.materialize(bundle,files) as path:
                replay = Tape(path)
                replay.event('BOUNDED_REQUEST',bytes_of({'a':1}))
                self.assertEqual(json.loads(replay.take('BOUNDED_RESPONSE')),{'result':2})
                replay.finish({'status':'COMPLETED'})
                self.assertEqual(path.read_bytes(),before['tape.json'])
            self.assertEqual(before,{p.name:p.read_bytes() for p in original.iterdir()})
            altered = dict(bundle); altered['files'] = dict(bundle['files'])
            altered['files']['../escape'] = altered['files']['tape.json']
            altered['seal'] = digest(canonical({k:v for k,v in altered.items() if k!='seal'}))
            with self.assertRaisesRegex(ArtifactError,'BUNDLE_FILE_NOT_ALLOWED'):
                tape_bundle.validate(altered)

    def test_cannot_label_legacy_raw_bytes_as_projected(self):
        with self.assertRaisesRegex(ArtifactError,'PROJECTED_BUNDLE_REQUIRES'):
            tape_bundle.pack('.',None,tape_class='PRIVACY_PROJECTED')

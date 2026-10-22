"""Restore slim platform inputs before entering the zero-socket replay child."""
from contextlib import contextmanager
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from investigator.runner_replay import replay


class MaterializeTests(unittest.TestCase):
    def loader(self,child):
        return SimpleNamespace(loader=SimpleNamespace(exec_module=lambda module:setattr(module,'replay_revision',child)))

    def test_slim_pointer_is_restored_in_parent_and_lives_until_child_returns(self):
        order=[];restored=Path('private-job-scratch/raw/tape.json')
        @contextmanager
        def restore(path):
            self.assertEqual(path,'capture/slim-recording.json')
            order.append('restore-enter')
            try:yield restored
            finally:order.append('restore-exit')
        def child(path,output,revision,*,estate_manifest):
            self.assertEqual(order,['restore-enter'])
            self.assertEqual(path,restored)
            self.assertEqual((output,revision,estate_manifest),('output','a'*40,'estate.json'))
            order.append('child');return {'matched':True,'network_requests':0}
        with patch('investigator.runner_replay.importlib.util.spec_from_file_location',return_value=self.loader(child)), \
             patch('investigator.runner_replay.importlib.util.module_from_spec',return_value=SimpleNamespace()), \
             patch('investigator.slim_recording.materialize',side_effect=restore):
            result=replay({'format':'investigation','tape':'capture/slim-recording.json','engine_revision':'a'*40,'manifest':'estate.json'},'output')
        self.assertTrue(result['matched'])
        self.assertEqual(order,['restore-enter','child','restore-exit'])

    def test_legacy_raw_tape_needs_no_storage_and_stays_byte_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            tape=Path(directory)/'tape.json';original=b'{"original":"raw sealed bytes"}';tape.write_bytes(original)
            def child(path,output,revision,*,estate_manifest):
                self.assertEqual(path,tape);self.assertEqual(path.read_bytes(),original)
                return {'matched':True,'network_requests':0}
            with patch('investigator.runner_replay.importlib.util.spec_from_file_location',return_value=self.loader(child)), \
                 patch('investigator.runner_replay.importlib.util.module_from_spec',return_value=SimpleNamespace()), \
                 patch('investigator.slim_recording.stores',side_effect=AssertionError('No platform lookup for raw tape')):
                result=replay({'format':'investigation','tape':str(tape),'engine_revision':'a'*40},'output')
            self.assertTrue(result['matched']);self.assertEqual(tape.read_bytes(),original)

if __name__=='__main__':unittest.main()

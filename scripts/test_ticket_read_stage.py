"""A ticket's composition capture cannot silently abandon its original reads."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from investigator import process_tape as journal
from investigator.run_recording import seal_read_stage
from investigator.onboarding import Conflict


def bootstrap():
    return {'entry_point':'synthetic','context_identity':'fixture','config':{},
            'profile':{},'usage_policy':{},'engine_hash':'synthetic','state':{}}


class ReadStageTests(unittest.TestCase):
    def test_seals_actual_read_return_once_and_replays_control_without_live_cache(self):
        with tempfile.TemporaryDirectory() as folder:
            read=journal.Tape(Path(folder)/'reads.json',bootstrap())
            actual={'operation':'run','error':None,'outputs':None,'status':'COMPLETED',
                    'result':{'id':'session','status':'COMPLETED','observations':[{'receipt':'original'}]}}
            read.pending_read_final=copy.deepcopy(actual)
            agent=SimpleNamespace(_run_tapes={'session':read},planner_profile={'adapter':'injected'})
            composition=journal.Tape(Path(folder)/'composition.json',bootstrap())
            with journal.active(composition):
                sealed=seal_read_stage(agent,'session')
                composition.finish(sealed)
            self.assertTrue(read.finished)
            final=json.loads(journal.validate_event(read.events[-1],read.events[-1]['ordinal']))
            self.assertEqual(final,actual)
            original=read.path.read_bytes()
            replay=journal.Tape(composition.path)
            with journal.active(replay):
                without_cache=SimpleNamespace(planner_profile={'adapter':'injected'})
                replayed=seal_read_stage(without_cache,'session');replay.finish(replayed)
            self.assertEqual(replayed,sealed);self.assertEqual(read.path.read_bytes(),original)
            with patch.object(read,'finish',side_effect=AssertionError('must not re-seal')):
                self.assertEqual(seal_read_stage(agent,'session'),sealed)

    def test_missing_live_capture_is_recorded_refusal_and_cannot_be_reconstructed(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict('os.environ',{'INVESTIGATOR_RECORD_RUNS':'1'}):
            agent=SimpleNamespace(planner_profile={'adapter':'injected'})
            capture=journal.Tape(Path(folder)/'composition.json',bootstrap())
            with journal.active(capture):
                with self.assertRaisesRegex(Conflict,'READ_STAGE_CAPTURE_UNAVAILABLE'):
                    seal_read_stage(agent,'session')
                capture.finish({'error':'READ_STAGE_CAPTURE_UNAVAILABLE'})
            replay=journal.Tape(capture.path)
            with journal.active(replay):
                with self.assertRaisesRegex(Conflict,'READ_STAGE_CAPTURE_UNAVAILABLE'):
                    seal_read_stage(agent,'session')
                replay.finish({'error':'READ_STAGE_CAPTURE_UNAVAILABLE'})

    def test_missing_original_return_never_synthesizes_a_final_from_current_state(self):
        with tempfile.TemporaryDirectory() as folder:
            read=journal.Tape(Path(folder)/'reads.json',bootstrap())
            agent=SimpleNamespace(_run_tapes={'session':read},planner_profile={'adapter':'injected'})
            with self.assertRaisesRegex(Conflict,'READ_STAGE_RETURN_UNAVAILABLE'):
                seal_read_stage(agent,'session')
            self.assertFalse(read.finished)


if __name__=='__main__':unittest.main()

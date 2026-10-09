"""A ticket's composition capture cannot silently abandon its original reads."""
import copy
import json
import tempfile
import sqlite3
from contextlib import contextmanager
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from investigator import process_tape as journal
from investigator.run_recording import seal_read_stage,retain_read_capture
from investigator.onboarding import Conflict


def bootstrap():
    return {'entry_point':'synthetic','context_identity':'fixture','config':{},
            'profile':{},'usage_policy':{},'engine_hash':'synthetic','state':{}}


def store_at(path):
    @contextmanager
    def connect():
        db=sqlite3.connect(path)
        try:
            with db:yield db
        finally:db.close()
    return SimpleNamespace(connect=connect)


class ReadStageTests(unittest.TestCase):
    def test_cold_resume_uses_immutable_original_final_and_refuses_changed_bytes(self):
        with tempfile.TemporaryDirectory() as folder,patch('investigator.run_recording.ROOT',Path(folder)):
            root=Path(folder)/'.local/process-tapes';root.mkdir(parents=True)
            actual={'operation':'run','error':None,'outputs':None,'status':'COMPLETED',
                    'result':{'id':'session','status':'COMPLETED','observations':[{'receipt':'original'}]}}
            read=journal.Tape(root/'reads.json',bootstrap());read.finish(actual)
            store=store_at(Path(folder)/'state.sqlite')
            agent=SimpleNamespace(store=store,planner_profile={'adapter':'azure'})
            retain_read_capture(agent,'session',read);original=read.path.read_bytes()
            # No _run_tapes cache exists; no current-state getter can supply a replacement.
            agent.get=lambda *_:self.fail('must not reconstruct the original return')
            result=seal_read_stage(agent,'session')
            self.assertEqual(result,{'status':'SEALED','tape_sha256':journal.sha(original)})
            self.assertEqual(read.path.read_bytes(),original)
            read.path.write_bytes(original+b' ')
            with self.assertRaisesRegex(journal.TapeError,'READ_CAPTURE_HASH_DIFFERS'):
                seal_read_stage(agent,'session')

    def test_cold_pointer_cannot_substitute_a_different_session(self):
        with tempfile.TemporaryDirectory() as folder,patch('investigator.run_recording.ROOT',Path(folder)):
            root=Path(folder)/'.local/process-tapes';root.mkdir(parents=True)
            read=journal.Tape(root/'reads.json',bootstrap())
            read.finish({'operation':'run','error':None,'outputs':None,'status':'COMPLETED',
                         'result':{'id':'other','status':'COMPLETED'}})
            agent=SimpleNamespace(store=store_at(Path(folder)/'state.sqlite'),
                                  planner_profile={'adapter':'azure'})
            retain_read_capture(agent,'session',read)
            with self.assertRaisesRegex(journal.TapeError,'READ_CAPTURE_SESSION_DIFFERS'):
                seal_read_stage(agent,'session')

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

"""Native verification time starts after controls, within the same job envelope."""
import copy
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock,patch

from cloud_binding_verifier import native_inputs,validate_native_window
from investigator.process_tape import Tape,active
from test_process_tape import bootstrap


class NativeWindowTests(unittest.TestCase):
    def test_delayed_capture_does_not_consume_native_window_and_replays_clock(self):
        inputs={'deadline':1800,'native_window':{'seconds':900,'finalization_seconds':120,'demo_seconds':300}}
        original=copy.deepcopy(inputs)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';tape=Tape(path,bootstrap())
            with active(tape),patch('investigator.process_tape.clock.__defaults__',(lambda:700,)):
                value=native_inputs(inputs)
            self.assertEqual(1380,value['deadline'])
            self.assertEqual(original,inputs);tape.finish(value)
            replay=Tape(path)
            with active(replay),patch('investigator.process_tape.clock.__defaults__',(Mock(side_effect=AssertionError('replay clock must be sealed')),)):
                again=native_inputs(inputs);replay.finish(again)
            self.assertEqual(value,again)

    def test_window_caps_probes_at_900_even_with_more_overall_time(self):
        with patch('investigator.process_tape.clock',return_value=100) as clock:
            value=native_inputs({'deadline':1800,'native_window':{'seconds':900,'finalization_seconds':120,'demo_seconds':0}})
        self.assertEqual(1000,value['deadline']);clock.assert_called_once_with('cloud-verification-native-window-start')

    def test_exhausted_controls_admit_no_native_window(self):
        with patch('investigator.process_tape.clock',return_value=1500):
            with self.assertRaisesRegex(ValueError,'NO_NATIVE_WINDOW'):
                native_inputs({'deadline':1800,'native_window':{'seconds':900,'finalization_seconds':120,'demo_seconds':300}})

    def test_old_tapes_keep_deadline_and_no_new_clock(self):
        old={'deadline':12345}
        with patch('investigator.process_tape.clock') as clock:
            self.assertIs(old,native_inputs(old))
        clock.assert_not_called()

    def test_bounds_reject_increased_or_missing_reserves(self):
        for window in ({'seconds':901,'finalization_seconds':120,'demo_seconds':300},
                       {'seconds':900,'finalization_seconds':0,'demo_seconds':300},
                       {'seconds':True,'finalization_seconds':120,'demo_seconds':300}):
            with self.subTest(window=window),self.assertRaisesRegex(ValueError,'NATIVE_WINDOW_BOUND'):validate_native_window(window)

    def test_runner_entry_not_handler_start_anchors_overall_deadline(self):
        from investigator.unified_runner import handlers
        with tempfile.TemporaryDirectory() as folder:
            ctx=SimpleNamespace(root=Path(folder),started_at=100,record=Mock(),step=lambda n,f:f())
            events=[]
            def execute(*args,**kwargs):
                events.append('execute');self.assertEqual(1900,kwargs['deadline'])
                self.assertEqual({'seconds':900,'finalization_seconds':120,'demo_seconds':0},kwargs['native_window'])
                return {'status':'FAILED'}
            with patch('cloud_runner_context.retain_dependencies',side_effect=lambda *a,**k:events.append('durable-before-reads')), \
                 patch('cloud_verification_run.execute',side_effect=execute),patch('investigator.unified_runner.time.time',return_value=700):
                handlers()['verification']({'manifest':'estate.json','run_id':'fresh','options':{'prepared':folder,'spec':'spec','spec_sha256':'sha'}},ctx)
            self.assertEqual(['durable-before-reads','execute'],events)


    def test_insufficient_demo_headroom_preserves_verification_and_defers(self):
        from investigator.unified_runner import handlers
        with tempfile.TemporaryDirectory() as folder:
            ctx=SimpleNamespace(root=Path(folder),started_at=0,record=Mock(),step=lambda n,f:f())
            result={'status':'COMPLETED','verification_status':'VERIFIED'}
            with patch('cloud_runner_context.retain_dependencies'), \
                 patch('cloud_runner_context.demo_after_verification') as demo, \
                 patch('cloud_verification_run.execute',return_value=result), \
                 patch('investigator.unified_runner.time.time',return_value=1500):
                value=handlers()['verification']({'manifest':'estate.json','run_id':'fresh','options':{'prepared':folder,'spec':'spec','spec_sha256':'sha','demo_ticket':'form.json'}},ctx)
            self.assertEqual('DEMO_DEFERRED_FOR_DEADLINE',value['status'])
            self.assertIs(result,value['verification']);self.assertIsNone(value['demo'])
            demo.assert_not_called()


if __name__=='__main__':unittest.main()

import hashlib
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from investigator.run_capture import DurableCapture
from investigator.run_timing import RunTiming
from investigator.process_tape import bytes_of

HEADER={'entry_point':'runner','context_identity':'fixture','config':{},'profile':{},'usage_policy':None,'engine_hash':'fixture','state':{}}


class Timing(unittest.TestCase):
    def test_step_publish_seal_sidecar_is_observational_and_does_not_rewrite_tape(self):
        with tempfile.TemporaryDirectory() as directory:
            clock=[0.0];sent={}
            def put(key,raw):sent[key]=raw;clock[0]+=2
            capture=DurableCapture(Path(directory)/'capture',put,run_id='one',bootstrap=HEADER,clock=lambda:clock[0])
            def value():clock[0]+=5;return {'quantity':16}
            result=capture.step('investigation',value)
            self.assertEqual(result,{'quantity':16})
            original={'ordinal':1,'kind':'PROVIDER_REQUEST','at':100.0,'body':'e30=','sha256':'a'*64}
            capture.event(SimpleNamespace(path='native-tape'),original)
            capture.event(SimpleNamespace(path='native-tape'),{**original,'ordinal':2,'kind':'PROVIDER_RESPONSE','at':103.0})
            seal=capture.seal();index=sent['one/run-record.json'];receipt=capture.publish_timing(seal)
            self.assertEqual(sent['one/run-record.json'],index)
            self.assertEqual(receipt['sha256'],hashlib.sha256(sent['one/timing-summary.json']).hexdigest())
            summary=receipt['summary'];self.assertEqual(summary['run_record_seal'],seal)
            self.assertEqual(summary['phases']['investigation']['wall_seconds'],5)
            self.assertEqual(summary['phases']['model']['wall_seconds'],3)
            self.assertGreater(summary['phases']['capture_publish']['wall_seconds'],0)
            self.assertGreater(summary['phases']['seal']['wall_seconds'],0)
            self.assertIsNone(summary['phases']['startup']['wall_seconds']);self.assertIsNone(summary['phases']['intake']['wall_seconds'])
            self.assertNotIn('one/timing-summary.json',[ref['key'] for ref in json.loads(index)['records']])
            event=json.loads(next(raw for key,raw in sent.items() if key.endswith('-tape-event.json')))
            self.assertEqual(event['event'],original)
    def test_failure_step_record_and_missing_or_reversed_model_times_are_not_fabricated(self):
        timing=RunTiming(lambda:10)
        timing.tape_event(SimpleNamespace(path='native'),{'kind':'PROVIDER_REQUEST','at':100})
        timing.tape_event(SimpleNamespace(path='native'),{'kind':'PROVIDER_RESPONSE','at':99})
        self.assertIsNone(timing.summary()['phases']['model']['wall_seconds'])
        self.assertIsNone(timing.summary()['phases']['dependency_io']['wall_seconds'])
    def test_manual_demo_deadline_is_hour_and_respects_smaller_explicit_deadline(self):
        import os
        from cloud_runner_context import demo_state_admission
        context=SimpleNamespace(started_at=1000,record=lambda *args:None)
        with patch('time.time',return_value=1100),patch('investigator.live_gateway._network_unlocked'),patch.dict(os.environ,{},clear=True):
            with demo_state_admission({'run_id':'one'},context) as admitted:self.assertEqual(admitted['deadline'],4600)
        with patch('time.time',return_value=1100),patch('investigator.live_gateway._network_unlocked'),patch.dict(os.environ,{'INVESTIGATOR_CLOUD_WORK_DEADLINE':'2000'},clear=True):
            with demo_state_admission({'run_id':'one'},context) as admitted:self.assertEqual(admitted['deadline'],2000)


if __name__=='__main__':unittest.main()

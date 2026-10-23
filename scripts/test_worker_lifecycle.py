"""Worker diagnostics carry state and exit evidence, never query/value data."""
import io
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from investigator.physical_reads import WORKER_OBSERVER, run, scope, worker_frame
from investigator.run_capture import DurableCapture
from managed_sql_worker import Protocol
from test_process_tape import bootstrap


class WorkerLifecycleTests(unittest.TestCase):
    def test_periodic_frames_exclude_sensitive_payload_and_actual_exit_is_separate(self):
        sink=io.StringIO();protocol=Protocol(True,sink=sink)
        with protocol.lifecycle({'stage':'connect'},interval=.01):time.sleep(.035)
        frames=[json.loads(x)for x in sink.getvalue().splitlines()]
        self.assertEqual(frames[0]['worker_event'],'START')
        self.assertEqual(frames[-1]['worker_event'],'EXIT')
        self.assertTrue(any(x['worker_event']=='HEARTBEAT'for x in frames))
        for frame in frames:
            self.assertEqual(set(frame),{'worker_event','pid','last_action'})
            self.assertEqual(worker_frame(frame),frame)

    def test_real_child_heartbeat_is_not_a_physical_request(self):
        events=[];physical=[]
        program='''import json,sys,time
from managed_sql_worker import Protocol
p=Protocol(True);json.loads(sys.stdin.readline())
with p.lifecycle({'stage':'connect'},interval=.01):
 time.sleep(.035)
 p.before('sql_identity');p.done('sql_identity')
 p.before('sql_quantity');p.done('sql_quantity')
p.emit({'value':7})
'''
        token=WORKER_OBSERVER.set(events.append)
        try:
            def meter(kind,fn):physical.append(kind);return fn()
            with scope(meter):result=run([sys.executable,'-c',program],input='{}',timeout=5)
        finally:WORKER_OBSERVER.reset(token)
        self.assertEqual(json.loads(result.stdout),{'value':7})
        self.assertEqual(physical,['sql_quantity'])  # Identity uses initial reservation.
        self.assertTrue(any(x['event']=='HEARTBEAT'for x in events))
        self.assertEqual(events[-1]['event'],'EXIT')
        self.assertEqual(events[-1]['worker_exit_code'],0)
        self.assertFalse(events[-1]['deadline_expired'])
        self.assertEqual(len({x['worker_id']for x in events}),1)

    def test_frames_with_query_values_unknown_actions_or_bad_pid_refuse(self):
        valid={'worker_event':'HEARTBEAT','pid':1,'last_action':'connect'}
        for frame in ({**valid,'query':'sensitive'}, {**valid,'last_action':'arbitrary'},
                      {**valid,'pid':True}, {**valid,'worker_event':'ALLOW'}):
            with self.subTest(frame=frame),self.assertRaisesRegex(ValueError,'WORKER_TELEMETRY_INVALID'):worker_frame(frame)

    def test_small_heartbeat_publishes_without_draining_pending_evidence(self):
        sent=[]
        with tempfile.TemporaryDirectory()as d:
            capture=DurableCapture(Path(d)/'capture',lambda key,raw:sent.append(key),run_id='alive',bootstrap=bootstrap())
            with capture.protocol_publications():
                evidence=capture.record('tape-event',{'unchanged':'evidence'})
                capture.worker_lifecycle({'event':'HEARTBEAT','worker_id':'synthetic','last_action':'connect'})
                self.assertNotIn(evidence['key'],sent)
                self.assertTrue(sent[-1].endswith('-worker-lifecycle.json'))
                self.assertEqual(len(capture._pending_publications),1)
            self.assertIn(evidence['key'],sent)
            self.assertEqual(capture._pending_publications,[])


if __name__=='__main__':unittest.main()

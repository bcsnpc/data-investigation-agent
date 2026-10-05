import errno
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock,patch
from investigator import process_failure
from investigator.process_tape import Tape,active
from investigator.tape_worker import run,popen,check_deadline
from sql_connect_retry import read_with_retry
from sql_layer_policy import policy
from serverless_control import prewarm
from test_process_tape import bootstrap


FAILED={'error':'SQL_READ_FAILED','stage':'connect','sql_error_number':40613}
ASSET='sql://server/database/object/1'
CONFIG={'sql':{'server':'server','database':'database'},'_estate':{'layers':[
    {'asset_id':ASSET,'serverless':True,'worker_timeout_seconds':240}]}}


def broken_worker(*args,**kwargs):
    raise OSError(errno.EPIPE,'Broken pipe')


class ServerlessSourceTests(unittest.TestCase):
    def test_declared_pause_has_bounded_waits_and_attempt_labels(self):
        read=Mock(return_value=FAILED);sleep=Mock()
        result=read_with_retry(read,sleep,serverless=True)
        self.assertEqual(read.call_count,5)
        self.assertEqual(sum(c.args[0] for c in sleep.call_args_list),60)
        self.assertTrue(all(a['condition']=='source paused; waiting for resume' for a in result['connection_attempts']))
        self.assertEqual(result['connection_attempts'][-1]['retry_delay_seconds'],0)
        for failure in (dict(FAILED,stage='query'),dict(FAILED,sql_error_number=18456)):
            read=Mock(return_value=failure);read_with_retry(read,Mock(),serverless=True)
            self.assertEqual(read.call_count,1)
        read=Mock(side_effect=OSError(errno.EPIPE,'Broken pipe'))
        with self.assertRaises(OSError):read_with_retry(read,Mock(),serverless=True)
        self.assertEqual(read.call_count,1)

    def test_exact_compiled_identity_selects_deadline_and_serverless(self):
        self.assertEqual(policy(CONFIG,{'asset_ids':[ASSET]}),{'serverless':True,'worker_timeout_seconds':240})
        self.assertEqual(policy(CONFIG,{'asset_ids':['unrelated']}),{'serverless':False,'worker_timeout_seconds':90})
        self.assertEqual(policy({},{}),{'serverless':False,'worker_timeout_seconds':90})

    def test_prewarm_connection_and_wait_are_controls_only(self):
        execute=Mock(side_effect=[FAILED,{'status':'CONNECTED','stage':'connect'}]);events=[];slots=[]
        def admit(kind,call):slots.append(kind);return call()
        result=prewarm(CONFIG,[ASSET],admit_control=admit,record_control=lambda k,d:events.append((k,d)),sleep=Mock(),execute=execute)
        self.assertEqual(result['status'],'CONNECTED')
        self.assertEqual(slots,['SERVERLESS_PREWARM']*2)
        self.assertEqual([e[0] for e in events],['SERVERLESS_RESUME_WAIT']*2+['SERVERLESS_PREWARM_RESULT'])
        request=execute.call_args.args[1]
        self.assertNotIn('query',request);self.assertEqual(request['control_mode'],'PREWARM')
        with self.assertRaises(ValueError):prewarm(CONFIG,['elsewhere'],admit_control=admit,record_control=Mock())

    def test_bounded_worker_error_retains_errno_message_location_in_tape_and_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';tape=Tape(path,bootstrap())
            with active(tape),self.assertRaises(OSError) as raised:
                run(['worker'],input='{}',timeout=240,fallback=broken_worker)
            detail=process_failure.capture(raised.exception)
            self.assertEqual((detail['error_type'],detail['errno'],detail['message']),('BrokenPipeError',errno.EPIPE,'Broken pipe'))
            self.assertEqual(detail['module'],Path(__file__).name);self.assertIsInstance(detail['line'],int)
            tape.finish({});replay=Tape(path)
            with active(replay),self.assertRaises(OSError) as repeated:
                run(['worker'],input='{}',timeout=240,fallback=lambda *a,**kw:self.fail('No live worker'))
            self.assertEqual(process_failure.capture(repeated.exception),detail)
            replay.finish({})

    def test_stream_pipe_error_is_a_distinct_replayable_worker_event(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';tape=Tape(path,bootstrap());child=Mock()
            child.stdin.write.side_effect=broken_worker;child.wait.return_value=1
            with active(tape),patch('investigator.tape_worker.subprocess.Popen',return_value=child):
                worker=popen(['worker'],worker_timeout=240)
                with self.assertRaises(OSError):worker.stdin.write('{}')
                worker.wait()
            tape.finish({});self.assertIn('WORKER_FAILURE',[e['kind'] for e in tape.events])
            replay=Tape(path)
            with active(replay):
                worker=popen(['worker'],worker_timeout=240)
                with self.assertRaises(OSError):worker.stdin.write('{}')
                worker.wait();replay.finish({})

    def test_expired_stream_deadline_is_recorded_and_replayed_without_a_timer(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';tape=Tape(path,bootstrap());child=Mock()
            child.wait.return_value=1
            with active(tape),patch('investigator.tape_worker.subprocess.Popen',return_value=child):
                worker=popen(['worker'],worker_timeout=240);worker.deadline_expired=True
                with self.assertRaises(OSError) as caught:check_deadline(worker)
                self.assertEqual(caught.exception.errno,errno.ETIMEDOUT)
                worker.wait()
            tape.finish({});replay=Tape(path)
            with active(replay):
                worker=popen(['worker'],worker_timeout=240)
                with self.assertRaises(OSError):check_deadline(worker)
                worker.wait();replay.finish({})

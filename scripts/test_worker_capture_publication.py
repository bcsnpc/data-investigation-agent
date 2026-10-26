"""Remote capture must not consume a child's read-admission deadline."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from investigator.physical_reads import run, scope
from investigator.run_capture import DurableCapture
from test_process_tape import bootstrap


class WorkerPublicationTests(unittest.TestCase):
    def test_actual_child_finishes_before_parent_publishes_its_budget_records(self):
        child=[];published=[]
        def put(key,raw):
            if child and not key.endswith('-worker-lifecycle.json'):
                self.assertIsNotNone(child[0].poll(), 'publication blocked a waiting SQL child')
            published.append(key)
        def popen(command,**kwargs):
            kwargs.pop('worker_timeout',None)
            worker=subprocess.Popen(command,**kwargs);child.append(worker);return worker
        program='''import sys,json
json.loads(sys.stdin.readline())
for kind in ('sql_identity','sql_database_permissions','sql_object_permissions','sql_quantity'):
 print(json.dumps({'physical_read':'REQUEST','kind':kind}),flush=True)
 assert sys.stdin.readline().strip()=='ALLOW'
 print(json.dumps({'physical_read':'DONE','kind':kind,'status':'AVAILABLE'}),flush=True)
print(json.dumps({'value':7}),flush=True)
'''
        with tempfile.TemporaryDirectory()as d:
            capture=DurableCapture(Path(d)/'capture',put,run_id='protocol',bootstrap=bootstrap())
            initial=len(published)
            def meter(kind,execute):
                capture.record('budget',{'kind':kind})
                self.assertEqual(len([k for k in published if not k.endswith('-worker-lifecycle.json')]),initial)
                return execute()
            with capture.observing(),scope(meter),patch('investigator.tape_worker.popen',side_effect=popen):
                result=run([sys.executable,'-c',program],input='{}',timeout=5)
            self.assertEqual(result.returncode,0)
            self.assertEqual(json.loads(result.stdout),{'value':7})
            self.assertEqual(len([k for k in published if not k.endswith('-worker-lifecycle.json')]),initial+3)
            self.assertEqual(capture._pending_publications,[])
            self.assertTrue(capture.seal())

    def test_original_error_still_flushes_durable_records(self):
        published=[]
        with tempfile.TemporaryDirectory()as d:
            capture=DurableCapture(Path(d)/'capture',lambda *args:published.append(args),run_id='failure',bootstrap=bootstrap())
            def fail(*args,**kwargs):
                capture.record('failure',{'error_type':'RuntimeError'})
                raise RuntimeError('original worker failure')
            with capture.observing(),patch('investigator.physical_reads._run',side_effect=fail):
                with self.assertRaisesRegex(RuntimeError,'original worker failure'):run([],input='{}',timeout=1)
            self.assertEqual(len(published),3)
            self.assertEqual(capture._pending_publications,[])

    def test_publication_failure_cannot_become_completed_step(self):
        with tempfile.TemporaryDirectory()as d:
            capture=DurableCapture(Path(d)/'capture',lambda *_:None,run_id='unpublished',bootstrap=bootstrap())
            with patch.object(capture,'put',side_effect=OSError('transport unavailable')):
                with self.assertRaises(OSError),capture.protocol_publications():capture.record('budget',{})
                self.assertEqual(len(capture._pending_publications),1)
                with self.assertRaisesRegex(RuntimeError,'CAPTURE_PUBLICATION_FAILED_NO_SEAL'):capture.seal()


if __name__=='__main__':unittest.main()

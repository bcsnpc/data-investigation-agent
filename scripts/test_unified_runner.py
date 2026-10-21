import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from investigator.unified_runner import run,retry,transient,load,command
from investigator.process_tape import Tape,bytes_of

HEADER={'entry_point':'runner','context_identity':'fixture-context','config':{},'profile':{},'usage_policy':None,'engine_hash':'fixture-engine','state':{}}

class RunnerTests(unittest.TestCase):
    def config(self,root):
        return {'version':'dia-runner-estate-v1','manifest':'/inputs/estate.json','image':'registry/worker@sha256:'+'a'*64,'capture':{},'checks':{'bronze':{'kind':'probe','options':{}}},'output_root':str(root/'results'),'bootstrap':HEADER}
    def test_header_refuses_before_any_transport_or_handler(self):
        with tempfile.TemporaryDirectory() as d:
            config=self.config(Path(d));config['bootstrap']={'request':'old malformed header'}
            calls=[]
            with self.assertRaisesRegex(ValueError,'TAPE_BOOTSTRAP_FIELDS'):
                run(config,'bronze',registry={'probe':lambda *_:calls.append('read')},put=lambda *_:calls.append('put'))
            self.assertEqual(calls,[])
    def test_native_result_retained_even_when_final_seal_fails(self):
        with tempfile.TemporaryDirectory() as d:
            retained={}
            def handler(plan,ctx):
                ctx.record('native-result',{'value':7661})
                raise ValueError('FINAL_SEAL_FAILED')
            with self.assertRaisesRegex(ValueError,'FINAL_SEAL_FAILED'):
                run(self.config(Path(d)),'bronze',registry={'probe':handler},put=lambda k,v:retained.setdefault(k,v))
            values=[json.loads(v) for v in retained.values()]
            self.assertIn({'value':7661},values)
            self.assertEqual(values[-1]['status'],'FAILED')
            self.assertTrue(values[-1]['partial'])
    def test_existing_tape_each_event_mirrored_before_read_can_return(self):
        with tempfile.TemporaryDirectory() as d:
            retained={}
            def handler(plan,ctx):
                tape=Tape(ctx.root/'native.json',bootstrap=HEADER)
                tape.event('CONFIGURATION',bytes_of({'value':16}))
                self.assertEqual(sum('tape-event' in k for k in retained),2)
                tape.finish({'value':16})
                return {'value':16}
            result=run(self.config(Path(d)),'bronze',registry={'probe':handler},put=lambda k,v:retained.setdefault(k,v))
            self.assertEqual(result['status'],'COMPLETED')
            self.assertEqual(sum('tape-event' in k for k in retained),3)
    def test_transient_twice_retry_and_no_authorization_retry(self):
        calls=[];wait=[];events=[]
        def call():
            calls.append(1)
            if len(calls)<3:raise TimeoutError('connect')
            return 16
        self.assertEqual(retry(call,record=lambda *x:events.append(x),sleep=wait.append),16)
        self.assertEqual(wait,[30,45]);self.assertEqual(len(events),2)
        self.assertFalse(transient(ValueError('billing authorization failed')))
        self.assertFalse(transient(ValueError('guardrail denied')))
    def test_registry_has_no_user_code_or_shell(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'estate.json';config=self.config(Path(d));config['checks']['bad']={'kind':'os.system','options':{}}
            p.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError,'RUNNER_TYPED_CHECK_REQUIRED'):load(p)
            self.assertEqual(command('/inputs/runner.json','bronze'),['python','/app/scripts/dia.py','run','bronze','--estate','/inputs/runner.json','--runtime','worker'])
    def test_real_process_kill_preserves_partial_remote_blob_objects(self):
        # The fake Blob service is an independent filesystem durable store. The
        # child uses the real runner and is killed while the second read blocks.
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);blob=root/'fake-blob';blob.mkdir()
            script=root/'child.py'
            config=self.config(root)
            script.write_text('''import json,time,sys
from pathlib import Path
from investigator.unified_runner import run
root=Path(sys.argv[1]);config=json.loads(sys.argv[2])
def put(key,raw):
 p=root/'fake-blob'/key;p.parent.mkdir(exist_ok=True,parents=True)
 with p.open('xb') as f:f.write(raw);f.flush();__import__('os').fsync(f.fileno())
def handler(plan,ctx):
 ctx.step('first-read',lambda:{'value':7661})
 (root/'ready').write_text('ready')
 time.sleep(60)
run(config,'bronze',registry={'probe':handler},put=put,run_id='killed-run')
''')
            env={**os.environ,'PYTHONPATH':str(Path(__file__).parent)}
            child=subprocess.Popen([sys.executable,str(script),str(root),json.dumps(config)],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                import time
                deadline=time.time()+15
                while not (root/'ready').exists() and child.poll() is None and time.time()<deadline:time.sleep(.05)
                self.assertTrue((root/'ready').exists(),child.communicate(timeout=1) if child.poll() is not None else 'child failed to reach read')
                child.kill();child.wait(timeout=5)
                entries=[json.loads(p.read_bytes()) for p in sorted((blob/'killed-run').glob('*.json'))]
                self.assertTrue(any(v.get('result')=={'value':7661} for v in entries))
                self.assertTrue(any(v.get('status')=='STARTED' and v.get('partial') for v in entries))
                self.assertFalse(any(v.get('status')=='COMPLETED' for v in entries))
            finally:
                if child.poll() is None:child.kill();child.wait()
                child.communicate()

if __name__=='__main__':unittest.main()

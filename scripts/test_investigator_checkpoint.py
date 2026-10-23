import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from investigator.investigator_checkpoint import Checkpoint, FileStore, SharedStore
from investigator.shared_state import SharedState, StateConflict


CHILD = r'''
import copy,json,os,sys
from pathlib import Path
import test_ledger_investigator as fixtures
from investigator.investigator_checkpoint import Checkpoint,FileStore
root=Path(sys.argv[1]);kill=sys.argv[2]=='kill'
tools,engine,reader,_=fixtures.ToolLoopTests().build()
engine.checkpoint=Checkpoint(FileStore(root/'checkpoint.json'),{'engine':'fixed-test-engine'})
def read(node,key,context):
    with (root/'reads.txt').open('a')as f:f.write(node+'\n')
    return fixtures.read(node,8 if node=='up'else 7,context)
reader.side_effect=read
def decide(payload,**kwargs):
    if not payload['case_file']['decisions']:
        return {'action':'TOOL','summary':'Compare the admitted boundary','hypotheses':['not found'],'tool':'compare_layers','arguments':{'key':'record-1','layers':['down','up'],'filters':tools.context}}
    if kill:
        (root/'before-kill-case.json').write_text(json.dumps(engine.case.snapshot(),sort_keys=True))
        os._exit(17)
    (root/'resumed-prefix-case.json').write_text(json.dumps(engine.case.snapshot(),sort_keys=True))
    return {'action':'VERDICT','verdict':'failed job','summary':'Report the linked failed load','hypotheses':['failed job'],'evidence_ids':list(tools.evidence._values)}
engine.decide=decide
answer=engine.run({'visual':'visual'})
(root/'answer.json').write_text(json.dumps(answer))
'''


class CheckpointTests(unittest.TestCase):
    def test_killed_investigation_resumes_completed_steps_and_identical_case_without_re_reads(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, 'PYTHONPATH': str(Path(__file__).parent.resolve())}
            first = subprocess.run([sys.executable, '-c', CHILD, tmp, 'kill'], env=env,
                                   capture_output=True, text=True, timeout=30)
            self.assertEqual(first.returncode, 17, first.stderr)
            root = Path(tmp)
            before = (root/'reads.txt').read_bytes()
            checkpoint = json.loads((root/'checkpoint.json').read_bytes())
            self.assertEqual(checkpoint['pending']['name'], 'model')
            self.assertIsNone(checkpoint['outcome'])
            second = subprocess.run([sys.executable, '-c', CHILD, tmp, 'resume'], env=env,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual((root/'reads.txt').read_bytes(), before)
            self.assertEqual(json.loads((root/'before-kill-case.json').read_bytes()),
                             json.loads((root/'resumed-prefix-case.json').read_bytes()))
            final = json.loads((root/'checkpoint.json').read_bytes())
            self.assertIsNotNone(final['outcome'])
            self.assertIsNone(final['pending'])
            self.assertEqual(final['outcome']['case_file']['current_step'], 'deliver')

    def test_corrupt_or_different_binding_refuses_before_reusing_an_operation(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FileStore(Path(tmp)/'checkpoint.json')
            original = Checkpoint(store, {'engine': 'one'})
            original.begin({'ticket': 'one'})
            original.save()
            with self.assertRaises(StateConflict):
                Checkpoint(store, {'engine': 'two'}).begin({'ticket': 'one'})
            value = store.load(); value['pins']['ticket'] = 'changed'; store.save(value)
            with self.assertRaises(StateConflict):
                Checkpoint(store, {'engine': 'one'}).begin({'ticket': 'one'})

    def test_shared_store_requires_explicit_resume_and_optimistic_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = SharedState.offline(Path(tmp)/'state.sqlite'); state.migrate()
            first = SharedStore(state, 'case-1'); self.assertIsNone(first.load())
            first.save({'case': 1})
            with self.assertRaises(StateConflict): SharedStore(state, 'case-1').load()
            second = SharedStore(state, 'case-1', resume=True)
            self.assertEqual(second.load(), {'case': 1})
            second.save({'case': 2})
            with self.assertRaises(StateConflict): first.save({'case': 3})


if __name__ == '__main__':
    unittest.main()

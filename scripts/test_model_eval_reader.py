import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import MagicMock
import test_investigator_workspace as fixture
from investigator.model_eval_reader import run_case
from investigator.process_tape import Tape


class ModelEvalReaderTests(unittest.TestCase):
    def setUp(self):
        self.h=fixture.WorkspaceTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        self.g=json.loads((Path(__file__).resolve().parents[1]/'acceptance/model_steps/reader.json').read_text())
        self.case=self.g['cases'][0]

    def execute(self,provider):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'reader.tape.json'
            result=run_case(self.h.agent,self.g,self.case,provider,path,'reader-evaluation')
            tape=Tape(path)
            self.assertFalse(any(e['kind'].startswith(('WORKER_','BOUNDED_')) for e in tape.events))
            self.h.native.assert_not_called();self.h.source.assert_not_called();self.h.planner.assert_not_called()
            return result,tape

    def test_one_metered_model_call_no_verification_and_exact_consumer_schema(self):
        p=copy.deepcopy(self.case['expected_bindings'][0]);p.update(extractor='MODEL',confidence=0.5)
        provider=MagicMock(return_value=([p],{'usage':{'input_tokens':10,'output_tokens':20}}))
        before=self.h.agent.governor.snapshot();r,tape=self.execute(provider)
        self.assertEqual(r['proposals'],[p]);self.assertFalse(r['verification_performed'])
        self.assertEqual(r['model_calls'],1);self.assertNotEqual(before,self.h.agent.governor.snapshot())
        self.assertEqual(provider.call_count,1)
        payload,schema,options=provider.call_args.args
        self.assertEqual(set(payload),{'code','layers'})
        self.assertEqual(schema['properties']['extractor'],{'type':'string','const':'MODEL'})
        def walk(node):
            if isinstance(node,dict):
                if 'enum' in node or 'const' in node:self.assertIn('type',node)
                for value in node.values():walk(value)
            elif isinstance(node,list):
                for value in node:walk(value)
        walk(schema)
        self.assertEqual(tape.bootstrap['entry_point'],'model_eval_reader')

    def test_rejected_raw_candidate_is_preserved_for_precision(self):
        p=copy.deepcopy(self.case['expected_bindings'][0]);p.update(extractor='MODEL',confidence=0.5)
        p['sources'][0]['table']='invented'
        r,_=self.execute(MagicMock(return_value=([p],{})))
        self.assertEqual(r['proposals'],[p]);self.assertIsNotNone(r['validation_error'])
        self.assertFalse(r['semantic_refusal'])

    def test_budget_refusal_sealed_without_provider_or_semantic_refusal(self):
        self.h.agent.governor.policy['daily_limits']['planner_calls']=1
        with self.h.runtime.db() as db:
            self.h.agent.governor.reserve(db,'earlier','one','planner',1,output_tokens=1500)
        provider=MagicMock();r,tape=self.execute(provider)
        provider.assert_not_called();self.assertEqual(r['model_calls'],0)
        self.assertTrue(r['budget_hold']);self.assertFalse(r['semantic_refusal'])
        self.assertEqual(tape.events[-1]['kind'],'FINAL')


if __name__=='__main__':unittest.main()

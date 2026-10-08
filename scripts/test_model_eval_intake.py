import json,tempfile,unittest
from pathlib import Path
from unittest.mock import MagicMock
from investigator.model_eval_intake import run_case
from investigator.process_tape import Tape
from test_investigator_workspace import WorkspaceTests
from test_question_intake import ask


class ModelEvalIntakeTests(unittest.TestCase):
    def test_thirteen_case_eval_retains_visual_coverage_without_sending_native_parts(self):
        golden=json.loads((Path(__file__).resolve().parents[1]/'acceptance/model_steps/intake-round-ten-misses.json').read_text())
        from investigator.model_eval_intake import workspace
        from investigator.question_intake import snapshot
        h=WorkspaceTests();h.setUp();self.addCleanup(h.doCleanups)
        owner=workspace(h.agent,golden['catalog'],None)
        view=snapshot(owner)
        self.assertEqual(sum(len(m['visuals']) for m in view['models']),52)
        for row in view['models']:
            self.assertNotIn('evaluation_context',row)
            self.assertNotIn('model_assets',row)
            self.assertNotIn('context',row)

    def test_real_intake_settles_existing_governor_and_has_no_estate_transport(self):
        h=WorkspaceTests();h.setUp();self.addCleanup(h.doCleanups)
        golden=json.loads((Path(__file__).resolve().parents[1]/'acceptance/model_steps/intake.json').read_text())
        case={'id':'unit-refusal','text':'Which information should I inspect?'}
        resolver=MagicMock(return_value=(ask(),{'usage':{'input_tokens':1,'output_tokens':1}}))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'eval.tape.json'
            before=h.agent.governor.snapshot()
            result=run_case(h.agent,golden,case,resolver,path,'one-evaluation')
            after=h.agent.governor.snapshot()
            self.assertEqual(result['status'],'NEEDS_INPUT')
            self.assertEqual(resolver.call_count,1)
            self.assertEqual(resolver.call_args.args[0]['models'][0]['id'],'inventory-model')
            self.assertNotEqual(before,after)
            tape=Tape(path)
            self.assertEqual(tape.bootstrap['entry_point'],'model_eval_intake')
            self.assertFalse(any(e['kind'].startswith(('WORKER_','BOUNDED_')) for e in tape.events))
            h.native.assert_not_called();h.source.assert_not_called();h.planner.assert_not_called()
            self.assertEqual(h.agent.store,h.store)


if __name__=='__main__':unittest.main()

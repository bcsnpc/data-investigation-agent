import json,tempfile,unittest
from pathlib import Path
from unittest.mock import MagicMock
from investigator.model_eval_intake import run_case
from investigator.process_tape import Tape
from test_investigator_workspace import WorkspaceTests
from test_question_intake import ask


class ModelEvalIntakeTests(unittest.TestCase):
    def test_current_golden_covers_all_fifty_sealed_texts_and_nine_families(self):
        root=Path(__file__).resolve().parents[1]
        golden=json.loads((root/'acceptance/model_steps/intake-round-ten-current-59.json').read_text())
        index=json.loads((root/'acceptance/tickets/round-ten/index.json').read_text())
        cases={c['id']:c for c in golden['cases']}
        self.assertEqual(len(cases),59)
        for entry in index['entries']:
            source=json.loads((root/entry['path']).read_text())
            self.assertEqual(cases[entry['id']]['text'],source['ticket_text'])
            self.assertEqual(cases[entry['id']]['source_sha256'],entry['sha256'])
            self.assertIn('nominated_question_kind',cases[entry['id']]['expected'])
        self.assertEqual({c['family'] for c in cases.values() if c['group']=='nine'},set('ABCDEFGHI'))

    def test_ci_quality_agent_installs_no_estate_reader(self):
        from investigator.model_eval_intake import ci_agent
        with tempfile.TemporaryDirectory() as directory:
            agent=ci_agent(directory,{'adapter':'injected'})
            self.assertIsNone(agent.runtime.native_transport)
            self.assertIsNone(agent.runtime.source_transport)
            self.assertIsNone(agent.planner)
            self.assertEqual(agent.governor.snapshot()['read_allowance']['ordinary_charged'],0)
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

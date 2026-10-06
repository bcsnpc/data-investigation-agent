import ast,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch,Mock
from investigator.acceptance_context import pin_run_context,assert_run_context,context_handles
from investigator.onboarding import Conflict,digest
from investigator.question_intake import Intake

class Store:
    def __init__(self,root,context,pins=None):
        self.database=root/'catalog';self.inventory=root/'inventory';self.environment='test'
        self.context_pins=pins or {};self.context=context
    def get(self,identity):
        return {'context_id':self.context['id'],'context':self.context,'revision':20,'enabled':True}

class RunPinTests(unittest.TestCase):
    def graph(self,store):
        runtime=NS(store=store);agent=NS(store=store,runtime=runtime,governor=NS(runtime=runtime))
        ws=NS(store=store,agent=agent)
        ws.intake=object.__new__(Intake);ws.intake.workspace=ws;ws.intake.store=store;ws.intake.resolver=Mock()
        ws.screenshots=NS(store=store,workspace=ws)
        return ws
    def selected(self,root,identity='old'):
        c={'id':identity};s=Store(root,c,{'model':{'context_id':identity,'hash':digest(c)}})
        s.acceptance_fixture_state={'name':'baseline','context':s.context_pins['model']};return s
    def pin(self,ws,selected):
        with patch('investigator.acceptance_context.load_case',return_value={'model_id':'model'}),patch('investigator.acceptance_context.select_store',return_value=selected) as select:
            self.assertIs(pin_run_context(ws,'case',fixture={}),selected)
            select.assert_called_once_with('case',select.call_args.args[1],'model',fixture={},invoked_state=None,invoked_context=None)
    def test_single_entry_pins_every_captured_store_and_future_consumer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);old=Store(root,{'id':'new'});ws=self.graph(old)
            ws.extra_consumer=NS(store=old)
            selected=self.selected(root);self.pin(ws,selected)
            handles=context_handles(ws)
            self.assertEqual({n for n,_ in handles},{'workspace.store','workspace.agent.store','workspace.agent.runtime.store','workspace.agent.governor.runtime.store','workspace.intake.store','workspace.screenshots.store','workspace.extra_consumer.store'})
            self.assertTrue(all(o.store is selected for _,o in handles));assert_run_context(ws)
    def test_each_mutated_handle_refuses_before_intake_with_all_values_named(self):
        for target in ('workspace.store','workspace.agent.store','workspace.agent.runtime.store','workspace.intake.store','workspace.screenshots.store'):
            with self.subTest(target=target),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);selected=self.selected(root);ws=self.graph(selected);self.pin(ws,selected)
                dict(context_handles(ws))[target].store=Store(root,{'id':'wrong'})
                with self.assertRaisesRegex(Conflict,'Run context handles disagree') as e:ws.intake.resolve({})
                for name,_ in context_handles(ws):self.assertIn(name,str(e.exception))
                self.assertIn('wrong',str(e.exception));ws.intake.resolver.assert_not_called()
    def test_sealed_family_a_mismatch_is_rejected_before_intake(self):
        fixture=json.loads((Path(__file__).parent/'fixtures/context_pin_a_failure.json').read_text())
        self.assertEqual(len(fixture['source_tape_sha256']),64)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);selected=self.selected(root,fixture['selected_context']['context_id']);ws=self.graph(selected);self.pin(ws,selected)
            ws.store=Store(root,{'id':fixture['preview_context_id']})
            with self.assertRaises(Conflict) as e:ws.intake.resolve({})
            self.assertIn(fixture['selected_context']['context_id'],str(e.exception))
            self.assertIn(fixture['preview_context_id'],str(e.exception));ws.intake.resolver.assert_not_called()
    def test_new_independent_handle_after_pin_refuses_and_foreign_estate_cannot_be_pinned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);selected=self.selected(root);ws=self.graph(selected);self.pin(ws,selected)
            ws.late_reader=NS(store=selected)
            with self.assertRaisesRegex(Conflict,'late_reader'):assert_run_context(ws)
            ws=self.graph(Store(root/'other',{'id':'foreign'}))
            with patch('investigator.acceptance_context.load_case',return_value={'model_id':'model'}),patch('investigator.acceptance_context.select_store',return_value=selected):
                with self.assertRaisesRegex(Conflict,'another estate'):pin_run_context(ws,'case',fixture={})
    def test_live_runner_has_one_pin_call_and_no_individual_context_setters(self):
        path=Path(__file__).resolve().parents[1]/'acceptance/known_domain/run.py'
        tree=ast.parse(path.read_text())
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='pin_run_context']
        self.assertEqual(len(calls),1)
        for node in ast.walk(tree):
            if isinstance(node,(ast.Assign,ast.AnnAssign,ast.AugAssign)):
                targets=node.targets if isinstance(node,ast.Assign) else [node.target]
                for target in targets:
                    self.assertFalse(isinstance(target,ast.Attribute) and target.attr in ('store','context_pins','context_id'),ast.dump(target))

if __name__=='__main__':unittest.main()

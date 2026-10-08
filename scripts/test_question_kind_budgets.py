import copy
import unittest
from unittest.mock import patch
from investigator import question_kind,process_budget,observation_journal,refusal_synthesis
from investigator.question_intake import validate,wire_contract
from investigator.process_debugging import vertical,_observation
from investigator.usage_governance import UsageHold
from test_declared_reproduction import NeutralAdapter,exact
import test_question_intake as intake_fixture


def subject(kind):
    return {'kind':kind,'source':{'start':0,'end':6,'quote':'Report'}}


class QuestionKindBudgetTests(unittest.TestCase):
    def test_budget_receipt_cannot_drop_accounting_required_by_renderer(self):
        from investigator.process_receipts import refusal,validate_for_synthesis
        from investigator.onboarding import Conflict
        budget={'diagnostic_reads':2,'diagnostic_limit':4,'phase_counts':{'WALK':2,'REPRODUCTION':0},
            'phase_limits':{'WALK':2,'REPRODUCTION':2},'admission_reason':'Synthetic stop',
            'not_run_probes':[{'operation':'third probe','layer':'remaining'}]}
        for field in budget:
            wrong=copy.deepcopy(budget);wrong.pop(field)
            with self.subTest(field=field),self.assertRaises(Conflict):refusal('BUDGET_STOP','Stopped.','stop',budget=wrong)
        receipt=refusal('BUDGET_STOP','Stopped.','stop',budget=budget)
        for field in budget:
            wrong=copy.deepcopy(receipt);wrong.pop(field)
            with self.subTest(field=field),self.assertRaises(Conflict):validate_for_synthesis(wrong)

    def test_optional_metadata_cannot_swallow_a_usage_hold(self):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        adapter=object.__new__(MicrosoftProcessAdapter)
        adapter.store=None;adapter.model={'workspace':'example'}
        adapter.read_snapshot_identity=lambda *_:(_ for _ in ()).throw(UsageHold('No credit'))
        adapter.read_refresh_timing=lambda:(_ for _ in ()).throw(UsageHold('No credit'))
        with patch('investigator.context_search.latest',return_value={}):
            with self.assertRaises(UsageHold):adapter.snapshot_identity(None)
        with self.assertRaises(UsageHold):adapter.refresh_timing({})

    def test_added_intake_context_does_not_remove_catalog_entries(self):
        import json
        from pathlib import Path
        data=json.loads((Path(__file__).parent/'fixtures/intake-nine-families.json').read_text())
        for case in data['cases']:
            payload=copy.deepcopy(case['payload']);before=copy.deepcopy(payload)
            wire,_,_=wire_contract(payload)
            self.assertEqual(payload,before)
            for field in ('measures','columns','reports'):
                self.assertEqual(sum(len(m.get(field,[])) for m in wire['models']),sum(len(m.get(field,[])) for m in payload['models']))

    def scope(self,kind):
        return {'filters':[{'column_id':'field-a','operator':'in','values':['y']}],'dimension_ids':[], 'reported_figure':exact(3),
                'question_kind':subject(kind)}

    def test_freshness_and_source_question_spend_no_reproduction_reads(self):
        for kind in ('FRESHNESS','SOURCE_CORRECTNESS'):
            adapter=NeutralAdapter();result=vertical(adapter,'metric',self.scope(kind))
            self.assertEqual(adapter.read_scopes,[])
            marker=next(o for o in result['_observations'] if o['id']=='declared-reproduction-not-applicable')
            self.assertEqual(marker['capability_status'],'UNDECLARED')
            self.assertIn(kind,marker['reason'])

    def test_visual_question_runs_reproduction(self):
        adapter=NeutralAdapter();result=vertical(adapter,'metric',self.scope('VISUAL_CONTENT'))
        self.assertEqual(len(adapter.read_scopes),2)
        self.assertTrue(any(o.get('check_kind')=='DECLARED_CONTEXT_REPRODUCTION' for o in result['_observations']))

    def test_four_read_cap_has_disjoint_binding_subbudgets(self):
        scope=self.scope('FIGURE_DIFFERENCE');scope.update(report_binding={'report_id':'report'},selection_request={'state':'REQUESTED'})
        state={'envelope':{'limits':{'cloud_calls':4},**scope},'cloud_calls':0}
        self.assertEqual(process_budget.allocation(4,scope),{'WALK':2,'REPRODUCTION':2})
        for phase in ('WALK','REPRODUCTION'):
            with process_budget.phase(phase):
                for _ in range(2):
                    process_budget.admit(state,'probe');process_budget.charge(state);state['cloud_calls']+=1
                with self.assertRaises(UsageHold):process_budget.admit(state,'third-probe')
        self.assertEqual(state['cloud_calls'],4)
        self.assertEqual(state['diagnostic_phase_counts'],{'WALK':2,'REPRODUCTION':2})

    def test_difference_with_selection_defers_reproduction_until_walk_stops(self):
        adapter=NeutralAdapter();scope=self.scope('FIGURE_DIFFERENCE')
        scope.update(report_binding={'report_id':'report'},selection_request={'state':'REQUESTED'})
        path=adapter.resolve_path('metric');path['layers']=path['layers'][:1]
        with patch.object(adapter,'resolve_path',return_value=path),patch('investigator.report_resolution.prepare',return_value=(scope,[])):
            result=vertical(adapter,'metric',scope)
        self.assertEqual(adapter.events[:1],['vertical-top'])
        self.assertEqual(adapter.events[1:3],['reproduction','reproduction'])
        self.assertEqual(len(result['business_output']['declared_context_reproductions']),1)

    def test_unknown_kind_refuses_before_any_diagnostic(self):
        value=intake_fixture.proposal();value['question_kind']={'kind':'INVENTED','source':{'start':0,'end':5,'quote':'ratio'}}
        with self.assertRaisesRegex(ValueError,'Unknown question kind'):
            validate(value,{'text':'ratio','models':[]})
        payload={'text':'Report','models':[]};_,schema,_=wire_contract(payload)
        self.assertEqual(schema['properties']['question_kind']['anyOf'][1]['properties']['kind']['enum'],list(question_kind.LEGACY_KINDS))
        self.assertIn('question_kind',schema['required'])

    def test_filter_effect_reproduces_but_never_reads_a_lower_layer(self):
        adapter=NeutralAdapter()
        with patch.object(adapter,'evaluate',wraps=adapter.evaluate) as evaluate:
            with self.assertRaisesRegex(question_kind.UnimplementedRoute,'no pipeline walk'):
                vertical(adapter,'metric',self.scope('FILTER_EFFECT'))
        self.assertEqual(len(adapter.read_scopes),2)
        self.assertEqual(evaluate.call_count,1)

    def test_unimplemented_route_refuses_at_intake_no_investigation_reads_or_calls(self):
        helper=intake_fixture.IntakeTests();helper.setUp();self.addCleanup(helper.doCleanups)
        value=intake_fixture.proposal();value['comparison_mode']='HORIZONTAL'
        helper.resolver.return_value=(value,{})
        result=helper.resolve()
        self.assertEqual(result['status'],'HELD');self.assertEqual(result['error'],'UNIMPLEMENTED_ROUTE')
        self.assertIn('HORIZONTAL',result['refusal_reason'])
        helper.h.native.assert_not_called();helper.h.source.assert_not_called();helper.h.planner.assert_not_called()

    def test_hold_preserves_two_original_probes_and_remaining_names(self):
        journal=observation_journal.Journal()
        try:
            with observation_journal.scope(journal):
                first=_observation({'id':'first','tool':'context','quantity':1},'established')
                second=_observation({'id':'second','tool':'context','quantity':2},'established')
                observation_journal.pending([{'operation':'third check','layer':'third'}, {'operation':'fourth check','layer':'fourth'}])
                raise UsageHold('Synthetic cap')
        except UsageHold:pass
        self.assertIs(journal[0],first);self.assertIs(journal[1],second)
        from investigator.process_receipts import refusal
        stop=refusal('BUDGET_STOP','Read budget stopped after 2 of 4 diagnostic reads; the next requested check did not run.','hold',budget={
            'diagnostic_reads':2,'diagnostic_limit':4,'phase_counts':{'WALK':2,'REPRODUCTION':0},
            'phase_limits':{'WALK':4,'REPRODUCTION':0},'admission_reason':'Synthetic cap',
            'not_run_probes':list(journal.pending_probes)})
        state={'envelope':{'symptom':'Is this figure current?'},'observations':[first,second,stop]}
        outputs=refusal_synthesis.render(state)
        for output in ('business_output','technical_output'):
            text=outputs[output]['explanation']['text']
            self.assertEqual(text.count(stop['reason']),1)
            self.assertNotIn('PROCESS_FAILED',text)
        text=outputs['technical_output']['explanation']['text']
        self.assertIn('third check on third',text);self.assertIn('fourth check on fourth',text)

    def test_runtime_hold_keeps_original_observations_not_process_failure(self):
        import test_flexible_investigation as fixture
        from investigator.adaptive_runtime import AdaptiveRuntime
        from investigator.process_debugging import VERSION
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        envelope=copy.deepcopy(helper.envelope);envelope['strategy']=VERSION
        envelope['limits']['cloud_calls']=4
        agent=AdaptiveRuntime(helper.runtime,lambda _:self.fail('No planner'))
        identity=agent.create(envelope,'synthetic-budget-stop')['id']
        def hold(adapter,*args):
            for name in ('first','second'):
                result=adapter.meter_read('bounded_dax',lambda n=name:{'id':n,'tool':'context','metadata':{'context_version':'test'},'quantity':1})
                _observation(result,'established')
            observation_journal.pending([{'operation':'third check','layer':'third'}, {'operation':'fourth check','layer':'fourth'}])
            raise UsageHold('Synthetic ordinary window exhausted')
        with patch('investigator.process_debugging.vertical',hold):result=agent.run(identity)
        self.assertEqual(result['stop_reason'],'BUDGET_LIMIT')
        self.assertEqual(result['cloud_calls'],2)
        self.assertEqual([o['id'] for o in result['observations'][:2]],['first','second'])
        stop=result['observations'][-1]
        self.assertEqual(stop['check_kind'],'BUDGET_STOP')
        self.assertEqual(len(stop['not_run_probes']),2)
        self.assertFalse(any(o.get('check_kind')=='PROCESS_FAILED' for o in result['observations']))

    def test_unimplemented_route_hold_retains_prior_receipts_and_is_not_a_crash(self):
        import test_flexible_investigation as fixture
        from investigator.adaptive_runtime import AdaptiveRuntime
        from investigator.process_debugging import VERSION
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        envelope=copy.deepcopy(helper.envelope);envelope['strategy']=VERSION
        agent=AdaptiveRuntime(helper.runtime,lambda _:self.fail('No planner'))
        identity=agent.create(envelope,'synthetic-filter-route-stop')['id']
        def hold(adapter,*args):
            result=adapter.meter_read('bounded_dax',lambda:{'id':'retained-read','tool':'context',
                'metadata':{'context_version':'test'},'quantity':16})
            _observation(result,'established')
            raise question_kind.UnimplementedRoute('Filter effects have not been tested.')
        with patch('investigator.process_debugging.vertical',hold):result=agent.run(identity)
        self.assertEqual(result['status'],'HELD');self.assertEqual(result['stop_reason'],'UNIMPLEMENTED_ROUTE')
        self.assertEqual(result['cloud_calls'],1)
        self.assertEqual(result['observations'][0]['id'],'retained-read')
        self.assertEqual(result['observations'][-1]['check_kind'],'UNIMPLEMENTED_ROUTE')
        self.assertFalse(any(o.get('check_kind')=='PROCESS_FAILED' for o in result['observations']))


if __name__=='__main__':unittest.main()

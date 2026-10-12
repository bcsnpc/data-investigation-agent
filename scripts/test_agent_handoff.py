import copy
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from investigator import agent_handoff as handoff
from investigator.onboarding import Conflict


class HandoffTests(unittest.TestCase):
    def workspace(self, enabled=True):
        return SimpleNamespace(execution_enabled=True, agent=SimpleNamespace(config={
            '_estate': {'investigation': {'mode': 'PIPELINE', 'automatic_handoff': {'enabled': enabled}}}}))

    def source(self):
        return {'id': 'claim', 'revision': 1, 'status': 'CONFIRMED', 'history': [], 'questions': []}

    def process(self, observations, **extras):
        return {'observations': observations, 'assessment': {'classification': 'NO_KNOWN_PATTERN',
            'support': {'process': {'capabilities_declared': ['transformation_definition'],
                'skipped_steps': [{'step': 5, 'capability': 'transformation_definition'}], **extras}}}}

    def assert_trigger(self, name, source, result=None):
        record = handoff.authority(self.workspace(), source, result)
        self.assertIn(name, record['eligible_kinds'])
        self.assertEqual(handoff.validate(self.workspace(), record, retained=lambda: record), record)
        self.assertEqual(source, record['original']['source'])

    def test_pipeline_gap_uses_retained_typed_unimplemented_step(self):
        self.assert_trigger('PIPELINE_GAP', self.source(), {'status': 'HELD', 'reason': 'CLAIM_SCOPE_NOT_COMPILED'})

    def test_metric_capability_gaps_are_eligible_but_read_and_budget_failures_are_not(self):
        for reason in ('METRIC_CANDIDATE_COVERAGE_INCOMPLETE', 'METRIC_CONTEXT_NOT_COMPARABLE',
                       'METRIC_MULTI_BRANCH_WALK_UNAVAILABLE', 'METRIC_FILTERED_LOWER_COMPARISON_UNSUPPORTED'):
            self.assert_trigger('PIPELINE_GAP', self.source(), {'status': 'HELD', 'reason': reason})
        for reason in ('METRIC_CANDIDATE_READ_UNAVAILABLE', 'CANDIDATE_DIAGNOSTIC_CAP',
                       'CANDIDATE_RECEIPT_INVALID', 'CANDIDATE_CONTEXT_CHANGED', 'AUTHORIZATION_FAILED'):
            self.assertIsNone(handoff.authority(self.workspace(), self.source(), {'status': 'HELD', 'reason': reason}))

    def test_unreadable_transformation_requires_actual_engine_check(self):
        self.assert_trigger('UNREADABLE_TRANSFORMATION', self.source(), self.process([]))

    def test_unknown_route_requires_one_real_question_reply_and_engine_route_failure(self):
        source = self.source(); source['history'] = [
            {'kind': 'QUESTION_PLANNED', 'question_id': 'q'},
            {'kind': 'REPLIED', 'question_id': 'q', 'request_hash': 'r'}]
        self.assert_trigger('UNKNOWN_ROUTE_AFTER_QUESTION', source,
            {'status': 'HELD', 'reason': 'UNIMPLEMENTED_CLAIM_ROUTE'})

    def test_conflicting_layers_require_comparable_original_probe_references(self):
        observations = [{'id': 'upper'}, {'id': 'lower'}, {'id': 'comparison', 'values_equal': False,
            'comparison_status': 'CROSS_SURFACE_VERIFIED', 'upper_evidence_id': 'upper', 'lower_evidence_id': 'lower'}]
        self.assert_trigger('CONFLICTING_LAYER_EVIDENCE', self.source(), self.process(observations))

    def test_unmatched_reply_requires_typed_fact_coverage_for_the_same_real_reply(self):
        source = self.source(); source['history'] = [
            {'kind': 'REPLY_TYPE_MATCH', 'question_id': 'q', 'request_hash': 'r',
             'status': 'NO_EXPECTED_TYPE', 'actual_fields': ['time']},
            {'kind': 'REPLIED', 'question_id': 'q', 'request_hash': 'r'}]
        self.assert_trigger('UNMATCHED_REPLY', source)

    def test_default_off_and_normal_completion_never_activate(self):
        w = self.workspace(); w.agent.config['_estate']['investigation'].pop('automatic_handoff')
        self.assertIsNone(handoff.authority(w, self.source(), {'status': 'HELD', 'reason': 'CLAIM_SCOPE_NOT_COMPILED'}))
        self.assertIsNone(handoff.authority(self.workspace(False), self.source(), {'status': 'HELD', 'reason': 'CLAIM_SCOPE_NOT_COMPILED'}))
        self.assertIsNone(handoff.authority(self.workspace(), self.source(), {'status': 'COMPLETED'}))

    def test_known_route_missing_direction_is_not_unknown_route(self):
        source = self.source(); source.update(status='CLARIFYING', questions=[{'field': 'direction'}])
        source['history'] = [{'kind': 'REPLIED', 'question_id': 'q', 'request_hash': 'r'}]
        self.assertIsNone(handoff.authority(self.workspace(), source))

    def test_missing_probe_or_missing_rule_status_does_not_mean_conflicting_evidence(self):
        comparison = {'id': 'comparison', 'values_equal': False, 'comparison_status': 'CROSS_SURFACE_VERIFIED',
                      'upper_evidence_id': 'upper', 'lower_evidence_id': 'lower'}
        self.assertNotIn('CONFLICTING_LAYER_EVIDENCE', handoff.candidates(self.source(), self.process([comparison])))
        result = {'observations': [{'id': 'upper'}, {'id': 'lower'}, comparison,
                    {'id': 'definition', 'process_roles': ['transformation_definition']}]}
        self.assertIsNone(handoff.authority(self.workspace(), self.source(), result))

    def test_free_text_hold_budget_readiness_and_user_or_agent_trigger_are_not_authority(self):
        for reason in ['HELD', 'ROUTE_NOT_READY', 'READ_BUDGET_EXHAUSTED', 'AUTHORIZATION_FAILED',
                       'unreadable transformation', 'CLAIM_EXTRACTION_UNAVAILABLE']:
            self.assertIsNone(handoff.authority(self.workspace(), self.source(), {'status': 'HELD', 'reason': reason}))
        source = self.source(); source['trigger'] = 'PIPELINE_GAP'
        self.assertIsNone(handoff.authority(self.workspace(), source))
        source['agent_decision'] = {'action': 'ACTIVATE', 'trigger': 'UNREADABLE_TRANSFORMATION'}
        self.assertIsNone(handoff.authority(self.workspace(), source))

    def test_hash_rebuilding_alone_does_not_replace_controller_retention(self):
        record = handoff.authority(self.workspace(), self.source(), {'status': 'HELD', 'reason': 'CLAIM_SCOPE_NOT_COMPILED'})
        with self.assertRaisesRegex(Conflict, 'not retained'):
            handoff.validate(self.workspace(), record, retained=lambda: None)
        changed = copy.deepcopy(record); changed['kind'] = 'UNMATCHED_REPLY'
        with self.assertRaisesRegex(Conflict, 'authority changed'):
            handoff.validate(self.workspace(), changed, retained=lambda: changed)

    def test_disabled_host_never_activates(self):
        w = self.workspace(); w.execution_enabled = False
        self.assertIsNone(handoff.authority(w, self.source(), {'status': 'HELD', 'reason': 'CLAIM_SCOPE_NOT_COMPILED'}))

    def test_production_ticket_gap_uses_existing_hybrid_loop_with_code_authority(self):
        from investigator import hybrid_ticket
        source={'id':'ticket','state':'HELD','history':[{'detail':{'reason':'CAPABILITY_NOT_IMPLEMENTED'}}],
                'source_intake':'intake'}
        saved={'revision':1,'ticket':source}
        process={'status':'HELD','cloud_calls':4,'observations':[],
            'assessment':{'classification':'NO_KNOWN_PATTERN','support':{'process':{
                'visibility_boundary':{'stopped_by':'CAPABILITY_NOT_IMPLEMENTED'}}}}}
        current=[copy.deepcopy(saved)]
        def update(identity,revision,apply):
            current[0]={'revision':revision+1,'ticket':apply(copy.deepcopy(current[0]['ticket']))}
            return current[0]
        w=self.workspace();w.intake=SimpleNamespace(get=Mock(return_value={'id':'intake'}))
        w.agent.get=Mock(return_value=process)
        current[0]['ticket']['session_id']='original'
        w.smart_intake=SimpleNamespace(tickets=SimpleNamespace(update=update,get=lambda identity:current[0]))
        def run(saved,**kwargs):
            self.assertTrue(handoff.controller_owned(w))
            self.assertEqual(kwargs['pipeline_result']['session'],process)
            self.assertEqual(saved['ticket']['agent_diagnostic_reads'],4)
            return 'same governed hybrid loop'
        with patch('investigator.agent_ticket.AgentTicket.run',side_effect=run) as agent:
            result=hybrid_ticket.complete(w,current[0])
        self.assertEqual(result,'same governed hybrid loop');agent.assert_called_once()
        self.assertIsNone(handoff.ACTIVE.get());self.assertIsNone(handoff.WORKSPACE.get())
        with self.assertRaises(Conflict):
            altered=copy.deepcopy(current[0]['ticket']['automatic_handoff']['authority']);altered['kind']='UNMATCHED_REPLY'
            with handoff.ticket_phase(w,altered):pass

    def test_normal_production_ticket_does_not_activate_even_when_enabled(self):
        from investigator.hybrid_ticket import submit
        w=self.workspace();w.agent.get=Mock()
        saved={'revision':1,'ticket':{'id':'ticket','state':'CLARIFYING','history':[{'detail':{}}]}}
        controller=SimpleNamespace(workspace=w)
        with patch('investigator.agent_ticket.AgentTicket.run') as agent:
            result=submit(controller,{},lambda request:saved)
        self.assertEqual(result,saved);agent.assert_not_called()


if __name__ == '__main__': unittest.main()

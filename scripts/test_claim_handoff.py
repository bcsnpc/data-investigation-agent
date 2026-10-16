import copy
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
import test_claim_intake as fixture
from investigator.claim_handoff import ClaimHandoff
from investigator.onboarding import Conflict, digest


class ClaimHandoffTests(unittest.TestCase):
    def setUp(self):
        self.h = fixture.ClaimTests(); self.h.setUp(); self.addCleanup(self.h.doCleanups)
        self.w = self.h.workspace; self.w.claims = self.h.controller
        self.w.execution_enabled = True
        self.w.agent.config = {'_estate': {'investigation': {'mode': 'PIPELINE',
            'automatic_handoff': {'enabled': True, 'step_cap': 2, 'wall_seconds': 60}}}}
        self.w.agent.clock = time.time

    def retained(self, direction=None):
        public = self.h.controller.submit(self.h.request(direction=direction))
        with self.w.store.connect() as db:
            return self.h.controller._load(db, public['id'])[1]

    def unmatched(self):
        source = self.retained()
        source['history'].extend([
            {'kind': 'REPLY_TYPE_MATCH', 'question_id': source['questions'][0]['id'],
             'request_hash': 'reply', 'actual_fields': ['time'], 'status': 'NO_EXPECTED_TYPE'},
            {'kind': 'REPLIED', 'question_id': source['questions'][0]['id'], 'request_hash': 'reply'}])
        source['revision'] += 1
        with self.w.store.connect() as db: self.h.controller._persist(db, source)
        return source

    def test_hook_is_off_by_default_without_constructing_agent(self):
        self.w.agent.config = {}
        with patch('investigator.claim_handoff.ClaimHandoff._run') as run:
            self.h.controller.submit(self.h.request())
        run.assert_not_called()

    def test_retained_claim_reply_hook_runs_one_phase_not_an_unrelated_ticket(self):
        source = self.unmatched(); phase = ClaimHandoff(self.w)
        def finish(body):
            body['status'] = 'HELD'; phase._save(body); return body
        with patch.object(phase, '_run', side_effect=finish) as run:
            first = phase.maybe(source); second = phase.maybe(source)
        self.assertEqual(first, second); run.assert_called_once()
        self.assertEqual(first['claim_id'], source['id'])
        self.assertEqual(first['authority']['original']['source'], source)

    def test_forged_source_with_recalculated_hash_never_enters_agent(self):
        source = self.unmatched(); source['claim']['settled']['direction'] = 'MORE'
        with patch('investigator.claim_handoff.ClaimHandoff._run') as run:
            with self.assertRaisesRegex(Conflict, 'current retained claim'):
                ClaimHandoff(self.w).maybe(source)
        run.assert_not_called()

    def test_real_loop_renders_grounded_question_and_preserves_settled_facts(self):
        source = self.unmatched(); before = copy.deepcopy(source['claim'])
        candidate=source['questions'][0]['choices'][0]['id']
        decide = Mock(return_value={'action': 'TOOL', 'summary':'Propose one source-backed interpretation.',
            'tool': 'propose_missing_answer', 'arguments': {'choice_id':candidate}})
        decide.calls = 1
        with patch('investigator.agent_provider.GovernedDecision', return_value=decide), \
             patch('investigator.question_intake.snapshot', return_value=copy.deepcopy(fixture.CAT)):
            phase = ClaimHandoff(self.w).maybe(source)
        self.assertEqual(phase['status'], 'WAITING_FOR_USER')
        self.assertEqual(phase['question']['field'], 'direction')
        self.assertEqual(phase['model_calls'], 1)
        self.assertEqual(phase['diagnostic_reads'], 0)
        self.assertEqual(phase['physical_requests'], 0)
        self.assertIsNone(phase['finding'])
        current = self.h.controller.get(source['id'])
        self.assertEqual(current['claim'], before)
        self.assertEqual(current['questions'], [phase['question']])
        self.assertEqual(current['status'], 'CLARIFYING')

    def test_agent_answer_cannot_turn_observation_into_unproved_finding(self):
        source = self.unmatched()
        decision = {'action': 'ANSWER', 'summary':'Answer from the saved claim.', 'outcome': 'NO_KNOWN_PATTERN',
            'claims': [{'text': 'The pipeline is defective.', 'evidence_ids': ['claim:' + digest(source)]}]}
        decide = Mock(return_value=decision); decide.calls = 2
        with patch('investigator.agent_provider.GovernedDecision', return_value=decide), \
             patch('investigator.question_intake.snapshot', return_value=copy.deepcopy(fixture.CAT)):
            phase = ClaimHandoff(self.w).maybe(source)
        self.assertEqual(phase['status'], 'HELD'); self.assertIsNone(phase['finding'])
        self.assertTrue(any(t['event'] in ('CLAIM_REJECTED', 'DECISION_REJECTED') for t in phase['loop']['transcript']))

    def test_changed_catalog_holds_before_model_or_queries(self):
        source = self.unmatched(); catalog = copy.deepcopy(fixture.CAT); catalog['models'][0]['name'] = 'changed'
        with patch('investigator.agent_provider.GovernedDecision') as provider, \
             patch('investigator.question_intake.snapshot', return_value=catalog):
            phase = ClaimHandoff(self.w).maybe(source)
        self.assertEqual(phase['reason'], 'HANDOFF_CATALOG_CHANGED'); provider.assert_not_called()

    def test_loop_exception_retains_provider_count_and_journal_reference(self):
        source=self.unmatched();decide=Mock();decide.calls=2
        with patch('investigator.agent_provider.GovernedDecision',return_value=decide), \
             patch('investigator.question_intake.snapshot',return_value=copy.deepcopy(fixture.CAT)), \
             patch('investigator.agent_loop.AgentLoop.run',side_effect=ValueError('recording failed after provider')):
            phase=ClaimHandoff(self.w).maybe(source)
        self.assertEqual(phase['status'],'HELD');self.assertEqual(phase['model_calls'],2)
        self.assertEqual(phase['journal_identity'],'claim-handoff:'+source['id'])


if __name__ == '__main__': unittest.main()

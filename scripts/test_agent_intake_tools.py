import copy
import unittest
from investigator.agent_intake_tools import IntakeTools
from investigator.onboarding import Conflict
from investigator import form_candidates
import test_form_controller

class IntakeToolTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_form_controller.FormControllerTests()
        self.fixture.setUp(); self.addCleanup(self.fixture.doCleanups)
        self.catalog = copy.deepcopy(self.fixture.catalog)
        self.catalog['versions'] = {m['id']: 'version-1' for m in self.catalog['models']}
        for m in self.catalog['models']: m['context_id'] = 'context-1'
        self.catalog['models'][0]['secret_unrelated'] = 'never-export-this'
        self.recorded = []
        self.tools = IntakeTools(lambda: self.catalog, self.record,
            candidate_reader=self.reader)
    def record(self, result):
        self.recorded.append(result); return 'evidence-' + str(len(self.recorded))
    def reader(self, candidate):
        return {'status': 'OBSERVED', 'complete': True, 'value': '16',
            'receipt_id': 'verified-receipt', 'query_hash': 'a'*64,
            'execution_surface': {'engine': 'semantic'}, 'attestation': {'consistency': 'MATCHED'},
            'query': 'never-export-query'}
    def search(self, **args):
        return self.tools.call('find_value_on_page', {'report_id': 'report', 'page_id': 'page', 'value': '16', **args})
    def second(self):
        other = copy.deepcopy(self.catalog['models'][0]['visuals'][0]); other['target_id'] = 'second'
        self.catalog['models'][0]['visuals'].append(other)
    def test_lists_only_retained_definition_fields_with_citation(self):
        for name, args in [('list_reports', {}), ('list_pages', {'report_id': 'report'}),
                           ('list_visuals', {'report_id': 'report', 'page_id': 'page'})]:
            result = self.tools.call(name, args)
            self.assertTrue(result['evidence_id']); self.assertEqual(result['provenance']['context_ids'], {'model': 'context-1'})
            self.assertNotIn('never-export', str(result))
        self.assertIn('declared_scope', self.recorded[-1]['visuals'][0]['measures'][0])
    def test_candidates_return_evidence_never_pick_even_equal_scopes(self):
        self.second(); result = self.search()
        self.assertEqual(len(result['matches']), 2); self.assertFalse(result['target_selected'])
        self.assertNotIn('scope', result); self.assertNotIn('never-export-query', str(result))
        self.assertFalse(result['coverage']['all_page_cells'])
    def test_empty_is_not_zero(self):
        self.second()
        self.tools.candidate_reader = lambda c: {**self.reader(c), 'value': None if c['target_id'] == 'card' else '0'}
        result = self.tools.call('find_value_on_page', {
            'report_id': 'report', 'page_id': 'page', 'value': 'empty'})
        self.assertEqual([r['target_id'] for r in result['matches']], ['card'])
    def test_picked_visual_is_not_changed_by_search(self):
        self.second(); self.tools._fixed = {'target_id': 'card', 'comparison': 'SOURCE_DATA'}
        original = self.tools.fixed_facts; result = self.search()
        self.assertEqual([r['target_id'] for r in result['observations']], ['card'])
        result['picked_form_facts']['target_id'] = 'second'
        self.assertEqual(self.tools.fixed_facts, original)
    def test_picked_report_page_measure_and_mode_cannot_be_replaced(self):
        for key, supplied in [('report_id', 'other'), ('page_id', 'other'), ('measure_id', 'other'), ('cell_mode', 'TOTAL')]:
            self.tools._fixed = {key: supplied}
            with self.assertRaises(Conflict): self.search(**({key: 'measure'} if key == 'measure_id' else {key: 'UNGROUPED'} if key == 'cell_mode' else {}))
    def test_absent_page_and_ambiguous_report_refuse(self):
        with self.assertRaises(Conflict): self.search(page_id='other')
        self.catalog['models'].append(copy.deepcopy(self.catalog['models'][0]))
        with self.assertRaises(Conflict): self.tools.call('list_reports', {})
    def test_incomplete_declaration_not_dropped(self):
        self.second(); self.catalog['models'][0]['visuals'][-1]['declared_scopes']['measure']['state'] = 'UNSUPPORTED'
        with self.assertRaises(form_candidates.NotMeasurable): self.search()
    def test_missing_or_unattested_probe_retains_partial_failure(self):
        self.second(); self.tools.candidate_reader = lambda c: self.reader(c) if c['target_id'] == 'card' else {'status': 'FAILED'}
        with self.assertRaises(form_candidates.NotMeasurable): self.search()
        self.assertEqual(self.recorded[-1]['status'], 'INCOMPLETE')
        self.assertEqual(len(self.recorded[-1]['observations']), 1)
        self.assertEqual(self.recorded[-1]['expected_candidates'], 2)
    def test_definition_drift_refuses_result(self):
        def mutate(c):
            self.catalog['versions']['model'] = 'version-2'; return self.reader(c)
        self.tools.candidate_reader = mutate
        with self.assertRaises(Conflict): self.search()
        self.assertEqual(self.recorded[-1]['status'], 'INCOMPLETE')
    def test_loop_handlers_validate_and_return_citations(self):
        result = self.tools.handlers()['list_reports']()
        self.assertEqual(result['evidence_ids'], [result['evidence_id']])
        self.assertFalse(result['finding_authority'])
        with self.assertRaises(Exception): self.tools.handlers()['list_reports'](extra='not allowed')
        result = self.search()
        self.assertIn('verified-receipt', result['native_evidence_ids'])

    def test_no_citation_no_result(self):
        self.tools.record_evidence = lambda result: None
        with self.assertRaises(Conflict): self.tools.call('list_reports', {})
    def test_extra_arguments_and_unknown_tools_refuse(self):
        with self.assertRaises(Exception): self.tools.call('list_reports', {'password': 'x'})
        with self.assertRaises(ValueError): self.tools.call('execute_sql', {})
    def test_question_waits_for_real_comment_answer(self):
        self.tools.comment_port = lambda request: {'comment_id': 'comment-1', 'answer': 'fabricated-by-port'}
        result = self.tools.call('ask_user', {'field':'VISUAL','report_id':'report','page_id':'page'})
        self.assertEqual(result['status'], 'WAITING_FOR_USER'); self.assertIsNone(result['answer'])
        self.assertEqual(result['comment_id'], 'comment-1')
    def test_screenshot_positions_are_validated_and_never_hidden_scope(self):
        self.tools.screenshot_reader = lambda image: {'image_sha256': 'a'*64, 'receipt_id': 'vision-receipt',
            'visible_text': 'North 16', 'items': [{'text': '16', 'box': [0.1, 0.2, 0.3, 0.4]}],
            'hidden_filters': 'invented', 'interpretation_verified': True}
        result = self.tools.call('read_screenshot', {'image_id': 'image-1'})
        self.assertEqual(result['positions_status'], 'AVAILABLE'); self.assertFalse(result['interpretation_verified'])
        self.assertNotIn('invented', str(result))
        self.tools.screenshot_reader = lambda image: {'image_sha256': 'a'*64, 'receipt_id': 'vision-receipt',
            'items': [{'text': '16', 'box': [0.8, 0.2, 0.3, 0.4]}]}
        with self.assertRaises(Conflict): self.tools.call('read_screenshot', {'image_id': 'image-1'})
    def test_legacy_screenshot_positions_explicitly_unavailable(self):
        self.tools.screenshot_reader = lambda image: {'image_sha256': 'a'*64, 'receipt_id': 'vision', 'visible_text': '16'}
        self.assertEqual(self.tools.call('read_screenshot', {'image_id': 'image'})['positions_status'], 'UNAVAILABLE_FROM_TRANSCRIPTION')
    def test_missing_ports_explicit_unavailability(self):
        self.assertEqual(self.tools.call('request_screenshot', {})['status'], 'UNAVAILABLE')
        self.assertEqual(self.tools.call('read_screenshot', {'image_id': 'image'})['status'], 'UNAVAILABLE')
        self.tools.candidate_reader = None
        self.assertEqual(self.search()['status'], 'UNAVAILABLE')

if __name__ == '__main__': unittest.main()

"""Synthetic regressions for saved-dev defects; no network or held-out data."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
import unittest

from jsonschema import Draft202012Validator, ValidationError
from investigator.guided_intake import Catalog, admit, admit_investigation_candidate
from investigator.guided_cases import Cases
from investigator.model_case_presentation import Presentation
from investigator.shared_state import SharedState
from investigator.terminal_findings import attach
from test_round23_intake_queries import graph, request


class SourceComparisonTests(unittest.TestCase):
    def test_loose_source_label_is_retained_not_resolved_or_dropped(self):
        catalog = Catalog(graph())
        original = request()
        original['compared_with'] = {'kind': 'SOURCE_SYSTEM', 'source': 'application records'}
        before = deepcopy(original)
        with self.assertRaisesRegex(ValueError, 'SOURCE_NAME_UNRESOLVED'):
            admit(original, catalog)
        value = admit_investigation_candidate(original, catalog)
        self.assertEqual(original, before)
        for field in ('report', 'page', 'visual', 'reported_figure'):
            self.assertEqual(value[field], before[field])
        self.assertEqual(value['comparison_context'], before['compared_with'])
        self.assertEqual(value['compared_with'], {'kind': 'NOTHING'})
        self.assertEqual(value['source_resolution']['status'], 'PENDING_INVESTIGATOR')
        self.assertNotIn('id', value['source_resolution'])

    def test_multiple_sources_are_not_silently_selected(self):
        native = graph()
        native['nodes'].append({'id': 'second-source', 'kind': 'SOURCE', 'label': 'Other app'})
        value = request()
        value['compared_with'] = {'kind': 'SOURCE_SYSTEM', 'source': 'the app'}
        result = admit_investigation_candidate(value, Catalog(native))
        self.assertEqual(result['comparison_context'], value['compared_with'])
        self.assertEqual(result['source_resolution']['status'], 'PENDING_INVESTIGATOR')
        self.assertNotIn('source', result['compared_with'])

    def test_exact_source_and_other_comparison_kinds_keep_strict_admission(self):
        for comparison in ({'kind': 'SOURCE_SYSTEM', 'source': 'source'},
                           {'kind': 'SOURCE_SYSTEM', 'source': 'Source'},
                           {'kind': 'NOTHING'},
                           {'kind': 'EXPECTED_NUMBER', 'figure': {
                               'state': 'NUMBER', 'value': '9', 'precision': 'EXACT'}}):
            value = request()
            value['compared_with'] = comparison
            self.assertEqual(admit_investigation_candidate(value, Catalog(graph())),
                             admit(value, Catalog(graph())))

    def test_unknown_explicit_addresses_and_wrong_node_kinds_stay_refused(self):
        for supplied in ('f' * 64, 'sql://other/database',
                         '12345678-1234-1234-1234-123456789012', 'report'):
            value = request()
            value['compared_with'] = {'kind': 'SOURCE_SYSTEM', 'source': supplied}
            with self.subTest(supplied=supplied), self.assertRaisesRegex(ValueError, 'SOURCE_NAME_UNRESOLVED'):
                admit_investigation_candidate(value, Catalog(graph()))

    def test_bad_target_and_malformed_shape_are_not_hidden_by_source_deferral(self):
        value = request()
        value['visual'] = 'othercard'
        value['compared_with'] = {'kind': 'SOURCE_SYSTEM', 'source': 'the app'}
        with self.assertRaisesRegex(ValueError, 'VISUAL_OUTSIDE_PAGE'):
            admit_investigation_candidate(value, Catalog(graph()))
        value = request()
        value['compared_with'] = {'kind': 'SOURCE_SYSTEM', 'source': 7}
        with self.assertRaises(ValidationError):
            admit_investigation_candidate(value, Catalog(graph()))

    def test_candidate_queue_preserves_original_ask_and_validates_every_target(self):
        with TemporaryDirectory() as folder:
            state = SharedState.offline(Path(folder) / 'state.sqlite')
            state.migrate()
            native = Mock()
            native.intake_catalog.return_value = graph()
            engine = Mock()
            service = Cases(state=state, graph=native, estate='test', engine_factory=engine)
            value = request()
            value['compared_with'] = {'kind': 'SOURCE_SYSTEM', 'source': 'application records'}
            original = deepcopy(value)
            inventory = {'candidates': [{'id': 'candidate', 'intake': value,
                                        'explicit': {'report': 'report', 'visual': 'card'}}]}
            result = service.submit_candidates(request_key='one', intake=value,
                inventory=inventory, source={'kind': 'MAPPED_TEXT', 'text': 'Compare with application records'})
            saved = state.get(service.namespace, result['id'])['body']
            self.assertEqual(saved['intake'], original)
            candidate = saved['candidate_inventory']['candidates'][0]['intake']
            self.assertEqual(candidate['comparison_context'], original['compared_with'])
            self.assertEqual(candidate['visual'], 'card')
            engine.assert_not_called()
            self.assertEqual(value, original)


class PresentationTests(unittest.TestCase):
    def test_selected_target_roundtrips_through_the_actual_model_boundary(self):
        target = 'a' * 64
        schema = {'type': 'object', 'properties': {'selected_target': {'enum': [target]}},
                  'required': ['selected_target']}
        tools = [{'name': 'submit_finding', 'input_schema': schema}]
        def complete(**wire):
            selected = wire['tools'][0]['input_schema']['properties']['selected_target']['enum'][0]
            self.assertNotEqual(selected, target)
            return {'content': [{'type': 'tool_use', 'name': 'submit_finding',
                'input': {'selected_target': selected, 'query': "SELECT 'addr1'", 'cause': 'literal addr1'}}]}
        value = Presentation({}, {}, 'instructions').complete(Mock(complete=complete),
            system='', messages=[], tools=tools)['content'][0]['input']
        Draft202012Validator(schema).validate(value)
        self.assertEqual(value['selected_target'], target)
        self.assertEqual(value['query'], "SELECT 'addr1'")
        self.assertEqual(value['cause'], 'literal addr1')
        self.assertEqual(tools[0]['input_schema'], schema)

    def test_null_and_unknown_alias_do_not_acquire_a_target(self):
        presentation = Presentation({}, {}, '')
        presentation.project({'selected_target': 'a' * 64})
        self.assertIsNone(presentation.restore({'selected_target': None})['selected_target'])
        unknown = presentation.restore({'selected_target': 'addr999'})
        with self.assertRaises(ValidationError):
            Draft202012Validator({'properties': {'selected_target': {'enum': ['a' * 64]}}}).validate(unknown)


class FallbackTests(unittest.TestCase):
    def test_failed_then_successful_recreation_is_not_described_as_the_cause(self):
        failed = {'id': 'failed', 'layer': 'one', 'purpose': 'recreate',
                  'status': 'ERROR', 'text': 'bad DAX', 'error': 'Unknown or ambiguous DAX member'}
        passed = {'id': 'passed', 'layer': 'one', 'purpose': 'recreate', 'status': 'SUCCEEDED',
                  'text': 'EVALUATE ROW("Units", [Units])', 'row_count': 1,
                  'result': {'rows': [{'Units': 8765}]}}
        original = deepcopy([failed, passed])
        value = attach({'status': 'UNRESOLVED', 'business': '', 'stop': 'TOOL_OR_TIME_LIMIT'},
            queries=[failed, passed], context={'conclusion_contract': 'question-first-v1',
                                              'layers': {'one': {'label': 'Semantic'}}})
        self.assertEqual(value['status'], 'UNRESOLVED')
        self.assertEqual(value['conclusion']['verdict_class'], 'UNRESOLVED')
        self.assertNotIn('DAX member', value['conclusion']['direct_answer'])
        self.assertNotIn('because', value['conclusion']['direct_answer'])
        observations = value['investigation_report']['findings_per_layer'][0]['observations']
        self.assertEqual([x['status'] for x in observations], ['READ_FAILED', 'OBSERVED'])
        self.assertEqual(observations[1]['rows_sample'], [{'Units': 8765}])
        self.assertEqual([failed, passed], original)
        self.assertIn('Unknown or ambiguous DAX member', value['business'])

    def test_unavailable_source_keeps_the_actual_limitation_and_no_finding(self):
        query = {'id': 'failed', 'layer': 'source', 'purpose': 'compare', 'status': 'ERROR',
                 'text': 'SELECT units FROM dbo.Items', 'error': 'Permission denied'}
        result = attach({'status': 'BLOCKED', 'business': '', 'stop': 'READ_UNAVAILABLE'},
            queries=[query], context={'conclusion_contract': 'question-first-v1'})
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertIn('Permission denied', result['business'])
        self.assertEqual(result['conclusion']['verdict_class'], 'UNRESOLVED')


class RetainedDefinitionTests(unittest.TestCase):
    def context(self):
        return {'retained_native_definitions': [{
            'id': 'native-measure', 'kind': 'Measure', 'name': 'Quantity',
            'content_hash': 'a' * 64,
            'metadata': {'expression': "SUM('Items'[units])"},
            'provenance': {'source': 'RETAINED_ASSET_CATALOG', 'qualification': 'Retained snapshot'}}]}

    def test_reference_is_citable_without_copying_content_or_claiming_freshness(self):
        from investigator.retained_definition_evidence import references, resolve
        from investigator.grounded_answers import cited
        from investigator.delivery_evaluator import payload
        context = self.context()
        before = deepcopy(context)
        reference = references(context)[0]
        self.assertNotIn('content', reference)
        case = {'context': context, 'queries': [], 'evidence': {'definition': reference}}
        support = cited({'evidence_ids': ['definition']}, case)
        self.assertEqual(support[0]['content'], "SUM('Items'[units])")
        self.assertFalse(support[0]['current_native_fetch_performed'])
        packet = payload({}, {'evidence_ids': ['definition']}, case)
        self.assertEqual(packet['cited_evidence']['definition'], resolve(reference, context))
        self.assertEqual(context, before)
        self.assertEqual(case['evidence']['definition'], reference)

    def test_unknown_hash_or_missing_provenance_never_becomes_native_support(self):
        from investigator.retained_definition_evidence import references, resolve
        context = self.context()
        reference = references(context)[0]
        with self.assertRaisesRegex(ValueError, 'PINNED_CONTEXT'):
            resolve({**reference, 'content_hash': 'b' * 64}, context)
        context['retained_native_definitions'][0]['provenance'] = None
        self.assertEqual(references(context), [])
        with self.assertRaisesRegex(ValueError, 'PINNED_CONTEXT'):
            resolve(reference, context)

    def test_projected_definition_keeps_original_hash_and_projection_label(self):
        from investigator.retained_definition_evidence import references, resolve
        context = self.context()
        item = context['retained_native_definitions'][0]
        item['projection'] = {'kind': 'PATH_TABLES_WITH_RELATED_SCHEMA', 'original_content_hash': 'a' * 64}
        value = resolve(references(context)[0], context)
        self.assertEqual(value['content_hash'], 'a' * 64)
        self.assertEqual(value['projection'], item['projection'])
        self.assertFalse(value['current_native_fetch_performed'])

    def test_loop_registers_existing_context_and_get_evidence_hydrates_without_reads(self):
        from investigator.ai_investigation import Investigator
        from investigator.investigative_queries import Queries
        from test_round23_intake_queries import sql_objects
        from test_round23_reasoning import MemoryCheckpoint, tool
        from investigator.retained_definition_evidence import KIND
        execute = Mock()
        queries = Queries({'source': {'dialect': 'T-SQL', 'objects': sql_objects()}},
                          execute=execute, reserve=Mock(), save=Mock())
        context = {**self.context(), 'intake': {'report': 'report'}, 'path': {'nodes': [], 'edges': []}}
        model = Mock()
        def answer(**_):
            identity = next(k for k, value in loop.state['evidence'].items() if value.get('kind') == KIND)
            return tool('submit_finding', {'verdict': 'definition explained', 'cause': 'Retained definition.',
                'numbers': [], 'checked': [], 'evidence_ids': [identity]})
        model.complete.side_effect = answer
        loop = Investigator(queries=queries, model=model, read_tools={},
            validate_finding=Mock(return_value={'business': 'Retained definition, not a live value.'}),
            checkpoint=MemoryCheckpoint(), case_id='definition-test', context=context, triage=[])
        result = loop.run()
        self.assertEqual(result['status'], 'ANSWERED')
        self.assertEqual(result['model_calls'], 1)
        self.assertEqual(result['tools_used'], 1)
        execute.assert_not_called()
        identity = next(k for k, value in loop.state['evidence'].items() if value.get('kind') == KIND)
        self.assertEqual(loop.dispatch('get_evidence', {'id': identity})['content'], "SUM('Items'[units])")
        self.assertEqual(loop.dispatch('get_evidence', {'id': identity})['evidence_id'], identity)
        self.assertIn('retained_definition_references', str(model.complete.call_args.kwargs['messages']))


if __name__ == '__main__':
    unittest.main()

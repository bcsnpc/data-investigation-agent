from copy import deepcopy
import unittest
from investigator.delivery_references import reformat
from investigator.grounded_answers import cited


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.query = {'id': 'query-one', 'layer': 'source', 'status': 'SUCCEEDED',
                      'time': '2026-11-21T00:00:00Z', 'result': {'rows': [{'units': 25}]}}
        self.evidence = {'fetch': {'tool': 'get_evidence', 'arguments': {'id': 'query-one'},
                                   'result': deepcopy(self.query)}}

    def run_reformat(self, args, evidence=None):
        return reformat(args, queries=[self.query], evidence=self.evidence if evidence is None else evidence,
                        layers={'source': {}})

    def test_exact_query_roles_are_reformatted_without_mutating_input(self):
        value = {'checked': ['query-one', 'source', 'fetch'], 'evidence_ids': ['fetch'],
                 'selected_target': 'explicit', 'numbers': [25]}
        before = deepcopy(value)
        result, changes = self.run_reformat(value)
        self.assertEqual(result['checked'], ['source'])
        self.assertEqual(result['evidence_ids'], ['query-one'])
        self.assertEqual(result['selected_target'], 'explicit')
        self.assertEqual(result['numbers'], [25])
        self.assertEqual(value, before)
        self.assertEqual(len(changes), 3)

    def test_unknown_and_graph_references_are_not_guessed(self):
        result, changes = self.run_reformat({'checked': ['graph-node', 'unknown'], 'evidence_ids': ['unknown']})
        self.assertEqual(result['checked'], ['graph-node', 'unknown'])
        self.assertEqual(result['evidence_ids'], ['unknown'])
        self.assertEqual(changes, [])

    def test_native_tool_wrapper_can_name_its_exact_query_layer(self):
        evidence = {'sql': {'tool': 'run_sql', 'result': {'record': self.query}}}
        result, _ = self.run_reformat({'checked': ['sql']}, evidence)
        self.assertEqual(result['checked'], ['source'])

    def test_nested_fetch_resolves_original_native_support(self):
        evidence = {**self.evidence, 'second': {'tool': 'get_evidence', 'arguments': {'id': 'fetch'}}}
        result, _ = self.run_reformat({'evidence_ids': ['second'], 'verdict': 'as designed'}, evidence)
        self.assertEqual(result['evidence_ids'], ['query-one'])
        self.assertEqual(cited(result, {'queries': [self.query], 'evidence': evidence})[0]['native_result'], self.query['result'])

    def test_fetch_does_not_turn_model_output_into_native_support(self):
        evidence = {'model': {'kind': 'MODEL_RESPONSE'},
                    'fetch': {'tool': 'get_evidence', 'arguments': {'id': 'model'}}}
        result, _ = self.run_reformat({'evidence_ids': ['fetch'], 'verdict': 'as designed'}, evidence)
        with self.assertRaisesRegex(ValueError, 'MODEL_OUTPUT_IS_NOT_NATIVE_SUPPORT'):
            cited(result, {'queries': [], 'evidence': evidence})

    def test_fetched_native_definition_retains_its_original_identity(self):
        definition = {'content': 'SUM(Activity[units])', 'provenance': {'source': 'COLLECTED_DEFINITION'}}
        evidence = {'definition': {'tool': 'get_definition', 'result': definition},
                    'fetch': {'tool': 'get_evidence', 'arguments': {'id': 'definition'}}}
        result, _ = self.run_reformat({'evidence_ids': ['fetch'], 'verdict': 'as designed'}, evidence)
        self.assertEqual(result['evidence_ids'], ['definition'])
        self.assertEqual(cited(result, {'queries': [], 'evidence': evidence}), [definition])

    def test_failed_query_still_cannot_support_a_successful_finding(self):
        self.query['status'] = 'ERROR'
        result, _ = self.run_reformat({'evidence_ids': ['fetch'], 'verdict': 'as designed'})
        with self.assertRaisesRegex(ValueError, 'FAILED_QUERY_DOES_NOT_SUPPORT'):
            cited(result, {'queries': [self.query], 'evidence': self.evidence})

    def test_cyclic_fetch_is_left_for_ordinary_validation(self):
        evidence = {'a': {'tool': 'get_evidence', 'arguments': {'id': 'b'}},
                    'b': {'tool': 'get_evidence', 'arguments': {'id': 'a'}}}
        result, changes = self.run_reformat({'evidence_ids': ['a']}, evidence)
        self.assertEqual(result['evidence_ids'], ['a'])
        self.assertEqual(changes, [])

    def test_dispatch_reformats_before_validation_and_records_the_change(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from jsonschema import Draft202012Validator
        from investigator.ai_investigation import Investigator, toolbox
        from investigator.regression_features import configured
        loop = object.__new__(Investigator)
        loop.context = {}
        loop.queries = SimpleNamespace(records=[self.query], layers={'source': {'dialect': 'TSQL'}})
        loop.state = {'evidence': deepcopy(self.evidence)}
        loop.refresh_tools = lambda: None
        loop.tools = toolbox(loop.queries.layers, {})
        loop.schemas = {t['name']: Draft202012Validator(t['input_schema']) for t in loop.tools}
        loop.case_view = Mock(return_value={})
        loop.validate_finding = Mock(return_value={'business': 'The scoped read returned 25.'})
        loop.repair_delivery = Mock(side_effect=ValueError('MODEL_REFORMAT_REQUIRED'))
        args = {'verdict': 'observed value', 'cause': 'Scoped native read.', 'numbers': [25],
                'checked': ['query-one'], 'evidence_ids': ['fetch']}
        with configured({'r27_delivery_reference_reformat': True}):
            result = loop.dispatch('submit_finding', args)
        self.assertEqual(result['business'], 'The scoped read returned 25.')
        delivered = loop.validate_finding.call_args.args[0]
        self.assertEqual(delivered['checked'], ['source'])
        self.assertEqual(delivered['evidence_ids'], ['query-one'])
        self.assertTrue(any(x.get('kind') == 'DELIVERY_REFERENCE_REFORMAT' for x in loop.state['evidence'].values()))
        loop.repair_delivery.assert_not_called()
        with configured({'r27_delivery_reference_reformat': False}):
            with self.assertRaisesRegex(ValueError, 'MODEL_REFORMAT_REQUIRED'):
                loop.dispatch('submit_finding', args)


if __name__ == '__main__':
    unittest.main()

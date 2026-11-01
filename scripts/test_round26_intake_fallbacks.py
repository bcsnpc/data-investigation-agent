from copy import deepcopy
import unittest
from investigator.guided_intake import Catalog, admit
from test_round23_intake_queries import graph, request


class ComparisonFallbackTests(unittest.TestCase):
    def test_missing_details_preserve_target_and_reach_recreation(self):
        for kind in ('SOURCE_SYSTEM', 'ANOTHER_REPORT', 'EXPECTED_NUMBER'):
            value = request()
            value['compared_with'] = {'kind': kind}
            original = deepcopy(value)
            result = admit(value, Catalog(graph()))
            self.assertEqual(value, original)
            self.assertEqual(result['status'], 'READY')
            self.assertEqual(result['visual'], 'card')
            self.assertEqual(result['compared_with'], {'kind': 'NOTHING'})
            self.assertEqual(result['comparison_context'], {'kind': kind})
            self.assertTrue(result['format_warnings'])

    def test_fallback_uses_only_explicit_single_source_declaration(self):
        value = request()
        value['compared_with'] = {'kind': 'EXPECTED_NUMBER'}
        g = graph()
        source = next(n for n in g['nodes'] if n['id'] == 'source')
        source['properties'] = {'system_of_record': True}
        result = admit(value, Catalog(g))
        self.assertEqual(result['compared_with'], {'kind': 'SOURCE_SYSTEM', 'source': 'source'})
        g['nodes'].append({'id': 'second', 'kind': 'SOURCE', 'label': 'Second',
                           'properties': {'system_of_record': True}})
        self.assertEqual(admit(value, Catalog(g))['compared_with'], {'kind': 'NOTHING'})

    def test_supporting_fields_do_not_crash_or_replace_selected_target(self):
        value = request()
        value['compared_with']['figure'] = {'state': 'NUMBER', 'value': '7', 'precision': 'EXACT'}
        result = admit(value, Catalog(graph()))
        self.assertEqual(result['compared_with'], {'kind': 'NOTHING'})
        self.assertEqual(result['comparison_context']['figure']['value'], '7')

    def test_competing_target_remains_explicit_ambiguity(self):
        value = request()
        value['compared_with'] = {'kind': 'SOURCE_SYSTEM', 'source': 'source', 'target': {'report': 'other'}}
        with self.assertRaisesRegex(ValueError, 'CONFLICTING_COMPARISON_TARGET'):
            admit(value, Catalog(graph()))
        del value['compared_with']['source']
        with self.assertRaisesRegex(ValueError, 'CONFLICTING_COMPARISON_TARGET'):
            admit(value, Catalog(graph()))

from copy import deepcopy
import unittest
from investigator.guided_intake import Catalog, admit, admit_or_question
from test_round23_intake_queries import graph, request


class ComparisonFallbackTests(unittest.TestCase):
    def test_public_boundary_fuzz_has_no_unhandled_shape_errors(self):
        catalog = Catalog(graph())
        forms = [None, [], '', 1, True, {}, request()]
        for field in request():
            missing = request(); del missing[field]; forms.append(missing)
            for malformed in (None, '', [], {}, 0, True):
                value = request(); value[field] = malformed; forms.append(value)
        for kind in ('NOTHING', 'SOURCE_SYSTEM', 'ANOTHER_REPORT', 'EXPECTED_NUMBER'):
            for field in ('target', 'source', 'figure'):
                for value in (None, {}, [], '', 'unknown', {'report': 'other'}):
                    form = request(); form['compared_with'] = {'kind': kind, field: value}; forms.append(form)
        for value in forms:
            with self.subTest(form=value):
                result = admit_or_question(value, catalog)
                self.assertIn(result['status'], ('READY', 'NEEDS_INPUT'))

    def test_malformed_figure_does_not_reask_known_report_page_or_visual(self):
        value = request(); value['reported_figure'] = {'state': 'NUMBER', 'value': '2'}
        result = admit_or_question(value, Catalog(graph()))
        self.assertEqual([f['field'] for f in result['question']['fields']], ['intake_details'])
        self.assertEqual(result['prefilled']['visual'], 'card')

    def test_unknown_id_choices_are_catalog_names(self):
        value = request(); value['visual'] = 'invented'
        result = admit_or_question(value, Catalog(graph()))
        self.assertEqual(result['question']['fields'][0]['choices'], [{'id': 'card', 'name': 'Card'}])

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

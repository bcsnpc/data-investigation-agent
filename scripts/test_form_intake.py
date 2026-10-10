import unittest
from investigator.form_intake import resolve, VERSION


class AuthoritativeFormTests(unittest.TestCase):
    def setUp(self):
        self.models = [{'id': 'model', 'reports': [{'id': 'report'}], 'visuals': [
            {'target_id': 'global-card', 'report_id': 'report', 'page_id': 'page',
             'measure_ids': ['measure'], 'grouping_columns': []},
            {'target_id': 'matrix', 'report_id': 'report', 'page_id': 'page',
             'measure_ids': ['measure'], 'grouping_columns': ['warehouse']}]}]
        self.request = {'version': VERSION, 'request_key': 'form-one',
            'report_id': 'report', 'page_id': 'page', 'target_id': 'global-card',
            'cell_mode': 'UNGROUPED', 'value_seen': '16',
            'comparison': 'LOOKS_WRONG', 'description': ''}

    def result(self, **changes):
        return resolve({**self.request, **changes}, self.models, None)

    def test_explicit_card_never_replaced_by_same_measure_matrix(self):
        r = self.result()
        self.assertEqual(r['status'], 'BOUND')
        self.assertEqual(r['scope']['target_id'], 'global-card')
        self.assertEqual(r['questions'], [])
        self.assertFalse(r['execution_authorized'])

    def test_missing_target_is_question_when_page_has_multiple_scopes(self):
        r = self.result(target_id=None)
        self.assertEqual(r['status'], 'NEEDS_INPUT')
        self.assertIsNone(r['scope'])
        self.assertEqual(len(r['questions']), 1)

    def test_target_outside_page_refuses(self):
        with self.assertRaisesRegex(ValueError, 'outside'):
            self.result(target_id='elsewhere')

    def test_matrix_ungrouped_cannot_replace_card(self):
        with self.assertRaisesRegex(ValueError, 'contradicts'):
            self.result(target_id='matrix')

    def test_missing_keys_use_existing_number_clarification_field(self):
        r = self.result(target_id='matrix', cell_mode='KEYED')
        self.assertEqual(r['status'], 'NEEDS_INPUT')
        self.assertEqual(r['questions'][0]['field'], 'NUMBER')
        self.assertIsNone(r['scope'])

    def test_figure_precision_is_supplied_not_tolerance(self):
        self.assertEqual(self.result(value_seen='about 3.4M')['scope']['reported_figure']['precision'],
                         {'state': 'STATED_PLACE', 'place': 5})
        with self.assertRaises(ValueError): self.result(value_seen='about 16')

    def test_missing_figure_remains_unspecified(self):
        self.assertEqual(self.result(value_seen=None)['scope']['reported_figure'], {'state': 'UNSPECIFIED'})

    def test_empty_is_not_zero(self):
        self.assertEqual(self.result(value_seen='empty')['scope']['reported_figure']['state'], 'EMPTY')
        self.assertEqual(self.result(value_seen='0')['scope']['reported_figure']['state'], 'NUMBER')

    def test_empty_and_number_do_not_silently_choose_empty(self):
        with self.assertRaisesRegex(ValueError, 'cannot share'):
            self.result(value_seen='empty or 16')

    def test_description_cannot_silently_override_form(self):
        r = self.result(description='Investigate the matrix instead, it shows 99.')
        self.assertTrue(r['description_requires_interpretation'])
        self.assertEqual(r['scope']['target_id'], 'global-card')
        self.assertEqual(r['scope']['reported_figure']['value'], '16')

    def test_other_report_explicitly_holds(self):
        self.assertEqual(self.result(comparison='OTHER_REPORT')['reason'], 'OTHER_REPORT_COMING_SOON')

    def test_model_cannot_add_hidden_scope_to_form(self):
        with self.assertRaises(Exception): self.result(filters=[{'column_id': 'warehouse'}])


if __name__ == '__main__': unittest.main()

import unittest
from investigator.guided_intake import Catalog, prefill
from test_round23_intake_queries import graph


class CatalogResolutionTests(unittest.TestCase):
    def catalog(self):
        g = graph()
        for node in g['nodes']:
            if node['id'] == 'measure':
                node['label'] = 'Net Revenue'
                node['enrichment'] = {'synonyms': ['receipts'], 'business_meaning': 'money collected'}
            if node['id'] == 'report':node['label'] = 'Billing Overview'
        return Catalog(g)

    def test_exact_normalized_synonym_and_typo_are_ranked_from_evidence(self):
        catalog = self.catalog()
        for text in ('Net Revenue is wrong', 'net-revenue is wrong', 'receipts is wrong', 'Net Reveneu is wrong'):
            matches = catalog.ranked(text, 'MEASURE')
            self.assertEqual(matches[0]['id'], 'measure')
            self.assertGreaterEqual(matches[0]['score'], .86)

    def test_measure_infers_only_unique_report_without_selecting_visual(self):
        result = prefill('Net Revenue looks old', {'issue_type': 'DATA_LOOKS_OLD'}, self.catalog())
        self.assertEqual(result['status'], 'READY')
        self.assertEqual(result['report'], 'report')
        self.assertNotIn('visual', result)
        self.assertEqual(result['resolution_assumptions'][0]['name'], 'Billing Overview')

    def test_same_measure_in_two_reports_asks_once_without_guessing(self):
        catalog = self.catalog()
        catalog.edges.append({'source': 'othercard', 'target': 'measure', 'kind': 'COMPUTED_FROM'})
        result = prefill('Net Revenue looks old', {'issue_type': 'DATA_LOOKS_OLD'}, catalog)
        self.assertEqual(result['status'], 'NEEDS_INPUT')
        self.assertEqual({c['id'] for c in result['question']['fields'][0]['choices']}, {'report', 'other'})

    def test_related_words_alone_do_not_silently_choose_report(self):
        result = prefill('money is odd', {'issue_type': 'NUMBER_LOOKS_WRONG'}, self.catalog())
        self.assertEqual(result['status'], 'NEEDS_INPUT')

    def test_missing_parent_does_not_create_named_report_binding(self):
        catalog = self.catalog(); catalog.edges = []
        self.assertEqual(catalog.report_matches('Net Revenue is wrong'), [])

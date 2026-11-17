from copy import deepcopy
import unittest
from investigator.guided_intake import Catalog
from investigator.intake_candidates import enumerate_targets, select_unique
from test_round23_intake_queries import graph, request


class CandidatesTests(unittest.TestCase):
    def setUp(self):
        self.raw = graph()
        self.raw['nodes'].append({'id': 'sibling', 'kind': 'VISUAL', 'label': 'Another card',
                                  'properties': {'filters': [{'warehouse': 2}]}})
        self.raw['edges'].extend([{'source': 'page', 'target': 'sibling', 'kind': 'CONTAINS'},
                                  {'source': 'sibling', 'target': 'measure', 'kind': 'COMPUTED_FROM'}])
        self.catalog = Catalog(self.raw)

    def test_explicit_visual_wins_and_other_report_is_excluded(self):
        inv = enumerate_targets(self.catalog, text='Other card', proposal=request(),
                                explicit={'report': 'report', 'page': 'page', 'visual': 'card'})
        self.assertEqual([c['id'] for c in inv['candidates']], ['card'])

    def test_real_scope_retained_for_each_candidate(self):
        before = deepcopy(self.raw)
        inv = enumerate_targets(self.catalog, text='quantity', proposal=request(), explicit={'report': 'report'})
        self.assertEqual({c['id'] for c in inv['candidates']}, {'card', 'sibling'})
        sibling = next(c for c in inv['candidates'] if c['id'] == 'sibling')
        self.assertEqual(sibling['retained_scope']['properties']['filters'], [{'warehouse': 2}])
        self.assertEqual(self.raw, before)

    def test_wrong_parent_cannot_be_replaced_by_matching_number(self):
        with self.assertRaisesRegex(ValueError, 'VISUAL_OUTSIDE'):
            enumerate_targets(self.catalog, text='Othercard', proposal=request(),
                              explicit={'report': 'report', 'visual': 'othercard'})

    def test_unique_requires_all_candidates_successful(self):
        inv = enumerate_targets(self.catalog, text='quantity', proposal=request(), explicit={'report': 'report'})
        figure = {'state': 'NUMBER', 'value': '950', 'precision': 'EXACT'}
        observed = [{'candidate': 'card', 'status': 'SUCCEEDED', 'value': 950, 'evidence_id': 'q1'}]
        self.assertIsNone(select_unique(inv, observed, figure)['selected'])
        observed.append({'candidate': 'sibling', 'status': 'SUCCEEDED', 'value': 949, 'evidence_id': 'q2'})
        self.assertEqual(select_unique(inv, observed, figure)['selected'], 'card')
        observed[1]['value'] = 950
        self.assertEqual(select_unique(inv, observed, figure)['reason'], 'MULTIPLE_MATCHES')

    def test_truncated_inventory_and_rounded_precision(self):
        inv = enumerate_targets(self.catalog, text='quantity', proposal=request(), explicit={'report': 'report'}, limit=1)
        self.assertFalse(inv['exhaustive'])
        candidate = inv['candidates'][0]['id']
        result = select_unique(inv, [{'candidate': candidate, 'status': 'SUCCEEDED', 'value': 950.1,
                                     'evidence_id': 'q1'}], {'state': 'NUMBER', 'value': '950', 'precision': {'place': 0}})
        self.assertEqual(result['matches'], [candidate])
        self.assertIsNone(result['selected'])


if __name__ == '__main__':
    unittest.main()

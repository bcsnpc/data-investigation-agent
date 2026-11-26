"""Fallback target selection must not promote an alias into native proof."""
import unittest
from investigator.intake_candidates import enumerate_targets, explicit_names, select_unique
from investigator.regression_features import configured
import test_round26_catalog_resolution as fixtures


class NativeCandidateTests(unittest.TestCase):
    def catalog(self):
        catalog = fixtures.CatalogResolutionTests().shared_visual_aliases()
        catalog.nodes['global']['enrichment'] = {}
        return catalog

    def inventory(self, catalog, text, **kwargs):
        return enumerate_targets(catalog, text=text, proposal={'issue_type': 'SOMETHING_ELSE'},
                                 explicit=explicit_names(catalog, text), **kwargs)

    def test_unique_alias_does_not_exclude_other_scope(self):
        catalog = self.catalog()
        result = self.inventory(catalog, 'Billing Overview Total revenue card')
        self.assertEqual({c['id'] for c in result['candidates']}, {'card', 'global'})
        self.assertTrue(result['exhaustive'])
        self.assertNotIn('visual', result['candidates'][0]['explicit'])
        self.assertIsNone(select_unique(result, [], None)['selected'])

    def test_native_title_wins_even_when_an_alias_disagrees(self):
        catalog = self.catalog()
        catalog.nodes['global']['label'] = 'Total revenue card'
        result = self.inventory(catalog, 'Billing Overview Total revenue card')
        self.assertEqual([c['id'] for c in result['candidates']], ['global'])
        self.assertEqual(select_unique(result, [], None)['selected'], 'global')

    def test_explicit_page_scope_is_preserved(self):
        result = self.inventory(self.catalog(), 'Billing Overview Global page Total revenue card')
        self.assertEqual([c['id'] for c in result['candidates']], ['global'])
        self.assertEqual(result['candidates'][0]['intake']['page'], 'globalpage')

    def test_truncation_still_prevents_unique_selection(self):
        result = self.inventory(self.catalog(), 'Billing Overview Total revenue card', limit=1)
        self.assertFalse(result['exhaustive'])
        self.assertIsNone(select_unique(result, [], None)['selected'])



if __name__ == '__main__':
    unittest.main()

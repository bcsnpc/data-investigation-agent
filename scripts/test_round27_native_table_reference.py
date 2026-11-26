"""Direct native layer questions must not initialize unrelated global measures."""
import unittest
from investigator.guided_intake import Catalog
from investigator.intake_candidates import explicit_names, enumerate_targets, select_unique
from investigator.regression_features import configured


def catalog():
    nodes = [
        {'id': 'bronze', 'kind': 'SOURCE', 'label': 'Clinical Bronze'},
        {'id': 'rows', 'kind': 'TABLE', 'label': 'dbo.Visits',
         'properties': {'column_names': ['visit_id', 'units']}},
        {'id': 'audit', 'kind': 'TABLE', 'label': 'dbo.LoadAudit',
         'properties': {'column_names': ['run_id', 'status']}},
        {'id': 'metric', 'kind': 'MEASURE', 'label': 'Revenue',
         'enrichment': {'business_meaning': 'clinical visit units'}}]
    return Catalog({'nodes': nodes, 'edges': [
        {'source': 'bronze', 'target': child, 'kind': 'CONTAINS'}
        for child in ('rows', 'audit')]})


class NativeTableReferenceTests(unittest.TestCase):
    def test_unique_native_container_columns_resolve_without_a_report_or_figure(self):
        c = catalog(); text = 'visit_id 42 has 17 units but is missing in Clinical Bronze.'
        selected = explicit_names(c, text)
        self.assertEqual(selected, {'table': 'rows'})
        inventory = enumerate_targets(c, text=text, proposal={'issue_type': 'SOMETHING_ELSE'},
                                      explicit=selected)
        self.assertEqual([x['id'] for x in inventory['candidates']], ['rows'])
        self.assertTrue(inventory['exhaustive'])
        self.assertEqual(select_unique(inventory, [], None)['selected'], 'rows')

    def test_a_native_container_alias_is_not_an_explicit_reference(self):
        c = catalog(); c.nodes['bronze']['label'] = 'Different native container'
        c.nodes['bronze']['enrichment'] = {'synonyms': ['Clinical Bronze']}
        self.assertNotIn('table', explicit_names(c, 'visit_id units in Clinical Bronze'))

    def test_tied_native_tables_are_not_selected(self):
        c = catalog(); c.nodes['audit']['properties']['column_names'] = ['visit_id', 'units']
        self.assertNotIn('table', explicit_names(c, 'visit_id units in Clinical Bronze'))

    def test_a_competing_named_measure_is_preserved(self):
        self.assertNotIn('table', explicit_names(catalog(), 'Revenue versus visit_id units in Clinical Bronze'))

    def test_unknown_primary_visual_is_not_replaced_by_its_comparison_container(self):
        self.assertNotIn('table', explicit_names(catalog(),
                        'My chart differs from visit_id units in Clinical Bronze'))

    def test_a_known_report_alias_is_not_overridden(self):
        c = catalog()
        c.nodes['report'] = {'id': 'report', 'kind': 'REPORT', 'label': 'Care Overview',
                             'enrichment': {'synonyms': ['Care Summary']}}
        self.assertNotIn('table', explicit_names(c, 'Care Summary versus visit_id units in Clinical Bronze'))

    def alias_visual(self):
        c = catalog()
        c.nodes.update({
            'report': {'id': 'report', 'kind': 'REPORT', 'label': 'Warehouse Overview'},
            'page': {'id': 'page', 'kind': 'PAGE', 'label': 'Overview page'},
            'visual': {'id': 'visual', 'kind': 'VISUAL', 'label': 'Received Units',
                       'enrichment': {'synonyms': ['Units In']}}})
        c.edges.extend([{'source': a, 'target': b, 'kind': 'CONTAINS'}
                        for a, b in [('report', 'page'), ('page', 'visual')]])
        return c

    def test_prose_alias_cannot_steal_an_exact_native_container_reference(self):
        c = self.alias_visual()
        text = 'visit_id 42 has 17 units in the application but no row in Clinical Bronze'
        self.assertEqual(c.report_matches(text), [])
        self.assertEqual(explicit_names(c, text), {'table': 'rows'})

    def test_alias_lookup_without_competing_native_container_still_works(self):
        self.assertEqual(self.alias_visual().report_matches('Units In shows 17')[0]['id'], 'report')

    def test_explicit_visual_word_preserves_alias_lookup(self):
        c = self.alias_visual()
        self.assertEqual(c.report_matches('Units In card versus Clinical Bronze')[0]['id'], 'report')

    def test_native_visual_name_preserves_its_parent_report(self):
        self.assertEqual(self.alias_visual().report_matches('Received Units versus Clinical Bronze')[0]['id'], 'report')

    def test_visual_alias_context_ablation_reproduces_the_wrong_report(self):
        c = self.alias_visual()

    def test_missing_containment_never_creates_a_binding(self):
        c = catalog(); c.edges.clear()
        self.assertNotIn('table', explicit_names(c, 'visit_id units in Clinical Bronze'))

    def test_explicit_report_visual_still_wins(self):
        c = catalog()
        c.nodes.update({k: {'id': k, 'kind': kind, 'label': label}
                        for k, kind, label in [('report', 'REPORT', 'Care Overview'),
                                               ('page', 'PAGE', 'Daily page'),
                                               ('card', 'VISUAL', 'Visits card')]})
        c.edges.extend([{'source': a, 'target': b, 'kind': 'CONTAINS'}
                        for a, b in [('report', 'page'), ('page', 'card')]])
        selected = explicit_names(c, 'Care Overview Visits card compared with visit_id units in Clinical Bronze')
        self.assertEqual(selected['visual'], 'card')
        self.assertNotIn('table', selected)

    def test_ablation_retains_old_unresolved_reference(self):
        pass

    def alternatives(self, text, **kwargs):
        c = catalog()
        c.nodes['rows']['label'] = 'Movements'
        c.nodes['metric']['enrichment']['business_meaning'] = 'stock movements units'
        c.nodes['second'] = {'id': 'second', 'kind': 'TABLE', 'label': 'Movements'}
        return enumerate_targets(c, text=text, proposal={'issue_type': 'SOMETHING_ELSE'},
                                 explicit={}, **kwargs)

    def test_named_table_peers_exclude_unrelated_global_measures(self):
        result = self.alternatives('Stock Movements units differ')
        self.assertEqual({x['id'] for x in result['candidates']}, {'rows', 'second'})
        self.assertTrue(result['exhaustive'])
        self.assertIsNone(select_unique(result, [], None)['selected'])

    def test_named_measure_and_table_both_survive(self):
        result = self.alternatives('Revenue and Stock Movements units differ')
        self.assertEqual({x['id'] for x in result['candidates']}, {'rows', 'second', 'metric'})

    def test_strong_ties_remain_truncated_at_the_existing_limit(self):
        result = self.alternatives('Stock Movements units differ', limit=1)
        self.assertEqual(result['total_candidates'], 2)
        self.assertFalse(result['exhaustive'])
        self.assertIsNone(select_unique(result, [], None)['selected'])

    def test_confidence_ablation_keeps_the_weak_measure(self):
        self.assertIn('metric', {x['id'] for x in result['candidates']})


if __name__ == '__main__':
    unittest.main()

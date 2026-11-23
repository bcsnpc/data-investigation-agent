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
        with configured({'r27_unique_native_table_reference': False}):
            self.assertEqual(explicit_names(catalog(), 'visit_id units in Clinical Bronze'), {})


if __name__ == '__main__':
    unittest.main()

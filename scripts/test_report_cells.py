"""General cells, separately conserved declarations, and bounded candidate evaluation."""
import copy
import json
import unittest
from unittest.mock import patch
from investigator.adapters import report_cells, report_predicates
from investigator import declared_reproduction, declaration_inventory, report_cell
import test_declared_predicate_adapter as fixture
from test_declared_predicate_adapter import field


class CellTests(unittest.TestCase):
    def setUp(self):
        fixture.DeclaredPredicateAdapterTests.setUp(self)
        self.report['report']['name']='Sales overview'
        self.scope['report_binding']={'resolution_kind':'STATED','report_id':self.report['report']['id'],
            'source':{'start':0,'end':14,'quote':'Sales overview'}}
    part = fixture.DeclaredPredicateAdapterTests.part
    modify = fixture.DeclaredPredicateAdapterTests.modify

    def address(self, scope=None):
        return report_cells.addresses(self.model, json.loads(self.visual['metadata']['content']),
            self.visual['id'], self.measure['id'], self.scope if scope is None else scope)

    def grouped(self):
        self.modify(self.visual, lambda d: d['visual'].update(visualType='tableEx'))
        self.modify(self.visual, lambda d: d['visual']['query']['queryState']['Values']['projections'].insert(0, {'field': field()}))

    def test_zero_grouping_is_the_general_rule_not_a_separate_card_guard(self):
        cell = self.address()[0]
        self.assertEqual(cell['mode'], 'UNGROUPED')
        self.assertEqual(cell['key_restrictions'], [])
        report_cell.validate(cell, self.measure['id'])
        result = declared_reproduction.run(self.adapter, self.layer, self.measure['id'], self.scope)
        self.assertEqual(result['finding']['label'], 'REPRODUCED')

    def test_one_stated_group_key_produces_a_scalar_cell(self):
        self.grouped(); cell = self.address()[0]
        self.assertEqual(cell['mode'], 'KEYED')
        self.assertEqual(cell['key_restrictions'], [{'field_id': self.column['id'], 'operator': 'IN', 'values': ['North']}])
        report_cell.validate(cell, self.measure['id'])

    def test_missing_second_key_names_the_column(self):
        self.grouped()
        another = {**self.column, 'id': 'resolved/customers/product', 'name': 'Product'}
        self.model['context']['model_assets'].append(another)
        self.modify(self.visual, lambda d: d['visual']['query']['queryState']['Values']['projections'].insert(0, {'field': field(column='Product')}))
        with self.assertRaisesRegex(report_predicates.Refusal, 'MISSING_CELL_KEYS: Product'):
            self.address()

    def test_totals_have_no_keys_and_compile_as_ungrouped_context(self):
        self.grouped(); keyed, total = self.address()
        self.assertEqual(total['mode'], 'TOTAL'); self.assertEqual(total['key_restrictions'], [])
        report_cell.validate(total, self.measure['id'])
        declaration = report_predicates.scoped_options(self.model, self.measure['id'],self.scope['report_binding'])[0]
        active = declared_reproduction.compose(declaration['restrictions'])
        self.assertEqual(report_predicates.quantity_query(self.model, self.measure['id'], active),
            report_predicates.quantity_query(self.model, self.measure['id'], declared_reproduction.compose(declaration['restrictions'] + total['key_restrictions'])))

    def test_nonprojected_measure_is_not_a_candidate(self):
        self.assertEqual(report_cells.addresses(self.model, json.loads(self.visual['metadata']['content']), self.visual['id'], 'other', self.scope), [])
        self.assertEqual(report_predicates.targets(self.model, 'other'), [])

    def test_visual_calculation_is_refused_by_name_not_substituted(self):
        self.modify(self.visual, lambda d: d['visual']['query']['queryState']['Values']['projections'].append(
            {'displayName': 'Running revenue', 'field': {'VisualCalculation': {'Expression': 'opaque'}}}))
        with self.assertRaisesRegex(report_predicates.Refusal, 'UNSUPPORTED_PROJECTED_FIELD: Running revenue'):
            self.address()

    def test_unfamiliar_visual_type_is_named_unsupported(self):
        self.modify(self.visual, lambda d: d['visual'].update(visualType='unfamiliarDataVisual'))
        with self.assertRaisesRegex(report_predicates.Refusal, 'UNSUPPORTED_VISUAL_TYPE: unfamiliarDataVisual'):
            self.address()

    def test_two_candidate_visuals_are_independently_evaluated_and_reported(self):
        document = json.loads(self.visual['metadata']['content']); document['name'] = 'other'
        self.part('definition/pages/p/visuals/other/visual.json', document)
        self.modify(self.page, lambda d: d['visualInteractions'].append({'source': 's', 'target': 'other', 'type': 'DataFilter'}))
        result = declared_reproduction.run(self.adapter, self.layer, self.measure['id'], self.scope)
        self.assertEqual(len(result['cells']), 2)
        self.assertEqual(len(self.requests), 2)
        self.assertTrue(all(r['finding']['label'] == 'REPRODUCED' for r in result['cells']))
        for r in result['cells']: self.assertIn(r['cell']['target_id'], result['technical_output'])

    def test_keys_do_not_enter_inventory_or_change_conservation(self):
        self.grouped()
        options = report_predicates.scoped_options(self.model, self.measure['id'],self.scope['report_binding'])
        batch = self.adapter.declared_cells(self.layer, self.measure['id'], self.scope)
        self.assertEqual(len(batch['cells']), 2)
        for declaration in batch['cells']:
            self.assertEqual(declaration['inventory'], options[0]['inventory'])
            entries = declared_reproduction._entries(declaration['evidence'],declaration['inventory'],declaration['restrictions'])
            self.assertEqual(len(entries), len(declaration['inventory']['discovered']))
            self.assertNotIn('key_restrictions', declaration['inventory'])
        result = declared_reproduction.run(self.adapter, self.layer, self.measure['id'], self.scope)
        self.assertEqual(result['cells'][0]['finding']['redundant_cell_keys'], [self.column['id']])

    def test_cap_names_unevaluated_cells_and_does_not_attempt_extra_reads(self):
        self.grouped()
        self.adapter.remaining_diagnostic_reads = lambda: 2 - len(self.requests)
        result = declared_reproduction.run(self.adapter, self.layer, self.measure['id'], self.scope)
        self.assertEqual(len(self.requests), 2)
        self.assertEqual(len(result['unevaluated_cells']), 0)
        self.assertTrue(self.adapter.duplicate_read_events)

    def test_no_reported_figure_still_obtains_values_without_a_verdict(self):
        self.scope['reported_figure'] = {'state': 'UNSPECIFIED'}
        result = declared_reproduction.run(self.adapter, self.layer, self.measure['id'], self.scope)
        self.assertEqual(result['reason'], declared_reproduction.NO_FIGURE)
        self.assertIsNone(result['finding']['label'])
        self.assertEqual(result['finding']['reproduced_value'], '3')
        self.assertEqual(len(self.requests), 2)

    def test_invented_key_is_refused_by_the_neutral_consumer(self):
        self.grouped(); cell = self.address()[0]
        with self.assertRaisesRegex(ValueError, 'not stated'):
            report_cell.validate(cell, self.measure['id'], {'filters': []})

    def test_empty_inventory_is_conserved_but_active_without_a_predicate_is_not(self):
        self.assertEqual(declaration_inventory.validate({'discovered': [], 'entries': []}, []), [])
        self.modify(self.page, lambda d: d.pop('filterConfig'))
        self.modify(self.visual, lambda d: d.pop('filterConfig'))
        self.parts.remove(self.slicer); self.parts.remove(self.bookmark)
        result = declared_reproduction.run(self.adapter, self.layer, self.measure['id'], self.scope)
        self.assertEqual(result['finding']['declarations'], [])
        self.assertEqual(len(self.requests), 1)


if __name__ == '__main__': unittest.main()

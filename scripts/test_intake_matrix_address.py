import copy
import unittest
from test_intake_extraction import fixture
from investigator import intake_extraction as extraction
from investigator.question_intake import validate
from investigator.visual_target import complete


class MatrixAddressTests(unittest.TestCase):
    def test_scoped_global_comparator_is_not_an_external_route_question(self):
        from investigator.ticket_route import settlement
        raw,payload=fixture('In Report, selected warehouse North Quantity differs from the global value. Explain the selected scope.',
            kind='VISUAL_CONTENT',comparisons=['global value'],
            selections=[{'quote':'selected warehouse North','column':'warehouse','value':'North','role':'PRIMARY'}])
        self.assertEqual(settlement(raw,payload['text'],None)['route'],'DECLARED_SUBJECT')

    def test_named_source_movements_establish_application_without_choice(self):
        from investigator.ticket_route import settlement
        raw,payload=fixture('In Report, Quantity is higher than source movements. Locate the difference.')
        self.assertEqual(settlement(raw,payload['text'],None)['route'],'APPLICATION')

    def test_equivalent_scope_requires_complete_inventory_not_same_measure(self):
        from investigator.visual_target import TargetUnresolved
        raw,payload=fixture('In Report, Quantity looks high.',visuals=[])
        with self.assertRaises(TargetUnresolved):extraction.resolve(raw,payload)
        for v in payload['models'][0]['visuals']:
            v['declared_scopes']={'measure':{'state':'COMPLETE','restrictions':[],
                'context_id':'pinned','context_hash':'hash','inventory_hash':'inventory'}}
        value=extraction.resolve(raw,payload);validate(value,payload)
        self.assertNotIn('target_visual',value)
        payload['models'][0]['visuals'][0]['declared_scopes']['measure']['restrictions']=[{'field_id':'warehouse','operator':'IN','values':['North']}]
        with self.assertRaises(TargetUnresolved):extraction.resolve(raw,payload)

    def fixture(self):
        ticket='In Report, Warehouse matrix Quantity North / Widget cell shows 149.'
        raw,payload=fixture(ticket,kind='VISUAL_CONTENT',
            visuals=[{'quote':'Warehouse matrix','role':'PRIMARY','form':'MATRIX'}],
            figures=[{'quote':'149','role':'PRIMARY','state':'NUMBER','precision_quote':None}],
            selections=[{'quote':'North / Widget cell','column':None,'value':'North / Widget','role':'PRIMARY'}])
        m=payload['models'][0]
        m['columns'].append({'column_id':'product','name':'product_name','data_type':'string'})
        matrix=m['visuals'][1];matrix['grouping_columns']=['product','warehouse']
        matrix['cell_key_order']=['warehouse','product']
        return raw,payload

    def test_two_keys_follow_declared_axes_not_sorted_identifiers(self):
        raw,payload=self.fixture();value=extraction.resolve(raw,payload);validate(value,payload)
        self.assertNotIn('selection_request',value)
        self.assertEqual(value['filters'],[{'column_id':'warehouse','operator':'in','values':['North']},
                                          {'column_id':'product','operator':'in','values':['Widget']}])
        complete(value['target_visual'],payload['models'][0]['visuals'],value['filters'])
        self.assertEqual(value['extracted_ticket']['response'],raw)

    def test_missing_axis_order_or_wrong_arity_stays_unresolved(self):
        raw,payload=self.fixture();payload['models'][0]['visuals'][1].pop('cell_key_order')
        value=extraction.resolve(raw,payload)
        with self.assertRaises(ValueError):complete(value['target_visual'],payload['models'][0]['visuals'],value['filters'])
        raw,payload=self.fixture();raw['selections'][0]['value']='North'
        self.assertIsNone(extraction.keyed_address(extraction.spans(raw,payload['text'])['selections'],
                            payload['models'][0]['visuals'][1],payload['models'][0],ticket=payload['text']))

    def test_ordinary_slash_selection_is_not_a_matrix_address(self):
        raw,payload=self.fixture();item=extraction.spans(raw,payload['text'])['selections'][0]
        item['quote']['quote']='selected North / Widget'
        self.assertIsNone(extraction.keyed_address([item],payload['models'][0]['visuals'][1],
                           payload['models'][0],ticket=payload['text']))


if __name__=='__main__':unittest.main()

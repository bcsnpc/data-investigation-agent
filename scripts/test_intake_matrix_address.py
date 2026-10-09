import copy
import unittest
from unittest.mock import patch
from test_intake_extraction import fixture
from investigator import intake_extraction as extraction
from investigator.question_intake import validate
from investigator.visual_target import complete


class MatrixAddressTests(unittest.TestCase):
    def test_confirmed_visual_resolves_unmatched_label_without_erasing_it(self):
        raw,payload=fixture('In Report, Global card shows 16.',
            measures=[{'quote':'Global card','role':'PRIMARY'}],
            figures=[{'quote':'16','role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        with self.assertRaisesRegex(ValueError,'Starting measure/model is unresolved'):extraction.resolve(raw,payload)
        start=payload['text'].index('16')
        with patch('investigator.intake_confirmation.values',return_value={'NUMBER':{
                'target_id':'card','mode':'UNGROUPED','figure_source':{'quote':'16','start':start,'end':start+2}}}):
            value=extraction.resolve(raw,{**payload,'_ticket_confirmation':{'test':'trusted validator result'}})
        self.assertEqual(value['measure_id'],'measure');self.assertIsNone(value['metric_quote'])
        self.assertEqual(value['extracted_ticket']['response'],raw)

    def test_scope_proof_does_not_reduce_model_directory_coverage_or_add_wire_cost(self):
        from investigator.question_intake import wire_contract
        from investigator.onboarding import encoded
        raw,payload=fixture('In Report, Quantity differs.')
        before=wire_contract(payload)[0]
        for v in payload['models'][0]['visuals']:
            v['declared_scopes']={'measure':{'state':'COMPLETE','context_hash':'x'*100000,'restrictions':[]}}
            v['cell_key_order']=v['grouping_columns']
        after=wire_contract(payload)[0]
        self.assertEqual(before,after)
        self.assertEqual(len(encoded(before)),len(encoded(after)))
        self.assertEqual(len(after['models'][0]['visuals']),2)
        self.assertEqual(extraction.wire(payload),extraction.wire({'text':payload['text'],'models':copy.deepcopy(payload['models'])}))

    def test_confirmed_single_measure_visual_selects_between_two_named_measures(self):
        raw,payload=fixture('In Report, Quantity and Value differ. Explain their definitions.',
            measures=[{'quote':'Quantity','role':'PRIMARY'},{'quote':'Value','role':'PRIMARY'}])
        payload['models'][0]['measures'].append({'id':'other','name':'Value'})
        with self.assertRaisesRegex(ValueError,'Starting measure/model is ambiguous'):extraction.resolve(raw,payload)
        with patch('investigator.intake_confirmation.values',return_value={'NUMBER':{
                'target_id':'card','mode':'UNGROUPED','figure_source':None}}):
            value=extraction.resolve(raw,{**payload,'_ticket_confirmation':{'test':'trusted validator result'}})
        self.assertEqual(value['measure_id'],'measure')
        self.assertEqual(value['extracted_ticket']['response']['measures'],raw['measures'])

    def test_named_single_axis_matrix_binds_its_stated_key(self):
        raw,payload=fixture('In Report, selected North Quantity differs on Warehouse matrix.',
            kind='VISUAL_CONTENT',visuals=[{'quote':'Warehouse matrix','role':'PRIMARY','form':'MATRIX'}],
            selections=[{'quote':'selected North','column':None,'value':'North','role':'PRIMARY'}])
        value=extraction.resolve(raw,payload);validate(value,payload)
        self.assertEqual(value['filters'],[{'column_id':'warehouse','operator':'in','values':['North']}])
        self.assertNotIn('selection_request',value)

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

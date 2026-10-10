"""No provider or estate calls: recover stated cells, never invented ones."""
import copy
import unittest
from investigator import intake_extraction, form_scope, form_intake, ticket_route
from investigator.visual_target import complete, TargetUnresolved
from test_intake_extraction import fixture


class PickedCellCoverageTests(unittest.TestCase):
    def payload(self, description, *, selections=()):
        raw,payload=fixture(description,selections=list(selections))
        model=payload['models'][0]
        model['columns'].append({'column_id':'product','name':'product_name','aliases':['product'],'data_type':'string'})
        visual=model['visuals'][1]
        visual.update(page_id='page',page_names=['Overview'],grouping_columns=['warehouse','product'],cell_key_order=['warehouse','product'])
        model['visuals'][0]['page_id']='page'
        request={'version':form_intake.VERSION,'request_key':'picked','report_id':'report','page_id':'page',
            'target_id':'matrix','cell_mode':None,'cell_keys':[],'value_seen':None,
            'comparison':None,'description':description}
        payload['_form_description_input']=request
        payload['text']=form_scope.document(request,None)['text']
        return raw,payload,visual

    def test_picked_matrix_explicit_cell_omitted_by_model_is_reconstructed(self):
        raw,payload,visual=self.payload('In Report, Quantity North / Component 1 cell shows 149.')
        value=intake_extraction.resolve(raw,payload)
        self.assertEqual(value['filters'],[
            {'column_id':'warehouse','operator':'in','values':['North']},
            {'column_id':'product','operator':'in','values':['Component 1']}])
        complete(value['target_visual'],[visual],value['filters'])
        self.assertEqual(value['extracted_ticket']['response'],raw)

    def test_axis_order_missing_does_not_guess_and_mentions_do_not_become_keys(self):
        for text in ('In Report, Quantity North / Component 1 shows 149.',
                     'In Report, Quantity North / Component 1 cell shows 149.'):
            raw,payload,visual=self.payload(text)
            visual.pop('cell_key_order')
            value=intake_extraction.resolve(raw,payload)
            with self.assertRaises(TargetUnresolved):complete(value['target_visual'],[visual],value['filters'])

    def test_explicit_address_conflicting_with_selection_refuses(self):
        raw,payload,_=self.payload('In Report, warehouse South; Quantity North / Component 1 cell shows 149.',
            selections=[{'quote':'warehouse South','column':'warehouse','value':'South','role':'PRIMARY'}])
        with self.assertRaisesRegex(ValueError,'conflicts'):intake_extraction.resolve(raw,payload)

    def test_comparator_cell_is_not_recovered_as_the_picked_cell(self):
        raw,payload,visual=self.payload('In Report, Quantity differs from Quantity North / Component 1 cell.')
        raw['comparisons']=['Quantity North / Component 1 cell']
        value=intake_extraction.resolve(raw,payload)
        with self.assertRaises(TargetUnresolved):complete(value['target_visual'],[visual],value['filters'])

    def test_selected_context_vs_global_routes_to_declared_subject(self):
        text='In Report, I selected warehouse North. Quantity differs from the global total. Explain what report context you can and cannot reproduce.'
        raw,_=fixture(text,comparisons=['the global total'],
            selections=[{'quote':'warehouse North','column':'warehouse','value':'North','role':'PRIMARY'}])
        route=ticket_route.from_request(raw,text,code_gate=True)
        self.assertEqual(route['route'],'DECLARED_SUBJECT')
        raw['comparisons']=['another report']
        raw['primary']=text.replace('the global total','another report')
        raw['comparisons']=['another report']
        self.assertIsNone(ticket_route.from_request(raw,raw['primary'],code_gate=True))

if __name__=='__main__':unittest.main()

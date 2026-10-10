import copy
import unittest
from investigator import form_scope, form_intake, intake_extraction
from investigator.question_intake import validate
import test_intake_extraction as fixtures


class FormDescriptionTests(unittest.TestCase):
    def payload(self,ticket,**updates):
        raw,payload=fixtures.fixture(ticket,**updates)
        for v in payload['models'][0]['visuals']:
            v.update(page_id='page',page_names=['Overview'])
            v['declared_scopes']={'measure':{'state':'COMPLETE','restrictions':[],
                'context_id':'context','context_hash':'a'*64,'inventory_hash':'b'*64}}
        request={'version':form_intake.VERSION,'request_key':'selected','report_id':'report',
            'page_id':'page','target_id':'matrix','cell_mode':'KEYED',
            'cell_keys':[{'column_id':'warehouse','value':'North'}],
            'comparison':'DECLARED_SUBJECT','value_seen':None,'description':ticket}
        doc=form_scope.document(request,None)
        payload['text']=doc['text'][:doc['parts'][0]['end']]
        payload['_form_description_input']=request
        return raw,payload,request

    def test_selected_visual_resolves_ambiguous_text_without_fake_confirmation(self):
        raw,p,r=self.payload('In Report Quantity differs; I selected North.',
            selections=[{'quote':'selected North','column':None,'value':'North','role':'PRIMARY'}])
        result=intake_extraction.resolve(raw,p);validate(result,p)
        self.assertEqual(result['target_visual']['target_id'],'matrix')
        self.assertEqual(result['report_binding']['resolution_kind'],'FORM_DESCRIPTION_SELECTION')
        self.assertNotIn('confirmation',result['extracted_ticket'])
        self.assertEqual(result['filters'],[{'column_id':'warehouse','operator':'in','values':['North']}])
        self.assertEqual(form_scope.build(r,p['models'],None,description_proposal=result)['proposal']['target_visual']['target_id'],'matrix')
        with self.assertRaises(ValueError):validate(result,{'text':p['text'],'models':p['models']})

    def test_explicit_other_visual_is_not_overridden_by_form(self):
        raw,p,r=self.payload('Report Global card Quantity differs.',
            visuals=[{'quote':'Global card','form':'TITLE','role':'PRIMARY'}])
        result=intake_extraction.resolve(raw,p);validate(result,p)
        self.assertEqual(result['target_visual']['target_id'],'card')
        with self.assertRaisesRegex(ValueError,'Description conflicts'):
            form_scope.build(r,p['models'],None,description_proposal=result)

    def test_missing_text_key_does_not_reask_a_picked_form_key(self):
        raw,p,r=self.payload('Report Quantity differs.')
        result=intake_extraction.resolve(raw,p)
        built=form_scope.build(r,p['models'],None,description_proposal=result)
        self.assertEqual(built['proposal']['filters'],[{'column_id':'warehouse','operator':'in','values':['North']}])

    def test_blank_value_field_does_not_contradict_verbatim_description_value(self):
        raw,p,r=self.payload('Report Quantity shows 16.',
            figures=[{'quote':'16','role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        b=form_scope.build(r,p['models'],None,description_proposal=intake_extraction.resolve(raw,p))
        self.assertEqual(b['proposal']['reported_figure']['value'],'16')
        self.assertEqual(b['proposal']['reported_figure']['source']['quote'],'16')

    def test_wrong_description_key_still_conflicts(self):
        raw,p,r=self.payload('Report Quantity differs; I selected warehouse South.',
            selections=[{'quote':'warehouse South','column':'warehouse','value':'South','role':'PRIMARY'}])
        with self.assertRaisesRegex(ValueError,'restrictions'):
            form_scope.build(r,p['models'],None,description_proposal=intake_extraction.resolve(raw,p))

    def test_identical_matrix_key_twice_is_not_a_conflict(self):
        raw,p,r=self.payload('Report Quantity differs; I selected warehouse North; North selection.',
            selections=[{'quote':'warehouse North','column':'warehouse','value':'North','role':'PRIMARY'},
                {'quote':'North selection','column':None,'value':'North','role':'PRIMARY'}])
        result=intake_extraction.resolve(raw,p)
        self.assertEqual(len(result['filters']),1)
        self.assertEqual(form_scope.build(r,p['models'],None,description_proposal=result)['proposal']['filters'],result['filters'])

    def test_changed_description_cannot_borrow_selected_input_authority(self):
        raw,p,r=self.payload('Report Quantity differs.')
        p['_form_description_input']['description']='Different text'
        with self.assertRaisesRegex(ValueError,'different text'):intake_extraction.resolve(raw,p)

    def test_one_transposition_resolves_only_inside_picked_visual_closed_measure_list(self):
        raw,p,r=self.payload('Report Qunatity differs.',measures=[{'quote':'Qunatity','role':'PRIMARY'}])
        model=p['models'][0];model['measures'].append({'id':'second','name':'Other'})
        model['visuals'][1]['measure_ids'].append('second')
        result=intake_extraction.resolve(raw,p);validate(result,p)
        self.assertEqual(result['measure_id'],'measure')
        self.assertTrue(any(e['resolution']=='FORM_PICKED_VISUAL_CLOSED_MEASURE_TRANSPOSITION' for e in result['extracted_ticket']['resolution_evidence']))
        model['measures'].append({'id':'third','name':'Quantity'})
        model['visuals'][1]['measure_ids'].append('third')
        with self.assertRaisesRegex(ValueError,'unique starting measure'):intake_extraction.resolve(raw,p)

    def test_empty_measurable_set_is_not_a_pass_or_a_crash(self):
        from investigator.conversational_oracle import score
        s=score([],[])
        self.assertEqual(s['gate'],'NOT_MEASURABLE');self.assertEqual(s['questions'],0)

    def test_candidate_receipt_is_addressed_to_resolved_cell(self):
        from unittest.mock import patch
        from investigator.adapters.form_candidate_values import plan
        from investigator.onboarding import digest
        cell={'target_id':'matrix','measure_id':'measure','grouping_columns':['warehouse'],
            'key_restrictions':[{'field_id':'warehouse','operator':'IN','values':['North']}],'mode':'KEYED'}
        cell['id']=digest(cell)
        candidate={'target_id':'matrix','measure_id':'measure','mode':'KEYED',
            'declaration':{'restrictions':[]},'scope':{'filters':[{'column_id':'warehouse','operator':'in','values':['North']}]}}
        model={'id':'model','revision':1,'context_id':'context'}
        with patch('investigator.adapters.report_predicates.quantity_query',return_value='EVALUATE ROW("quantity", 16)'), \
                patch('investigator.adapters.report_predicates._document',return_value={}), \
                patch('investigator.adapters.report_cells.addresses',return_value=[cell]) as cells:
            compiled=plan(model,candidate)
        self.assertEqual(compiled['read_address'],{'kind':'CELL','cell':cell})
        self.assertEqual(cells.call_args.args[-1]['target_visual']['target_id'],'matrix')


if __name__=='__main__':unittest.main()

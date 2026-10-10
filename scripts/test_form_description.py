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

    def test_generic_shape_noise_cannot_displace_picked_visual(self):
        raw,p,r=self.payload('Report Quantity differs; the chart total is confusing.',
            visuals=[{'quote':'chart','form':'CHART','role':'PRIMARY'},
                     {'quote':'total','form':'TOTAL','role':'PRIMARY'}])
        result=intake_extraction.resolve(raw,p);validate(result,p)
        self.assertEqual(result['target_visual']['target_id'],'matrix')
        self.assertEqual(result['target_visual']['mode'],'KEYED')

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

    def test_picked_comparison_is_not_conflicted_by_an_inferred_description_route(self):
        raw,p,r=self.payload('What is Report Quantity?')
        raw.update(kind='VISUAL_CONTENT',triage='BUSINESS_QUESTION:NONE')
        r['comparison']='APPLICATION'
        p['text']=form_scope.document(r,None)['text'].split('\n\nComparison')[0]
        b=form_scope.build(r,p['models'],None,description_proposal=intake_extraction.resolve(raw,p))
        self.assertEqual(b['proposal']['ticket_route']['route'],'APPLICATION')

    def test_form_identifiers_survive_the_scope_projection(self):
        raw,p,r=self.payload('Report Quantity differs; record Q49.',
            identifiers=[{'quote':'Q49','role':'PRIMARY'}])
        interpreted=intake_extraction.resolve(raw,p)
        b=form_scope.build(r,p['models'],None,description_proposal=interpreted)
        self.assertEqual(b['proposal']['expected_records'],interpreted['expected_records'])
        self.assertEqual(b['proposal']['expected_records'][0]['value'],'Q49')
        self.assertEqual(b['proposal']['numeral_mentions'],interpreted['numeral_mentions'])
        validate(b['proposal'],{'text':b['document']['text'],'models':p['models'],
            '_form_request':r,'_form_description':interpreted})

    def test_candidate_receipts_reach_description_resolution_without_fake_pick(self):
        from investigator.form_candidates import observe
        raw,p,r=self.payload('Report Quantity differs.')
        r.update(target_id=None,cell_mode='UNGROUPED',value_seen='16');r.pop('cell_keys')
        binding,matched=observe(r,p['models'],lambda c:{'status':'OBSERVED','complete':True,'value':'16',
            'receipt_id':'receipt','query_hash':'a'*64,'execution_surface':{'engine':'engine'},'attestation':{'consistency':'MATCHED'}})
        p['_form_description_candidate_binding']=binding
        result=intake_extraction.resolve(raw,p);validate(result,p)
        self.assertEqual(result['target_visual']['target_id'],'card')
        self.assertEqual(result['report_binding']['resolution_kind'],'FORM_DESCRIPTION_VALUE_MATCH')
        self.assertIsNone(r['target_id'])
        self.assertEqual(form_scope.build(r,p['models'],None,description_proposal=result,candidate_binding=binding)['proposal']['target_visual']['target_id'],'card')

    def test_invoked_bookmark_is_a_retryable_model_error_not_uncertain_precision(self):
        from investigator.intake_rules import RuleViolation
        raw,p,r=self.payload('Report Quantity differs; I invoked North saved bookmark.',
            identifiers=[{'quote':'North saved bookmark','role':'PRIMARY'}])
        with self.assertRaisesRegex(RuleViolation,'PAGE_STATE_IS_NOT_IDENTIFIER'):intake_extraction.resolve(raw,p)

    def test_bad_bookmark_identifier_retries_then_admits_without_question(self):
        import test_form_controller
        f=test_form_controller.FormControllerTests();f.setUp();self.addCleanup(f.doCleanups)
        ticket='Report Quantity shows 16; I invoked North saved bookmark.'
        raw,_=fixtures.fixture(ticket,kind='VISUAL_CONTENT',triage='BUSINESS_QUESTION:NONE',
            figures=[{'quote':'16','role':'PRIMARY','state':'NUMBER','precision_quote':None}],
            identifiers=[{'quote':'North saved bookmark','role':'PRIMARY'}])
        corrected=copy.deepcopy(raw);corrected['identifiers']=[];attempts=[raw,corrected]
        f.catalog['models'][0]['reports'][0]['name']='Report'
        def resolver(payload):
            response=attempts.pop(0);meta={'usage':{'input_tokens':2,'output_tokens':3,'total_tokens':5}}
            try:return intake_extraction.resolve(response,payload),meta
            except Exception as exc:
                exc.provider_metadata=meta;exc.retained_extraction=response;raise
        f.workspace.intake.resolver=resolver
        saved=f.submit(description=ticket)
        self.assertEqual(saved['ticket']['questions'],[])
        self.assertIn('intake_id',saved['ticket']);self.assertEqual(attempts,[])
        source=f.workspace.intake.get(saved['ticket']['source_intake'])
        self.assertEqual(source['resolution_attempts'][0]['rule'],'PAGE_STATE_IS_NOT_IDENTIFIER')

    def test_named_member_of_equal_candidate_set_is_preserved(self):
        from investigator.form_candidates import observe
        raw,p,r=self.payload('Report Other card Quantity differs.',
            visuals=[{'quote':'Other card','form':'TITLE','role':'PRIMARY'}])
        other=copy.deepcopy(p['models'][0]['visuals'][0]);other.update(target_id='other',names=['Other card'])
        p['models'][0]['visuals'].append(other)
        r.update(target_id=None,cell_mode='UNGROUPED',value_seen='16');r.pop('cell_keys')
        binding,_=observe(r,p['models'],lambda c:{'status':'OBSERVED','complete':True,'value':'16',
            'receipt_id':c['target_id'],'query_hash':'a'*64,'execution_surface':{'engine':'engine'},'attestation':{'consistency':'MATCHED'}})
        p['_form_description_candidate_binding']=binding
        result=intake_extraction.resolve(raw,p)
        self.assertEqual(result['target_visual']['target_id'],'other')
        b=form_scope.build(r,p['models'],None,description_proposal=result,candidate_binding=binding)
        self.assertEqual(b['proposal']['target_visual']['target_id'],'other')

    def test_business_form_refusal_preserves_the_existing_category(self):
        import test_form_controller
        f=test_form_controller.FormControllerTests();f.setUp();self.addCleanup(f.doCleanups)
        ticket='Decide whether the business rule for Quantity is correct.'
        raw,_=fixtures.fixture(ticket,kind='BUSINESS_MEANING',triage='BUSINESS_QUESTION:NONE',reports=[])
        def resolver(payload):
            try:return intake_extraction.resolve(raw,payload),{'usage':{'input_tokens':2,'output_tokens':3,'total_tokens':5}}
            except Exception as exc:
                exc.provider_metadata={'usage':{'input_tokens':2,'output_tokens':3,'total_tokens':5}};exc.retained_extraction=raw;raise
        f.workspace.intake.resolver=resolver
        saved=f.submit(target_id=None,cell_mode=None,value_seen=None,comparison='BUSINESS_MEANING',description=ticket)
        self.assertEqual(saved['ticket']['questions'],[]);self.assertNotIn('intake_id',saved['ticket'])
        self.assertTrue(saved['ticket']['state']=='BUSINESS_VALIDATION' or saved['ticket']['history'][-1]['detail'].get('route')=='BUSINESS_VALIDATION')

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

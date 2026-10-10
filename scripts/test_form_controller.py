import copy
import unittest
from unittest.mock import patch
from investigator import form_intake, form_scope
from investigator.question_intake import validate
from investigator.onboarding import Conflict
from investigator.visual_target import validate as target_validate
import test_smart_intake as fixtures


class FormControllerTests(unittest.TestCase):
    def setUp(self):
        self.helper=fixtures.SmartIntakeTests();self.helper.setUp();self.addCleanup(self.helper.doCleanups)
        self.workspace=self.helper.workspace;self.catalog=self.helper.catalog
        for visual in self.catalog['models'][0]['visuals']:
            visual.update(page_id='page',page_names=['Overview'])
            visual['declared_scopes']={'measure':{'state':'COMPLETE','restrictions':[],
                'context_id':'context','context_hash':'a'*64,'inventory_hash':'b'*64}}
        p=patch('investigator.form_controller.snapshot',return_value=self.catalog)
        p.start();self.addCleanup(p.stop)
        self.request={'version':form_intake.VERSION,'request_key':'form-submit','report_id':'report',
            'page_id':'page','target_id':'card','cell_mode':'UNGROUPED',
            'value_seen':'16','comparison':'LOOKS_WRONG','description':''}

    def submit(self,**changes):return self.workspace.forms.submit({**self.request,**changes})

    def proposal(self,saved):return self.workspace.intake.get(saved['ticket']['intake_id'])

    def test_complete_form_adopts_without_model_or_fake_confirmation(self):
        saved=self.submit();record=self.proposal(saved)
        self.assertEqual(saved['ticket']['questions'],[])
        self.assertEqual(saved['ticket']['confirmed'],{})
        self.assertEqual(record['scope_provenance'],'SAVED_USER_SUPPLIED_FORM')
        self.assertEqual(record['proposal']['target_visual']['target_id'],'card')
        self.assertEqual(record['proposal']['reported_figure']['value'],'16')
        self.assertEqual(self.helper.calls,0)
        self.helper.h.native.assert_not_called();self.helper.h.source.assert_not_called()

    def test_duplicate_submit_cannot_reinterpret_or_restart(self):
        first=self.submit();self.assertEqual(self.submit(),first)
        with self.assertRaises(Conflict):self.submit(value_seen='17')

    def test_missing_target_asks_then_actual_user_choice_adopts(self):
        saved=self.submit(target_id=None,cell_mode=None,value_seen=None)
        self.assertNotIn('intake_id',saved['ticket'])
        q=saved['ticket']['questions'][0]
        c=next(c for c in q['choices'] if saved['ticket']['form_choices'][c['id']]['target_id']=='card')
        reply={'ticket_id':saved['ticket']['id'],'revision':saved['revision'],
               'answers':[{'question_id':q['id'],'choice_id':c['id']}],'request_key':'answer'}
        resumed=self.workspace.forms.reply(reply)
        self.assertEqual(self.proposal(resumed)['proposal']['target_visual']['target_id'],'card')
        self.assertEqual(self.workspace.forms.reply(reply),resumed)
        self.assertEqual(self.helper.calls,0)

    def test_changed_catalog_refuses_old_choices(self):
        saved=self.submit(target_id=None,value_seen=None);self.catalog['versions'].append('changed')
        q=saved['ticket']['questions'][0]
        with self.assertRaisesRegex(Conflict,'stale'):
            self.workspace.forms.reply({'ticket_id':saved['ticket']['id'],'revision':saved['revision'],
                'answers':[{'question_id':q['id'],'choice_id':q['choices'][0]['id']}],'request_key':'reply'})

    def test_missing_keys_never_becomes_total(self):
        saved=self.submit(target_id='matrix',cell_mode='KEYED')
        self.assertEqual(saved['ticket']['state'],'HELD')
        self.assertIn('CELL_KEYS_UNRESOLVED',saved['ticket']['history'][-1]['detail']['reason'])
        self.assertNotIn('intake_id',saved['ticket'])

    def test_complete_typed_key_preserved_into_procedure(self):
        saved=self.submit(target_id='matrix',cell_mode='KEYED',cell_keys=[{'column_id':'warehouse','value':'North'}])
        p=self.proposal(saved)['proposal']
        self.assertEqual(p['target_visual']['mode'],'KEYED')
        self.assertEqual(p['filters'],[{'column_id':'warehouse','operator':'in','values':['North']}])

    def test_cross_page_target_is_saved_refusal(self):
        self.catalog['models'][0]['visuals'][0]['page_id']='other'
        saved=self.submit()
        self.assertEqual(saved['ticket']['state'],'HELD')
        self.assertNotIn('intake_id',saved['ticket'])

    def test_empty_and_zero_remain_distinct(self):
        empty=self.proposal(self.submit(value_seen='empty'))['proposal']['reported_figure']
        zero=self.proposal(self.submit(value_seen='0',request_key='zero'))['proposal']['reported_figure']
        self.assertEqual(empty['state'],'EMPTY');self.assertEqual(zero['state'],'NUMBER')

    def test_model_cannot_supply_form_authority(self):
        built=form_scope.build(self.request,self.catalog['models'],None)
        with self.assertRaisesRegex(ValueError,'Model response'):
            validate(built['proposal'],{'text':built['document']['text'],'models':self.catalog['models']})

    def test_changed_form_proposal_fails_recomputation(self):
        built=form_scope.build(self.request,self.catalog['models'],None)
        p=copy.deepcopy(built['proposal']);p['reported_figure']['value']='99'
        with self.assertRaisesRegex(ValueError,'recomputed'):
            validate(p,{'text':built['document']['text'],'models':self.catalog['models'],'_form_request':self.request})

    def test_same_measure_matrix_cannot_replace_sealed_card(self):
        built=form_scope.build(self.request,self.catalog['models'],None)
        p=copy.deepcopy(built['proposal']['target_visual']);p['target_id']='matrix'
        with self.assertRaises(ValueError):target_validate(p,ticket=built['document']['text'],
            candidates=self.catalog['models'][0]['visuals'],report_id='report',measure_id='measure')

    def test_review_detects_changed_form_after_adoption(self):
        saved=self.submit();record=self.proposal(saved)
        self.workspace.smart_intake.tickets.update(saved['ticket']['id'],saved['revision'],
            lambda t:{**t,'form_input':{**t['form_input'],'value_seen':'17'}})
        p=record['proposal'];request={k:p[k] for k in ('model_id','measure_id','filters','dimension_ids')}
        request.update(symptom=record['text'],predecessor=None)
        with self.assertRaisesRegex(Conflict,'decisions changed'):self.workspace.intake.review(record['id'],request)

    def test_description_not_discarded_to_obtain_bound_scope(self):
        request={**self.request,'description':'Investigate the other cell.'}
        with self.assertRaisesRegex(Conflict,'not been interpreted'):
            form_scope.build(request,self.catalog['models'],None)

    def test_other_report_stays_explicit_hold(self):
        saved=self.submit(comparison='OTHER_REPORT')
        self.assertEqual(saved['ticket']['history'][-1]['detail']['reason'],'OTHER_REPORT_COMING_SOON')
        self.assertNotIn('intake_id',saved['ticket']);self.assertEqual(self.helper.calls,0)

    def test_definition_question_hands_off_without_pipeline_claim(self):
        self.workspace.smart_intake.ownership['business']=[{'measure_or_area':'measure','owner':'owner'}]
        saved=self.submit(comparison='BUSINESS_MEANING')
        self.assertEqual(saved['ticket']['state'],'BUSINESS_VALIDATION')
        self.assertEqual(saved['ticket']['handoff']['delivery'],'RECORDED_NOT_SENT')
        self.assertNotIn('intake_id',saved['ticket']);self.assertEqual(self.helper.calls,0)

    def test_authenticated_api_routes_form_and_reply_to_typed_controller(self):
        result=self.helper.h.http('/api/workspace/forms',self.request)
        self.assertTrue(result['status'].startswith('200'))
        self.assertIn('intake_id',result['body']['ticket'])
        denied=self.helper.h.http('/api/workspace/forms',self.request,token='wrong')
        self.assertTrue(denied['status'].startswith('401'))

    def test_catalog_api_does_not_claim_retained_lists_are_live(self):
        result=self.helper.h.http('/api/workspace/forms/catalog')
        self.assertTrue(result['status'].startswith('200'))
        self.assertEqual(result['body']['source'],'RETAINED_APPROVED_CONTEXT')
        self.assertFalse(result['body']['live_lists_connected'])
        self.helper.h.native.assert_not_called();self.helper.h.source.assert_not_called()

    def test_target_reply_api_uses_actual_saved_form_choices(self):
        first=self.helper.h.http('/api/workspace/forms',{**self.request,'target_id':None,'cell_mode':None,'value_seen':None})['body']
        q=first['ticket']['questions'][0]
        c=next(c for c in q['choices'] if first['ticket']['form_choices'][c['id']]['target_id']=='card')
        result=self.helper.h.http('/api/workspace/tickets/'+first['ticket']['id']+'/reply',{
            'revision':first['revision'],'answers':[{'question_id':q['id'],'choice_id':c['id']}],
            'request_key':'api-reply'})
        self.assertTrue(result['status'].startswith('200'))
        self.assertEqual(self.proposal(result['body'])['proposal']['target_visual']['target_id'],'card')

    def test_stale_reply_revision_cannot_replace_target(self):
        first=self.submit(target_id=None,value_seen=None)
        q=first['ticket']['questions'][0];c=q['choices'][0]
        request={'ticket_id':first['ticket']['id'],'revision':first['revision']-1,
            'answers':[{'question_id':q['id'],'choice_id':c['id']}],'request_key':'stale'}
        with self.assertRaises(Conflict):self.workspace.forms.reply(request)
        self.assertEqual(self.workspace.smart_intake.tickets.get(first['ticket']['id']),first)

    def test_wrong_typed_key_and_extra_key_do_not_create_scope(self):
        self.catalog['models'][0]['columns'][0]['data_type']='int64'
        wrong=self.submit(target_id='matrix',cell_mode='KEYED',cell_keys=[{'column_id':'warehouse','value':'North'}])
        self.assertEqual(wrong['ticket']['state'],'HELD');self.assertNotIn('intake_id',wrong['ticket'])
        extra=self.submit(request_key='extra',target_id='matrix',cell_mode='KEYED',
            cell_keys=[{'column_id':'warehouse','value':1},{'column_id':'other','value':1}])
        self.assertEqual(extra['ticket']['state'],'HELD');self.assertNotIn('intake_id',extra['ticket'])

    def test_description_conflict_cannot_be_silently_overridden(self):
        request={**self.request,'description':'Other number.'}
        base=form_scope.build(self.request,self.catalog['models'],None)['proposal']
        base['target_visual']['target_id']='matrix'
        with self.assertRaisesRegex(Conflict,'conflicts'):
            form_scope.build(request,self.catalog['models'],None,description_proposal=base)

    def description_proposal(self,request,**updates):
        from investigator import form_scope
        proposal=form_scope.build({**self.request,'value_seen':None},self.catalog['models'],None)['proposal']
        proposal.update(updates)
        part=next(p for p in form_scope.document(request,None)['parts'] if p['pointer']=='/description')
        proposal['question_kind']={'kind':'METRIC_COMPONENTS','source':{k:part[k] for k in ('start','end','quote')}}
        proposal['ticket_shape']='BUSINESS_QUESTION';proposal['comparison_mode']='NONE'
        proposal['ticket_route']={'route':'DECLARED_SUBJECT'}
        return proposal

    def test_blank_comparator_uses_validated_declared_subject_without_new_question(self):
        request={**self.request,'comparison':None,'value_seen':None,'description':'What does Quantity mean?'}
        p=self.description_proposal(request)
        built=form_scope.build(request,self.catalog['models'],None,description_proposal=p)
        self.assertEqual(built['proposal']['ticket_route']['route'],'DECLARED_SUBJECT')
        self.assertEqual(built['proposal']['target_visual']['target_id'],'card')

    def test_complete_r1_scope_does_not_invent_a_visual(self):
        for visual in self.catalog['models'][0]['visuals']:
            visual['declared_scopes']={'measure':{'state':'COMPLETE','restrictions':[],
                'context_id':'context','context_hash':'a'*64,'inventory_hash':'b'*64}}
        request={**self.request,'target_id':None,'cell_mode':None,'comparison':None,
                 'value_seen':None,'description':'What does Quantity mean?'}
        p=self.description_proposal(request,target_visual=None,extracted_ticket={'resolution_evidence':[
            {'resolution':'COMPLETE_DECLARED_SCOPE_EQUIVALENCE','measure_id':'measure','candidate_ids':['card','matrix']}]})
        built=form_scope.build(request,self.catalog['models'],None,description_proposal=p)
        self.assertIsNone(built['proposal']['target_visual'])
        self.assertEqual(built['form']['mode'],'MEASURE_AT_SCOPE')

    def test_missing_r1_candidate_cannot_admit_model_scope(self):
        request={**self.request,'target_id':None,'cell_mode':None,'comparison':None,
                 'value_seen':None,'description':'Quantity'}
        p=self.description_proposal(request,target_visual=None,extracted_ticket={'resolution_evidence':[
            {'resolution':'COMPLETE_DECLARED_SCOPE_EQUIVALENCE','measure_id':'measure','candidate_ids':['missing']}]})
        with self.assertRaisesRegex(Conflict,'R1 proof'):
            form_scope.build(request,self.catalog['models'],None,description_proposal=p)

    def test_form_proof_cannot_pair_null_target_with_cell_mode(self):
        from jsonschema import Draft202012Validator,ValidationError
        proof=form_scope.build(self.request,self.catalog['models'],None)['form']
        for altered in ({**proof,'target_id':None},{**proof,'mode':'MEASURE_AT_SCOPE'}):
            with self.assertRaises(ValidationError):Draft202012Validator(form_scope.PROOF).validate(altered)

    def test_selected_visual_carries_complete_declared_filters_and_saved_defaults(self):
        visual=next(v for v in self.catalog['models'][0]['visuals'] if v['target_id']=='card')
        restrictions=[{'field_id':'warehouse','operator':'IN','values':['North']}]
        visual['declared_scopes']['measure']['restrictions']=restrictions
        p=self.proposal(self.submit())['proposal']
        self.assertEqual(p['target_visual']['match_basis']['form']['declared_scope']['restrictions'],restrictions)
        self.assertEqual(p['target_visual']['target_id'],'card')

    def test_missing_definition_scope_never_means_unfiltered(self):
        for visual in self.catalog['models'][0]['visuals']:visual.pop('declared_scopes')
        saved=self.submit()
        self.assertEqual(saved['ticket']['state'],'HELD')
        self.assertIn('scope is unavailable',saved['ticket']['history'][-1]['detail']['reason'])
        self.assertNotIn('intake_id',saved['ticket'])

    def test_picked_multimeasure_visual_uses_description_measure_not_another_question(self):
        visual=next(v for v in self.catalog['models'][0]['visuals'] if v['target_id']=='card')
        request={**self.request,'comparison':None,'value_seen':None,'description':'Explain Quantity.'}
        p=self.description_proposal(request)
        visual['measure_ids'].append('other-measure')
        built=form_scope.build(request,self.catalog['models'],None,description_proposal=p)
        self.assertEqual(built['proposal']['measure_id'],'measure')
        target_validate(built['proposal']['target_visual'],ticket=built['document']['text'],
            candidates=self.catalog['models'][0]['visuals'],report_id='report',measure_id='measure')

    def test_description_cannot_select_a_measure_absent_from_picked_visual(self):
        request={**self.request,'description':'Explain another measure.'}
        p=self.description_proposal(request,measure_id='unbound')
        with self.assertRaisesRegex(Conflict,'conflicts'):
            form_scope.build(request,self.catalog['models'],None,description_proposal=p)

    def test_description_declared_subject_route_is_derived_from_retained_extraction(self):
        request={**self.request,'comparison':None,'value_seen':None,
                 'description':'In Report, explain the global numerator and denominator of Quantity.'}
        p=self.description_proposal(request);p.pop('ticket_route')
        raw,_=fixtures.fixture(form_scope.document(request,None)['text'],figures=[])
        raw['kind']='METRIC_COMPONENTS'
        p['extracted_ticket']={'response':raw}
        built=form_scope.build(request,self.catalog['models'],None,description_proposal=p)
        self.assertEqual(built['proposal']['ticket_route']['route'],'DECLARED_SUBJECT')

    def test_description_read_does_not_duplicate_supplied_form_figure(self):
        request={**self.request,'description':'Quantity shows 16.'}
        with patch.object(self.workspace.intake,'resolve',return_value={
                'id':'description','status':'HELD','refusal_reason':'Recorded refusal'}) as resolver:
            saved=self.workspace.forms.submit(request)
        text=resolver.call_args.args[0]['text']
        self.assertEqual(text.count('16'),1)
        self.assertNotIn('Comparison selected',text)
        self.assertEqual(saved['ticket']['state'],'HELD')

    def test_description_subject_cannot_quote_generated_label_as_user_provenance(self):
        request={**self.request,'comparison':None,'value_seen':None,'description':'Explain Quantity.'}
        p=self.description_proposal(request)
        p['question_kind']['source']={'start':0,'end':11,'quote':'Description'}
        with self.assertRaisesRegex(Conflict,'user description'):
            form_scope.build(request,self.catalog['models'],None,description_proposal=p)

    def test_business_question_with_missing_target_never_crashes(self):
        saved=self.submit(comparison='BUSINESS_MEANING',target_id=None,cell_mode=None,value_seen=None)
        self.assertEqual(saved['ticket']['state'],'CLARIFYING')
        self.assertNotIn('intake_id',saved['ticket'])

    def test_conflict_offers_user_decision_and_review_respects_it(self):
        request={**self.request,'description':'Another value.'}
        p=form_scope.build({**self.request,'value_seen':'17'},self.catalog['models'],None)['proposal']
        # A separately retained interpretation conflicts with the explicit 16.
        with patch.object(self.workspace.intake,'resolve',wraps=self.workspace.intake.resolve) as resolver:
            saved=self.workspace.smart_intake.tickets.submit(request,request['request_key'])
            from investigator.onboarding import digest
            def retain(t):
                t.update(form_input=copy.deepcopy(request),form_catalog_hash=digest(self.catalog));return t
            saved=self.workspace.smart_intake.tickets.update(saved['ticket']['id'],saved['revision'],retain)
            offered=self.workspace.forms._conflict(saved,self.catalog,'Description conflicts with the figure',p)
        self.assertEqual(len(offered['ticket']['questions']),1)
        q=offered['ticket']['questions'][0];choice=next(c for c in q['choices'] if c['label']=='Use my selected form details')
        resumed=self.workspace.forms.reply({'ticket_id':saved['ticket']['id'],'revision':offered['revision'],
            'answers':[{'question_id':q['id'],'choice_id':choice['id']}],'request_key':'conflict-answer'})
        record=self.proposal(resumed);proposal=record['proposal']
        self.assertEqual(proposal['reported_figure']['value'],'16')
        review={k:proposal[k] for k in ('model_id','measure_id','filters','dimension_ids')}
        review.update(symptom=record['text'],predecessor=None)
        self.assertEqual(self.workspace.intake.review(record['id'],review)['target_visual']['target_id'],'card')

    def test_invalid_form_is_400_without_creating_a_ticket(self):
        result=self.helper.h.http('/api/workspace/forms',{**self.request,'query':'SELECT 1'})
        self.assertTrue(result['status'].startswith('400'))
        self.assertEqual(self.workspace.smart_intake.tickets.list()['tickets'],[])

    def test_form_operation_is_supported_by_the_existing_tape_contract(self):
        from investigator import process_tape as journal
        self.assertIn('form_submit',journal.SMART_OPERATIONS)
        self.assertIn('form_reply',journal.SMART_OPERATIONS)
        self.assertEqual(self.workspace.forms.configuration,self.workspace.smart_intake.configuration)
        self.assertEqual(self.workspace.forms.auto_start,self.workspace.smart_intake.auto_start)


if __name__=='__main__':unittest.main()

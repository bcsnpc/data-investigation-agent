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
        saved=self.submit(target_id=None,cell_mode=None)
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
        saved=self.submit(target_id=None);self.catalog['versions'].append('changed')
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
        first=self.helper.h.http('/api/workspace/forms',{**self.request,'target_id':None,'cell_mode':None})['body']
        q=first['ticket']['questions'][0]
        c=next(c for c in q['choices'] if first['ticket']['form_choices'][c['id']]['target_id']=='card')
        result=self.helper.h.http('/api/workspace/tickets/'+first['ticket']['id']+'/reply',{
            'revision':first['revision'],'answers':[{'question_id':q['id'],'choice_id':c['id']}],
            'request_key':'api-reply'})
        self.assertTrue(result['status'].startswith('200'))
        self.assertEqual(self.proposal(result['body'])['proposal']['target_visual']['target_id'],'card')

    def test_stale_reply_revision_cannot_replace_target(self):
        first=self.submit(target_id=None)
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

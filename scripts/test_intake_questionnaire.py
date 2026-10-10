import copy,unittest
from pathlib import Path
from jsonschema import ValidationError
from investigator.intake_questionnaire import VERSION,DEFINITION,validate,to_form
import test_form_controller as fixtures

class QuestionnaireTests(unittest.TestCase):
    def test_screenshot_actions_refresh_investigations_not_browser_history(self):
        source=(Path(__file__).parents[1]/'apps/investigator-workspace/screenshots.js').read_text(encoding='utf8')
        self.assertNotIn('await history()',source)
        self.assertIn('await investigationHistory()',source)
    def setUp(self):
        self.h=fixtures.FormControllerTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        self.models=self.h.catalog['models']
        self.request={'version':VERSION,'request_key':'q','report_id':'report','page_id':'page','visual_id':'card',
            'comparing':{'kind':'APPLICATION'},'description':''}
    def test_schema_owns_order_and_exact_four_comparisons(self):
        self.assertEqual([f['name'] for f in DEFINITION['fields']],['report_id','page_id','visual_id','comparing','description','screenshot_review_id'])
        self.assertEqual([c['value'] for c in DEFINITION['fields'][3]['choices']],['OTHER_REPORT','OTHER_PAGE','APPLICATION','NOTHING'])
        with self.assertRaises(ValidationError):validate({**self.request,'value_seen':'16'},self.models)
        with self.assertRaises(ValidationError):validate({**self.request,'request_key':'x'*101},self.models)
    def test_pick_is_identity_not_reported_figure_or_total_guess(self):
        r=to_form(self.request,self.models);self.assertEqual(r['target_id'],'card');self.assertEqual(r['cell_mode'],'UNGROUPED');self.assertIsNone(r['value_seen'])
        matrix=next(v for v in self.models[0]['visuals'] if v['target_id']=='matrix')
        r=to_form({**self.request,'visual_id':matrix['target_id']},self.models)
        self.assertIsNone(r['cell_mode']);self.assertEqual(r['cell_keys'],[])
    def test_optional_visual_never_selects_a_representative(self):
        self.assertIsNone(to_form({**self.request,'visual_id':None},self.models)['target_id'])
    def test_measure_question_route_is_explicit_and_cannot_select_a_visual(self):
        request={**self.request,'subject':'MEASURE_TEXT','report_id':None,'page_id':None,'visual_id':None,
            'description':'Why is Quantity stale?'}
        result=to_form(request,self.models)
        self.assertEqual(result['subject'],'MEASURE_TEXT')
        self.assertIsNone(result['target_id']);self.assertIsNone(result['report_id'])
        with self.assertRaises(ValidationError):to_form({**request,'visual_id':'card'},self.models)
        with self.assertRaises(ValidationError):to_form({**request,'subject':'REPORT'},self.models)
        from investigator.questionnaire_eval_inputs import map_form
        self.assertEqual(map_form(result,result['description'])['subject'],'MEASURE_TEXT')
    def test_measure_subject_uses_existing_controller_with_original_questionnaire(self):
        from unittest.mock import patch
        request={**self.request,'subject':'MEASURE_TEXT','report_id':None,'page_id':None,'visual_id':None,
            'description':'Why is Quantity stale?'}
        controller=self.h.workspace.smart_intake
        with patch.object(controller,'submit',return_value=controller.tickets.submit(
                {'text':request['description'],'request_key':'measure-question'},'measure-question')) as submit:
            saved=self.h.workspace.forms.submit(request)
        self.assertEqual(submit.call_args.args[0]['structured']['subject'],'MODEL_MEASURE')
        self.assertNotIn('report_page',submit.call_args.args[0]['structured'])
        self.assertEqual(saved['ticket']['form_origin']['subject'],'MEASURE_TEXT')
    def test_nothing_with_description_preserves_subject_instead_of_inventing_discrepancy(self):
        from investigator import form_scope
        import test_smart_intake
        request=to_form({**self.request,'comparing':{'kind':'NOTHING'},
            'description':'In Report, explain the global numerator and denominator of Quantity.'},self.models)
        p=self.h.description_proposal(request);p.pop('ticket_route')
        raw,_=test_smart_intake.fixture(form_scope.document(request,None)['text'],figures=[])
        raw['kind']='METRIC_COMPONENTS';p['extracted_ticket']={'response':raw}
        built=form_scope.build(request,self.models,None,description_proposal=p)
        self.assertEqual(built['proposal']['ticket_route']['route'],'DECLARED_SUBJECT')
        self.assertEqual(built['proposal']['target_visual']['target_id'],'card')
    def test_blank_nothing_and_explicit_application_keep_their_routes(self):
        self.assertEqual(to_form({**self.request,'comparing':{'kind':'NOTHING'}},self.models)['comparison'],'LOOKS_WRONG')
        self.assertEqual(to_form({**self.request,'description':'Explain Quantity.'},self.models)['comparison'],'APPLICATION')
    def test_eval_mapping_cannot_invent_a_comparison_or_required_pick(self):
        from investigator.questionnaire_eval_inputs import map_form
        form=to_form(self.request,self.models)
        self.assertEqual(map_form(form,'original text')['description'],'original text')
        for change in ({'comparison':None},{'comparison':'OTHER_REPORT'},{'page_id':None}):
            with self.assertRaisesRegex(ValueError,'QUESTIONNAIRE_NOT_MEASURABLE'):
                map_form({**form,**change},'original text')
        self.assertEqual(map_form({**form,'comparison':'DECLARED_SUBJECT'},'Explain Quantity')['comparing'],{'kind':'NOTHING'})
    def test_unresolved_description_cannot_reask_selected_nothing(self):
        request={**self.request,'comparing':{'kind':'NOTHING'},'description':'Explain Quantity.'}
        controller=self.h.workspace.forms
        saved=controller.smart.tickets.submit(request,request['request_key'])
        def retain(ticket):
            ticket['questionnaire_input']=copy.deepcopy(request)
            ticket['form_input']=to_form(request,self.models)
            return ticket
        saved=controller.smart.tickets.update(saved['ticket']['id'],saved['revision'],retain)
        result=controller._ask(saved,{'models':self.models},{'questions':[{'field':'COMPARISON'}]})
        self.assertEqual(result['ticket']['state'],'HELD')
        self.assertEqual(result['ticket']['questions'],[])
        self.assertIn('DESCRIPTION_SUBJECT_UNRESOLVED',result['ticket']['history'][-1]['detail']['reason'])
        self.assertEqual(result['ticket']['questionnaire_input'],request)
    def test_other_page_and_report_cannot_alias_or_escape_declared_context(self):
        for comparison in ({'kind':'OTHER_PAGE','page_id':'page'},{'kind':'OTHER_REPORT','report_id':'absent','page_id':'x'}):
            with self.assertRaises(ValueError):validate({**self.request,'comparing':comparison},self.models)
    def test_source_value_does_not_become_the_reported_number(self):
        r=to_form({**self.request,'comparing':{'kind':'APPLICATION','source_value':'999'}},self.models)
        self.assertEqual(r['description'],'');self.assertIsNone(r['value_seen'])
    def test_review_required_and_attached_text_is_never_truncated(self):
        r={**self.request,'screenshot_review_id':'review'}
        with self.assertRaises(ValueError):to_form(r,self.models)
        review={'id':'review','provenance':'USER_REVIEWED_SCREENSHOT_TRANSCRIPTION','text':'Card shows 16'}
        self.assertIn('Card shows 16',to_form(r,self.models,review=review)['description'])
        with self.assertRaises(ValueError):to_form({**r,'description':'a'*2000},self.models,review=review)
    def test_full_submission_retains_questionnaire_facts_with_idempotency(self):
        saved=self.h.workspace.forms.submit(self.request)
        self.assertEqual(saved['ticket']['questionnaire_input'],self.request)
        self.assertEqual(saved['request'],self.request)
        self.assertEqual(saved,self.h.workspace.forms.submit(self.request))
        self.assertEqual(saved['ticket']['form_input']['target_id'],'card')
        self.assertEqual(saved['ticket']['questions'],[])
    def test_cross_page_route_is_honest_hold_and_retains_both_picks(self):
        v=copy.deepcopy(self.models[0]['visuals'][0]);v.update(page_id='other',target_id='other-card');self.models[0]['visuals'].append(v)
        r={**self.request,'comparing':{'kind':'OTHER_PAGE','page_id':'other'}}
        saved=self.h.workspace.forms.submit(r)
        self.assertEqual(saved['ticket']['state'],'HELD');self.assertIn('UNIMPLEMENTED_ROUTE',saved['ticket']['history'][-1]['detail']['reason'])
        self.assertEqual(saved['ticket']['questionnaire_input'],r)

    def test_comment_is_retained_and_cannot_change_admitted_scope(self):
        from investigator.ticket_comments import append,progress
        saved=self.h.workspace.forms.submit(self.request)
        before=copy.deepcopy(saved['ticket']['form_input'])
        request={'ticket_id':saved['ticket']['id'],'revision':saved['revision'],'request_key':'comment',
            'text':'Can you check this screenshot?','attachment_id':None,'review_id':None}
        result=append(self.h.workspace,request)
        self.assertEqual(result['ticket']['form_input'],before)
        self.assertEqual(result['ticket']['comments'][0]['text'],request['text'])
        self.assertEqual(append(self.h.workspace,request),result)
        self.assertEqual(progress(self.h.workspace,saved['ticket']['id'])['steps'],[])
        with self.assertRaises(ValueError):append(self.h.workspace,{**request,'actor':'AGENT'})

    def test_agent_can_request_screenshot_in_same_retained_thread(self):
        from investigator.ticket_comments import append
        saved=self.h.workspace.forms.submit(self.request)
        request={'ticket_id':saved['ticket']['id'],'revision':saved['revision'],'request_key':'agent-image',
            'text':'Can you attach a screenshot of the value in the source system?','attachment_id':None,'review_id':None}
        result=append(self.h.workspace,request,actor='AGENT')
        self.assertEqual(result['ticket']['comments'][0]['actor'],'AGENT')

    def test_api_and_form_share_schema_and_scope_validation(self):
        http=self.h.helper.h.http
        result=http('/api/workspace/questionnaire/schema')
        self.assertEqual(result['body'],DEFINITION)
        saved=http('/api/workspace/questionnaire',self.request)
        self.assertTrue(saved['status'].startswith('200'))
        self.assertEqual(saved['body']['ticket']['questionnaire_input'],self.request)
        bad=http('/api/workspace/questionnaire',{**self.request,'request_key':'bad','visual_id':'not-on-page'})
        self.assertTrue(bad['status'].startswith('400'))

    def test_screenshot_reply_never_replaces_an_admitted_scope(self):
        from investigator.onboarding import Conflict
        saved=self.h.workspace.forms.submit(self.request)
        with self.assertRaisesRegex(Conflict,'unresolved'):
            self.h.workspace.forms.screenshot_reply({'ticket_id':saved['ticket']['id'],
                'revision':saved['revision'],'review_id':'review','request_key':'screenshot'})

    def test_changed_question_preserves_picked_facts_and_archives_old_scope(self):
        from unittest.mock import patch
        saved=self.h.workspace.forms.submit(self.request)
        with patch.object(self.h.workspace.forms,'_plan',side_effect=lambda s,c:s):
            result=self.h.workspace.smart_intake.respond({'ticket_id':saved['ticket']['id'],
                'revision':saved['revision'],'kind':'RESTATE_QUESTION','text':'Is that number stale?'})
        for field in ('report_id','page_id','target_id','comparison'):
            self.assertEqual(result['ticket']['form_input'][field],saved['ticket']['form_input'][field])
        self.assertNotIn('intake_id',result['ticket'])
        self.assertEqual(result['ticket']['question_versions'][0]['intake_id'],saved['ticket']['intake_id'])
        self.assertEqual(result['ticket']['questionnaire_input']['description'],'Is that number stale?')

    def test_pending_screenshot_answer_supersedes_interpretation_not_selected_facts(self):
        from unittest.mock import patch
        saved=self.h.workspace.forms.submit({**self.request,'visual_id':None})
        ticket_id=saved['ticket']['id']
        saved=self.h.workspace.smart_intake.tickets.update(ticket_id,saved['revision'],lambda t:{**t,'source_intake':'old-extraction'})
        review={'id':'review','provenance':'USER_REVIEWED_SCREENSHOT_TRANSCRIPTION','text':'Global card shows 16.','attachment':{'id':'image','name':'card.png'}}
        with patch.object(self.h.workspace.screenshots,'saved',return_value=review),patch.object(self.h.workspace.forms,'_plan',side_effect=lambda s,c:s):
            result=self.h.workspace.forms.screenshot_reply({'ticket_id':ticket_id,'revision':saved['revision'],'review_id':'review','request_key':'screen-answer'})
        self.assertEqual(result['ticket']['superseded_source_intakes'],['old-extraction'])
        self.assertNotIn('source_intake',result['ticket'])
        self.assertEqual(result['ticket']['form_description_generation'],1)
        self.assertEqual(result['ticket']['form_input']['report_id'],self.request['report_id'])
        self.assertIn(review['text'],result['ticket']['form_input']['description'])
        self.assertEqual(result['ticket']['evidence']['screenshot_review'],review)

if __name__=='__main__':unittest.main()

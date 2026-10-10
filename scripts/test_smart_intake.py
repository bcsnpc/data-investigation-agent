import copy
import unittest
from unittest.mock import patch
from investigator.smart_intake import SmartIntake
from investigator import intake_extraction, ticket_protocol as protocol
from investigator.onboarding import digest, Conflict
from test_intake_extraction import fixture
import test_investigator_workspace as workspace_fixture


class SmartIntakeTests(unittest.TestCase):
    def test_model_subject_is_preserved_through_scope_adoption_without_visual_question(self):
        self.raw,self.payload=fixture('Is the global Quantity in Model current?',
            kind='FRESHNESS',triage='MISMATCH_COMPLAINT:VERTICAL',
            reports=[{'quote':'Model','role':'PRIMARY'}],
            visuals=[{'quote':'global','role':'PRIMARY','form':'UNGROUPED'}])
        self.catalog['models']=self.payload['models']
        request={'text':self.payload['text'],'request_key':'model-measure',
                 'structured':{'subject':'MODEL_MEASURE','comparison':'STALE'}}
        self.controller.configuration['must_confirm']=[]
        saved=self.controller.submit(request)
        self.assertEqual(saved['ticket']['questions'],[])
        adopted=self.workspace.intake.get(saved['ticket']['intake_id'])
        self.assertEqual(adopted['input_request'],request)
        self.assertNotIn('target_visual',adopted['proposal'])
        self.assertNotIn('report_binding',adopted['proposal'])
        self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_identifier_phrase_is_retried_once_and_exact_opaque_token_proceeds(self):
        from investigator import form_scope,form_intake
        from investigator.question_intake import azure_resolve
        text='In Report, Global card Quantity reflects adjustment reason X73.'
        good,payload=fixture(text,kind='SOURCE_CORRECTNESS',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}],
            identifiers=[{'quote':'X73','role':'PRIMARY'}])
        bad=copy.deepcopy(good);bad['identifiers'][0]['quote']='adjustment reason X73'
        for visual in payload['models'][0]['visuals']:visual['page_id']='page'
        self.catalog['models']=payload['models']
        request={'version':form_intake.VERSION,'request_key':'identifier-form','report_id':'report',
            'page_id':'page','target_id':'card','cell_mode':'UNGROUPED','comparison':'APPLICATION',
            'value_seen':None,'description':text}
        doc=form_scope.document(request,self.workspace.intake_configuration)
        end=next(p['end'] for p in doc['parts'] if p['pointer']=='/description')
        self.workspace.intake.resolver=azure_resolve
        with patch('ticket_planner.azure_generate',side_effect=[(bad,{}),(good,{})]) as provider:
            saved=self.workspace.intake.resolve({'text':doc['text'][:end],
                'request_key':'identifier-repair','parent_id':None},retain_extraction=True,form_request=request)
        self.assertEqual(saved['status'],'PROPOSED',saved)
        self.assertEqual(provider.call_count,2)
        self.assertEqual(saved['resolution_attempts'][0]['rule'],'IDENTIFIER_QUOTE_INVALID')
        self.assertEqual(saved['proposal']['expected_records'][0]['value'],'X73')
        self.assertEqual(saved['retained_extraction'],bad)
        self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_incomplete_two_key_cell_holds_before_adoption_and_every_reader(self):
        self.raw,self.payload=fixture('In Report, Warehouse matrix Quantity North / One shows 16. Can saved context reproduce it?',
            kind='VISUAL_CONTENT',triage='BUSINESS_QUESTION:NONE',
            visuals=[{'quote':'Warehouse matrix','role':'PRIMARY','form':'TITLE'}],
            figures=[{'quote':'16','role':'PRIMARY','state':'NUMBER','precision_quote':None}],
            selections=[{'quote':'North / One','column':None,'value':'North / One','role':'PRIMARY'}])
        model=self.payload['models'][0];model['visuals'][1]['grouping_columns'].append('product')
        model['columns'].append({'column_id':'product','name':'product','data_type':'string'})
        self.catalog['models']=self.payload['models']
        saved=self.submit()
        self.assertEqual(saved['ticket']['state'],'HELD');self.assertNotIn('intake_id',saved['ticket'])
        self.assertIn('Every grouping column',saved['ticket']['history'][-1]['detail']['reason'])
        self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_supplied_report_link_reaches_scope_without_fake_confirmation(self):
        from test_input_reference import setup_reference
        self.raw,self.payload,request=setup_reference()
        self.catalog['models']=self.payload['models']
        saved=self.controller.submit(request)
        self.assertEqual(saved['ticket']['questions'],[])
        proposal=self.workspace.intake.get(saved['ticket']['intake_id'])['proposal']
        self.assertEqual(proposal['report_binding']['resolution_kind'],'DECLARED_REFERENCE')
        self.assertEqual(proposal['target_visual']['target_id'],'card')
        self.assertEqual(saved['ticket']['confirmed'],{})
        self.assertEqual(self.calls,1);self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_unsupported_supplied_link_is_a_saved_hold_before_provider_or_estate_calls(self):
        from test_input_reference import setup_reference,LINK
        self.raw,self.payload,request=setup_reference();self.catalog['models']=self.payload['models']
        request['structured']['report_link']=LINK+'?bookmarkGuid=SavedState'
        saved=self.controller.submit(request)
        self.assertEqual(saved['ticket']['state'],'HELD')
        self.assertIn('CONTEXT_UNSUPPORTED',saved['ticket']['history'][-1]['detail']['message'])
        self.assertEqual(saved['request'],request)
        self.assertEqual(self.controller.submit(request),saved)
        self.assertEqual(self.calls,0);self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_supplied_link_container_never_becomes_a_redundant_question(self):
        from test_input_reference import setup_reference,ASSET
        self.raw,self.payload,request=setup_reference();self.catalog['models']=self.payload['models']
        self.controller.configuration['must_confirm']=['REPORT_PAGE']
        saved=self.controller.submit(request)
        self.assertEqual(saved['ticket']['questions'],[])
        self.assertIn('intake_id',saved['ticket'])
        self.assertEqual(saved['ticket']['settled']['REPORT_PAGE']['value']['report_binding']['report_id'],ASSET)

    def test_reference_narrows_choices_to_its_page_without_selecting_a_visual(self):
        from test_input_reference import setup_reference,ASSET
        self.raw,self.payload,request=setup_reference();self.catalog['models']=self.payload['models'];self.raw['visuals']=[]
        visual=copy.deepcopy(self.payload['models'][0]['visuals'][0]);visual['target_id']='second-card'
        self.catalog['models'][0]['visuals'].append(visual)
        saved=self.controller.submit(request)
        self.assertEqual([q['field'] for q in saved['ticket']['questions']],['NUMBER'])
        meanings=list(saved['ticket']['choice_values'].values())
        self.assertEqual({v['target_id'] for v in meanings},{'card','second-card'})
        self.assertTrue(all(v['page_id']==ASSET+'/page/PageA' for v in meanings))
        self.assertNotIn('intake_id',saved['ticket']);self.assertEqual(self.calls,1)

    def test_historical_route_does_not_ask_for_a_current_visual_or_comparison(self):
        self.raw,self.payload=fixture('Why did Quantity change between the earlier and later report states?',
            kind='TEMPORAL_COMPARISON',triage='BUSINESS_QUESTION:NONE',reports=[],measures=[])
        saved=self.submit()
        self.assertEqual(saved['ticket']['state'],'HELD')
        self.assertEqual(saved['ticket']['questions'],[])
        self.assertEqual(saved['ticket']['history'][-1]['detail']['capability'],'UNIMPLEMENTED_ROUTE')
        self.assertIn('earlier-state',saved['ticket']['history'][-1]['detail']['reason'])
        self.assertNotIn('intake_id',saved['ticket']);self.assertEqual(self.calls,1)
        self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_named_reproduction_question_adopts_scope_without_a_comparison_question(self):
        self.raw,self.payload=fixture('In Report, Global card Quantity shows 16. Can the saved context reproduce that figure?',
            kind='VISUAL_CONTENT',triage='BUSINESS_QUESTION:NONE',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}],
            figures=[{'quote':'16','role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        saved=self.submit()
        self.assertEqual(saved['ticket']['questions'],[])
        proposal=self.workspace.intake.get(saved['ticket']['intake_id'])['proposal']
        self.assertEqual(proposal['ticket_route']['route'],'DECLARED_SUBJECT')
        self.assertEqual(proposal['target_visual']['target_id'],'card')
        self.assertEqual(proposal['reported_figure']['value'],'16')
        self.assertEqual(self.calls,1)
        self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_changed_question_can_resume_from_a_waiting_clarification(self):
        waiting=self.submit();old_questions=copy.deepcopy(waiting['ticket']['questions'])
        self.raw,self.payload=fixture('In Report, Global card Quantity shows 25 and looks wrong.',
            figures=[{'quote':'25','role':'PRIMARY','state':'NUMBER','precision_quote':None}],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        changed=self.controller.respond({'ticket_id':waiting['ticket']['id'],'revision':waiting['revision'],
            'kind':'RESTATE_QUESTION','text':self.payload['text']})
        self.assertEqual(changed['ticket']['questions'],[])
        self.assertEqual(changed['ticket']['settled']['COMPARISON']['value']['route'],'LOOKS_WRONG')
        self.assertEqual(changed['ticket']['question_versions'][0]['questions'],old_questions)
        self.assertEqual(changed['ticket']['prior_clarifying_rounds'],1)
        self.assertEqual(changed['ticket']['rounds'],0)
        self.assertEqual(self.calls,2);self.h.native.assert_not_called()

    def test_old_confirmed_cell_cannot_settle_a_new_ambiguous_target(self):
        shared=self.findings()
        self.raw,self.payload=fixture('In Report, Quantity shows 25 and looks wrong.',
            figures=[{'quote':'25','role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        changed=self.controller.respond({'ticket_id':shared['ticket']['id'],'revision':shared['revision'],
            'kind':'RESTATE_QUESTION','text':self.payload['text']})
        self.assertEqual(changed['ticket']['state'],'CLARIFYING')
        self.assertEqual(changed['ticket']['confirmed'],{})
        self.assertNotIn('NUMBER',changed['ticket']['settled'])
        self.assertNotIn('intake_id',changed['ticket'])
        self.assertIn('NUMBER',[q['field'] for q in changed['ticket']['questions']])
        self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_user_changed_question_keeps_the_ticket_and_history_but_not_old_scope_authority(self):
        shared=self.findings();before=copy.deepcopy(shared)
        self.raw,self.payload=fixture('In Report, Global card Quantity shows 25 and looks wrong.',
            figures=[{'quote':'25','role':'PRIMARY','state':'NUMBER','precision_quote':None}],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        changed=self.controller.respond({'ticket_id':shared['ticket']['id'],'revision':shared['revision'],
            'kind':'RESTATE_QUESTION','text':self.payload['text']})
        self.assertEqual(changed['ticket']['id'],shared['ticket']['id'])
        self.assertEqual(changed['request'],before['request'])
        self.assertEqual(changed['ticket']['current_input']['text'],self.payload['text'])
        self.assertEqual(changed['ticket']['state'],'CLARIFYING',changed['ticket']['history'])
        self.assertEqual(changed['ticket']['settled']['COMPARISON']['value']['route'],'LOOKS_WRONG')
        self.assertNotIn('findings',changed['ticket'])
        self.assertNotEqual(changed['ticket']['intake_id'],before['ticket']['intake_id'])
        self.assertEqual(changed['ticket']['confirmed'],{})
        archived=changed['ticket']['question_versions'][0]
        self.assertEqual(archived['findings'],before['ticket']['findings'])
        self.assertEqual(archived['intake_id'],before['ticket']['intake_id'])
        self.assertEqual(archived['confirmed'],before['ticket']['confirmed'])
        self.assertEqual(changed['ticket']['evidence'],before['ticket']['evidence'])
        self.assertEqual(self.calls,2)
        resumed=changed
        proposal=self.workspace.intake.get(resumed['ticket']['intake_id'])['proposal']
        self.assertEqual(proposal['reported_figure']['value'],'25')
        self.assertEqual(proposal['target_visual']['target_id'],'card')
        self.assertEqual(self.calls,2);self.h.native.assert_not_called();self.h.source.assert_not_called()
        with self.assertRaises(Conflict):self.controller.attach({
            'ticket_id':resumed['ticket']['id'],'revision':resumed['revision'],'session_id':'session'})

    def test_changed_question_rejects_a_stale_revision_before_calling_the_model(self):
        shared=self.findings()
        with self.assertRaises(Conflict):self.controller.respond({
            'ticket_id':shared['ticket']['id'],'revision':shared['revision']-1,
            'kind':'RESTATE_QUESTION','text':'New question'})
        self.assertEqual(self.calls,1)

    def test_changed_question_retains_a_provider_failure_without_reusing_old_findings(self):
        shared=self.findings()
        with patch.object(self.workspace.intake,'resolve',side_effect=RuntimeError('retained synthetic failure')):
            changed=self.controller.respond({'ticket_id':shared['ticket']['id'],'revision':shared['revision'],
                'kind':'RESTATE_QUESTION','text':'New question'})
        self.assertEqual(changed['ticket']['state'],'HELD')
        self.assertEqual(changed['ticket']['history'][-1]['detail']['message'],'retained synthetic failure')
        self.assertEqual(changed['ticket']['history'][-1]['detail']['exception_type'],'RuntimeError')
        self.assertNotIn('findings',changed['ticket']);self.assertNotIn('intake_id',changed['ticket'])
        self.assertEqual(len(changed['ticket']['question_versions']),1)
        self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_named_visual_content_does_not_ask_for_an_unmentioned_external_comparison(self):
        self.raw,self.payload=fixture('In Report, what does Global card Quantity show?',kind='VISUAL_CONTENT',
            triage='BUSINESS_QUESTION:NONE',visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        saved=self.submit()
        self.assertEqual(saved['ticket']['questions'],[])
        proposal=self.workspace.intake.get(saved['ticket']['intake_id'])['proposal']
        self.assertEqual(proposal['ticket_route']['route'],'DECLARED_SUBJECT')
        self.assertEqual(proposal['target_visual']['target_id'],'card')
        self.assertEqual(self.calls,1);self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_optional_fields_retain_original_request_and_exact_source_intervals(self):
        from investigator.ticket_inputs import document
        request={'text':'Check this.','request_key':'fields',
            'structured':{'number':'Global card Quantity shows 16.','report_page':'In Report.',
                          'comparison':'APPLICATION'}}
        derived=document(request)
        self.raw,self.payload=fixture(derived['text'],
            figures=[{'quote':'16','role':'PRIMARY','state':'NUMBER','precision_quote':None}],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        saved=self.controller.submit(request)
        self.assertEqual(saved['request'],request)
        self.assertEqual(saved['ticket']['input_document'],derived['provenance'])
        proposal=self.workspace.intake.get(saved['ticket']['intake_id'])['proposal']
        self.assertEqual(proposal['reported_figure']['value'],'16')
        self.assertEqual(proposal['target_visual']['target_id'],'card')
        self.assertEqual(self.calls,1);self.h.native.assert_not_called()

    def test_disabled_structured_comparison_refuses_before_model_or_ticket_write(self):
        self.controller.configuration['comparison_choices']=[{'route':'STALE','label':'Freshness'}]
        with self.assertRaisesRegex(ValueError,'not enabled'):
            self.controller.submit({'text':'Check Quantity.','request_key':'disabled',
                                    'structured':{'comparison':'APPLICATION'}})
        self.assertEqual(self.calls,0)

    def test_structured_comparison_still_requires_estate_confirmation(self):
        self.raw,self.payload=fixture('In Report, Global card Quantity differs.',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        self.controller.configuration['must_confirm']=['COMPARISON']
        saved=self.controller.submit({'text':self.payload['text'],'request_key':'required',
                                      'structured':{'comparison':'APPLICATION'}})
        self.assertEqual([q['field'] for q in saved['ticket']['questions']],['COMPARISON'])
        self.assertNotIn('COMPARISON',saved['ticket']['settled'])

    def test_conflicting_text_and_structured_comparisons_require_a_user_choice(self):
        self.raw,self.payload=fixture('In Report, Global card Quantity is stale.',kind='FRESHNESS',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        saved=self.controller.submit({'text':self.payload['text'],'request_key':'conflict',
                                      'structured':{'comparison':'APPLICATION'}})
        self.assertEqual([q['field'] for q in saved['ticket']['questions']],['COMPARISON'])
        self.assertNotIn('intake_id',saved['ticket'])
        self.assertNotIn('COMPARISON',saved['ticket']['settled'])
        self.h.native.assert_not_called()

    def test_optional_comparison_supplied_at_input_uses_its_own_provenance(self):
        self.raw,self.payload=fixture('In Report, Global card Quantity differs.',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        request={'text':self.payload['text'],'request_key':'structured',
                 'structured':{'comparison':'APPLICATION'}}
        saved=self.controller.submit(request)
        self.assertEqual(saved['request'],request);self.assertEqual(saved['ticket']['questions'],[])
        self.assertEqual(saved['ticket']['settled']['COMPARISON']['authority'],'USER_SUPPLIED_INPUT')
        self.assertNotIn('COMPARISON',saved['ticket']['confirmed'])
        proposal=self.workspace.intake.get(saved['ticket']['intake_id'])['proposal']
        self.assertEqual(proposal['ticket_route']['route'],'APPLICATION')
        self.assertEqual(proposal['ticket_route']['source_input_hash'],digest(request))
        self.assertEqual(self.calls,1);self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_user_can_hold_for_missing_information_and_resume_the_same_offer(self):
        saved=self.submit();request=self.reply(saved)
        unanswered=copy.deepcopy(request)
        unanswered['answers']=[{'question_id':a['question_id'],'unavailable':True} for a in request['answers']]
        unanswered['request_key']='missing-information'
        held=self.controller.reply(unanswered)
        self.assertEqual(held['ticket']['state'],'HELD')
        self.assertNotIn('intake_id',held['ticket'])
        self.assertEqual(held['ticket']['confirmed'],{})
        self.assertEqual(self.controller.reply(unanswered),held)
        request['revision']=held['revision'];request['request_key']='now-known'
        resumed=self.controller.reply(request)
        self.assertIn('intake_id',resumed['ticket']);self.assertEqual(resumed['ticket']['rounds'],1)
        self.assertEqual(self.calls,1);self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_named_definition_question_does_not_ask_for_an_external_comparator(self):
        self.raw,self.payload=fixture('In Report, explain Global card Quantity components.',
            kind='METRIC_COMPONENTS',visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        saved=self.submit();ticket=saved['ticket']
        self.assertEqual(ticket['questions'],[])
        adopted=self.workspace.intake.get(ticket['intake_id'])
        self.assertEqual(adopted['proposal']['ticket_route']['route'],'DECLARED_SUBJECT')
        self.assertEqual(adopted['proposal']['question_kind']['kind'],'METRIC_COMPONENTS')
        self.assertNotIn('COMPARISON',ticket['confirmed'])
        self.assertEqual(self.calls,1);self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_successful_extraction_survives_later_consumer_route_refusal(self):
        from investigator.question_kind import UnimplementedRoute
        self.raw,self.payload=fixture('In Report, Global card Quantity is stale.',kind='FRESHNESS',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        with patch('investigator.question_intake.question_kind.intake_route',
                   side_effect=UnimplementedRoute('A named procedure capability is unavailable.')):
            saved=self.submit()
        ticket=saved['ticket'];source=self.workspace.intake.get(ticket['source_intake'])
        self.assertEqual(source['error'],'UNIMPLEMENTED_ROUTE')
        self.assertEqual(source['resolver_extraction'],self.raw)
        self.assertEqual(source['retained_extraction'],self.raw)
        self.assertEqual(intake_extraction.retained_response(source),self.raw)
        self.assertIsNone(source.get('proposal'))
        self.assertEqual(ticket['state'],'HELD');self.assertEqual(ticket['questions'],[])
        self.assertEqual(ticket['history'][-1]['detail']['reason'],source['refusal_reason'])
        self.assertEqual(self.calls,1);self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_meaning_only_ticket_routes_to_declared_owner_without_fabricating_findings(self):
        self.raw,self.payload=fixture('In Report, Quantity: decide whether the business rule is correct.',
            kind='BUSINESS_MEANING',triage='BUSINESS_QUESTION:NONE')
        self.controller.ownership['business']=[{'measure_or_area':'measure','owner':'Operations owner'}]
        saved=self.submit();ticket=saved['ticket']
        self.assertEqual(ticket['state'],'BUSINESS_VALIDATION');self.assertEqual(ticket['questions'],[])
        self.assertEqual(ticket['handoff']['owner'],'Operations owner')
        self.assertEqual(ticket['handoff']['delivery'],'RECORDED_NOT_SENT')
        self.assertNotIn('findings',ticket);self.assertNotIn('figure',ticket['handoff'])
        self.assertEqual(self.workspace.intake.get(ticket['source_intake'])['error'],'UNIMPLEMENTED_ROUTE')
        self.assertEqual(self.calls,1);self.h.native.assert_not_called();self.h.source.assert_not_called()
        reply=self.controller.respond({'ticket_id':ticket['id'],'revision':saved['revision'],
            'kind':'DISPUTE','text':'The owner needs to review this rule.'})
        self.assertEqual(reply['ticket']['state'],'BUSINESS_VALIDATION')
        self.assertEqual(reply['ticket']['history'][-1]['detail']['technical_findings'],'NOT_OBTAINED')
        self.assertNotIn('findings',reply['ticket']);self.assertEqual(self.calls,1)

    def test_model_freshness_ticket_never_asks_for_absent_visual(self):
        self.raw,self.payload=fixture('In Report, Quantity may be stale. Check freshness.',kind='FRESHNESS')
        saved=self.submit();self.assertEqual(saved['ticket']['questions'],[])
        adopted=self.workspace.intake.get(saved['ticket']['intake_id'])
        self.assertNotIn('target_visual',adopted['proposal'])
        self.assertEqual(adopted['proposal']['ticket_route']['route'],'STALE')
        self.h.native.assert_not_called();self.assertEqual(self.calls,1)

    def test_checkable_text_takes_precedence_over_estate_policy_default(self):
        self.raw,self.payload=fixture('In Report, Global card Quantity looks wrong.',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        self.controller.configuration['default_route']='LOOKS_WRONG'
        saved=self.submit();ticket=saved['ticket']
        self.assertEqual(ticket['questions'],[]);self.assertNotIn('COMPARISON',ticket['confirmed'])
        self.assertEqual(ticket['settled']['COMPARISON']['authority'],'CODE_ESTABLISHED_REQUEST_COMPARISON')
        adopted=self.workspace.intake.get(ticket['intake_id'])
        self.assertEqual(adopted['proposal']['ticket_route']['version'],'ticket-comparison-request-v1')
        self.assertEqual(self.calls,1)

    def test_confirmed_keyed_cell_keeps_original_scope(self):
        self.raw,self.payload=fixture('In Report, warehouse North Quantity shows 17.',
            figures=[{'quote':'17','role':'PRIMARY','state':'NUMBER','precision_quote':None}],
            selections=[{'quote':'warehouse North','column':'warehouse','value':'North','role':'PRIMARY'}])
        saved=self.submit();request=self.reply(saved)
        q=next(q for q in saved['ticket']['questions'] if q['field']=='NUMBER')
        choice=next(c for c in q['choices'] if saved['ticket']['choice_values'][digest(q)+'/'+c['id']].get('mode')=='KEYED'
            )
        next(a for a in request['answers'] if a['question_id']==q['id'])['choice_id']=choice['id']
        resumed=self.controller.reply(request)
        adopted=self.workspace.intake.get(resumed['ticket']['intake_id'])
        self.assertEqual(adopted['proposal']['target_visual']['mode'],'KEYED')
        self.assertEqual(adopted['proposal']['filters'],[{'column_id':'warehouse','operator':'in','values':['North']}])
        self.assertEqual(self.calls,1);self.h.native.assert_not_called()

    def test_explicit_freshness_settles_without_comparison_question(self):
        self.raw,self.payload=fixture('In Report, Global card Quantity is stale.',kind='FRESHNESS',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        saved=self.submit()
        self.assertEqual(saved['ticket']['questions'],[])
        adopted=self.workspace.intake.get(saved['ticket']['intake_id'])
        self.assertEqual(adopted['proposal']['ticket_route']['route'],'STALE')
        self.assertEqual(self.calls,1);self.h.native.assert_not_called()

    def test_explicit_request_comparison_is_not_asked_again(self):
        self.raw,self.payload=fixture('In Report, Global card Quantity is stale.',kind='FRESHNESS',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        self.controller.configuration['must_confirm']=['COMPARISON']
        saved=self.submit()
        self.assertEqual(saved['ticket']['questions'],[])
        self.assertEqual(saved['ticket']['settled']['COMPARISON']['value']['route'],'STALE')
        self.assertTrue(any(e['detail'].get('reason')=='COMPARISON_ESTABLISHED_FROM_REQUEST'
            for e in saved['ticket']['history']))

    def test_current_producer_retries_nonverbatim_once_and_preserves_both_attempts(self):
        from investigator.question_intake import azure_resolve
        good,payload=fixture('In Report, Global card Quantity differs.',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        bad=copy.deepcopy(good);bad['measures'][0]['quote']='Invented metric'
        self.workspace.intake.resolver=azure_resolve
        with patch('ticket_planner.azure_generate',side_effect=[(bad,{}),(good,{})]) as provider:
            saved=self.workspace.intake.resolve({'text':payload['text'],'request_key':'exact-retry','parent_id':None},retain_extraction=True)
        self.assertEqual(saved['status'],'PROPOSED',saved)
        self.assertEqual(provider.call_count,2)
        self.assertEqual([a['event'] for a in saved['resolution_attempts']],
                         ['PROVENANCE_QUOTE_NOT_FOUND','PROVENANCE_QUOTE_RETRY'])
        self.assertEqual(saved['retained_extraction'],bad)
        self.assertEqual(intake_extraction.retained_response(saved),good)
        with patch('ticket_planner.azure_generate',side_effect=[(bad,{}),(bad,{})]) as provider:
            refused=self.workspace.intake.resolve({'text':payload['text'],'request_key':'double-bad','parent_id':None},retain_extraction=True)
        self.assertEqual(refused['status'],'NEEDS_INPUT');self.assertEqual(provider.call_count,2)
        self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_business_intent_refusal_is_not_reopened_as_visual_clarification(self):
        self.raw,self.payload=fixture('In Report, Quantity: decide whether the business rule is correct.',
            kind='BUSINESS_MEANING',triage='BUSINESS_QUESTION:NONE')
        saved=self.submit()
        self.assertEqual(saved['ticket']['state'],'HELD');self.assertEqual(saved['ticket']['questions'],[])
        self.assertEqual(saved['ticket']['history'][-1]['detail']['route'],'BUSINESS_VALIDATION')
        self.assertEqual(self.calls,1);self.h.native.assert_not_called();self.h.source.assert_not_called()

    def setUp(self):
        self.h=workspace_fixture.WorkspaceTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        self.workspace=self.h.workspace
        self.raw,self.payload=fixture('In Report, Quantity shows 17.',
            figures=[{'quote':'17','role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        self.catalog={'models':self.payload['models'],'versions':[]}
        self.calls=0
        def resolver(payload):
            self.calls+=1
            try:return intake_extraction.resolve(self.raw,payload),{'usage':None}
            except Exception as exc:
                exc.provider_metadata={'usage':None};exc.retained_extraction=copy.deepcopy(self.raw)
                raise
        self.workspace.intake.resolver=resolver
        patcher=patch('investigator.question_intake.snapshot',return_value=self.catalog)
        patcher.start();self.addCleanup(patcher.stop)
        # Controller uses the same catalog producer; patch its imported alias.
        patcher=patch('investigator.smart_intake.snapshot',return_value=self.catalog)
        patcher.start();self.addCleanup(patcher.stop)
        self.controller=SmartIntake(self.workspace)
        self.workspace._smart_intake=self.controller

    def submit(self):return self.controller.submit({'text':self.payload['text'],'request_key':'submit'})

    def reply(self,saved):
        t=saved['ticket'];answers=[]
        for question in t['questions']:
            choice=next(c for c in question['choices'] if (
                question['field']=='REPORT_PAGE' or
                question['field']=='COMPARISON' and t['choice_values'][digest(question)+'/'+c['id']]['route']=='APPLICATION' or
                question['field']=='NUMBER' and t['choice_values'][digest(question)+'/'+c['id']]['target_id']=='card' or
                question['field']=='FIGURE' and t['choice_values'][digest(question)+'/'+c['id']]['figure_source']['quote']=='17'))
            answers.append({'question_id':question['id'],'choice_id':choice['id']})
        return {'ticket_id':t['id'],'revision':saved['revision'],'answers':answers,'request_key':'reply'}

    def test_two_figures_are_settled_before_target_and_comparison_without_another_model_call(self):
        self.raw,self.payload=fixture('In Report, Quantity shows 16 and 17.',
            figures=[{'quote':v,'role':'PRIMARY','state':'NUMBER','precision_quote':None} for v in ('16','17')])
        first=self.submit()
        self.assertEqual([q['field'] for q in first['ticket']['questions']],['FIGURE'])
        second=self.controller.reply(self.reply(first))
        self.assertNotIn('intake_id',second['ticket'])
        self.assertEqual([q['field'] for q in second['ticket']['questions']],['NUMBER','COMPARISON'])
        request=self.reply(second);request['request_key']='target-and-comparison'
        final=self.controller.reply(request)
        proposal=self.workspace.intake.get(final['ticket']['intake_id'])['proposal']
        self.assertEqual(proposal['reported_figure']['value'],'17')
        self.assertEqual(proposal['target_visual']['target_id'],'card')
        self.assertEqual(final['ticket']['rounds'],2)
        self.assertEqual(self.calls,1)
        self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_one_batch_resumes_retained_extraction_without_another_call(self):
        saved=self.submit();self.assertEqual(saved['ticket']['state'],'CLARIFYING')
        self.assertEqual(saved['ticket']['rounds'],1);self.assertEqual(self.calls,1)
        request=self.reply(saved);before=self.h.agent.governor.snapshot()
        resumed=self.controller.reply(request)
        self.assertEqual(self.calls,1);self.assertEqual(self.h.agent.governor.snapshot(),before)
        adopted=self.workspace.intake.get(resumed['ticket']['intake_id'])
        self.assertEqual(adopted['proposal']['reported_figure']['value'],'17')
        self.assertEqual(adopted['proposal']['target_visual']['target_id'],'card')
        self.assertEqual(adopted['proposal']['ticket_route']['route'],'APPLICATION')
        self.assertEqual(adopted['provider_calls'],0)
        self.assertEqual(self.controller.reply(request),resumed)
        self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_public_reply_cannot_supply_a_scope_or_unoffered_choice(self):
        saved=self.submit();request=self.reply(saved)
        for change in ({'scope':{'target_id':'card'}},{'answers':[{'question_id':'number','choice_id':'invented'}]}):
            with self.subTest(change=change),self.assertRaises(ValueError):self.controller.reply({**request,**change})
        self.assertEqual(self.controller.tickets.get(saved['ticket']['id'])['revision'],saved['revision'])

    def test_changed_catalog_holds_and_no_query_is_dispatched(self):
        saved=self.submit();request=self.reply(saved)
        self.catalog['models'][0]['name']='Changed'
        resumed=self.controller.reply(request)
        self.assertEqual(resumed['ticket']['state'],'HELD')
        self.assertIn('metadata changed',resumed['ticket']['history'][-1]['detail']['reason'])
        self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_projected_installation_refuses_before_persisting_raw_ticket(self):
        self.workspace.agent.config['_estate']={'recording':{'tape_class':'PRIVACY_PROJECTED'}}
        from investigator.process_tape import TapeError
        with self.assertRaisesRegex(TapeError,'PRIVACY_PROJECTED_REQUIRES_ATOMIC'):self.submit()
        with self.workspace.store.connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM smart_tickets').fetchone()[0],0)

    def test_authenticated_api_batches_replies_and_retains_history(self):
        result=self.h.http('/api/workspace/tickets',{'text':self.payload['text'],'request_key':'submit'})
        self.assertTrue(result['status'].startswith('200'),result)
        saved=result['body'];request=self.reply(saved);identity=request.pop('ticket_id')
        replied=self.h.http('/api/workspace/tickets/'+identity+'/reply',request)
        self.assertTrue(replied['status'].startswith('200'),replied)
        self.assertIn('intake_id',replied['body']['ticket'])
        self.assertEqual(self.h.http('/api/workspace/tickets/'+identity)['body'],replied['body'])
        history=self.h.http('/api/workspace/tickets')['body']['tickets']
        self.assertEqual(history,[replied['body']]);self.assertEqual(self.calls,1)
        self.assertTrue(self.h.http('/api/workspace/tickets',token='wrong')['status'].startswith('401'))

    def test_api_rejects_extra_scope_and_stale_revision(self):
        saved=self.submit();request=self.reply(saved);identity=request.pop('ticket_id')
        self.assertTrue(self.h.http('/api/workspace/tickets/'+identity+'/reply',
            {**request,'scope':{'target_id':'card'}})['status'].startswith('400'))
        self.assertTrue(self.h.http('/api/workspace/tickets/'+identity+'/reply',
            {**request,'revision':0})['status'].startswith('409'))

    def findings(self,classification='CONSISTENT_TO_SOURCE',*,share=True):
        saved=self.controller.reply(self.reply(self.submit()))
        from test_ticket_findings import TicketFindingsTests
        state=TicketFindingsTests().state(classification)
        state['status']='COMPLETED'
        view={'intake':{'id':saved['ticket']['intake_id']}}
        patcher=patch.object(self.workspace,'session',return_value=view);patcher.start();self.addCleanup(patcher.stop)
        patcher=patch.object(self.workspace.agent,'get',return_value=state);patcher.start();self.addCleanup(patcher.stop)
        attached=self.controller.attach({'ticket_id':saved['ticket']['id'],'revision':saved['revision'],'session_id':'session'})
        return self.controller.share({'ticket_id':attached['ticket']['id'],'revision':attached['revision']}) if share else attached

    def test_findings_share_and_only_user_can_close(self):
        shared=self.findings();ticket=shared['ticket']
        self.assertEqual(ticket['state'],'FINDINGS_SHARED')
        self.assertEqual(ticket['findings']['question'],'Does this answer your question?')
        with self.assertRaises(ValueError):protocol.transition(ticket,'CLOSED',actor='AGENT',detail={})
        with self.assertRaises(ValueError):self.controller.close({'ticket_id':ticket['id'],'revision':shared['revision'],'actor':'AGENT'})
        closed=self.controller.close({'ticket_id':ticket['id'],'revision':shared['revision']})
        self.assertEqual(closed['ticket']['state'],'CLOSED')
        self.assertEqual(closed['ticket']['history'][-1]['actor'],'USER')
        self.assertEqual(self.calls,1);self.h.native.assert_not_called()

    def test_dispute_routes_to_configured_business_owner_without_new_read(self):
        shared=self.findings()
        self.controller.ownership={'business':[{'measure_or_area':'measure','owner':'measure-owner'}],'technical':[]}
        before=self.h.agent.governor.snapshot()
        result=self.controller.respond({'ticket_id':shared['ticket']['id'],'revision':shared['revision'],
            'kind':'DISPUTE','text':'I still disagree with the number.'})
        self.assertEqual(result['ticket']['state'],'BUSINESS_VALIDATION')
        self.assertEqual(result['ticket']['handoff']['owner'],'measure-owner')
        self.assertEqual(result['ticket']['handoff']['delivery'],'RECORDED_NOT_SENT')
        self.assertEqual(self.h.agent.governor.snapshot(),before);self.h.native.assert_not_called()

    def test_change_routes_to_technical_owner_and_historical_reply_is_qualified(self):
        shared=self.findings('TRANSFORMATION_LOGIC')
        self.controller.ownership={'business':[],'technical':[{'layer_or_pipeline':'layer-1','owner':'pipeline-team'}]}
        retained=self.controller.respond({'ticket_id':shared['ticket']['id'],'revision':shared['revision'],
            'kind':'EXPLAIN_RECORDED_RESULT','text':'Show me the retained explanation again.'})
        self.assertIn('not a new reading',retained['ticket']['retained_answer']['qualification'])
        result=self.controller.respond({'ticket_id':retained['ticket']['id'],'revision':retained['revision'],
            'kind':'REQUEST_CHANGE','text':'Please ask the owning team to change it.'})
        self.assertEqual(result['ticket']['state'],'TECH_HANDOFF')
        self.assertEqual(result['ticket']['handoff']['owner'],'pipeline-team')
        self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_missing_owner_keeps_findings_and_names_the_gap(self):
        shared=self.findings()
        result=self.controller.respond({'ticket_id':shared['ticket']['id'],'revision':shared['revision'],
            'kind':'DISPUTE','text':'I disagree.'})
        self.assertEqual(result['ticket']['state'],'FINDINGS_SHARED')
        self.assertEqual(result['ticket']['history'][-1]['detail']['handoff_unavailable'],'OWNERSHIP_UNDECLARED')

    def test_technical_cause_routes_on_sharing_without_waiting_for_another_question(self):
        self.controller.ownership={'business':[],'technical':[{'layer_or_pipeline':'layer-1','owner':'pipeline-team'}]}
        shared=self.findings('TRANSFORMATION_LOGIC')
        self.assertEqual(shared['ticket']['state'],'TECH_HANDOFF')
        self.assertEqual(shared['ticket']['handoff']['delivery'],'RECORDED_NOT_SENT')
        self.assertEqual(shared['ticket']['history'][-2]['to'],'FINDINGS_SHARED')
        self.assertEqual(shared['ticket']['history'][-1]['to'],'TECH_HANDOFF')
        retained=self.controller.respond({'ticket_id':shared['ticket']['id'],'revision':shared['revision'],
            'kind':'EXPLAIN_RECORDED_RESULT','text':'Explain the retained finding.'})
        self.assertEqual(retained['ticket']['state'],'TECH_HANDOFF')
        self.assertIn('not a new reading',retained['ticket']['retained_answer']['qualification'])
        self.h.native.assert_not_called();self.h.source.assert_not_called()

    def test_a_foreign_run_cannot_be_attached_to_the_ticket(self):
        saved=self.controller.reply(self.reply(self.submit()))
        with patch.object(self.workspace,'session',return_value={'intake':{'id':'foreign'}}),self.assertRaises(Conflict):
            self.controller.attach({'ticket_id':saved['ticket']['id'],'revision':saved['revision'],'session_id':'foreign'})

    def test_finish_reuses_completed_synthesis_and_never_recomposes(self):
        saved=self.findings(share=False)
        original=copy.deepcopy(self.workspace.agent.get.return_value['synthesis']['outputs'])
        with patch.object(self.workspace.agent,'synthesize',side_effect=AssertionError('Must not recompose')):
            finished=self.controller.finish({'ticket_id':saved['ticket']['id'],'revision':saved['revision']})
        self.assertEqual(finished['ticket']['state'],'FINDINGS_SHARED')
        self.assertEqual(finished['ticket']['findings']['outputs'],original)

    def test_finish_waits_for_running_work_without_spending(self):
        saved=self.findings(share=False)
        self.workspace.agent.get.return_value['status']='EXECUTING'
        with patch.object(self.workspace.agent,'synthesize',side_effect=AssertionError('Must not compose yet')),self.assertRaises(Conflict):
            self.controller.finish({'ticket_id':saved['ticket']['id'],'revision':saved['revision']})

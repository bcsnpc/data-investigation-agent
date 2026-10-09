import copy
import unittest
from unittest.mock import patch
from investigator.smart_intake import SmartIntake
from investigator import intake_extraction, ticket_protocol as protocol
from investigator.onboarding import digest, Conflict
from test_intake_extraction import fixture
import test_investigator_workspace as workspace_fixture


class SmartIntakeTests(unittest.TestCase):
    def setUp(self):
        self.h=workspace_fixture.WorkspaceTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        self.workspace=self.h.workspace
        self.raw,self.payload=fixture('In Report, Quantity shows 16 and 17.',
            figures=[{'quote':v,'role':'PRIMARY','state':'NUMBER','precision_quote':None} for v in ('16','17')])
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
                question['field']=='NUMBER' and t['choice_values'][digest(question)+'/'+c['id']]['target_id']=='card' and
                t['choice_values'][digest(question)+'/'+c['id']]['figure_source']['quote']=='17'))
            answers.append({'question_id':question['id'],'choice_id':choice['id']})
        return {'ticket_id':t['id'],'revision':saved['revision'],'answers':answers,'request_key':'reply'}

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

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

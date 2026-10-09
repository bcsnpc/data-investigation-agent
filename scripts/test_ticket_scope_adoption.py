import copy
import unittest
from unittest.mock import patch
from investigator import ticket_protocol as protocol, intake_confirmation
from investigator.ticket_state import Tickets
from investigator.question_intake import Intake
from investigator.onboarding import digest, encoded, Conflict
from test_intake_extraction import fixture
import test_investigator_workspace as workspace_fixture


class TicketScopeAdoptionTests(unittest.TestCase):
    def setUp(self):
        self.h=workspace_fixture.WorkspaceTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        self.owner=self.h.workspace;self.intake=self.owner.intake
        self.raw,self.payload=fixture('In Report, Quantity shows 16 and 17 for the same card.',
            figures=[{'quote':v,'role':'PRIMARY','state':'NUMBER','precision_quote':None} for v in ('16','17')])
        self.catalog={'models':self.payload['models'],'versions':[]}
        self.snap=patch('investigator.question_intake.snapshot',return_value=self.catalog);self.snap.start();self.addCleanup(self.snap.stop)
        source=self.intake._new_record({'request_key':'original'},self.payload['text'],self.catalog)
        source.update(status='NEEDS_INPUT',retained_extraction=self.raw)
        self.source=copy.deepcopy(source)
        with self.owner.store.connect() as db:
            db.execute('INSERT INTO workspace_intakes VALUES(?,?,?,?)',
                       (source['id'],'original',encoded(source),digest(source)))
        self.tickets=Tickets(self.owner.store)
        saved=self.tickets.submit({'text':self.payload['text']},'ticket')
        self.identity=saved['ticket']['id']
        from investigator.intake_extraction import spans
        selected=spans(self.raw,self.payload['text'])['figures'][0]['quote']
        values={'NUMBER':{'target_id':'card','mode':'UNGROUPED','figure_source':selected},
                'REPORT_PAGE':{'report_id':'report','page_id':None},
                'COMPARISON':{'route':'APPLICATION'}}
        questions=[{'id':f.lower(),'field':f,'question':'Choose '+f,
                    'choices':[{'id':'chosen','label':f+' choice','highlight':None}]} for f in protocol.FIELDS]
        def offer(t):
            t['source_intake']=source['id']
            return intake_confirmation.offer(t,questions,{digest(q)+'/chosen':values[q['field']] for q in questions},
                request_text=self.payload['text'],models=self.payload['models'])
        self.tickets.update(self.identity,0,offer)
        self.tickets.update(self.identity,1,lambda t:protocol.answer(t,[{'question_id':q['id'],'choice_id':'chosen'} for q in questions]))

    def request(self,record):
        return {k:copy.deepcopy(record['proposal'][k]) for k in ('model_id','measure_id','filters','dimension_ids')}|{
            'symptom':record['text'],'predecessor':None}

    def test_adoption_uses_existing_extraction_without_model_budget_or_data_reads(self):
        before=self.h.agent.governor.snapshot()
        saved=self.intake._adopt_ticket(self.identity,2,'adopt')
        self.assertEqual(saved['status'],'PROPOSED');self.assertEqual(saved['provider_calls'],0)
        self.assertEqual(saved['proposal']['reported_figure']['value'],'16')
        self.assertEqual(saved['proposal']['ticket_route']['route'],'APPLICATION')
        self.assertEqual(self.h.agent.governor.snapshot(),before)
        self.h.native.assert_not_called();self.h.source.assert_not_called();self.h.planner.assert_not_called()
        self.assertEqual(self.intake.get(self.source['id']),self.source)
        self.assertEqual(self.intake._adopt_ticket(self.identity,2,'adopt'),saved)
        reviewed=self.intake.review(saved['id'],self.request(saved))
        self.assertEqual(reviewed['provenance'],'SAVED_USER_CONFIRMED_SCOPE_PROPOSAL')

    def test_stale_revision_and_changed_context_cannot_adopt(self):
        with self.assertRaises(Conflict):self.intake._adopt_ticket(self.identity,1,'adopt')
        changed=copy.deepcopy(self.catalog);changed['models'][0]['name']='Changed'
        with patch('investigator.question_intake.snapshot',return_value=changed),self.assertRaises(Conflict):
            self.intake._adopt_ticket(self.identity,2,'adopt')

    def test_changing_a_decision_invalidates_its_old_scope_but_state_progress_does_not(self):
        saved=self.intake._adopt_ticket(self.identity,2,'adopt')
        self.tickets.update(self.identity,2,lambda t:protocol.transition(t,'INVESTIGATING',actor='AGENT',detail={}))
        self.intake.review(saved['id'],self.request(saved))
        def change(t):t['settled']['COMPARISON']['choice_id']='another';return t
        self.tickets.update(self.identity,3,change)
        with self.assertRaisesRegex(Conflict,'Ticket decisions changed'):self.intake.review(saved['id'],self.request(saved))


if __name__=='__main__':unittest.main()

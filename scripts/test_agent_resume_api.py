import unittest
from unittest.mock import patch, Mock
from investigator.agent_ticket import AgentTicket
from test_agent_ticket import AgentTicketTests


class AgentResumeApiTests(unittest.TestCase):
    def setUp(self):
        self.f = AgentTicketTests(); self.f.setUp(); self.addCleanup(self.f.doCleanups)
        self.workspace = self.f.workspace
        self.http = self.f.fixture.f.helper.h.http

    def test_authentication_closed_shape_and_pipeline_gate(self):
        path = '/api/workspace/tickets/'+self.f.saved['ticket']['id']+'/agent-resume'
        with patch('investigator.agent_ticket.AgentTicket.resume') as resume:
            self.assertTrue(self.http(path,{'revision':0,'comment_id':'reply'},token='wrong')['status'].startswith('401'))
            self.assertTrue(self.http(path,{'revision':0,'comment_id':'reply','text':'invented'})['status'].startswith('400'))
            self.assertTrue(self.http(path,{'revision':True,'comment_id':'reply'})['status'].startswith('400'))
            self.workspace.agent.config['_estate']['investigation']['mode'] = 'PIPELINE'
            self.assertTrue(self.http(path,{'revision':0,'comment_id':'reply'})['status'].startswith('409'))
            resume.assert_not_called()

    def test_endpoint_requires_actual_retained_reply(self):
        self.f.decisions([{'action':'TOOL','summary':'Ask target','tool':'ask_user','arguments':{'field':'SELECTION'}}])
        waiting = AgentTicket(self.workspace).run(self.f.saved)
        path = '/api/workspace/tickets/'+waiting['ticket']['id']+'/agent-resume'
        result = self.http(path,{'revision':waiting['revision'],'comment_id':'fabricated'})
        self.assertTrue(result['status'].startswith('409'),result)

    def test_real_public_comment_then_resume_continues_same_bounded_loop(self):
        self.workspace.agent.config['_estate']['investigation']['step_cap'] = 2
        decisions = self.f.decisions([{'action':'TOOL','summary':'Ask target','tool':'ask_user','arguments':{'field':'SELECTION'}},self.f.hold()])
        waiting = AgentTicket(self.workspace).run(self.f.saved)
        prefix = '/api/workspace/tickets/'+waiting['ticket']['id']
        posted = self.http(prefix+'/comments',{'revision':waiting['revision'],'request_key':'real-api-reply','text':'The Global card.','attachment_id':None,'review_id':None})
        self.assertTrue(posted['status'].startswith('200'),posted)
        continued = self.http(prefix+'/agent-resume',{'revision':posted['body']['revision'],'comment_id':'real-api-reply'})
        self.assertTrue(continued['status'].startswith('200'),continued)
        self.assertEqual(continued['body']['ticket']['agent_loop']['status'],'HELD')
        self.assertEqual(decisions.call_count,2)
        self.assertEqual(decisions.call_args.args[0]['steps_remaining'],1)
        self.f.fixture.f.helper.h.native.assert_not_called(); self.f.fixture.f.helper.h.source.assert_not_called()


if __name__ == '__main__':unittest.main()

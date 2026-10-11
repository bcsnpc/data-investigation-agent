import copy
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

    def hybrid_waiting(self):
        from investigator.onboarding import digest
        self.workspace.agent.config['_estate']['investigation'].update(mode='HYBRID', step_cap=2)
        parent = {'saved_ticket': copy.deepcopy(self.f.saved), 'intake': None, 'session': None,
                  'gap': {'reason': 'TARGET_UNRESOLVED'}}
        parent['hash'] = digest(parent)
        def retain(ticket):
            ticket['hybrid_pipeline'] = copy.deepcopy(parent)
            return ticket
        saved = self.workspace.smart_intake.tickets.update(self.f.saved['ticket']['id'], self.f.saved['revision'], retain)
        decisions = self.f.decisions([{'action': 'TOOL', 'summary': 'Ask target', 'tool': 'ask_user',
                                      'arguments': {'field': 'SELECTION'}}, self.f.hold()])
        waiting = AgentTicket(self.workspace).run(saved, pipeline_result=parent)
        self.assertEqual(waiting['ticket']['agent_loop']['status'], 'WAITING_FOR_USER')
        return waiting, parent, decisions

    def test_hybrid_public_comment_resume_keeps_pipeline_authority_and_budget(self):
        waiting, parent, decisions = self.hybrid_waiting()
        prefix = '/api/workspace/tickets/' + waiting['ticket']['id']
        posted = self.http(prefix + '/comments', {'revision': waiting['revision'], 'request_key': 'hybrid-author-reply',
            'text': 'The Global card.', 'attachment_id': None, 'review_id': None})
        self.assertTrue(posted['status'].startswith('200'), posted)
        continued = self.http(prefix + '/agent-resume', {'revision': posted['body']['revision'], 'comment_id': 'hybrid-author-reply'})
        self.assertTrue(continued['status'].startswith('200'), continued)
        ticket = continued['body']['ticket']
        self.assertEqual(ticket['hybrid_pipeline'], parent)
        self.assertEqual(ticket['investigation_mode'], 'HYBRID')
        self.assertEqual(ticket['agent_consumed_replies'], ['hybrid-author-reply'])
        self.assertEqual(ticket['agent_loop']['status'], 'HELD')
        self.assertEqual(decisions.call_count, 2)
        self.assertEqual(decisions.call_args.args[0]['steps_remaining'], 1)
        self.f.fixture.f.helper.h.native.assert_not_called(); self.f.fixture.f.helper.h.source.assert_not_called()

    def test_hybrid_fabricated_stale_or_agent_authored_reply_is_refused(self):
        from investigator.ticket_comments import append
        waiting, _, decisions = self.hybrid_waiting()
        path = '/api/workspace/tickets/' + waiting['ticket']['id'] + '/agent-resume'
        for revision, identity in ((waiting['revision'], 'fabricated'), (waiting['revision'] - 1, 'fabricated')):
            result = self.http(path, {'revision': revision, 'comment_id': identity})
            self.assertTrue(result['status'].startswith('409'), result)
        agent_comment = append(self.workspace, {'ticket_id': waiting['ticket']['id'], 'revision': waiting['revision'],
            'request_key': 'not-a-user', 'text': 'The Global card.', 'attachment_id': None, 'review_id': None}, actor='AGENT')
        result = self.http(path, {'revision': agent_comment['revision'], 'comment_id': 'not-a-user'})
        self.assertTrue(result['status'].startswith('409'), result)
        self.assertEqual(decisions.call_count, 1)

    def test_hybrid_terminal_hold_is_not_reopened_by_comment(self):
        waiting, _, decisions = self.hybrid_waiting()
        tickets = self.workspace.smart_intake.tickets
        def terminal(ticket):
            ticket['agent_loop']['status'] = 'HELD'
            return ticket
        held = tickets.update(waiting['ticket']['id'], waiting['revision'], terminal)
        prefix = '/api/workspace/tickets/' + held['ticket']['id']
        posted = self.http(prefix + '/comments', {'revision': held['revision'], 'request_key': 'terminal-note',
            'text': 'The Global card.', 'attachment_id': None, 'review_id': None})
        result = self.http(prefix + '/agent-resume', {'revision': posted['body']['revision'], 'comment_id': 'terminal-note'})
        self.assertTrue(result['status'].startswith('409'), result)
        self.assertEqual(decisions.call_count, 1)

    def test_hybrid_consumed_reply_or_reply_before_question_cannot_continue(self):
        waiting, _, decisions = self.hybrid_waiting()
        tickets = self.workspace.smart_intake.tickets
        def old_reply(ticket):
            ticket['comments'].insert(0, {'id': 'old-user-reply', 'actor': 'USER', 'text': 'The Global card.'})
            return ticket
        saved = tickets.update(waiting['ticket']['id'], waiting['revision'], old_reply)
        prefix = '/api/workspace/tickets/' + saved['ticket']['id']
        result = self.http(prefix + '/agent-resume', {'revision': saved['revision'], 'comment_id': 'old-user-reply'})
        self.assertTrue(result['status'].startswith('409'), result)
        posted = self.http(prefix + '/comments', {'revision': saved['revision'], 'request_key': 'consumed-user-reply',
            'text': 'The Global card.', 'attachment_id': None, 'review_id': None})
        def consumed(ticket):
            ticket['agent_consumed_replies'] = ['consumed-user-reply']
            return ticket
        saved = tickets.update(saved['ticket']['id'], posted['body']['revision'], consumed)
        result = self.http(prefix + '/agent-resume', {'revision': saved['revision'], 'comment_id': 'consumed-user-reply'})
        self.assertTrue(result['status'].startswith('409'), result)
        self.assertEqual(decisions.call_count, 1)

    def test_long_human_wait_preserves_900_active_seconds_and_cumulative_steps(self):
        waiting, _, decisions = self.hybrid_waiting()
        self.f.fixture.f.helper.h.clock.return_value = 10000
        prefix = '/api/workspace/tickets/' + waiting['ticket']['id']
        posted = self.http(prefix + '/comments', {'revision': waiting['revision'], 'request_key': 'hours-later',
            'text': 'The Global card.', 'attachment_id': None, 'review_id': None})
        self.f.fixture.f.helper.h.clock.return_value = 10005
        result = self.http(prefix + '/agent-resume', {'revision': posted['body']['revision'], 'comment_id': 'hours-later'})
        self.assertTrue(result['status'].startswith('200'), result)
        ticket = result['body']['ticket']
        self.assertEqual(ticket['agent_loop']['reason'], 'UNRESOLVED')
        self.assertEqual(ticket['agent_loop_started_at'], 1000)
        self.assertEqual(ticket['agent_wait_pauses'][0]['seconds'], 9000)
        from investigator import agent_ticket
        self.assertEqual(agent_ticket.GovernedDecision.call_args.kwargs['deadline'], 10900)
        self.assertEqual(decisions.call_count, 2)
        self.assertEqual(decisions.call_args.args[0]['steps_remaining'], 1)

    def test_active_time_after_reply_still_holds_at_900(self):
        waiting, _, decisions = self.hybrid_waiting()
        self.f.fixture.f.helper.h.clock.return_value = 10000
        prefix = '/api/workspace/tickets/' + waiting['ticket']['id']
        posted = self.http(prefix + '/comments', {'revision': waiting['revision'], 'request_key': 'active-deadline',
            'text': 'The Global card.', 'attachment_id': None, 'review_id': None})
        self.f.fixture.f.helper.h.clock.return_value = 10901
        result = self.http(prefix + '/agent-resume', {'revision': posted['body']['revision'], 'comment_id': 'active-deadline'})
        self.assertTrue(result['status'].startswith('200'), result)
        self.assertEqual(result['body']['ticket']['agent_loop']['reason'], 'AGENT_WALL_LIMIT')
        self.assertEqual(decisions.call_count, 1)


if __name__ == '__main__':unittest.main()

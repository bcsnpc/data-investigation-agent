import copy
from datetime import datetime, timezone
import unittest
from investigator.agent_wait_time import interval, total
from investigator.onboarding import Conflict


def iso(at): return datetime.fromtimestamp(at, timezone.utc).isoformat()


class HumanWaitTests(unittest.TestCase):
    def setUp(self):
        self.result = {'status': 'WAITING_FOR_USER', 'comment_id': 'question'}
        self.loop = {'status': 'WAITING_FOR_USER', 'transcript': [
            {'event': 'TOOL_RESULT', 'receipt_id': 'receipt', 'result': self.result}]}
        self.ticket = {'comments': [{'id': 'question', 'actor': 'AGENT', 'created': iso(1000)},
                                   {'id': 'reply', 'actor': 'USER', 'created': iso(10000)}]}
        self.journal = [{'id': 'receipt', 'event': 'TOOL_RESULT', 'at': 1001,
                         'detail': {'result': self.result}}]

    def test_only_real_human_wait_is_excluded(self):
        pause = interval(self.ticket, self.loop, 'reply', self.journal, now=10005)
        self.assertEqual(pause['seconds'], 8999)
        self.ticket.update(agent_loop_history=[self.loop], agent_wait_pauses=[pause])
        self.assertEqual(total(self.ticket, self.journal, now=10005), 8999)
        self.assertEqual(10005 - 990 - total(self.ticket, self.journal, now=10005), 16)

    def test_terminal_hold_cannot_pause(self):
        self.loop['status'] = 'HELD'
        with self.assertRaises(Conflict): interval(self.ticket, self.loop, 'reply', self.journal, now=10005)

    def test_missing_timestamp_or_original_wait_receipt_refuses(self):
        with self.assertRaises(Conflict): interval(self.ticket, self.loop, 'reply', [], now=10005)
        del self.ticket['comments'][1]['created']
        with self.assertRaises(Conflict): interval(self.ticket, self.loop, 'reply', self.journal, now=10005)

    def test_future_reversed_or_non_user_reply_cannot_pause(self):
        for created, actor in ((iso(10006), 'USER'), (iso(999), 'USER'), (iso(10000), 'AGENT')):
            self.ticket['comments'][1].update(created=created, actor=actor)
            with self.assertRaises(Conflict): interval(self.ticket, self.loop, 'reply', self.journal, now=10005)

    def test_changed_duration_or_double_counted_reply_refuses(self):
        pause = interval(self.ticket, self.loop, 'reply', self.journal, now=10005)
        self.ticket.update(agent_loop_history=[self.loop], agent_wait_pauses=[dict(pause, seconds=100000)])
        with self.assertRaises(Conflict): total(self.ticket, self.journal, now=10005)
        self.ticket['agent_wait_pauses'] = [pause, copy.deepcopy(pause)]
        with self.assertRaises(Conflict): total(self.ticket, self.journal, now=10005)

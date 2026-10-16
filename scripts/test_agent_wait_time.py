import copy
from datetime import datetime, timezone
import unittest
from investigator.agent_wait_time import interval, total,queued_reply
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

    def queue(self,now):
        human=interval(self.ticket,self.loop,'reply',self.journal,now=now)
        queue=queued_reply(self.ticket,self.loop,'reply',self.journal,now=now)
        self.journal.append({'id':'consumed','event':'QUEUED_REPLY_WAIT_EXCLUDED','at':now,'detail':{'pause':copy.deepcopy(queue)}})
        queue['receipt_id']='consumed'
        self.ticket.update(agent_loop_history=[self.loop],agent_wait_pauses=[human],
            agent_reply_queue_pauses=[queue],agent_consumed_replies=['reply'])
        return queue

    def test_recorded_reply_waiting_for_worker_does_not_consume_active_wall(self):
        self.queue(23040)
        self.assertEqual(total(self.ticket,self.journal,now=23040),22039)
        self.assertEqual(23040-990-total(self.ticket,self.journal,now=23040),11)
        self.assertEqual(total(self.ticket,self.journal,now=23045),22039)
        self.assertEqual(self.ticket['comments'][1]['created'],iso(10000))

    def test_queue_without_consumption_receipt_or_with_activity_refuses(self):
        self.queue(23040);original=copy.deepcopy(self.journal)
        self.journal.pop()
        with self.assertRaisesRegex(Conflict,'consumption receipt'):total(self.ticket,self.journal,now=23040)
        self.journal=original+[{'id':'work','event':'DECISION','at':15000}]
        with self.assertRaisesRegex(Conflict,'active agent work'):total(self.ticket,self.journal,now=23040)

    def test_queue_cannot_extend_or_count_a_reply_twice(self):
        queue=self.queue(23040);queue['seconds']+=1
        with self.assertRaises(Conflict):total(self.ticket,self.journal,now=23040)
        queue['seconds']-=1;self.ticket['agent_reply_queue_pauses'].append(copy.deepcopy(queue))
        with self.assertRaisesRegex(Conflict,'unique consumed'):total(self.ticket,self.journal,now=23040)

    def test_historical_hybrid_timestamps_preserve_204_seconds_of_prior_work(self):
        started=1791751159.3428476;waiting=1791751364.024605;reply=1791773568.631943;consumed=1791786609.3091953
        self.ticket['comments'][0]['created']='2026-10-11T20:42:43.974572+00:00'
        self.ticket['comments'][1]['created']='2026-10-12T02:52:48.631943+00:00'
        self.journal[0]['at']=waiting
        self.queue(consumed)
        active=consumed-started-total(self.ticket,self.journal,now=consumed)
        self.assertAlmostEqual(active,204.68175745010376,places=5)
        self.assertEqual(int(900-active),695)
        self.assertEqual(self.ticket['agent_wait_pauses'][0]['replied_at'],'2026-10-12T02:52:48.631943+00:00')

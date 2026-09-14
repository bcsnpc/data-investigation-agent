from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import unittest
import test_github_issue_adapter as fixtures
from email_delivery_adapter import EmailAdapter
from routing_drafts import save
from ticket_workflow import Conflict


class EmailTests(unittest.TestCase):
    def setUp(self):
        self.response = lambda: fixtures.GithubTests.response(self)
        fixtures.GithubTests.setUp(self)
        self.sent = []
        self.refused = {}
        def send(message, **kwargs):
            self.sent.append((message, kwargs))
            if isinstance(self.refused, Exception): raise self.refused
            return self.refused
        self.email = EmailAdapter(self.review, SimpleNamespace(send_message=send))
        self.sender = 'investigator@example.invalid'

    def ready(self):
        self.adapter.create_issue(self.identity, authorized_hash=self.hash)
        return self.email.preview(self.identity, authorized_hash=self.hash, sender=self.sender)

    def send(self, preview):
        return self.email.send(self.identity, authorized_hash=self.hash, sender=self.sender,
                               authorized_envelope_hash=preview['envelope_hash'])

    def test_issue_receipt_required(self):
        with self.assertRaises(Conflict): self.email.preview(self.identity, authorized_hash=self.hash, sender=self.sender)
        self.assertEqual(self.sent, [])

    def test_exact_content_acceptance_and_no_resend(self):
        preview = self.ready(); result = self.send(preview)
        self.assertEqual(result, self.send(preview)); self.assertEqual(len(self.sent), 1)
        message, kwargs = self.sent[0]
        self.assertEqual(message['From'], self.sender)
        self.assertEqual(message['Subject'], preview['envelope']['subject'])
        self.assertEqual(message.get_content().rstrip('\n'), preview['envelope']['body'].rstrip('\n'))
        self.assertEqual(kwargs['to_addrs'], preview['envelope']['recipients'])
        self.assertEqual(result['state'], 'ACCEPTED'); self.assertFalse(result['delivery_confirmed'])

    def test_changed_sender_or_policy_blocked(self):
        preview = self.ready(); self.sender = 'changed@example.invalid'
        with self.assertRaises(Conflict): self.send(preview)
        self.sender = 'investigator@example.invalid'; self.policy['owners'][0]['team'] = 'Changed'
        with self.assertRaises(Conflict): self.send(preview)
        self.assertEqual(self.sent, [])

    def test_timeout_is_held_and_redacted(self):
        preview = self.ready(); self.refused = TimeoutError('private-provider-details')
        with self.assertRaises(Conflict) as error: self.send(preview)
        self.assertNotIn('private-provider-details', str(error.exception))
        with self.assertRaises(Conflict): self.send(preview)
        self.assertEqual(len(self.sent), 1)

    def test_refusal_has_no_automatic_retry(self):
        preview = self.ready(); self.refused = {'triage@example.invalid': (550, b'private-response')}
        result = self.send(preview)
        self.assertEqual(result['state'], 'REFUSED'); self.assertNotIn('private-response', str(result))
        with self.assertRaises(Conflict): self.send(preview)
        self.assertEqual(len(self.sent), 1)

    def test_partial_acceptance_is_held_without_resending(self):
        self.policy['owners'][0]['destination']['notification']['recipients'].append('other@example.invalid')
        self.record = save(self.store, self.item, self.policy)
        self.identity = self.record['id']; self.hash = self.review.detail(self.identity)['draft_hash']
        self.issue = self.record['draft']['destination_preview']['issue']
        self.review.approve(self.identity, self.hash)
        preview = self.ready(); self.refused = {'other@example.invalid': (550, b'refused')}
        result = self.send(preview)
        self.assertEqual(result['state'], 'PARTIAL')
        self.assertEqual(result['accepted_recipients'], ['triage@example.invalid'])
        with self.assertRaises(Conflict): self.send(preview)
        self.assertEqual(len(self.sent), 1)

    def test_sender_header_injection_rejected(self):
        self.ready()
        with self.assertRaises(ValueError):
            self.email.preview(self.identity, authorized_hash=self.hash, sender='x@example.invalid\r\nBcc: y@example.invalid')
        self.assertEqual(self.sent, [])

    def test_concurrent_senders_only_send_once(self):
        preview = self.ready()
        def run(_):
            try: return self.send(preview)
            except Conflict: return None
        with ThreadPoolExecutor(4) as pool: list(pool.map(run, range(4)))
        self.assertEqual(len(self.sent), 1)


if __name__ == '__main__': unittest.main()

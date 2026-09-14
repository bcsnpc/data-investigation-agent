from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
from pathlib import Path
import subprocess
import sys
import unittest
import test_email_delivery_adapter as fixtures
from envelope_workflow import EnvelopeWorkflow
from ticket_workflow import Conflict


class EnvelopeTests(unittest.TestCase):
    def setUp(self):
        fixtures.EmailTests.setUp(self)
        self.adapter.create_issue(self.identity, authorized_hash=self.hash)
        self.flow = EnvelopeWorkflow(self.email)
        self.detail = self.flow.prepare(self.identity, authorized_hash=self.hash, sender=self.sender)
        self.key = self.detail['preview']['envelope_hash']

    def test_prepare_and_approval_are_idempotent(self):
        self.assertEqual(self.detail, self.flow.prepare(self.identity, authorized_hash=self.hash, sender=self.sender))
        with self.assertRaises(Conflict): self.flow.approve(self.key)
        first = self.flow.approve(self.key, confirm=True)
        self.assertEqual(first['approval'], self.flow.approve(self.key, confirm=True)['approval'])
        self.assertEqual(self.sent, [])

    def test_default_disabled_and_approval_required(self):
        with self.assertRaises(Conflict): self.flow.execute(self.key)
        enabled = EnvelopeWorkflow(self.email, delivery_enabled=True)
        with self.assertRaises(Conflict): enabled.execute(self.key)
        self.assertEqual(self.sent, [])

    def test_approved_execution_uses_adapter_and_is_idempotent(self):
        self.flow.approve(self.key, confirm=True)
        enabled = EnvelopeWorkflow(self.email, delivery_enabled=True)
        result = enabled.execute(self.key)
        self.assertEqual(result['attempt']['state'], 'ACCEPTED')
        self.assertFalse(result['delivery_confirmed'])
        enabled.execute(self.key); self.assertEqual(len(self.sent), 1)

    def test_changed_receipt_or_policy_blocks_execution(self):
        self.flow.approve(self.key, confirm=True)
        with closing(self.store.connect()) as db:
            row = db.execute('SELECT receipt FROM github_issue_attempts WHERE draft_id=?', (self.identity,)).fetchone()
            receipt = json.loads(row[0]); receipt['number'] = 2; receipt['url'] = receipt['url'][:-1] + '2'
            db.execute('UPDATE github_issue_attempts SET receipt=? WHERE draft_id=?', (json.dumps(receipt), self.identity)); db.commit()
        with self.assertRaises(Conflict): EnvelopeWorkflow(self.email, delivery_enabled=True).execute(self.key)
        self.policy['owners'][0]['team'] = 'Changed'
        with self.assertRaises(Conflict): self.flow.approve(self.key, confirm=True)
        self.assertEqual(self.sent, [])

    def test_timeout_remains_visible_after_restart(self):
        self.flow.approve(self.key, confirm=True); self.refused = TimeoutError()
        with self.assertRaises(Conflict): EnvelopeWorkflow(self.email, delivery_enabled=True).execute(self.key)
        restarted = EnvelopeWorkflow(self.email, delivery_enabled=True)
        self.assertEqual(restarted.detail(self.key)['attempt']['state'], 'UNCERTAIN')
        with self.assertRaises(Conflict): restarted.execute(self.key)
        self.assertEqual(len(self.sent), 1)

    def test_concurrent_approval_has_one_timestamp(self):
        with ThreadPoolExecutor(3) as pool:
            rows = list(pool.map(lambda _: self.flow.approve(self.key, confirm=True), range(3)))
        self.assertTrue(all(row['approval'] == rows[0]['approval'] for row in rows))

    def test_cli_approval_and_status_do_not_send(self):
        folder = Path(self.temp.name); policy = folder / 'policy.json'; policy.write_text(json.dumps(self.policy))
        common = [sys.executable, str(Path(__file__).with_name('envelope_workflow.py')), '--workflow', str(folder/'review.sqlite'),
                  '--evidence', str(folder/'evidence.sqlite'), '--ownership', str(policy), '--envelope-hash', self.key]
        for action in ('approve', 'status'):
            result = subprocess.run(common + [action, '--confirm'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout); self.assertIsNotNone(data['approval']); self.assertFalse(data['delivery_enabled'])
        self.assertEqual(self.sent, [])


if __name__ == '__main__': unittest.main()

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
from pathlib import Path
import subprocess
import sys
import unittest
import test_routing_review as fixtures
from routing_delivery_rehearsal import DeliveryRehearsal
from ticket_workflow import Conflict


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        fixtures.ReviewTests.setUp(self)
        self.identity = self.record['id']
        self.delivery = DeliveryRehearsal(self.review)

    def approved(self):
        self.review.approve(self.identity, self.review.detail(self.identity)['draft_hash'])
        return self.delivery.enqueue(self.identity)

    def test_approval_required(self):
        with self.assertRaises(Conflict):
            self.delivery.enqueue(self.identity)

    def test_stages_are_ordered_idempotent_and_local(self):
        first = self.approved()
        self.assertEqual(first, self.delivery.enqueue(self.identity))
        result = self.delivery.advance(self.identity)
        self.assertEqual([s['state'] for s in result['steps']], ['SUCCEEDED', 'PENDING'])
        result = self.delivery.advance(self.identity)
        self.assertTrue(result['complete'])
        self.assertFalse(result['external_delivery'])
        self.assertEqual(result, self.delivery.advance(self.identity))
        with closing(self.store.connect()) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM routing_rehearsal_receipts').fetchone()[0], 2)
            payload = json.loads(db.execute("SELECT payload FROM routing_rehearsal_steps WHERE stage='notification'").fetchone()[0])
            self.assertEqual(payload['issue_reference']['stage'], 'issue')

    def test_interruption_survives_restart_without_replay(self):
        self.approved()
        state = self.delivery.advance(self.identity, interrupt_after_receipt=True)
        self.assertEqual(state['steps'][0]['state'], 'UNCERTAIN')
        restarted = DeliveryRehearsal(self.review)
        with self.assertRaises(Conflict):
            restarted.advance(self.identity)
        restarted.reconcile(self.identity)
        self.assertTrue(restarted.advance(self.identity)['complete'])

    def test_notification_interruption_does_not_recreate_issue(self):
        self.approved(); self.delivery.advance(self.identity)
        self.delivery.advance(self.identity, interrupt_after_receipt=True)
        self.assertTrue(self.delivery.reconcile(self.identity)['complete'])
        with closing(self.store.connect()) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM routing_rehearsal_receipts').fetchone()[0], 2)

    def test_absent_or_mismatched_receipt_stays_held(self):
        self.approved(); self.delivery.advance(self.identity, interrupt_after_receipt=True)
        with closing(self.store.connect()) as db:
            db.execute("UPDATE routing_rehearsal_receipts SET payload_hash='wrong'"); db.commit()
        with self.assertRaises(Conflict):
            self.delivery.reconcile(self.identity)
        with closing(self.store.connect()) as db:
            db.execute('DELETE FROM routing_rehearsal_receipts'); db.commit()
        with self.assertRaises(Conflict):
            self.delivery.reconcile(self.identity)
        self.assertEqual(self.delivery.status(self.identity)['steps'][0]['state'], 'UNCERTAIN')

    def test_changed_owner_or_evidence_blocks_each_stage(self):
        self.approved(); self.delivery.advance(self.identity)
        self.policy['owners'][0]['team'] = 'Changed'
        with self.assertRaises(Conflict):
            self.delivery.advance(self.identity)
        self.policy['owners'][0]['team'] = 'Fixture Data Team'
        self.item['result']['root_cause'] = 'Changed'
        with self.assertRaises(Conflict):
            self.delivery.advance(self.identity)
        self.assertFalse(self.delivery.status(self.identity)['complete'])

    def test_cli_rehearsal_and_recovery(self):
        self.approved()
        folder = Path(self.temp.name)
        policy = folder / 'ownership.json'
        policy.write_text(json.dumps(self.policy))
        common = [sys.executable, str(Path(__file__).with_name('routing_delivery_rehearsal.py')),
                  '--draft-id', self.identity, '--workflow', str(folder / 'review.sqlite'),
                  '--evidence', str(folder / 'evidence.sqlite'), '--ownership', str(policy)]
        def call(action, *flags):
            result = subprocess.run(common + [action, *flags], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertEqual(call('advance', '--interrupt-after-receipt')['steps'][0]['state'], 'UNCERTAIN')
        self.assertFalse(call('reconcile')['complete'])
        self.assertTrue(call('advance')['complete'])
        self.assertFalse(call('status')['external_delivery'])

    def test_concurrent_workers_do_not_duplicate_receipts(self):
        self.approved()
        def run(_):
            try: self.delivery.advance(self.identity)
            except Conflict: pass
        with ThreadPoolExecutor(4) as pool:
            list(pool.map(run, range(4)))
        with closing(self.store.connect()) as db:
            count = db.execute('SELECT COUNT(*) FROM routing_rehearsal_receipts').fetchone()[0]
        self.assertIn(count, (1, 2))
        self.assertTrue(self.delivery.advance(self.identity)['complete'])


if __name__ == '__main__':
    unittest.main()

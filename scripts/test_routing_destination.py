from copy import deepcopy
from contextlib import closing
import json
import unittest
import test_routing_review as fixtures
from routing_destination import validate_destination
from routing_drafts import save
from routing_delivery_rehearsal import DeliveryRehearsal
from ticket_workflow import Conflict


def destination():
    return {'issue': {'provider': 'github', 'repository': 'fixture-org/fixture-issues'},
            'notification': {'provider': 'email', 'recipients': ['triage@example.invalid']}}


class DestinationTests(unittest.TestCase):
    def setUp(self):
        fixtures.ReviewTests.setUp(self)

    def configured(self):
        self.policy['owners'][0]['destination'] = destination()
        return save(self.store, self.item, self.policy)

    def test_legacy_draft_has_no_destination(self):
        self.assertNotIn('destination_preview', self.record['draft'])

    def test_preview_is_explicit_deterministic_and_bound(self):
        record = self.configured()
        preview = record['draft']['destination_preview']
        self.assertEqual(record, save(self.store, self.item, self.policy))
        self.assertNotEqual(record['id'], self.record['id'])
        self.assertEqual(preview['issue']['repository'], 'fixture-org/fixture-issues')
        self.assertEqual(preview['notification']['recipients'], ['triage@example.invalid'])
        self.assertIn('-99.0000', preview['issue']['body'])
        self.assertIn(record['draft']['scope'], preview['notification']['body'])
        self.assertFalse(preview['external_delivery_enabled'])
        self.assertIn('local paths', preview['limitation'])

    def test_destination_change_requires_new_review(self):
        record = self.configured()
        old_hash = self.review.detail(record['id'])['draft_hash']
        self.review.approve(record['id'], old_hash)
        self.policy['owners'][0]['destination']['notification']['recipients'] = ['another@example.invalid']
        with self.assertRaises(Conflict): self.review.approve(record['id'], old_hash)
        with self.assertRaises(Conflict): DeliveryRehearsal(self.review).enqueue(record['id'])
        new = save(self.store, self.item, self.policy)
        self.assertNotEqual(record['id'], new['id'])
        self.assertIsNone(self.review.detail(new['id'])['approval'])

    def test_repository_change_also_invalidates_approval(self):
        record = self.configured()
        old_hash = self.review.detail(record['id'])['draft_hash']
        self.policy['owners'][0]['destination']['issue']['repository'] = 'fixture-org/another'
        with self.assertRaises(Conflict): self.review.approve(record['id'], old_hash)

    def test_invalid_destinations_rejected(self):
        bad = []
        for repository in ('https://github.com/org/repo', 'org/repo/extra', '../repo', 'org/repo\n', ''):
            value = destination(); value['issue']['repository'] = repository; bad.append(value)
        for recipients in ([], ['x@example.invalid', 'X@example.invalid'], ['x@example.invalid\r\nBcc: y@example.invalid'], ['Name <x@example.invalid>'], 'x@example.invalid', ['x@example.invalid']*21):
            value = destination(); value['notification']['recipients'] = recipients; bad.append(value)
        value = destination(); value['issue']['provider'] = 'unknown'; bad.append(value)
        value = destination(); value['notification']['secret'] = 'not-allowed'; bad.append(value)
        bad.extend((None, {}, {'issue': None, 'notification': None}))
        for value in bad:
            with self.subTest(value=value), self.assertRaises(ValueError): validate_destination(value)

    def test_rehearsal_retains_reviewed_content(self):
        record = self.configured()
        self.review.approve(record['id'], self.review.detail(record['id'])['draft_hash'])
        rehearsal = DeliveryRehearsal(self.review); rehearsal.enqueue(record['id'])
        rehearsal.advance(record['id']); self.assertTrue(rehearsal.advance(record['id'])['complete'])
        with closing(self.store.connect()) as db:
            rows = db.execute('SELECT payload FROM routing_rehearsal_steps WHERE draft_id=?', (record['id'],)).fetchall()
        for row in rows:
            self.assertEqual(json.loads(row[0])['draft']['destination_preview'], record['draft']['destination_preview'])


if __name__ == '__main__': unittest.main()

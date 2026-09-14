from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import unittest
import test_routing_destination as fixtures
from github_issue_adapter import GithubIssueAdapter
from ticket_workflow import Conflict


class GithubTests(unittest.TestCase):
    def setUp(self):
        fixtures.DestinationTests.setUp(self)
        self.record = fixtures.DestinationTests.configured(self)
        self.identity = self.record['id']
        self.hash = self.review.detail(self.identity)['draft_hash']
        self.review.approve(self.identity, self.hash)
        self.issue = self.record['draft']['destination_preview']['issue']
        self.calls = []
        self.handler = lambda method, path, payload: (201, self.response())
        def transport(method, path, payload):
            self.calls.append((method, path, payload))
            return self.handler(method, path, payload)
        self.adapter = GithubIssueAdapter(self.review, transport)

    def response(self, number=1):
        return {'number': number, 'title': self.issue['title'], 'body': self.issue['body'],
                'html_url': 'https://github.com/fixture-org/fixture-issues/issues/' + str(number)}

    def create(self): return self.adapter.create_issue(self.identity, authorized_hash=self.hash)
    def reconcile(self): return self.adapter.reconcile(self.identity, authorized_hash=self.hash)

    def test_exact_request_and_idempotent_success(self):
        first = self.create(); self.assertEqual(first, self.create())
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0], ('POST', '/repos/fixture-org/fixture-issues/issues',
                                       {'title': self.issue['title'], 'body': self.issue['body']}))
        self.assertEqual(first['number'], 1)

    def test_concurrent_workers_create_once(self):
        def run(_):
            try: return self.create()
            except Conflict: return None
        with ThreadPoolExecutor(4) as pool: list(pool.map(run, range(4)))
        self.assertEqual(len(self.calls), 1)

    def test_timeout_is_held_and_can_recover_receipt(self):
        self.handler = lambda *args: (_ for _ in ()).throw(TimeoutError('secret-not-for-output'))
        with self.assertRaises(Conflict) as error: self.create()
        self.assertNotIn('secret-not-for-output', str(error.exception))
        with self.assertRaises(Conflict): self.create()
        self.assertEqual(len(self.calls), 1)
        self.handler = lambda *args: (200, [self.response()])
        self.assertEqual(self.reconcile()['number'], 1)
        self.assertEqual(self.create()['number'], 1)
        self.assertEqual([c[0] for c in self.calls], ['POST', 'GET'])

    def test_missing_duplicate_and_edited_receipts_hold(self):
        self.handler = lambda *args: (500, {})
        with self.assertRaises(Conflict): self.create()
        edited = self.response(); edited['title'] = 'edited'
        for rows in ([], [self.response(), self.response(2)], [edited]):
            self.handler = lambda *args: (200, rows)
            with self.assertRaises(Conflict): self.reconcile()
        with self.assertRaises(Conflict): self.create()
        self.assertEqual(sum(c[0] == 'POST' for c in self.calls), 1)

    def test_pagination_bounded_and_pull_requests_ignored(self):
        self.handler = lambda *args: (503, {})
        with self.assertRaises(Conflict): self.create()
        pr = self.response(); pr['pull_request'] = {}
        self.handler = lambda *args: (200, [pr]*100)
        with self.assertRaises(Conflict): self.reconcile()
        self.assertEqual(len(self.calls), 6)
        self.assertIn('page=5', self.calls[-1][1])

    def test_wrong_authorization_or_changed_policy_has_no_call(self):
        with self.assertRaises(Conflict): self.adapter.create_issue(self.identity, authorized_hash='wrong')
        self.policy['owners'][0]['destination']['issue']['repository'] = 'fixture-org/changed'
        with self.assertRaises(Conflict): self.create()
        self.assertEqual(self.calls, [])

    def test_invalid_success_reference_remains_held(self):
        row = self.response(); row['html_url'] = 'https://other.invalid/issues/1'
        self.handler = lambda *args: (201, row)
        with self.assertRaises(Conflict): self.create()
        with self.assertRaises(Conflict): self.create()
        self.assertEqual(len(self.calls), 1)

    def test_paged_recovery_requires_complete_scan(self):
        self.handler = lambda *args: (403, {})
        with self.assertRaises(Conflict): self.create()
        def pages(method, path, payload):
            return (200, [self.response()] + [{'body': ''}]*99) if path.endswith('&page=1') else (200, [])
        self.handler = pages
        self.assertEqual(self.reconcile()['number'], 1)
        self.assertEqual(len(self.calls), 3)


if __name__ == '__main__': unittest.main()

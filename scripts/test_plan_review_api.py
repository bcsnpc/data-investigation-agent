from io import BytesIO
import json
import threading
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen
from uuid import uuid4
from wsgiref.simple_server import make_server
import test_reviewed_handoff as fixtures
from plan_review_api import PlanReviews
from investigation_evidence_api import create_app
from serve_investigations import QuietHandler


class ReviewApiTests(unittest.TestCase):
    def setUp(self):
        fixtures.HandoffTests.setUp(self)
        self.token = 'local-test-' + 'x' * 40
        reviews = PlanReviews(self.store, self.config, lambda: self.estate)
        self.app = create_app(self.store.database, self.token, self.store, self.lineage, reviews)
        self.path = '/api/plans/' + self.record['id']
        graph_patch=patch('review_ticket_plan.load_graph',return_value=self.graph)
        graph_patch.start();self.addCleanup(graph_patch.stop)

    def request(self, path=None, method='GET', body=None, token=None, query=''):
        raw = json.dumps(body).encode() if body is not None else b''
        captured = {}
        def start(status, headers): captured.update(status=status, headers=dict(headers))
        with patch('review_ticket_plan.load_graph', return_value=self.graph):
            output = b''.join(self.app(dict(PATH_INFO=path or self.path, REQUEST_METHOD=method,
                QUERY_STRING=query, HTTP_AUTHORIZATION='Bearer ' + (token or self.token),
                CONTENT_TYPE='application/json', CONTENT_LENGTH=str(len(raw)), **{'wsgi.input': BytesIO(raw)}), start))
        return captured['status'], json.loads(output)

    def test_authenticated_list_and_detail(self):
        self.assertTrue(self.request(token='wrong')[0].startswith('401'))
        status, body = self.request('/api/tickets/' + self.original + '/plans')
        self.assertEqual(body['items'][0]['id'], self.record['id'])
        self.assertIsNone(body['next_offset'])
        status, body = self.request()
        self.assertEqual(body['draft']['plan']['order_id'], 'ORD-000002')
        self.assertIsNone(body['approval'])
        self.assertEqual(len(body['plan_hash']), 64)

    def test_hash_bound_approval_replay_and_link(self):
        digest = self.request()[1]['plan_hash']
        body = dict(confirm=True, plan_hash=digest)
        status, first = self.request(self.path + '/approve', 'POST', body)
        self.assertTrue(status.startswith('201'))
        status, second = self.request(self.path + '/approve', 'POST', body)
        self.assertTrue(status.startswith('200'))
        self.assertEqual(first['ticket_id'], second['ticket_id'])
        self.assertEqual(self.request()[1]['approval']['ticket_id'], first['ticket_id'])
        self.assertEqual(self.request(first['status_url'])[1]['ticket']['status'], 'QUEUED')

    def test_stale_or_missing_confirmation_cannot_queue(self):
        for body, expected in [(dict(confirm=True, plan_hash='0' * 64),'409'),
                               (dict(confirm=False, plan_hash='0' * 64),'400'),
                               (dict(confirm=True, plan_hash='0' * 64, sql='DROP'),'400')]:
            self.assertTrue(self.request(self.path + '/approve','POST',body)[0].startswith(expected))
        digest = self.request()[1]['plan_hash']
        self.estate['investigation']['lineage_run'] = str(uuid4())
        self.assertTrue(self.request(self.path + '/approve','POST',dict(confirm=True,plan_hash=digest))[0].startswith('409'))

    def test_missing_and_invalid_routes(self):
        self.assertTrue(self.request('/api/plans/' + str(uuid4()))[0].startswith('404'))
        self.assertTrue(self.request('/api/plans/not-a-uuid')[0].startswith('400'))
        self.assertTrue(self.request(query='extra=1')[0].startswith('400'))
        self.assertTrue(self.request('/api/tickets/' + self.original + '/plans',query='offset=-1')[0].startswith('400'))
        self.assertTrue(self.request(self.path + '/approve')[0].startswith('405'))

    def test_real_http_review_and_approval(self):
        server = make_server('127.0.0.1', 0, self.app, handler_class=QuietHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = 'http://127.0.0.1:' + str(server.server_port) + self.path
            headers = {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}
            with urlopen(Request(url, headers=headers), timeout=5) as response:
                draft = json.load(response)
            body = json.dumps(dict(confirm=True, plan_hash=draft['plan_hash'])).encode()
            with patch('review_ticket_plan.load_graph', return_value=self.graph):
                with urlopen(Request(url + '/approve', data=body, headers=headers), timeout=5) as response:
                    self.assertEqual(response.status, 201)
                    result = json.load(response)
            self.assertEqual(self.store.get(result['ticket_id'])['status'], 'QUEUED')
        finally:
            server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__': unittest.main()

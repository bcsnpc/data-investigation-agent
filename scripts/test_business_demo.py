import base64
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from uuid import uuid4
from business_demo import BusinessDemo, create_app
from demo import prepare
from defect_lab import mutate

PNG = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jN3sAAAAASUVORK5CYII='


class BusinessDemoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = prepare(Path(self.temp.name) / 'demo')
        mutate(self.folder / 'lab.duckdb', 'inject-double-refund')
        self.service = BusinessDemo(self.folder)

    def body(self):
        return {'snapshot_id': self.service.snapshot()['id'], 'question': 'Net cash looks too low. Why?',
                'screenshot': PNG, 'app_screenshot': PNG, 'request_key': str(uuid4())}

    def test_business_flow_with_preserved_attachments(self):
        body = self.body()
        identity = self.service.submit(body, launch=False)
        self.service.run(identity)
        item = self.service.detail(identity)
        self.assertEqual(item['status'], 'COMPLETED')
        self.assertEqual(item['result']['reported'], '55.0000')
        self.assertEqual(item['result']['expected'], '154.0000')
        self.assertTrue(item['result']['verified'])
        self.assertEqual(len(item['steps']), 5)
        self.assertNotIn('Silver', item['result']['explanation'])
        with self.service.connect() as db:
            self.assertEqual(db.execute('SELECT screenshot FROM cases').fetchone()[0], base64.b64decode(PNG))

    def test_changed_report_is_held(self):
        identity = self.service.submit(self.body(), launch=False)
        mutate(self.folder / 'lab.duckdb', 'reset')
        self.service.run(identity)
        self.assertEqual(self.service.detail(identity)['status'], 'NEEDS_REVIEW')

    def test_submission_idempotency_and_validation(self):
        body = self.body()
        identity = self.service.submit(body, launch=False)
        self.assertEqual(self.service.submit(body, launch=False), identity)
        body['question'] = 'A changed question'
        with self.assertRaises(ValueError): self.service.submit(body, launch=False)
        body['screenshot'] = base64.b64encode(b'not an image').decode()
        with self.assertRaises(ValueError): self.service.submit(body, launch=False)

    def test_restart_holds_unfinished_work(self):
        identity = self.service.submit(self.body(), launch=False)
        restarted = BusinessDemo(self.folder)
        self.assertEqual(restarted.detail(identity)['status'], 'INTERRUPTED')

    def test_api_requires_auth(self):
        app = create_app(self.service, 'x' * 32)
        statuses = []
        app({'PATH_INFO': '/api/report', 'REQUEST_METHOD': 'GET'}, lambda s, h: statuses.append(s))
        self.assertEqual(statuses, ['401 Unauthorized'])
        statuses.clear()
        raw = b''.join(app({'PATH_INFO': '/api/report', 'REQUEST_METHOD': 'GET', 'HTTP_AUTHORIZATION': 'Bearer ' + 'x' * 32}, lambda s, h: statuses.append(s)))
        self.assertEqual(statuses, ['200 OK'])
        self.assertEqual(json.loads(raw)['reported'], '55.0000')


if __name__ == '__main__': unittest.main()

"""Local HTTP replay, authentication, requester propagation and durable audit tests."""
from copy import deepcopy
import io
import json
from pathlib import Path
import secrets
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen
from wsgiref.simple_server import make_server, WSGIRequestHandler
from investigator.investigation_api import ReplayEngine, TokenAuth, Service, create_app, request
from test_round28_configuration import draft


class Quiet(WSGIRequestHandler):
    def log_message(self, *args): pass


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(); self.addCleanup(self.folder.cleanup)
        self.token = secrets.token_urlsafe(48)
        self.auth = TokenAuth(self.token, principal='tester', estates=['draft'])
        self.submission = dict(text='Why does the selected count show 12?', estate_id='draft', requester='tester', report='Example', page='Summary', visual='Count')
        self.result = {'verdict': 'AS DESIGNED', 'explanation': 'The retained count is 12.',
            'evidence_summary': [{'id': 'e1', 'rows': [[12]]}], 'handoff': {'queries': ['SELECT COUNT(*) FROM app.entries']}}
        self.engine = ReplayEngine([{'request': self.submission, 'result': self.result}])
        # HTTP unit tests isolate the already separately-tested installation validator.
        config = draft(); config['enabled'] = True
        with patch('investigator.estate_config.validate', side_effect=deepcopy):
            self.service = Service(root=self.folder.name, engine=self.engine, estates={'draft': config})
        self.app = create_app(self.service, self.auth, port=8765)

    def call(self, path, method='GET', body=None, *, auth=True, principal=None, host='127.0.0.1:8765', query=''):
        raw = json.dumps(body).encode() if body is not None else b''
        env = dict(REQUEST_METHOD=method, PATH_INFO=path, HTTP_HOST=host, QUERY_STRING=query,
                   CONTENT_TYPE='application/json', CONTENT_LENGTH=str(len(raw)), **{'wsgi.input': io.BytesIO(raw)})
        if auth: env['HTTP_AUTHORIZATION'] = 'Bearer ' + self.token
        status = []
        result = b''.join(self.app(env, lambda s, h: status.append(int(s.split()[0]))))
        return status[0], json.loads(result)

    def test_every_endpoint_requires_auth_including_health_and_every_call_is_recorded(self):
        for path, method in [('/v1/health', 'GET'), ('/v1/investigations', 'POST'),
                             ('/v1/investigations/'+'a'*32, 'GET'), ('/v1/investigations/'+'a'*32+'/result', 'GET')]:
            self.assertEqual(self.call(path, method, auth=False)[0], 401)
        self.assertEqual(self.call('/v1/health')[1]['live_enabled'], False)
        rows = [json.loads(x) for x in (Path(self.folder.name)/'audit.jsonl').read_text().splitlines()]
        self.assertEqual(len(rows), 5)
        self.assertEqual(len(list(Path(self.folder.name).glob('access-*.json'))), 5)
        self.assertNotIn(self.token, ''.join(p.read_text() for p in Path(self.folder.name).glob('*')))

    def test_submit_status_result_exact_replay_and_requester_persisted(self):
        status, admitted = self.call('/v1/investigations', 'POST', self.submission)
        self.assertEqual(status, 202)
        path = admitted['status_url']
        self.assertEqual(self.call(path)[1]['status'], 'COMPLETED')
        self.assertEqual(self.call(path+'/result'), (200, self.result))
        stored = json.loads((Path(self.folder.name)/(admitted['case_id']+'.json')).read_text())
        self.assertEqual(stored['requester'], 'tester')
        self.assertEqual(stored['request'], self.submission)
        self.assertEqual(len(stored['events']), 3)

    def test_no_impersonation_estate_escape_or_fallback_to_native(self):
        bad = dict(self.submission, requester='somebody-else')
        self.assertEqual(self.call('/v1/investigations', 'POST', bad)[0], 403)
        bad = dict(self.submission, estate_id='another')
        self.assertEqual(self.call('/v1/investigations', 'POST', bad)[0], 403)
        bad = dict(self.submission, text='A different ticket')
        with patch('socket.socket.connect', side_effect=AssertionError('NETWORK_FORBIDDEN')):
            self.assertEqual(self.call('/v1/investigations', 'POST', bad)[0], 400)
        self.assertEqual(self.call('/v1/health', host='public.example')[0], 401)
        self.assertEqual(self.call('/v1/health', query='token=do-not-log')[0], 400)
        logs = ''.join(p.read_text() for p in Path(self.folder.name).glob('*'))
        self.assertNotIn('do-not-log', logs)

    def test_results_are_scoped_to_authenticated_subject_and_disabled_estates_refuse(self):
        _, admitted = self.call('/v1/investigations', 'POST', self.submission)
        other = TokenAuth(self.token, principal='other', estates=['draft'])
        app = self.app; self.app = create_app(self.service, other, port=8765)
        self.assertEqual(self.call(admitted['status_url'])[0], 404)
        self.app = app
        self.service.estates['draft']['enabled'] = False
        self.assertEqual(self.call('/v1/investigations', 'POST', self.submission)[0], 400)

    def test_bad_request_shapes_screenshots_and_duplicate_json_fail(self):
        for value in ({}, dict(self.submission, text=''), dict(self.submission, live=True),
                      dict(self.submission, screenshot='not-an-image'), dict(self.submission, requester=['tester'])):
            with self.assertRaises(ValueError): request(value)
        with self.assertRaises(ValueError): ReplayEngine([{'request': self.submission, 'result': {}}, {'request': self.submission, 'result': {}}])
        with self.assertRaises(ValueError): TokenAuth('short', principal='p', estates=['draft'])

    def test_secret_store_resolver_called_by_name_only(self):
        calls = []
        def resolve(vault, name): calls.append((vault, name)); return self.token
        auth = TokenAuth.from_secret_store(resolve, vault='configured-vault', secret_name='api-token', principal='tester', estates=['draft'])
        self.assertEqual(auth.check('Bearer '+self.token), 'tester')
        self.assertEqual(calls, [('configured-vault', 'api-token')])

    def test_real_loopback_http_submit_and_get_saved_result(self):
        server = make_server('127.0.0.1', 0, lambda *a: [], handler_class=Quiet)
        port = server.server_port
        server.set_app(create_app(self.service, self.auth, port=port))
        thread = Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            headers = {'Authorization': 'Bearer '+self.token, 'Content-Type': 'application/json'}
            base = 'http://127.0.0.1:'+str(port)
            with urlopen(Request(base+'/v1/investigations', data=json.dumps(self.submission).encode(), headers=headers), timeout=5) as response:
                self.assertEqual(response.status, 202); admitted = json.load(response)
            with urlopen(Request(base+admitted['status_url']+'/result', headers=headers), timeout=5) as response:
                self.assertEqual(json.load(response), self.result)
        finally:
            server.shutdown(); server.server_close(); thread.join(5)


if __name__ == '__main__': unittest.main()

from contextlib import contextmanager
import copy
from io import BytesIO
import json
from pathlib import Path
import sqlite3
from threading import Event, Thread
import unittest
from unittest.mock import MagicMock, patch

from investigator.workspace import Workspace
from investigator.workspace_api import create_app
from investigator.runtime import Runtime
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.onboarding import Conflict
import test_source_diagnostics as source_fixture
from test_native_diagnostics import response
from test_adaptive_investigation import decision


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        helper = source_fixture.SourceTests(); helper.setUp(); self.addCleanup(helper.doCleanups)
        self.store, self.model, self.config = helper.store, helper.model, helper.config
        @contextmanager
        def connect():
            db = sqlite3.connect(Path(helper.temp.name) / 'catalog.sqlite', timeout=10)
            db.row_factory = sqlite3.Row
            try:
                with db: yield db
            finally: db.close()
        self.store.connect.side_effect = connect
        self.store.environment = 'test'
        self.store.list.return_value = [self.model]
        self.model['name'] = 'Example reporting model'
        self.clock = MagicMock(return_value=1000)
        self.native = MagicMock(return_value=response([{'[m0]': 7}]))
        self.source = MagicMock()
        self.runtime = Runtime(self.store, self.config, self.native, self.source)
        self.planner = MagicMock(side_effect=lambda p: (decision(p['candidates'][0]['id']) if not p['observations'] else decision(), {}))
        self.policy = {'environment': 'test', 'daily_limits': {'planner_calls': 100, 'cloud_calls': 100, 'input_characters': 1000000, 'output_tokens': 100000},
                       'max_inflight_planners': 1, 'no_progress_limit': 2}
        self.agent = AdaptiveRuntime(self.runtime, self.planner, self.clock, usage_policy=self.policy)
        self.workspace = Workspace(self.agent, execution_enabled=True, clock=self.clock)
        self.request = {'model_id': 'model', 'measure_id': 'Unseen ratio', 'filters': [{'column_id': 'c', 'operator': 'in', 'values': ['USD']}],
                        'dimension_ids': [], 'symptom': 'This number looks lower than expected.', 'predecessor': None}
        self.token = 'workspace-' + 'a' * 40
        self.app = create_app(self.workspace, self.token)

    def preview(self): return self.workspace.preview(copy.deepcopy(self.request))
    def start(self): return self.workspace.start(self.preview()['id'])

    def http(self, path, body=None, token=None, method=None, **headers):
        raw = json.dumps(body).encode() if body is not None else b''
        env = {'PATH_INFO': path, 'REQUEST_METHOD': method or ('POST' if body is not None else 'GET'),
               'HTTP_HOST': '127.0.0.1:8776', 'HTTP_AUTHORIZATION': 'Bearer ' + (self.token if token is None else token),
               'CONTENT_TYPE': 'application/json', 'CONTENT_LENGTH': str(len(raw)), 'wsgi.input': BytesIO(raw), **headers}
        captured = {}
        def start(status, response_headers): captured.update(status=status, headers=dict(response_headers))
        data = b''.join(self.app(env, start))
        captured['body'] = json.loads(data) if captured['headers']['Content-Type'].startswith('application/json') else data
        return captured

    def test_catalog_and_preview_no_cloud_or_llm(self):
        self.assertEqual(self.workspace.models()['models'][0]['measures'][0]['id'], 'Unseen ratio')
        p = self.preview(); self.assertEqual(p['cloud_calls'], 0)
        self.assertGreater(p['candidate_count'], 0)
        self.planner.assert_not_called(); self.native.assert_not_called(); self.source.assert_not_called()

    def test_unknown_fields_and_measure_rejected(self):
        self.request['query'] = 'SELECT 1'
        with self.assertRaises(ValueError): self.preview()
        del self.request['query']; self.request['measure_id'] = 'invented'
        with self.assertRaises((ValueError, KeyError)): self.preview()

    def test_preview_tampering_is_rejected(self):
        p = self.preview()
        with self.store.connect() as db: db.execute("UPDATE workspace_previews SET body='{}'")
        with self.assertRaises(Conflict): self.workspace.start(p['id'])
        self.native.assert_not_called()

    def test_expired_preview(self):
        p = self.preview(); self.clock.return_value = p['expires'] + 1
        with self.assertRaises(Conflict): self.workspace.start(p['id'])

    def test_stale_revision(self):
        p = self.preview(); self.model['revision'] += 1
        with self.assertRaises(Conflict): self.workspace.start(p['id'])

    def test_changed_context_even_with_same_revision(self):
        p = self.preview(); self.model['context']['semantic_graph']['measures']['Unseen ratio']['operations'] = ['SUM']
        with self.assertRaises(Conflict): self.workspace.start(p['id'])

    def test_history_cannot_be_relabelled_with_another_preview(self):
        run = self.start(); self.request['symptom'] = 'Different question'; other = self.preview()
        with self.store.connect() as db:
            db.execute('UPDATE workspace_jobs SET preview_id=? WHERE session_id=?', (other['id'], run['id']))
        with self.assertRaises(Conflict): self.workspace.session(run['id'])

    def test_unbounded_scope_is_not_offered_by_backend(self):
        self.request['filters'] = []
        with self.assertRaises(ValueError): self.preview()

    def test_changed_engine(self):
        p = self.preview()
        with patch('investigator.workspace.fingerprint', return_value='different'):
            with self.assertRaises(Conflict): self.workspace.start(p['id'])

    def test_duplicate_start_executes_once(self):
        p = self.preview(); one = self.workspace.start(p['id']); two = self.workspace.start(p['id'])
        self.assertEqual(one['id'], two['id']); self.native.assert_not_called()
        self.assertTrue(self.workspace.run_once()); self.assertFalse(self.workspace.run_once())
        replay = self.workspace.start(p['id']); self.assertEqual(replay['id'], one['id'])
        self.native.assert_called_once(); self.assertEqual(replay['status'], 'COMPLETED')

    def test_only_one_active_job(self):
        self.start(); p = self.preview()
        with self.assertRaises(Conflict): self.workspace.start(p['id'])

    def test_shared_projection_hash_and_values(self):
        run = self.start(); self.workspace.run_once(); saved = self.workspace.session(run['id'])
        self.assertEqual(saved['facts'][0]['values'], [{'[m0]': {'type': 'decimal', 'value': '7'}}])
        self.assertEqual(saved['outcome_hash'], saved['technical']['outcome_hash'])
        self.assertEqual(saved['scope_hash'], saved['technical']['scope_hash'])
        self.assertFalse(saved['cause_verified']); self.assertFalse(saved['delivery_eligible'])
        for _ in range(3): self.workspace.session(run['id']); self.workspace.sessions()
        self.native.assert_called_once()

    def test_foreign_session_not_visible(self):
        with self.assertRaises(KeyError): self.workspace.session('foreign')

    def test_cancel_queued_prevents_dispatch(self):
        run = self.start(); result = self.workspace.cancel(run['id'])
        self.assertEqual(result['status'], 'CANCELLED'); self.assertFalse(self.workspace.run_once())
        self.planner.assert_not_called(); self.native.assert_not_called()

    def test_cancel_inflight_fences_worker(self):
        entered, release = Event(), Event()
        def native(_): entered.set(); release.wait(5); return response([{'[m0]': 7}])
        self.native.side_effect = native
        run = self.start(); worker = Thread(target=self.workspace.run_once); worker.start()
        self.assertTrue(entered.wait(5))
        self.workspace.cancel(run['id']); release.set(); worker.join(5)
        self.assertFalse(worker.is_alive())
        saved = self.workspace.session(run['id'])
        self.assertEqual(saved['status'], 'CANCELLED'); self.assertEqual(saved['job_status'], 'CANCELLED')

    def test_new_host_does_not_take_old_queue(self):
        run = self.start(); restarted = Workspace(self.agent, execution_enabled=True, clock=self.clock)
        self.assertFalse(restarted.run_once()); saved = restarted.session(run['id'])
        self.assertFalse(saved['worker_attached']); self.assertIn('not attached', saved['summary'])
        restarted.cancel(run['id']); self.assertEqual(restarted.session(run['id'])['status'], 'CANCELLED')

    def test_worker_exception_is_visible_without_replay(self):
        run = self.start()
        with patch.object(self.agent, 'run', side_effect=RuntimeError('private error')): self.workspace.run_once()
        saved = self.workspace.session(run['id']); self.assertEqual(saved['job_status'], 'INTERRUPTED')
        self.assertIn('not attached', saved['summary']); self.assertFalse(self.workspace.run_once())

    def test_clarification_new_session_no_old_evidence(self):
        self.planner.side_effect = None
        self.planner.return_value = decision(question='Which period do you mean?'), {}
        run = self.start(); self.workspace.run_once()
        self.request['predecessor'] = run['id']; self.request['symptom'] += ' Clarification: use the selected USD records.'
        successor = self.start()
        self.assertNotEqual(successor['id'], run['id']); self.assertEqual(successor['predecessor'], run['id'])
        self.assertEqual(successor['facts'], [])

    def test_clarification_cannot_reuse_completed_session(self):
        run = self.start(); self.workspace.run_once(); self.request['predecessor'] = run['id']
        with self.assertRaises(Conflict): self.preview()

    def test_history_only_start_disabled(self):
        view = Workspace(self.agent, clock=self.clock)
        p = view.preview(self.request)
        with self.assertRaises(Conflict): view.start(p['id'])
        self.assertFalse(view.models()['execution_enabled'])

    def test_live_requires_governance(self):
        self.agent.governor = None
        with self.assertRaises(ValueError): Workspace(self.agent, execution_enabled=True)

    def test_auth_origin_host_and_body_guards(self):
        cases = [('401', {'token': ''}), ('403', {'HTTP_HOST': 'attacker.test'}), ('403', {'HTTP_ORIGIN': 'https://attacker.test'}), ('400', {'QUERY_STRING': 'token=bad'})]
        for status, kwargs in cases:
            with self.subTest(kwargs=kwargs): self.assertTrue(self.http('/api/workspace/models', **kwargs)['status'].startswith(status))
        self.assertTrue(self.http('/api/workspace/previews', {}, CONTENT_TYPE='text/plain')['status'].startswith('400'))
        self.assertTrue(self.http('/api/workspace/sessions', {}, CONTENT_LENGTH='20000')['status'].startswith('400'))

    def test_api_preview_start_poll_cancel(self):
        p = self.http('/api/workspace/previews', self.request); self.assertTrue(p['status'].startswith('200'))
        r = self.http('/api/workspace/sessions', {'preview_id': p['body']['id']}); self.assertTrue(r['status'].startswith('200'))
        identity = r['body']['id']
        self.assertTrue(self.http('/api/workspace/sessions/' + identity)['status'].startswith('200'))
        result = self.http('/api/workspace/sessions/' + identity + '/cancel', {})
        self.assertEqual(result['body']['status'], 'CANCELLED')
        self.planner.assert_not_called()

    def test_static_assets_and_no_store(self):
        page = self.http('/', token='')
        self.assertIn(b'Follow the numbers.', page['body'])
        self.assertEqual(page['headers']['Cache-Control'], 'no-store')
        self.assertIn("frame-ancestors 'none'", page['headers']['Content-Security-Policy'])
        self.assertTrue(self.http('/api/workspace/sessions', method='DELETE')['status'].startswith('405'))


if __name__ == '__main__': unittest.main()

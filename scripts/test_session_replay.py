"""Full runtime replay and per-step fault probes, using zero-network recordings."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import httpx
from openai import DefaultHttpxClient
import test_flexible_investigation as fixture
from investigator import planner_recording
from investigator.adaptive_planner import azure_plan
from investigator.adaptive_runtime import AdaptiveRuntime

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'acceptance/unknown_domain'))
from session_replay import replay, ReplayError
from run_ledger import row, append


class SessionReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.helper = fixture.DynamicTests()
        self.helper.setUp()
        self.addCleanup(self.helper.doCleanups)
        self.calls = 0
        policy = {'environment': self.helper.store.environment,
            'daily_limits': {'planner_calls': 100, 'cloud_calls': 30, 'input_characters': 2000000, 'output_tokens': 150000},
            'max_inflight_planners': 1, 'no_progress_limit': 2}
        self.helper.envelope['limits']['input_characters'] = 384000
        agent = AdaptiveRuntime(self.helper.runtime, azure_plan, clock=lambda: 1000,
                                planner_profile={'adapter': 'azure'}, usage_policy=policy)
        def transport(request):
            self.calls += 1
            body = json.loads(request.content)
            payload = json.loads(body['input'])
            slots = body['tools'][0]['parameters']['properties']['hypotheses']['required']
            hypotheses = {slot: None for slot in slots}
            source = next(a for a in payload['context_entry_points'] if a['kind'] == 'SqlObject')
            if self.calls in (1, 5):
                action = {'kind': 'LOOKUP', 'operation': 'asset', 'value': source['id']}
                if self.calls == 1:
                    hypotheses['h1'] = {'claim': 'The source may be empty.', 'status': 'OPEN', 'evidence_ids': []}
            elif self.calls in (2, 3):
                observed = next(o['metadata']['asset'] for o in payload['observations']
                                if o.get('metadata', {}).get('asset', {}).get('kind') == 'SqlObject')
                target = observed['name']
                query = 'DROP TABLE ' + target if self.calls == 2 else 'SELECT COUNT(*) AS n FROM ' + target
                action = {'kind': 'QUERY', 'tool': 'bounded_sql', 'text': query, 'max_rows': 20}
            elif self.calls == 4:
                action = {'kind': 'QUERY', 'tool': 'bounded_dax', 'text': 'EVALUATE ROW("value",[Total])', 'max_rows': 20}
                evidence = next(o['id'] for o in payload['observations'] if o['tool'] == 'bounded_sql')
                hypotheses['h1'] = {'claim': 'A scoped source observation is available.', 'status': 'REFINED', 'evidence_ids': [evidence]}
            else:
                evidence = [o['id'] for o in payload['observations'] if o['tool'] in ('bounded_sql', 'bounded_dax')]
                action = {'kind': 'STOP', 'assessment': {'classification': 'BUSINESS_CONTEXT_REQUIRED',
                    'claim': 'Scoped observations do not establish the intended business rule.',
                    'evidence_ids': evidence, 'alternatives': ['The intended rule may differ.'],
                    'limits': ['Business intent is not supplied.'], 'support': {
                        'mechanism': 'Scoped readings are available.', 'mechanism_evidence_ids': evidence,
                        'intent_dependency': 'UNKNOWN', 'intent_basis': 'No intended rule was supplied.',
                        'intent_evidence_ids': [], 'remaining_test': 'Obtain the intended rule.'}}}
            return httpx.Response(200, json={'id': 'mock-'+str(self.calls), 'object': 'response',
                'model': 'offline-fixture', 'status': 'completed', 'usage': None,
                'output': [{'type': 'function_call', 'call_id': 'call-'+str(self.calls),
                    'name': 'dynamic_investigation_action', 'arguments': json.dumps({'next': action, 'hypotheses': hypotheses})}]})
        with patch.object(planner_recording, 'ROOT', self.root), patch.dict(os.environ, {
                'INVESTIGATOR_RECORD_PLANNER': '1', 'AZURE_OPENAI_ENDPOINT': 'https://offline.openai.azure.com',
                'AZURE_OPENAI_DEPLOYMENT': 'offline-fixture', 'AZURE_OPENAI_API_KEY': 'offline-placeholder-credential'}), \
                patch('openai.DefaultHttpxClient', side_effect=lambda **kw: DefaultHttpxClient(
                    transport=httpx.MockTransport(transport), **kw)):
            self.original = agent.run(agent.create(self.helper.envelope, 'recorded-session')['id'])
        self.assertEqual(self.original['planner_calls'], 6)
        self.assertEqual(self.original['stop_reason'], 'ENOUGH_DIAGNOSTICS')
        self.recordings = self.root / '.local/planner-recordings'

    def replay(self, name='replay', **kwargs):
        return replay(self.original['id'], self.recordings, self.helper.store.database,
            self.helper.store.inventory, self.helper.config, self.root / name, **kwargs)

    def test_complete_session_replays_without_network_or_source_changes(self):
        original_hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in (self.helper.store.database, self.helper.store.inventory)}
        result = self.replay()
        self.assertEqual(result['status'], 'MATCHED', result['differences'])
        self.assertEqual(result['network_calls'], 0)
        self.assertEqual(result['unrecorded_tool_attempts'], 0)
        self.assertEqual(len(result['comparisons']), 6)
        self.assertEqual(result['session']['cloud_calls'], 2)
        self.assertTrue(any(o['status'] == 'REJECTED' for o in result['session']['observations']))
        self.assertTrue(any(o.get('duplicate_of') for o in result['session']['observations']))
        self.assertEqual(result['session']['hypotheses'][0]['status'], 'REFINED')
        self.assertEqual(result['business_correctness'], 'NOT_GRADED')
        entry = row(result, planner_recording.load_session(self.original['id'], self.recordings))
        self.assertEqual((entry['planner_calls'], entry['reads_sql'], entry['reads_dax']), (6, 1, 1))
        self.assertEqual((entry['retrieval_calls'], entry['test_calls']), (2, 3))
        ledger = self.root / 'ledger.jsonl'
        append(ledger, entry)
        original_line = ledger.read_bytes()
        append(ledger, dict(entry, session_id='another-evaluation'))
        self.assertTrue(ledger.read_bytes().startswith(original_line))
        for path, sha in original_hashes.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), sha)

    def test_malformed_proposal_at_every_step_uses_runtime_rejection_path(self):
        malformed = {'next': {'kind': 'ASK', 'question': 42}, 'hypotheses': {}}
        for step in range(1, 7):
            with self.subTest(step=step):
                result = self.replay('injection-'+str(step), inject_at=step, injection=malformed)
                self.assertEqual(result['status'], 'INJECTION_PROBE')
                self.assertEqual(result['session']['planner_calls'], step)
                self.assertEqual(result['session']['events'][-1]['kind'], 'PROPOSAL_REJECTED')
                self.assertEqual(result['network_calls'], 0)

    def test_config_drift_and_output_reuse_fail_closed(self):
        changed = dict(self.helper.config, unexpected=True)
        with self.assertRaisesRegex(ReplayError, 'CONFIGURATION_MISMATCH'):
            replay(self.original['id'], self.recordings, self.helper.store.database,
                   self.helper.store.inventory, changed, self.root / 'changed')
        self.replay()
        with self.assertRaises(FileExistsError):
            self.replay()

    def test_prerequisite_repair_reuses_only_the_recorded_query_receipt(self):
        first = planner_recording.load_session(self.original['id'], self.recordings)[0]
        source = next(a for a in first['context']['payload']['context_entry_points'] if a['kind'] == 'SqlObject')
        proposal = {'next': {'kind': 'QUERY', 'tool': 'bounded_sql',
                    'text': 'SELECT COUNT(*) AS n FROM '+source['name'], 'max_rows': 20}, 'hypotheses': {}}
        result = self.replay('prerequisite', inject_at=1, injection=proposal)
        self.assertTrue(any(e['kind']=='PROPOSAL_REPAIRED' and e['detail']['repair_kind']=='schema_prefetch'
                            for e in result['session']['events']))
        self.assertEqual(result['status'],'INJECTION_PROBE')
        self.assertEqual(result['session']['cloud_calls'],1)
        self.assertEqual(result['unrecorded_tool_attempts'],0)

    def test_recorded_timeout_replays_without_inventing_a_response(self):
        first = planner_recording.load_session(self.original['id'], self.recordings)[0]
        agent = AdaptiveRuntime(self.helper.runtime, azure_plan, clock=lambda: 1000,
                                planner_profile={'adapter': 'azure'}, usage_policy=first['context']['usage_policy'])
        def timeout(request):
            raise httpx.ReadTimeout('Synthetic offline timeout', request=request)
        with patch.object(planner_recording, 'ROOT', self.root), patch.dict(os.environ, {
                'INVESTIGATOR_RECORD_PLANNER': '1', 'AZURE_OPENAI_ENDPOINT': 'https://offline.openai.azure.com',
                'AZURE_OPENAI_DEPLOYMENT': 'offline-fixture', 'AZURE_OPENAI_API_KEY': 'offline-placeholder-credential'}), \
                patch('openai.DefaultHttpxClient', side_effect=lambda **kw: DefaultHttpxClient(
                    transport=httpx.MockTransport(timeout), **kw)):
            self.original = agent.run(agent.create(self.helper.envelope, 'timeout-session')['id'])
        result = self.replay('timeout-replay')
        self.assertEqual(result['status'], 'MATCHED', result['differences'])
        self.assertEqual(result['session']['stop_reason'], 'PLANNER_FAILED')
        self.assertEqual(result['session']['planner_calls'], 1)
        entry = row(result, planner_recording.load_session(self.original['id'], self.recordings))
        self.assertEqual(entry['provider_errors']['timeout'], 1)


if __name__ == '__main__':
    unittest.main()

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
from openai import DefaultHttpxClient

from investigator import planner_recording as recording
from ticket_planner import azure_generate


class RecordingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.addCleanup(patch.stopall)
        patch.object(recording, 'ROOT', self.root).start()
        patch.dict(os.environ, {recording.FLAG: '1', 'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_DEPLOYMENT': 'test-deployment', 'AZURE_OPENAI_API_KEY': 'synthetic-private-credential'}).start()
        self.sent = []
        self.body = b'{"id":"r1","object":"response","status":"completed","model":"test","output":[],"usage":null}'
        self.status = 200
        def transport(request):
            self.sent.append(request.content)
            return httpx.Response(self.status, content=self.body, headers={'Authorization': 'never-save-headers'})
        patch('openai.DefaultHttpxClient', side_effect=lambda **kw: DefaultHttpxClient(
            transport=httpx.MockTransport(transport), **kw)).start()

    def calls(self):
        return recording.load_session('session', self.root / '.local/planner-recordings')

    def invoke(self):
        with recording.recording({'session_id': 'session', 'planner_call': 1,
                                  'context_version': 'context-1', 'budget': {'remaining': 2},
                                  'reservation': {'key': 'planner:1', 'output_tokens': 1500}}):
            azure_generate({'unicode': '\u03bb', 'content': 'retained definition'})

    def test_exact_transport_bytes_even_when_decoding_fails(self):
        with self.assertRaises(ValueError):
            self.invoke()
        call = self.calls()[0]
        self.assertEqual(call['bodies']['request.body'], self.sent[0])
        self.assertEqual(call['bodies']['response.body'], self.body)
        request = json.loads(self.sent[0])
        self.assertIn('instructions', request)
        self.assertIn('text', request)
        self.assertEqual(json.loads(request['input'])['unicode'], '\u03bb')
        self.assertEqual(call['context']['context_version'], 'context-1')
        self.assertEqual(call['context']['reservation']['key'], 'planner:1')
        all_bytes = b''.join(p.read_bytes() for p in (self.root / '.local').rglob('*') if p.is_file())
        self.assertNotIn(b'synthetic-private-credential', all_bytes)
        self.assertNotIn(b'never-save-headers', all_bytes)

    def test_http_error_body_preserved_without_retry(self):
        self.status = 429
        self.body = b'{"error":{"message":"test limit","type":"rate_limit"}}'
        with self.assertRaises(Exception):
            self.invoke()
        self.assertEqual(len(self.sent), 1)
        self.assertEqual(self.calls()[0]['bodies']['response.body'], self.body)
        self.assertEqual(json.loads(self.calls()[0]['bodies']['response-status.json'])['status_code'], 429)

    def test_secret_in_request_is_blocked_before_transport(self):
        with self.assertRaises(Exception):
            with recording.recording({'session_id': 'session'}):
                azure_generate({'content': 'synthetic-private-credential'})
        self.assertEqual(self.sent, [])
        self.assertFalse(self.calls()[0]['manifest']['request_captured'])

    def test_secret_in_response_is_withheld_explicitly(self):
        self.body = b'{"error":"synthetic-private-credential"}'
        with self.assertRaises(Exception):
            self.invoke()
        self.assertFalse(self.calls()[0]['manifest']['response_captured'])
        self.assertEqual(self.calls()[0]['manifest']['exclusion'], 'SECRET_DETECTED')
        self.assertFalse(any(p.name == 'response.body' for p in self.root.rglob('*')))

    def test_timeout_preserves_request_and_marks_response_missing(self):
        def timeout(request):
            self.sent.append(request.content)
            raise httpx.ReadTimeout('synthetic timeout', request=request)
        with patch('openai.DefaultHttpxClient', side_effect=lambda **kw: DefaultHttpxClient(
                transport=httpx.MockTransport(timeout), **kw)):
            with self.assertRaises(Exception):
                self.invoke()
        call = self.calls()[0]
        self.assertEqual(call['bodies']['request.body'], self.sent[0])
        self.assertFalse(call['manifest']['response_captured'])
        self.assertEqual(call['manifest']['error_type'], 'APITimeoutError')

    def test_off_by_default_and_context_reset(self):
        os.environ.pop(recording.FLAG)
        with recording.recording({'session_id': 'session'}) as record:
            self.assertIsNone(record)
            self.assertEqual(recording.http_options(), {})
        self.assertFalse((self.root / '.local').exists())
        self.assertIsNone(recording.ACTIVE.get())

    def test_loader_detects_tampering_and_interruption(self):
        with self.assertRaises(ValueError):
            self.invoke()
        path = next((self.root / '.local/planner-recordings').glob('*/response.body'))
        path.write_bytes(b'changed')
        with self.assertRaisesRegex(recording.RecordingError, 'INTEGRITY'):
            self.calls()
        path.with_name('manifest.json').unlink()
        with self.assertRaisesRegex(recording.RecordingError, 'INTERRUPTED'):
            self.calls()

    def test_credential_patterns_rejected_without_echo(self):
        for value in [b'Password=examplepassword', b'Bearer examplecredential',
                      b'{"api_key":"unconfiguredcredential"}']:
            with self.assertRaisesRegex(recording.RecordingError, '^RECORDING_SECRET_DETECTED$'):
                recording._safe(value)

    def test_runtime_reservation_and_state_are_reconstructable(self):
        import test_runtime_governance as fixture
        from investigator.adaptive_planner import azure_plan
        helper = fixture.GovernanceTests()
        helper.setUp()
        self.addCleanup(helper.doCleanups)
        helper.agent.planner = azure_plan
        proposal = {'action': 'STOP', 'candidate_id': None, 'question': None,
                    'stop_reason': 'NO_USEFUL_TEST', 'hypotheses': []}
        self.body = json.dumps({'id': 'r1', 'object': 'response', 'status': 'completed',
            'model': 'test', 'output': [{'type': 'function_call', 'name': 'investigation_action',
            'call_id': 'c1', 'arguments': json.dumps(proposal)}], 'usage': None}).encode()
        session = helper.agent.run(helper.create())
        self.assertEqual(session['stop_reason'], 'NO_USEFUL_TEST')
        calls = recording.load_session(session['id'], self.root / '.local/planner-recordings')
        self.assertEqual(len(calls), 1)
        context = calls[0]['context']
        self.assertEqual(context['state']['planner_calls'], 1)
        self.assertEqual(context['budget']['reserved_today']['planner_calls'], 1)
        self.assertEqual(context['reservation']['output_tokens'], 1500)
        self.assertEqual(context['context_version'], session['context_hash'])
        self.assertNotIn('token', context['state'])
        self.assertEqual(json.loads(json.loads(calls[0]['bodies']['request.body'])['input']), context['payload'])


if __name__ == '__main__':
    unittest.main()

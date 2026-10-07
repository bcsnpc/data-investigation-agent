"""OTLP schema and sealed-event conservation; no provider or estate transport."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from investigator import tape_trace as trace


class TapeTraceTests(unittest.TestCase):
    def example(self):
        events = []
        def event(kind, at, body):
            raw = json.dumps(body).encode()
            events.append({'kind': kind, 'at': at, 'ordinal': len(events) + 1,
                           'body': base64.b64encode(raw).decode(), 'sha256': hashlib.sha256(raw).hexdigest()})
        event('BOOTSTRAP', 1, {})
        event('OPERATION_START', 2, {'name': 'run'})
        event('PROVIDER_REQUEST', 3, {'model': 'test-model', 'input': 'must not appear in trace'})
        event('PROVIDER_RESPONSE', 4, {'status': 200, 'body': base64.b64encode(json.dumps(
            {'model': 'test-model', 'usage': {'input_tokens': 20, 'output_tokens': 5}}).encode()).decode()})
        request = {'session_id': 's', 'key': 'read', 'operation': 'reserve', 'args': ['cloud']}
        event('BUDGET', 4.1, {'phase': 'BEFORE', 'request': request, 'state': {'reservation': None}})
        event('BUDGET', 4.2, {'phase': 'AFTER', 'request': request, 'state': {'reservation': ['RESERVED']}})
        event('OPERATION_END', 9, {'name': 'run'})
        runtime = [
            {'kind': 'PROCESS_READ_RESERVED', 'created': '1970-01-01T00:00:05Z', 'detail': {'tool': 'bounded_sql'}},
            {'kind': 'PROCESS_READ_RESERVED', 'created': '1970-01-01T00:00:06Z', 'detail': {'tool': 'permission'}},
            {'kind': 'PROCESS_READ_RECORDED', 'created': '1970-01-01T00:00:07Z',
             'detail': {'tool': 'permission', 'status': 'AVAILABLE', 'guard_receipt': 'guard-1'}},
            {'kind': 'PROCESS_READ_RECORDED', 'created': '1970-01-01T00:00:08Z',
             'detail': {'tool': 'identity', 'status': 'AVAILABLE', 'logical_tool': 'bounded_sql',
                        'logical_receipt': {'receipt_id': 'read-1'}}}]
        event('FINAL', 10, {'result': {'physical_calls': 2, 'cloud_calls': 1, 'events': runtime,
            'observations': [{'id': 'read-1', 'execution_surface': {'identity': 'reader', 'engine': 'SQL'},
                              'surface_attestation': {'status': 'PARTIAL'}, 'layer_role': 'SOURCE'}]}})
        return events

    def convert(self,events=None):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'tape.json'; path.write_text('sealed synthetic fixture')
            tape = SimpleNamespace(path=path, events=events or self.example(), version='test', engine_revision='abc')
            with patch.object(trace, 'Tape', return_value=tape):
                return trace.convert(path)

    def test_all_physical_receipts_export_even_without_direct_receipt_id(self):
        value, summary = self.convert()
        spans = value['resourceSpans'][0]['scopeSpans'][0]['spans']
        probes = [s for s in spans if s['name'] == 'probe']
        self.assertEqual(len(probes), 2)
        ids = [next(a['value']['stringValue'] for a in s['attributes'] if a['key'] == 'dia.receipt.id') for s in probes]
        self.assertEqual(ids, ['guard-1', 'read-1'])
        self.assertEqual(summary['recorded_physical_requests'], 2)
        self.assertEqual(summary['stages']['walk']['model_calls'], 1)
        self.assertEqual(summary['stages']['walk']['input_tokens'], 20)
        self.assertEqual(summary['stages']['walk']['physical_admissions'], 1)
        self.assertEqual(summary['network_calls'], 0)
        self.assertNotIn('must not appear', json.dumps(value))

    def test_official_schema_rejects_unknown_fields(self):
        value, _ = self.convert()
        value['resourceSpans'][0]['scopeSpans'][0]['spans'][0]['inventedField'] = True
        with self.assertRaises(Exception): trace.validate(value)

    def test_tree_rejects_missing_parent_and_interval_escape(self):
        value, _ = self.convert(); spans = value['resourceSpans'][0]['scopeSpans'][0]['spans']
        bad = copy.deepcopy(value); bad['resourceSpans'][0]['scopeSpans'][0]['spans'][1]['parentSpanId'] = 'f' * 16
        with self.assertRaisesRegex(ValueError, 'parent is missing'): trace.validate(bad)
        spans[-1]['endTimeUnixNano'] = '11000000000'
        with self.assertRaisesRegex(ValueError, 'leaves its recorded parent'): trace.validate(value)

    def test_footer_uses_counts_and_names_missing_timing(self):
        _, summary = self.convert(); text = trace.footer(summary)
        self.assertIn('walk: 7.000s, 1 model calls, 20/5 input/output tokens, 1 physical admissions', text)
        self.assertIn('source: timing not recorded separately', text)
        self.assertIn('currency cost not recorded', text)

    def test_new_stage_events_attribute_source_probes_without_guessing_tool_names(self):
        events=self.example();final=json.loads(base64.b64decode(events[-1]['body']))
        runtime=final['result']['events']
        runtime[:0]=[{'kind':'PROCESS_STAGE_STARTED','created':'1970-01-01T00:00:02Z',
                      'detail':{'stage':'source','operation':'ingestion'}}]
        runtime.append({'kind':'PROCESS_STAGE_FINISHED','created':'1970-01-01T00:00:09Z',
                        'detail':{'stage':'source','operation':'ingestion','error_type':None}})
        raw=json.dumps(final).encode();events[-1]['body']=base64.b64encode(raw).decode();events[-1]['sha256']=hashlib.sha256(raw).hexdigest()
        value,summary=self.convert(events)
        self.assertEqual(summary['recorded_stages'],['source'])
        self.assertEqual(summary['stages']['source']['model_calls'],1)
        self.assertEqual(summary['stages']['source']['wall_seconds'],7)
        spans=value['resourceSpans'][0]['scopeSpans'][0]['spans']
        source=next(s for s in spans if s['name']=='source')
        self.assertTrue(all(s['parentSpanId']==source['spanId'] for s in spans if s['name'] in ('model','probe')))


if __name__ == '__main__': unittest.main()

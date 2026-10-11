import json
import sqlite3
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from investigator.agent_journal import Journal
from investigator.agent_provider import GovernedDecision


class Store:
    def __init__(self, path): self.path = path
    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path); db.row_factory = sqlite3.Row
        try:
            with db: yield db
        finally: db.close()


class Governor:
    def __init__(self): self.events = []
    def reserve(self, db, session, key, kind, size, **bounds):
        self.events.append(('reserve', key, size, bounds))
    def settle(self, db, session, key, usage, **flags):
        self.events.append(('settle', key, usage, flags))


class Boundaries(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.store = Store(Path(self.tmp.name) / 'store.sqlite')
        with self.store.connect() as db:
            db.execute('CREATE TABLE adaptive_usage(session_id TEXT,reservation_key TEXT)')

    def test_progress_records_public_summary_arguments_and_receipts(self):
        journal = Journal(self.store, 'ticket', now=lambda: 1)
        identity = journal.persist({'event': 'TOOL_RESULT', 'summary': 'Read the definition',
            'tool': 'lineage', 'arguments': {'target_id': 't'},
            'result': {'status': 'AVAILABLE', 'evidence_ids': ['receipt-a']}})
        rows = journal.read()
        self.assertEqual(rows[0]['id'], identity)
        self.assertEqual(rows[0]['result_ids'], ['receipt-a'])
        self.assertEqual(rows[0]['arguments'], {'target_id': 't'})

    def test_projection_precedes_disk_and_integrity_is_checked(self):
        journal = Journal(self.store, 'ticket', projection=lambda value:
                          json.loads(json.dumps(value).replace('private-value', 'projected')), now=lambda: 1)
        journal.persist({'event': 'STARTED', 'summary': 'private-value'})
        self.assertNotIn(b'private-value', self.store.path.read_bytes())
        with self.store.connect() as db:
            db.execute("UPDATE agent_progress SET hash='wrong'")
        with self.assertRaisesRegex(Exception, 'integrity'): journal.read()

    def runtime(self, cap=32000):
        return SimpleNamespace(config={}, governor=Governor(), runtime=SimpleNamespace(db=self.store.connect),
            generation_options={'timeout_seconds': 45, 'max_output_tokens': 1500,
                                'max_payload_characters': cap})

    def test_provider_reserves_full_wire_body_then_settles_usage(self):
        runtime = self.runtime()
        def generate(payload, **options):
            self.assertEqual(len(runtime.governor.events), 1)
            self.assertIn('decision', options['schema']['properties'])
            return {'decision': {'action': 'HOLD'}}, {'usage': {'output_tokens': 20}}
        with patch('investigator.agent_provider.input_characters', side_effect=lambda v: len(json.dumps(v))):
            result = GovernedDecision(runtime, 's', generate=generate)({'a': 'b'}, instructions='Choose.', schema={'type':'object','properties':{},'required':[],'additionalProperties':False})
        self.assertEqual(result, {'action': 'HOLD'})
        self.assertEqual(runtime.governor.events[0][0], 'reserve')
        self.assertEqual(runtime.governor.events[-1][2], {'output_tokens': 20})

    def test_request_bound_refuses_before_reservation_or_dispatch(self):
        runtime = self.runtime(8000)
        generate = lambda *a, **k: self.fail('dispatched oversized request')
        with self.assertRaisesRegex(ValueError, 'REQUEST_BOUND'):
            GovernedDecision(runtime, 's', generate=generate)({'text': 'x'*9000}, instructions='Choose.', schema={'type':'object','properties':{},'required':[],'additionalProperties':False})
        self.assertEqual(runtime.governor.events, [])

    def test_agent_override_dispatches_above_profile_and_refuses_above_approved_bound(self):
        runtime = self.runtime()
        runtime.config = {'_estate': {'investigation': {'mode': 'AGENT', 'input_characters_per_request': 150000}}}
        seen=[]
        def generate(*args, **kwargs):
            seen.append(kwargs['max_request_characters'])
            return {'decision': {'action':'HOLD'}}, {'usage': {'input_tokens':1,'output_tokens':1}}
        decision=GovernedDecision(runtime, 's', generate=generate)
        contract={'type':'object','properties':{},'required':[],'additionalProperties':False}
        decision({'text':'x'*40000}, instructions='Choose.', schema=contract)
        self.assertEqual(seen,[150000])
        with self.assertRaisesRegex(ValueError,'AGENT_PROVIDER_REQUEST_BOUND'):
            decision({'text':'x'*150000}, instructions='Choose.', schema=contract)
        self.assertEqual(seen,[150000])

    def test_provider_failure_keeps_uncertain_reservation(self):
        runtime = self.runtime()
        def generate(*args, **kwargs): raise ConnectionError('no response')
        with self.assertRaises(ConnectionError):
            GovernedDecision(runtime, 's', generate=generate)({}, instructions='Choose.', schema={'type':'object','properties':{},'required':[],'additionalProperties':False})
        self.assertTrue(runtime.governor.events[-1][3]['uncertain'])

    def test_restart_does_not_reset_model_call_cap(self):
        with self.store.connect() as db:
            db.executemany('INSERT INTO adaptive_usage VALUES(?,?)',
                [('s', 'agent-model:'+str(i)) for i in range(1,26)])
        runtime = self.runtime()
        with self.assertRaisesRegex(ValueError, 'MODEL_CALL_CAP'):
            GovernedDecision(runtime, 's', generate=lambda *a, **k: self.fail('dispatched'))({}, instructions='Choose.', schema={'type':'object','properties':{},'required':[],'additionalProperties':False})
        self.assertEqual(runtime.governor.events, [])


if __name__ == '__main__': unittest.main()

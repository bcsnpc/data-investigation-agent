import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock

from import_fixture import build
from investigator.native_identity import KEY, make
from investigator.onboarding import Conflict
from verify_reader_runtime import run, compile_fixture, FixtureStore
from test_reader_execution import config, READER, MODEL, WORKSPACE


class ReaderRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / 'runtime.sqlite'
        self.bundle = build({'tables': [{'name': 'Events', 'columns': [{'name': 'Id', 'type': 'int64'}, {'name': 'Flag', 'type': 'boolean'}],
            'rows': [[1, True], [2, False]], 'measures': [{'name': 'New Metric', 'expression': 'COUNTROWS(Events)'}]}], 'relationships': []})
        self.scope = {'table': 'Events', 'measures': ['New Metric'], 'filter_column': 'Id', 'filter_values': [1, 2],
                      'dimension': 'Flag', 'record_columns': ['Id', 'Flag'], 'key_columns': ['Id']}
        self.transport = MagicMock(side_effect=self.response)

    def response(self, cfg, request):
        if request.get('backend') == 'native_records':
            rows = [{'[c0]': 1, '[c1]': True, '[multiplicity]': 1}, {'[c0]': 2, '[c1]': False, '[multiplicity]': 1}]
        elif request.get('dimension_id'):
            rows = [{'[dimension]': True, '[m0]': 1}, {'[dimension]': False, '[m0]': 1}]
        else: rows = [{'[m0]': 2}]
        raw = {'results': [{'tables': [{'rows': rows}]}]}
        return dict(raw, **{KEY: make(raw, request, READER)})

    def execute(self, **kwargs):
        return run(config(), self.bundle, MODEL, self.scope, self.database, 'verify', execute=self.transport, **kwargs)

    def test_durable_three_tools_and_replay_make_no_new_calls(self):
        first = self.execute()
        self.assertTrue(first['summary']['runtime_verification_passed'])
        self.assertFalse(first['summary']['live_acceptance_ready'])
        self.assertFalse(first['summary']['generation_proven'])
        self.assertEqual(self.transport.call_count, 3)
        self.assertEqual(self.execute()['summary'], first['summary'])
        self.assertEqual(self.execute(status_only=True)['summary'], first['summary'])
        self.assertEqual(self.transport.call_count, 3)

    def test_bad_scope_cannot_make_any_query(self):
        self.scope['filter_values'] = [True]
        with self.assertRaises(ValueError): self.execute()
        self.transport.assert_not_called()

    def test_changed_profile_cannot_relabel_history(self):
        self.execute(); cfg = config(); cfg['fabric']['native_reader']['account'] = 'another@example.test'
        with self.assertRaises(Conflict):
            run(cfg, self.bundle, MODEL, self.scope, self.database, 'verify', execute=self.transport, status_only=True)
        self.assertEqual(self.transport.call_count, 3)

    def test_changed_manifest_requires_separate_context(self):
        self.execute(); spec = copy.deepcopy(self.bundle['spec']); spec['tables'][0]['rows'].append([3, True]); self.bundle = build(spec)
        with self.assertRaises(Conflict): self.execute()
        self.assertEqual(self.transport.call_count, 3)

    def test_record_content_mismatch_is_not_pass(self):
        def changed(cfg, request):
            raw = self.response(cfg, request)
            if request.get('backend') == 'native_records':
                raw.pop(KEY); raw['results'][0]['tables'][0]['rows'][0]['[c0]'] = 99
                raw[KEY] = make(raw, request, READER)
            return raw
        self.transport.side_effect = changed
        result = self.execute()
        self.assertFalse(result['summary']['projected_fixture_rows_match'])
        self.assertFalse(result['summary']['runtime_verification_passed'])

    def test_interrupted_remote_call_is_not_automatically_repeated(self):
        self.transport.side_effect = TimeoutError('uncertain')
        first = self.execute(); self.assertEqual(first['summary']['status'], 'HELD')
        with self.assertRaises(Conflict): self.execute()
        self.transport.assert_called_once()

    def test_manifest_does_not_claim_report_onboarding(self):
        model, _ = compile_fixture(self.bundle, WORKSPACE, MODEL, self.scope)
        self.assertEqual(model['reports'], [])
        self.assertFalse(model['context']['provenance']['report_context_available'])
        self.assertNotIn('rows', json.dumps(model))

    def test_sealed_receipt_tamper_breaks_history(self):
        first = self.execute(); model, _ = compile_fixture(self.bundle, WORKSPACE, MODEL, self.scope)
        store = FixtureStore(self.database, model)
        with store.connect() as db:
            db.execute('UPDATE native_diagnostics SET result=? WHERE id=?', ('{}', first['summary']['receipts'][0]))
        with self.assertRaises(Conflict): self.execute(status_only=True)
        self.assertEqual(self.transport.call_count, 3)

    def test_deleted_seal_cannot_be_accepted_as_legacy_history(self):
        self.execute(); model, _ = compile_fixture(self.bundle, WORKSPACE, MODEL, self.scope)
        store = FixtureStore(self.database, model)
        with store.connect() as db: db.execute('DELETE FROM aggregate_receipt_seals')
        with self.assertRaises(Conflict): self.execute(status_only=True)
        self.assertEqual(self.transport.call_count, 3)


if __name__ == '__main__': unittest.main()

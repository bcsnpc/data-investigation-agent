import base64
import copy
from decimal import Decimal
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from investigator import native_identity as identity, native_diagnostics as native, record_readback as records
from investigator.adaptive_candidates import catalog, observation
from investigator.adaptive_projection import read as project
from investigator.receipt_integrity import verify as verify_seal
from investigator.onboarding import Conflict
from metadata_config import load_config, ROOT
from run_native_diagnostic import execute, transport
import test_native_diagnostics as native_fixture
import test_keyed_readback as record_fixture
import test_adaptive_investigation as adaptive_fixture

TENANT = '11111111-1111-1111-1111-111111111111'
PRINCIPAL = '22222222-2222-2222-2222-222222222222'
MODEL = '33333333-3333-3333-3333-333333333333'
WORKSPACE = '44444444-4444-4444-4444-444444444444'
READER = {'mode': 'isolated_reader', 'tenant_id': TENANT, 'account': 'reader@example.test',
          'principal_id': PRINCIPAL, 'model_ids': [MODEL]}


def config():
    value = json.loads((ROOT / 'infra/metadata/development.json').read_text(encoding='utf-8-sig'))
    value['fabric'].update(workspace_id=WORKSPACE, native_reader=copy.deepcopy(READER))
    value['fabric']['auth']['tenant_id'] = TENANT
    return value


def issued(oid=PRINCIPAL):
    claims = {'oid': oid, 'tid': TENANT, 'upn': READER['account'], 'aud': 'https://analysis.windows.net/powerbi/api'}
    return 'test.' + base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip('=') + '.test'


class ReaderExecutionTests(unittest.TestCase):
    def setUp(self):
        self.model, self.plan = native_fixture.fixture()
        self.model.update(workspace=WORKSPACE, native_id=MODEL)
        self.request = native.build(self.model, self.plan)
        self.raw = native_fixture.response([{'[m0]': 42}])

    def bound(self, raw=None, request=None):
        raw = copy.deepcopy(self.raw if raw is None else raw)
        return dict(raw, **{identity.KEY: identity.make(raw, request or self.request, READER)})

    def test_config_accepts_reader_and_preserves_metadata_login(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'config.json'; path.write_text(json.dumps(config()))
            loaded = load_config(path)
        self.assertEqual(loaded['fabric']['native_reader'], READER)
        self.assertEqual(loaded['fabric']['auth']['mode'], 'fabric_cli')

    def test_config_rejects_secret_unknown_mode_or_mismatched_tenant(self):
        for change in [{'password': 'secret'}, {'mode': 'fabric_cli'}, {'tenant_id': PRINCIPAL},
                       {'principal_id': ''}, {'account': 'reader @example.test'}, {'model_ids': []},
                       {'model_ids': [MODEL, MODEL]}, {'model_ids': ['not-a-model']}, {'model_ids': MODEL}]:
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                value = config(); value['fabric']['native_reader'].update(change)
                path = Path(directory) / 'config.json'; path.write_text(json.dumps(value))
                with self.assertRaises(ValueError): load_config(path)

    def test_legacy_receipt_has_no_fabricated_principal(self):
        self.assertIsNone(identity.observed(self.raw, self.request))
        self.assertNotIn('execution_identity', native.extract(self.raw, self.request))

    def test_exact_decimal_blank_and_boolean_binding(self):
        for value in (Decimal('123456789.123456789012345'), None, True, 0):
            raw = native_fixture.response([{'[m0]': value}]); bound = self.bound(raw)
            result = native.extract(bound, self.request)
            self.assertEqual(result['execution_identity']['principal_id'], PRINCIPAL)
            self.assertFalse(result['execution_identity']['effective_identity_verified'])

    def test_query_target_response_and_extra_identity_fields_rejected(self):
        for field, value in [('query_hash', 'bad'), ('model_id', PRINCIPAL), ('workspace_id', PRINCIPAL),
                             ('response_hash', 'bad'), ('captured_at', '2026-09-15'), ('token', 'secret')]:
            with self.subTest(field=field):
                raw = self.bound(); raw[identity.KEY][field] = value
                with self.assertRaises(ValueError): native.extract(raw, self.request)
        raw = self.bound(); raw['results'][0]['tables'][0]['rows'][0]['[m0]'] = 99
        with self.assertRaises(ValueError): native.extract(raw, self.request)

    def test_observation_cannot_satisfy_another_principal(self):
        raw = self.bound()
        for field, value in [('principal_id', TENANT), ('account', 'publisher@example.test')]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                identity.require(raw, self.request, dict(READER, **{field: value}))

    def test_configured_reader_missing_metadata_is_rejected(self):
        with self.assertRaises(ValueError): identity.require(self.raw, self.request, READER)

    def test_transport_preserves_precision_and_uses_reader_only(self):
        raw = b'{"results":[{"tables":[{"rows":[{"[m0]":123.123456789012345}]}]}]}'
        with patch('connect_fixture_reader.application'), patch('connect_fixture_reader.token', return_value=issued()) as token, \
             patch('run_native_diagnostic.FabricCliTokens') as publisher, patch('run_native_diagnostic.build_opener') as opener:
            opener.return_value.open.return_value.__enter__.return_value.read.return_value = raw
            result = json.loads(execute(self.request, TENANT, READER), parse_float=Decimal)
            token.assert_called_once(); publisher.assert_not_called()
            http = opener.return_value.open.call_args.args[0]
            self.assertEqual(http.get_header('Authorization'), 'Bearer ' + issued())
            self.assertNotIn('impersonatedUserName', json.loads(http.data))
        value = native.extract(result, self.request)
        self.assertEqual(value['rows'][0]['[m0]']['value'], '123.123456789012345')
        self.assertEqual(value['execution_identity']['account'], READER['account'])

    def test_wrong_object_id_never_dispatches_or_falls_back(self):
        with patch('connect_fixture_reader.application'), patch('connect_fixture_reader.token', return_value=issued(TENANT)), \
             patch('run_native_diagnostic.FabricCliTokens') as publisher, patch('run_native_diagnostic.build_opener') as opener:
            with self.assertRaises(ValueError): execute(self.request, TENANT, READER)
            publisher.assert_not_called(); opener.assert_not_called()

    def test_missing_reader_token_never_dispatches_or_falls_back(self):
        with patch('connect_fixture_reader.application'), patch('connect_fixture_reader.token', side_effect=RuntimeError('No reader')), \
             patch('run_native_diagnostic.FabricCliTokens') as publisher, patch('run_native_diagnostic.build_opener') as opener:
            with self.assertRaises(RuntimeError): execute(self.request, TENANT, READER)
            publisher.assert_not_called(); opener.assert_not_called()

    def test_outside_allowlist_rejected_before_token_and_worker(self):
        request = dict(self.request, native_model_id=PRINCIPAL)
        with patch('connect_fixture_reader.application') as app:
            with self.assertRaises(ValueError): execute(request, TENANT, READER)
            app.assert_not_called()
        with patch('run_native_diagnostic.subprocess.run') as worker:
            with self.assertRaises(ValueError): transport(config(), request)
            worker.assert_not_called()

    def test_wrong_workspace_rejected_before_worker(self):
        with patch('run_native_diagnostic.subprocess.run') as worker:
            with self.assertRaises(ValueError): transport(config(), dict(self.request, workspace=MODEL))
            worker.assert_not_called()

    def test_worker_output_cannot_omit_reader_binding(self):
        with patch('run_native_diagnostic.subprocess.run') as worker:
            worker.return_value = MagicMock(returncode=0, stdout=json.dumps(self.raw))
            with self.assertRaises(ValueError): transport(config(), self.request)
            self.assertEqual(worker.call_count, 1)

    def test_worker_bound_output_accepted_without_extra_queries(self):
        with patch('run_native_diagnostic.subprocess.run') as worker:
            worker.return_value = MagicMock(returncode=0, stdout=json.dumps(self.bound()))
            result = transport(config(), self.request)
            self.assertEqual(identity.observed(result, self.request)['principal_id'], PRINCIPAL)
            self.assertEqual(worker.call_count, 1)

    def test_native_receipt_identity_is_sealed(self):
        with tempfile.TemporaryDirectory() as directory:
            store = MagicMock(); store.get.return_value = self.model
            store.connect.side_effect = lambda: native_fixture.database(Path(directory) / 'catalog.sqlite')
            result = native.run(store, self.plan, lambda request: self.bound(request=request))
            self.assertEqual(result['status'], 'COMPLETED')
            self.assertFalse(result['result']['effective_identity_verified'])
            with store.connect() as db:
                self.assertEqual(verify_seal(db, 'native', result['id'])['state'], 'SEALED')
                saved = json.loads(db.execute('SELECT result FROM native_diagnostics').fetchone()[0])
                saved['execution_identity']['account'] = 'other@example.test'
                db.execute('UPDATE native_diagnostics SET result=?', (json.dumps(saved),))
                with self.assertRaises(Conflict): verify_seal(db, 'native', result['id'])

    def test_record_identity_persisted_and_integrity_checked(self):
        helper = record_fixture.ReadbackTests(); helper.setUp(); self.addCleanup(helper.doCleanups)
        helper.model.update(workspace=WORKSPACE, native_id=MODEL)
        helper.config['fabric']['workspace_id'] = WORKSPACE
        def execute_records(request):
            return self.bound(helper.native_rows([('A', '10', 1)]), request)
        result = records.run(helper.store, helper.nplan, helper.config, 'native_records', execute_records)
        self.assertEqual(result['status'], 'COMPLETED')
        saved = records.read(helper.store, 'model', result['id'])
        self.assertEqual(saved['result']['execution_identity']['principal_id'], PRINCIPAL)
        with helper.store.connect() as db:
            raw = json.loads(db.execute('SELECT result FROM record_readbacks WHERE id=?', (result['id'],)).fetchone()[0])
            raw['execution_identity']['principal_id'] = TENANT
            db.execute('UPDATE record_readbacks SET result=? WHERE id=?', (json.dumps(raw), result['id']))
        with self.assertRaises(ValueError): records.read(helper.store, 'model', result['id'])

    def test_model_rejected_before_adaptive_planner(self):
        helper = adaptive_fixture.AdaptiveTests(); helper.setUp(); self.addCleanup(helper.doCleanups)
        helper.config['fabric']['native_reader'] = READER
        with self.assertRaises(Conflict): catalog(helper.store, helper.config, helper.envelope)
        helper.planner.assert_not_called()

    def test_adaptive_observation_keeps_identity_without_proof_upgrade(self):
        candidate = {'id': 'candidate', 'tool': 'native', 'measure_id': 'metric', 'dimension_id': None, 'plan': {}}
        receipt = {'id': 'receipt', 'status': 'COMPLETED', 'request_hash': 'hash',
                   'result': native.extract(self.bound(), self.request)}
        result = observation(candidate, {'id': 'run', 'steps': [{'result': receipt}]})
        self.assertEqual(result['execution_identity']['principal_id'], PRINCIPAL)
        self.assertFalse(result['proof_eligible'])

    def test_runtime_injected_transport_cannot_bypass_reader_requirement(self):
        from investigator.native_identity import guarded
        callback = MagicMock(return_value=self.raw)
        with self.assertRaises(ValueError): guarded(config(), self.request, callback)
        callback.assert_called_once()
        callback.reset_mock()
        with self.assertRaises(ValueError): guarded(config(), dict(self.request, native_model_id=TENANT), callback)
        callback.assert_not_called()

    def test_saved_adaptive_identity_is_excluded_from_planner_payload(self):
        helper = adaptive_fixture.AdaptiveTests(); helper.setUp(); self.addCleanup(helper.doCleanups)
        helper.model.update(workspace=WORKSPACE, native_id=MODEL)
        helper.config['fabric'].update(workspace_id=WORKSPACE, native_reader=READER)
        helper.envelope.update(source_tests=[], dimension_ids=[])
        helper.native.side_effect = lambda request: self.bound(request=request)
        seen = []
        def planner(payload):
            seen.append(payload)
            if payload['observations']: return adaptive_fixture.decision(), {}
            return adaptive_fixture.decision(payload['candidates'][0]['id']), {}
        helper.planner.side_effect = planner
        result = helper.agent.run(helper.create())
        self.assertEqual(result['observations'][0]['execution_identity']['principal_id'], PRINCIPAL)
        self.assertNotIn(READER['account'], json.dumps(seen))
        self.assertNotIn(PRINCIPAL, json.dumps(seen))
        technical = project(helper.store, 'model', result['id'])
        self.assertEqual(technical['outcome']['facts'][0]['execution_identity']['principal_id'], PRINCIPAL)
        self.assertFalse(technical['outcome']['cause_verified'])


if __name__ == '__main__': unittest.main()

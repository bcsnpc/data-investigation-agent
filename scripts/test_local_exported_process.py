import json
import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from investigator.local_bundle import LocalBundle, sha, UnsupportedLocalQuantity
from investigator.onboarding import Conflict
from investigator.adapters.local_process import LocalProcessAdapter
from investigator.process_debugging import attest

class LocalExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name); db = self.folder/'data.sqlite'
        with closing(sqlite3.connect(db)) as con, con:
            con.execute('CREATE TABLE t0000 (units TEXT, key INTEGER)')
            con.executemany('INSERT INTO t0000 VALUES (?,?)', [('0.1', 1), ('0.2', 1), (None, 2)])
        self.manifest = {'version': 'local-fixture-export-v1', 'engine': 'SQLITE_LOCAL_COPY', 'estate_id': 'fixture',
            'status': 'COMPLETE', 'tape_class': 'EXACT', 'database': {'file': 'data.sqlite', 'sha256': sha(db)}, 'assets': [
                {'asset_id': 'semantic-table', 'table': 't0000', 'role': 'SEMANTIC', 'rows': 3,
                 'columns': [{'name': 'units', 'logical_type': 'DECIMAL'}, {'name': 'key', 'logical_type': 'INTEGER'}],
                 'receipt': {'request_id': 'native-export'}}], 'definitions': [], 'missing_layers': []}
        self.write_manifest()
    def write_manifest(self):
        (self.folder/'manifest.json').write_text(json.dumps(self.manifest))
    def bundle(self): return LocalBundle(self.folder, sha(self.folder/'manifest.json'))
    def test_decimal_sum_and_blank_are_exact_actual_rows(self):
        bundle = self.bundle(); self.assertEqual(bundle.quantity('semantic-table', 'units')['value'], '0.3')
        self.assertIsNone(bundle.quantity('semantic-table', 'units', [{'column': 'key', 'operator': 'IN', 'values': []}])['value'])
        self.assertIsNone(bundle.quantity('semantic-table', 'units', [{'column': 'key', 'operator': 'IN', 'values': [2]}])['value'])
    def test_numeric_filter_does_not_coerce_boolean_or_null(self):
        for value in (True, None, '1'):
            with self.assertRaises(UnsupportedLocalQuantity):
                self.bundle().quantity('semantic-table', 'units', [{'column': 'key', 'operator': 'IN', 'values': [value]}])

    def test_read_only_connection(self):
        with self.bundle().connect() as db:
            with self.assertRaises(sqlite3.OperationalError): db.execute('DELETE FROM t0000')
    def test_changed_file_and_wal_overlay_refused(self):
        bundle = self.bundle(); (self.folder/'data.sqlite-wal').write_bytes(b'overlay')
        with self.assertRaises(Conflict): bundle.quantity('semantic-table', 'units')
        (self.folder/'data.sqlite-wal').unlink()
        with closing(sqlite3.connect(self.folder/'data.sqlite')) as db, db: db.execute("UPDATE t0000 SET units='4' WHERE key=1")
        with self.assertRaises(Conflict): bundle.quantity('semantic-table', 'units')
    def test_wrong_asset_column_and_numeric_type_never_fallback(self):
        bundle = self.bundle()
        for asset, column in [('guessed', 'units'), ('semantic-table', 'missing')]:
            with self.assertRaises(UnsupportedLocalQuantity): bundle.quantity(asset, column)
        self.manifest['assets'][0]['columns'][0]['logical_type'] = 'REAL'; self.write_manifest()
        with self.assertRaises(Conflict): self.bundle().quantity('semantic-table', 'units')
    def test_manifest_pin_schema_mismatch_and_projection_refusal(self):
        with self.assertRaises(Conflict): LocalBundle(self.folder, '0'*64)
        self.manifest['assets'][0]['columns'][0]['name'] = 'different'; self.write_manifest()
        with self.assertRaises(Conflict): self.bundle()
        self.manifest['tape_class'] = 'PRIVACY_PROJECTED'; self.write_manifest()
        with self.assertRaises(UnsupportedLocalQuantity): self.bundle()
    def adapter(self, expression="SUM('Activity'[units])"):
        from investigator.model_context import assets
        # model_context assets traverses all asset-bearing graph nodes.
        model = {'id': 'model', 'revision': 1, 'context': {'assets': []}, 'context_id': 'ctx'}
        catalog = [{'id': 'measure', 'parent_id': 'semantic-table', 'kind': 'Measure', 'metadata': {'expression': expression}},
            {'id': 'semantic-table', 'kind': 'SemanticTable', 'name': 'Activity'},
            {'id': 'column-key', 'parent_id': 'semantic-table', 'kind': 'SemanticColumn', 'name': 'key'}]
        self.records = []
        from investigator.onboarding import digest
        self.manifest.update(contexts=[{'model_id': 'model', 'revision': 1, 'context_id': 'ctx', 'context_hash': digest(model['context'])}],
            enterprise_context={'id': 'enterprise', 'hash': digest({'assets': []})}, estate_manifest_hash='a'*64)
        self.write_manifest()
        with patch('investigator.context_search.latest', return_value={'version': 'enterprise', 'assets': []}):
            adapter = LocalProcessAdapter(None, {'_estate': {'manifest_hash': 'new-local-installation', 'execution': {'source_manifest_hash': 'a'*64}}}, model, self.bundle(), record_evidence=lambda e: self.records.append(e) or 'local-read-1')
        return adapter, catalog
    def test_adapter_honest_local_probe_no_network_and_snapshot_caveat(self):
        adapter, catalog = self.adapter()
        with patch('investigator.adapters.local_process.assets', return_value=catalog), patch('socket.create_connection', side_effect=AssertionError('network forbidden')):
            probe = adapter.evaluate({'id': 'semantic-table', 'kind': 'presentation'}, 'measure', {'filters': [], 'dimension_ids': []})
        self.assertEqual(probe.value, {'quantity': '0.3'})
        self.assertEqual(attest(probe).evidence['surface_attestation']['coverage'], 'FULL')
        self.assertEqual(probe.execution_surface['engine'], 'SQLITE_LOCAL_COPY')
        self.assertEqual(probe.evidence['snapshot_alignment'], 'SNAPSHOT_UNVERIFIED')
        self.assertEqual(probe.evidence['native_export_receipt']['request_id'], 'native-export')
    def test_unsupported_dax_cross_table_and_grouping_refuse(self):
        adapter, catalog = self.adapter('DIVIDE(SUM(Activity[units]),COUNTROWS(Activity))')
        with patch('investigator.adapters.local_process.assets', return_value=catalog):
            self.assertEqual(adapter.evaluate({'id': 'semantic-table', 'kind': 'presentation'}, 'measure', {'filters': []}).status, 'NOT_COMPARABLE')
        adapter, catalog = self.adapter(); catalog[-1]['parent_id'] = 'other'
        with patch('investigator.adapters.local_process.assets', return_value=catalog):
            probe = adapter.evaluate({'id': 'semantic-table', 'kind': 'presentation'}, 'measure', {'filters': [{'column_id': 'column-key', 'values': [1]}]})
            self.assertEqual(probe.status, 'NOT_COMPARABLE')
        self.assertEqual(adapter.evaluate({'id': 'semantic-table', 'kind': 'presentation'}, 'measure', {'dimension_ids': ['column-key']}).status, 'NOT_COMPARABLE')
    def test_execution_switch_is_explicit_and_never_native(self):
        from investigator.adapters.estate_installation import transports
        native, source = transports({'_estate': {'execution': {'mode': 'LOCAL_EXPORTED'}}})
        for port in (native, source):
            with self.assertRaises(ValueError): port({})
        from investigator.adapters.local_process import create
        with self.assertRaises(Conflict): create(None, {}, {}, record_evidence=lambda e: 'x')

    def test_manifest_modes_are_orthogonal_closed_and_default_absent(self):
        from investigator.estate_manifest import validate
        from investigator.adapters.estate_installation import configuration
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads((root/'infra/estates/fixture.json').read_text())
        validate(manifest)
        self.assertNotIn('execution', configuration(manifest)['_estate'])
        self.assertNotIn('investigation', configuration(manifest)['_estate'])
        manifest['execution'] = {'mode': 'LOCAL_EXPORTED', 'bundle': str(self.folder), 'manifest_sha256': sha(self.folder/'manifest.json'), 'source_manifest_hash': 'a'*64}
        manifest['investigation'] = {'mode': 'AGENT', 'step_cap': 25, 'wall_seconds': 900}
        validate(manifest)
        config = configuration(manifest)
        self.assertEqual(config['_estate']['execution'], manifest['execution'])
        self.assertNotEqual(config['_estate']['manifest_hash'], config['_estate']['execution']['source_manifest_hash'])
        self.assertEqual(config['_estate']['investigation'], manifest['investigation'])
        manifest['execution']['native_fallback'] = True
        with self.assertRaises(ValueError): validate(manifest)
        manifest['execution'].pop('native_fallback'); manifest['investigation']['step_cap'] = 26
        with self.assertRaises(ValueError): validate(manifest)

    def test_context_pins_and_definition_bytes_cannot_be_relabelled(self):
        adapter, _ = self.adapter()
        model = adapter.model
        self.manifest['contexts'][0]['context_hash'] = 'wrong'
        self.write_manifest()
        with patch('investigator.context_search.latest', return_value={'version': 'enterprise', 'assets': []}):
            with self.assertRaises(Conflict): LocalProcessAdapter(None, adapter.config, model, self.bundle(), record_evidence=lambda e: 'x')
        definition = self.folder/'definition-0000.txt'; definition.write_text('retained definition')
        self.manifest['definitions'] = [{'file': definition.name, 'sha256': sha(definition)}]; self.write_manifest()
        bundle = self.bundle(); definition.write_text('changed definition')
        with self.assertRaises(Conflict): bundle.quantity('semantic-table', 'units')

    def test_missing_receipt_refuses_measured_result(self):
        adapter, catalog = self.adapter(); adapter.record_evidence = lambda e: None
        with patch('investigator.adapters.local_process.assets', return_value=catalog):
            with self.assertRaises(Conflict): adapter.evaluate({'id': 'semantic-table', 'kind': 'presentation'}, 'measure', {'filters': []})

if __name__ == '__main__': unittest.main()

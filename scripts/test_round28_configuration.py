"""Offline estate configuration and literal-boundary regressions."""
from copy import deepcopy
import json
import os
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
from investigator import estate_config as config

ROOT = Path(__file__).resolve().parents[1]


def draft():
    limits = dict(requests_per_ticket=10, requests_per_day=100, microdollars_per_ticket=1000,
                  microdollars_per_day=10000, microdollars_per_month=100000)
    return {'version': 'estate-config/1', 'id': 'draft', 'name': 'Draft installation', 'enabled': False,
        'status': 'DRAFT', 'references': dict(tenant='tenant-ref', subscription='subscription-ref', resource_group='group-ref'),
        'connectors': [dict(id='data', kind='azure-sql', enabled=False, identity='reader', adapter='data', objects=[], discovery=['declared objects'])],
        'layers': {role: dict(connectors=['data'], objects=[], discovery=['declared '+role]) for role in config.ROLES},
        'source_of_truth': 'source', 'deepest_reachable': 'bronze',
        'identities': {'reader': dict(kind='managed-identity', reference='reader-ref', tenant='tenant-ref', secret_refs=[])},
        'secrets': dict(vault='vault-ref', names=['model-key']),
        'model': dict(provider='configured-provider', model='configured-model', secret_ref='model-key', limits=limits),
        'limits': limits, 'optional_sources': {key: dict(enabled=False, adapter='not-installed') for key in ('catalog','ontology','glossary')},
        'deployment': {'jobs': dict(worker='test-worker', graph='test-graph', collectors='test-collectors')}, 'installation': None}


class EstateConfigurationTests(unittest.TestCase):
    def test_draft_load_and_dry_run_cannot_connect_or_resolve_secrets(self):
        with patch('socket.socket.connect', side_effect=AssertionError('NETWORK_FORBIDDEN')):
            value = config.validate(draft())
            self.assertEqual(config.dry_run(value)['status'], 'DRAFT_DISABLED')
            with self.assertRaisesRegex(ValueError, 'ESTATE_DISABLED'): config.engine_manifest(value)
        self.assertFalse(value['enabled'])

    def test_smoke_and_sealed_states_never_admit_ticket_execution(self):
        for status in ('SMOKE_ONLY', 'READY_SEALED_TEST'):
            value = draft(); value['status'] = status
            with patch('socket.socket.connect', side_effect=AssertionError('NETWORK_FORBIDDEN')):
                self.assertEqual(config.dry_run(value)['status'], status)
                self.assertFalse(config.dry_run(value)['execution_enabled'])
                with self.assertRaisesRegex(ValueError, 'ESTATE_DISABLED'):
                    config.engine_manifest(value)
                value['enabled'] = True
                with self.assertRaisesRegex(ValueError, 'connectivity only'):
                    config.validate(value)

    def test_schema_is_closed_and_reports_missing_fields_and_layer_gaps(self):
        changes = [lambda v: v.update(extra=True), lambda v: v['layers'].pop('gold'),
            lambda v: v['layers']['gold'].update(objects=[], discovery=[]),
            lambda v: v['layers']['bronze'].update(connectors=['unknown']),
            lambda v: v['connectors'].append(deepcopy(v['connectors'][0])),
            lambda v: v['connectors'][0].update(identity='missing'),
            lambda v: v['identities']['reader'].update(secret_refs=['missing']),
            lambda v: v['model'].update(secret_ref='missing'),
            lambda v: v['limits'].update(requests_per_ticket=101),
            lambda v: v['optional_sources']['glossary'].update(enabled=True),
            lambda v: v.update(enabled=True, status='CONFIGURED')]
        for change in changes:
            with self.subTest(change=change):
                value = draft(); change(value)
                with self.assertRaises(ValueError): config.validate(value)

    def test_secret_values_duplicate_json_keys_and_bad_versions_refuse(self):
        for field in ('password', 'api_key', 'client_secret', 'refresh_token', 'connection_string'):
            with self.assertRaises(ValueError): config._reject_values({'nested': [{field: 'do-not-store'}]})
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'estate.json'
            path.write_text('{"version":1,"version":2}')
            with self.assertRaises(ValueError): config.load(path)
        value = draft(); value['version'] = 'estate-config/2'
        with self.assertRaises(ValueError): config.validate(value)

    def test_runtime_setting_is_explicit_and_reloads_modified_configuration(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'estate.json'; value = draft(); path.write_text(json.dumps(value))
            with patch.dict(os.environ, {'DIA_ESTATE_CONFIG': str(path)}):
                self.assertEqual(config.configured()['id'], 'draft')
                snapshot = config.configured(); snapshot['name'] = 'mutated'
                self.assertEqual(config.configured()['name'], 'Draft installation')
                value['name'] = 'Different name'; path.write_text(json.dumps(value))
                self.assertEqual(config.configured()['name'], 'Different name')

    def test_current_practice_and_hospital_validate_and_native_bindings_are_unchanged(self):
        path = ROOT/'config/estates/practice-fixture.json'
        if not path.exists(): self.skipTest('Deployment configurations intentionally excluded from public image')
        from investigator.estate_manifest import load
        current = config.load(path)
        self.assertEqual(load(path), current['installation'])
        self.assertEqual(config.load(ROOT/'config/estates/example-hospital.json')['status'], 'DRAFT')
        self.assertEqual(json.loads((ROOT/'config/estates/estate-config.schema.json').read_text())['properties'], config.SCHEMA['properties'])
        for field in ('provider', 'model'):
            bad = deepcopy(current); bad['model'][field] = 'different'
            with self.assertRaises(ValueError): config.validate(bad)
        bad = deepcopy(current); bad['layers']['source']['objects'] = ['unknown-object']
        with self.assertRaises(ValueError): config.validate(bad)

    def test_engine_has_no_known_estate_names_ids_hosts_or_connection_strings(self):
        # Deployment runners are outside this narrowed owner-approved cleanup scope.
        pattern = re.compile(r'skynwhy\.com|sql-orderops-9696025|\bbillingapp\b|\bordersops\b|'
            r'kv-dia-d5dd7d65|149f8d99-1c66-4a0a-9624-759be002bb60|'
            r'531419ef-1610-415a-b8bf-01a4b6aad751|orderops_investigator|'
            r'(?i:password\s*=\s*[^;\s]+;.*(?:server|database)\s*=)')
        hits = []
        paths = list((ROOT/'scripts/investigator').rglob('*.py'))
        paths += [path for path in (ROOT/'scripts').glob('*.py') if path.name.startswith(
            ('cloud_', 'run_', 'metadata_', 'serve_')) or path.name == 'dia.py']
        for path in paths:
            if pattern.search(path.read_text(encoding='utf8')): hits.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(hits, [])
        self.assertTrue(pattern.search('Server=x;Password=secret;Database=y;'))


if __name__ == '__main__': unittest.main()

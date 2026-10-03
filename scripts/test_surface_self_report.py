"""An execution surface is established by the surface's own answer, not the client's belief."""
import json
from pathlib import Path
import re
import subprocess
import unittest
from unittest.mock import patch

import fabric_sql_auth
import fabric_sql_surface
from investigator import flexible_tools
from investigator.process_debugging import attest_surface

ROOT = Path(__file__).resolve().parents[1]
TENANT = '00000000-0000-0000-0000-000000000001'
READER = {'account': 'reader@example.com', 'profile': '.local/test-reader-profile', 'server': 'example.invalid'}
CONFIG = {'fabric': {'auth': {'tenant_id': TENANT}, 'sql_reader': READER}}


class AttestationTests(unittest.TestCase):
    DECLARED = {'engine': 'E', 'connection': 'C', 'object': 'gold', 'identity': 'reader@example.com'}

    def test_matching_report_names_attested_and_unattested_fields(self):
        result = attest_surface(self.DECLARED, {'identity': 'READER@example.com', 'object': 'gold'})
        self.assertEqual(result['status'], 'PARTIAL')
        self.assertEqual(result['consistency'], 'MATCHED')
        self.assertEqual(result['attested_fields'], ['identity', 'object'])
        self.assertEqual(result['unattested_fields'], ['connection', 'engine'])

    def test_database_contradiction_is_refused_and_recorded(self):
        # The shape of the 2026-09-26 near-miss: a connection meant for Gold opened Bronze.
        result = attest_surface(self.DECLARED, {'identity': 'reader@example.com', 'object': 'bronze'})
        self.assertEqual(result['status'], 'CONTRADICTED')
        self.assertEqual(result['contradictions'], [{'field': 'object', 'declared': 'gold', 'reported': 'bronze'}])

    def test_identity_contradiction_is_refused(self):
        # The other near-miss: receipts labelled isolated were made by an administrator.
        result = attest_surface(self.DECLARED, {'identity': 'admin@example.com', 'object': 'gold'})
        self.assertEqual(result['status'], 'CONTRADICTED')

    def test_absent_or_partial_report_is_missing(self):
        for report in (None, {}, {'identity': ''}, {'identity': 5}):
            self.assertEqual(attest_surface(self.DECLARED, report)['status'], 'MISSING', report)

    def test_answered_object_without_required_identity_is_partial_but_not_eligible(self):
        result=attest_surface(self.DECLARED,{'object':'gold'})
        self.assertEqual(result['coverage'],'PARTIAL')
        self.assertEqual(result['missing_required_fields'],['identity'])

    def test_reported_field_absent_from_declaration_contradicts(self):
        declared = {k: v for k, v in self.DECLARED.items() if k != 'object'}
        self.assertEqual(attest_surface(declared, {'identity': 'reader@example.com', 'object': 'gold'})['status'],
                         'CONTRADICTED')


class AdmissionSplitTests(unittest.TestCase):
    REQUEST = {'tool': 'bounded_sql', 'max_rows': 21, 'limitation': 'l',
               'surface_report_columns': {'identity': 'surface_identity'}}

    def extract(self, rows, request=None):
        return flexible_tools.extract({'rows': rows, 'column_types': {}}, request or self.REQUEST)

    def test_report_is_separated_from_values(self):
        result = self.extract([{'n': 'x', 'surface_identity': 'reader'}])
        self.assertEqual(result['surface_report'], {'identity': 'reader'})
        self.assertEqual([list(r) for r in result['rows']], [['n']])
        self.assertEqual(result['columns'], ['n'])

    def test_bracketed_dax_label_is_recognised(self):
        result = self.extract([{'[n]': 'x', '[surface_identity]': 'reader'}])
        self.assertEqual(result['surface_report'], {'identity': 'reader'})

    def test_inconsistent_or_missing_answers_give_no_report(self):
        self.assertIsNone(self.extract([{'n': 1, 'surface_identity': 'a'}, {'n': 2, 'surface_identity': 'b'}])['surface_report'])
        self.assertIsNone(self.extract([{'n': 1}])['surface_report'])
        self.assertIsNone(self.extract([])['surface_report'])

    def test_request_without_report_columns_is_unchanged(self):
        request = {k: v for k, v in self.REQUEST.items() if k != 'surface_report_columns'}
        self.assertNotIn('surface_report', self.extract([{'n': 'x'}], request))

    def test_report_request_labels_are_validated(self):
        for bad in ({}, {'identity': 'a b'}, {'Identity': 'x'}, {'a': 'x', 'b': 'x'}, 'identity'):
            with self.assertRaises(ValueError):
                flexible_tools.surface_columns(bad)


class ReaderSessionTests(unittest.TestCase):
    def test_profile_must_be_relative_and_under_local(self):
        for bad in ('C:/x', '/x', '../x', 'infra/x', '.local/../infra', ''):
            with self.assertRaises(ValueError):
                fabric_sql_auth.profile_path(bad)
        self.assertTrue(str(fabric_sql_auth.profile_path('.local/azure-reader-sql')).endswith('azure-reader-sql'))

    def test_missing_profile_requires_sign_in_without_calling_cli(self):
        with patch('fabric_sql_auth.cli', side_effect=AssertionError('no cli call expected')):
            with self.assertRaises(fabric_sql_auth.SignInRequired) as caught:
                fabric_sql_auth.get_sql_token(TENANT, 'reader@example.com', '.local/profile-that-does-not-exist')
        self.assertEqual(caught.exception.account, 'reader@example.com')

    def test_profile_holding_another_account_is_refused_not_used(self):
        with patch.object(fabric_sql_auth.Path, 'is_dir', return_value=True), \
             patch('fabric_sql_auth.cli', return_value={'tenantId': TENANT, 'user': {'name': 'admin@example.com'}}) as cli:
            with self.assertRaisesRegex(RuntimeError, 'account or tenant differs'):
                fabric_sql_auth.get_sql_token(TENANT, 'reader@example.com', '.local/test-reader-profile')
        self.assertEqual(cli.call_count, 1)  # no token was requested for the wrong account

    def test_no_account_is_hardcoded(self):
        source = (ROOT/'scripts/fabric_sql_auth.py').read_text(encoding='utf-8')
        self.assertIsNone(re.search(r'[A-Za-z0-9._-]+@[A-Za-z0-9-]+\.[A-Za-z]', source))
        self.assertNotIn('azure-fabric-sql', source)


class SurfaceTransportTests(unittest.TestCase):
    def test_database_is_required_before_any_token_or_connection(self):
        for bad in (None, '', ' ', 'gold;drop', 'a' * 129):
            with self.assertRaises(ValueError):
                fabric_sql_surface.self_report(CONFIG, bad, token=self.fail, run=self.fail)

    def test_unconfigured_reader_is_explicitly_unavailable(self):
        result = fabric_sql_surface.self_report({'fabric': {'auth': {'tenant_id': TENANT}}}, 'gold',
                                                token=self.fail, run=self.fail)
        self.assertEqual((result['status'], result['reason']), ('UNAVAILABLE', 'SQL_READER_NOT_CONFIGURED'))

    def test_missing_session_names_the_sign_in_and_never_falls_back(self):
        def token(tenant, account, profile):
            self.assertEqual((account, profile), (READER['account'], READER['profile']))
            raise fabric_sql_auth.SignInRequired(account, profile)
        result = fabric_sql_surface.self_report(CONFIG, 'gold', token=token, run=self.fail)
        self.assertEqual((result['status'], result['reason']), ('UNAVAILABLE', 'SIGN_IN_REQUIRED'))
        self.assertEqual(result['account'], READER['account'])
        self.assertIn('--session sql_reader', result['sign_in'])

    def test_request_names_the_database_and_carries_no_query(self):
        seen = {}
        def run(command, input, **kwargs):
            seen.update(json.loads(input))
            return subprocess.CompletedProcess(command, 0, json.dumps(
                {'status': 'REACHABLE', 'login_name': 'reader@example.com', 'database_name': 'gold'}), '')
        result = fabric_sql_surface.self_report(CONFIG, 'gold', token=lambda *a: 'token', run=run)
        self.assertEqual(sorted(seen), ['access_token', 'database', 'server'])
        self.assertEqual(seen['database'], 'gold')
        self.assertEqual(result['surface_report'], {'identity': 'reader@example.com', 'object': 'gold'})
        self.assertEqual(result['execution_surface']['identity'], READER['account'])
        self.assertEqual(attest_surface(result['execution_surface'], result['surface_report'])['status'], 'PARTIAL')

    def test_endpoint_default_database_is_caught_by_attestation(self):
        def run(command, input, **kwargs):
            return subprocess.CompletedProcess(command, 0, json.dumps(
                {'status': 'REACHABLE', 'login_name': 'reader@example.com', 'database_name': 'bronze'}), '')
        result = fabric_sql_surface.self_report(CONFIG, 'gold', token=lambda *a: 'token', run=run)
        self.assertEqual(attest_surface(result['execution_surface'], result['surface_report'])['status'], 'CONTRADICTED')

    def test_failed_connection_is_unavailable_with_its_stage(self):
        def run(command, input, **kwargs):
            return subprocess.CompletedProcess(command, 1, json.dumps(
                {'status': 'UNAVAILABLE', 'stage': 'connect', 'error_type': 'SqlException', 'sql_error_number': 18456}), '')
        result = fabric_sql_surface.self_report(CONFIG, 'gold', token=lambda *a: 'token', run=run)
        self.assertEqual((result['status'], result['stage'], result['sql_error_number']), ('UNAVAILABLE', 'connect', 18456))
        self.assertIsNone(result['surface_report'])


class ConnectionScriptTests(unittest.TestCase):
    def test_every_sql_connection_script_names_its_database(self):
        scripts = [p for p in (ROOT/'infra/scripts').glob('*.ps1')
                   if 'SqlConnection' in p.read_text(encoding='utf-8-sig')]
        self.assertTrue(scripts)
        for path in scripts:
            self.assertIn('Initial Catalog', path.read_text(encoding='utf-8-sig'), path.name)

    def test_self_report_script_refuses_empty_database_and_accepts_no_query(self):
        source = (ROOT/'infra/scripts/Read-FabricSqlSurface.ps1').read_text(encoding='utf-8-sig')
        self.assertIn("IsNullOrWhiteSpace($request.database)", source)
        self.assertIn("'access_token,database,server'", source)
        self.assertEqual(source.count('CommandText='), 1)
        self.assertIn('SUSER_SNAME()', source)
        self.assertIn('DB_NAME()', source)


class CapabilityTests(unittest.TestCase):
    def adapter(self, surface, execute_lower=lambda database, request: {}):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        return MicrosoftProcessAdapter(None, None, None, None, None, lower_surface=surface, execute_lower=execute_lower)

    def test_lower_surface_is_declared_only_when_the_session_is_ready(self):
        self.assertIn('independent_lower_surface', self.adapter({'status': 'READY'}).capabilities())
        # A ready session without a transport cannot read; it is not declared.
        without = self.adapter({'status': 'READY'}, execute_lower=None)
        self.assertNotIn('independent_lower_surface', without.capabilities())
        self.assertIn('no reader transport', without.capability_gaps()['independent_lower_surface'])
        for surface in (None, {'status': 'SIGN_IN_REQUIRED', 'account': 'a@b.c', 'profile': '.local/p'},
                        {'status': 'ACCOUNT_MISMATCH'}):
            adapter = self.adapter(surface)
            self.assertNotIn('independent_lower_surface', adapter.capabilities())
            self.assertIn('independent_lower_surface', adapter.capability_gaps())
        gap = self.adapter({'status': 'SIGN_IN_REQUIRED', 'account': 'a@b.c', 'profile': '.local/p'}).capability_gaps()
        self.assertIn('a@b.c', gap['independent_lower_surface'])

    def test_gap_report_never_crashes_on_a_partial_session_status(self):
        for surface in ({'status': 'SIGN_IN_REQUIRED'}, {'status': 'SIGN_IN_REQUIRED', 'account': 'a@b.c'},
                        {'status': 'SIGN_IN_REQUIRED', 'profile': '.local/p'}):
            gap = self.adapter(surface).capability_gaps()['independent_lower_surface']
            self.assertIn('Sign-in required', gap)


class ConfigTests(unittest.TestCase):
    def test_reader_and_session_profiles_must_differ(self):
        from metadata_config import load_config
        import tempfile
        base = json.loads((ROOT/'infra/metadata/development.json').read_text(encoding='utf-8-sig'))
        base['fabric']['sql_reader'] = {'account': 'reader@example.com', 'profile': base['fabric']['sql_session']['profile'],
                                        'server': 'example.invalid'}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'config.json'
            path.write_text(json.dumps(base), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'separate profiles'):
                load_config(path)


if __name__ == '__main__':
    unittest.main()

"""Cloud authentication contract tests; no Azure calls or secret reads."""
import base64
import copy
import io
import json
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, MagicMock, patch

from investigator.adapters import managed_identity as auth

TENANT = '11111111-1111-1111-1111-111111111111'
CLIENT = '22222222-2222-2222-2222-222222222222'
PRINCIPAL = '33333333-3333-3333-3333-333333333333'
WORKSPACE = '44444444-4444-4444-4444-444444444444'
MODEL = '55555555-5555-5555-5555-555555555555'
IDENTITY = {'mode':'managed_identity', 'tenant_id':TENANT,
            'client_id':CLIENT, 'principal_id':PRINCIPAL}


def token(scope='https://analysis.windows.net/powerbi/api/.default', **changes):
    claims = {'aud':scope.removesuffix('/.default'), 'tid':TENANT, 'oid':PRINCIPAL}
    claims.update(changes)
    return 'header.' + base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip('=') + '.signature'


def cloud_manifest():
    root = Path(__file__).resolve().parents[1]
    m = json.loads((root / 'estates/fixture.json').read_text())
    options = m['adapters'][0]['options']
    options['sql']['auth'] = {**IDENTITY, 'account':'synthetic-worker'}
    fabric = options['fabric']
    fabric.pop('xmla_client', None)
    fabric['auth'] = {**IDENTITY, 'python':'python'}
    fabric['native_reader'] = {'mode':'managed_identity', 'tenant_id':TENANT,
                              'principal_id':PRINCIPAL, 'account':'synthetic-worker',
                              'workspace_ids':[fabric['workspace_id']]}
    fabric['sql_reader'] = {**IDENTITY, 'account':'synthetic-worker',
                            'server':fabric['sql_reader']['server']}
    for identity in m['identities']:
        identity['principal'] = 'synthetic-worker'
        identity['credential_reference'] = auth.reference(IDENTITY)
    m['model']['credential'] = dict(IDENTITY)
    return m


class ManagedIdentityTests(unittest.TestCase):
    def test_known_vault_guid_is_only_an_alias_for_vault_and_identity_stays_pinned(self):
        scope='https://vault.azure.net/.default'
        alias='cfa8b339-82a2-471a-a3c9-0fc0be7a4093'
        credential=Mock(get_token=Mock(return_value=SimpleNamespace(token=token(scope,aud=alias))))
        provider=auth.Tokens(IDENTITY,credential=credential)
        self.assertEqual(provider.get_token(scope),token(scope,aud=alias))
        for other_scope in auth.SCOPES-{scope}:
            with self.assertRaisesRegex(auth.TokenBindingError,'AUDIENCE_MISMATCH'):
                provider.get_token(other_scope)
        for changes,reason in [({'aud':CLIENT},'AUDIENCE_MISMATCH'),
                               ({'aud':alias,'tid':CLIENT},'TENANT_MISMATCH'),
                               ({'aud':alias,'oid':CLIENT},'PRINCIPAL_MISMATCH')]:
            credential.get_token.return_value=SimpleNamespace(token=token(scope,**changes))
            with self.assertRaisesRegex(auth.TokenBindingError,reason):provider.get_token(scope)

    def test_token_failure_reason_is_stable_and_never_includes_provider_text(self):
        scope='https://vault.azure.net/.default'
        failures=[('not-a-token','TOKEN_NOT_JWT'),
                  (token(scope,tid=CLIENT),'TENANT_MISMATCH'),
                  (token(scope,oid=CLIENT),'PRINCIPAL_MISMATCH'),
                  (token(scope,aud='https://wrong.invalid'),'AUDIENCE_MISMATCH')]
        for value,reason in failures:
            credential=Mock(get_token=Mock(return_value=SimpleNamespace(token=value)))
            with self.assertRaises(auth.TokenBindingError) as error:
                auth.Tokens(IDENTITY,credential=credential).get_token(scope)
            self.assertEqual(error.exception.reason,reason)
            self.assertNotIn(value,str(error.exception))
        credential=Mock(get_token=Mock(side_effect=RuntimeError('raw-secret-detail')))
        with self.assertRaises(auth.TokenBindingError) as error:
            auth.Tokens(IDENTITY,credential=credential).get_token(scope)
        self.assertEqual(error.exception.reason,'TOKEN_ACQUISITION_FAILED')
        self.assertNotIn('raw-secret-detail',str(error.exception))

    def test_explicit_identity_and_audience_are_pinned_before_use(self):
        scope = 'https://database.windows.net/.default'
        credential = Mock()
        credential.get_token.return_value = SimpleNamespace(token=token(scope))
        provider = auth.Tokens(IDENTITY, credential=credential)
        self.assertEqual(provider.get_token(scope), token(scope))
        credential.get_token.assert_called_once_with(scope)
        for mismatch in ({'tid':CLIENT}, {'oid':CLIENT}, {'aud':'https://unexpected.invalid'}):
            credential.get_token.return_value = SimpleNamespace(token=token(scope, **mismatch))
            with self.assertRaisesRegex(RuntimeError, 'BINDING_MISMATCH'):
                provider.get_token(scope)
        credential.reset_mock()
        with self.assertRaisesRegex(ValueError, 'AUDIENCE_UNDECLARED'):
            provider.get_token('https://attacker.invalid/.default')
        credential.get_token.assert_not_called()

    def test_auth_failure_does_not_expose_secret_or_try_operator_credentials(self):
        credential = Mock()
        credential.get_token.side_effect = RuntimeError('sensitive-token-do-not-output')
        with patch('subprocess.run', side_effect=AssertionError('No CLI fallback')):
            with self.assertRaises(RuntimeError) as failed:
                auth.Tokens(IDENTITY, credential=credential).get_token('https://database.windows.net/.default')
        self.assertNotIn('sensitive-token', str(failed.exception))

    def test_explicit_sdk_identity_never_uses_a_default_credential_chain(self):
        factory = Mock()
        with patch.dict(sys.modules, {'azure.identity': SimpleNamespace(ManagedIdentityCredential=factory)}):
            auth.Tokens(IDENTITY)
        factory.assert_called_once_with(client_id=CLIENT)

    def test_schema_projects_cloud_refs_without_legacy_paths_or_second_schema(self):
        from investigator.estate_manifest import validate
        from investigator.adapters.estate_installation import configuration
        value = cloud_manifest()
        projected = configuration(validate(value))
        self.assertNotIn('credential_file', projected['sql']['auth'])
        self.assertNotIn('profile', projected['fabric']['sql_reader'])
        self.assertEqual(projected['fabric']['auth']['python'], 'python')
        bad = copy.deepcopy(value)
        bad['adapters'][0]['options']['sql']['auth']['password'] = 'not-allowed'
        with self.assertRaises(ValueError):
            validate(bad)
        bad = copy.deepcopy(value)
        bad['identities'][0]['credential_reference'] = 'managed-identity://' + WORKSPACE
        with self.assertRaisesRegex(ValueError, 'reference differs'):
            validate(bad)

    def test_native_managed_principal_remains_query_bound_and_partial(self):
        import run_native_diagnostic as native
        from investigator.native_identity import require, observed
        reader = {'mode':'managed_identity', 'tenant_id':TENANT, 'principal_id':PRINCIPAL,
                  'account':'synthetic-worker', 'workspace_ids':[WORKSPACE]}
        request = {'workspace':WORKSPACE, 'native_model_id':MODEL, 'query':'EVALUATE ROW("v", 1)'}
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value.read.return_value = b'{"results":[{"tables":[{"rows":[{"v":1}]}]}]}'
        # Current direct sender and the gateway sender both eventually use this opener.
        gateway = SimpleNamespace(open_http=lambda opened, request, **kw: opened.open(request,timeout=kw['timeout']))
        with patch.dict(sys.modules, {'investigator.live_gateway':gateway}), \
             patch.object(native, 'build_opener', return_value=opener), \
             patch.object(auth, 'Tokens') as tokens:
            tokens.return_value.get_token.return_value = token()
            response = json.loads(native.execute(request,TENANT,reader,IDENTITY))
        self.assertEqual(require(response,request,reader), response)
        self.assertFalse(observed(response,request)['effective_identity_verified'])
        self.assertEqual(observed(response,request)['principal_id'], PRINCIPAL)
        with self.assertRaisesRegex(ValueError, 'binding differs'):
            native.execute(request,TENANT,reader,{**IDENTITY,'principal_id':CLIENT})

    def test_managed_sql_never_falls_through_to_dpapi_or_cli(self):
        import run_source_diagnostic, fabric_sql_surface
        from investigator.adapters.estate_installation import configuration
        config = configuration(cloud_manifest())
        request={'query':'SELECT 1','max_rows':2,'result_columns':['value'],'read_only_objects':['dbo.synthetic'],
                 'response_mode':'records','require_read_only':True}
        completed=SimpleNamespace(returncode=0,stdout='{"rows":[]}')
        with patch('subprocess.run', side_effect=AssertionError('No legacy auth fallback')), \
             patch('investigator.physical_reads.run',return_value=completed) as run:
            run_source_diagnostic.read_once(config, request)
            self.assertTrue(run.call_args.args[0][-1].endswith('managed_sql_worker.py'))
            self.assertEqual(json.loads(run.call_args.kwargs['input'])['authentication']['mode'],'managed_identity')
            fabric_sql_surface.read(config, 'synthetic', request)
            self.assertTrue(run.call_args.args[0][-1].endswith('managed_sql_worker.py'))

    def test_model_context_uses_explicit_credential_without_environment_secrets(self):
        from run_adaptive_investigation import local_azure_key
        from investigator.provider_selection import DEPLOYMENT
        prior = dict(os.environ)
        settings = {**IDENTITY, 'endpoint':'https://synthetic.openai.azure.com', 'deployment':'synthetic'}
        with patch('subprocess.run', side_effect=AssertionError('No account key lookup')):
            with local_azure_key(settings):
                self.assertEqual(DEPLOYMENT.get(), 'synthetic')
                self.assertEqual(auth.MODEL_SESSION.get()['credential'], IDENTITY)
                self.assertEqual(dict(os.environ), prior)
        self.assertIsNone(auth.MODEL_SESSION.get())

    def test_versioned_vault_secret_uses_only_exact_declared_endpoint(self):
        reference = {'vault_url':'https://synthetic.vault.azure.net', 'secret_name':'model-key',
                     'secret_version':'a'*32, 'identity':IDENTITY}
        uri = reference['vault_url'] + '/secrets/model-key/' + 'a'*32
        provider = Mock()
        provider.get_token.return_value = 'in-memory-auth'
        response = io.BytesIO(json.dumps({'id':uri,'value':'synthetic-secret'}).encode())
        gateway = Mock(return_value=response)
        with patch.dict(sys.modules, {'investigator.live_gateway':SimpleNamespace(open_http=gateway)}):
            self.assertEqual(auth.secret(reference,tokens=provider,gateway_identity='worker'), 'synthetic-secret')
        request = gateway.call_args.args[1]
        self.assertEqual(request.full_url, uri + '?api-version=7.4')
        self.assertEqual(request.method,'GET')
        self.assertEqual(gateway.call_args.kwargs['identity'],'worker')
        provider.get_token.assert_called_once_with('https://vault.azure.net/.default')
        for change in ({'secret_version':''}, {'vault_url':'http://synthetic.vault.azure.net'},
                       {'secret_name':'../other'}, {'password':'not-accepted'}):
            with self.assertRaises(ValueError):
                auth.validate_secret_reference({**reference,**change})

    def test_metadata_worker_forwards_explicit_identity_without_cli_fallback(self):
        from metadata_auth import WorkerTransport
        completed = SimpleNamespace(returncode=0,stdout='{"value":[]}')
        with patch('investigator.physical_reads.run', return_value=completed) as run:
            WorkerTransport('python', TENANT, 'worker.py', authentication=IDENTITY)('workspaces')
        request = json.loads(run.call_args.kwargs['input'])
        self.assertEqual(request['authentication'],IDENTITY)
        self.assertEqual(request['tenant'],TENANT)

    def test_report_listing_accepts_managed_principal_only_with_matching_auth(self):
        from report_list_worker import read
        reader = {'mode':'managed_identity','tenant_id':TENANT,'principal_id':PRINCIPAL,
                  'account':'synthetic-worker','workspace_ids':[WORKSPACE]}
        request = {'endpoint':'groups/'+WORKSPACE+'/reports','workspace_ids':[WORKSPACE],
                   'reader':reader,'authentication':IDENTITY}
        factory = Mock()
        factory.return_value.return_value = {'status_code':200,'text':{'value':[]}}
        with patch.object(auth,'Tokens') as tokens, \
             patch('connect_fixture_reader.application',side_effect=AssertionError('No interactive reader')):
            result = read(request,http_factory=factory)
        tokens.assert_called_once_with(IDENTITY)
        self.assertEqual(result['reader']['principal_id'],PRINCIPAL)
        with self.assertRaisesRegex(ValueError,'identity differs'):
            read({**request,'authentication':{**IDENTITY,'principal_id':CLIENT}},http_factory=factory)


if __name__ == '__main__':
    unittest.main()

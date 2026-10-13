"""Synthetic federation, principal binding and no credential leakage."""
import copy
import io
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from urllib.parse import urlencode

from investigator.adapters import federated_reader as auth
from investigator.live_gateway import Gateway, configured
from test_managed_identity_auth import IDENTITY, TENANT, CLIENT, PRINCIPAL, token, cloud_manifest

D = {'mode':auth.MODE, 'tenant_id':TENANT, 'client_id':CLIENT,
     'principal_id':PRINCIPAL, 'managed_identity':IDENTITY}
SCOPE = 'https://analysis.windows.net/powerbi/api/.default'
URL = 'https://login.microsoftonline.com/'+TENANT+'/oauth2/v2.0/token'


def policy():
    return {'version':1,'live_enabled':True,'identities':{auth.channel(D,SCOPE):{'http':[
        {'method':'POST','url':URL,'purpose':'auth_federation','authentication':D,'scope':SCOPE}]}}}


class FederationTests(unittest.TestCase):
    def test_public_exchange_resource_id_is_same_audience_not_an_arbitrary_guid(self):
        grant=policy()['identities'][auth.channel(D,SCOPE)]['http'][0]
        for audience in ('api://AzureADTokenExchange', 'fb60f99c-7a34-4190-8149-302f77469936'):
            assertion=token(auth.EXCHANGE,aud=audience)
            managed=Mock(get_token=Mock(return_value=SimpleNamespace(token=assertion)))
            access=token(appid=CLIENT)
            opener=Mock(open=Mock(return_value=io.BytesIO(json.dumps({'access_token':access}).encode())))
            with configured(policy()):
                self.assertEqual(auth.Tokens(D,managed=managed,opener=opener).get_token(SCOPE),access)
            self.assertTrue(auth.validate_request('POST',URL,opener.open.call_args.args[0].data,grant))
        for audience in (CLIENT, 'https://graph.microsoft.com', 'api://AzureADTokenExchange/evil'):
            opener=Mock()
            with self.assertRaises(auth.FederationUnavailable):
                auth.Tokens(D,managed=Mock(get_token=Mock(return_value=SimpleNamespace(token=token(auth.EXCHANGE,aud=audience)))),opener=opener).get_token(SCOPE)
            opener.open.assert_not_called()

    def test_success_keeps_assertion_and_access_token_in_memory(self):
        managed=Mock(get_token=Mock(return_value=SimpleNamespace(token=token(auth.EXCHANGE))))
        access=token(appid=CLIENT)
        opener=Mock(open=Mock(return_value=io.BytesIO(json.dumps({'access_token':access}).encode())))
        with configured(policy()), patch('builtins.open',side_effect=AssertionError('No disk credential')), patch('subprocess.run',side_effect=AssertionError('No CLI fallback')):
            self.assertEqual(auth.Tokens(D,managed=managed,opener=opener).get_token(SCOPE),access)
        managed.get_token.assert_called_once_with(auth.EXCHANGE)
        request=opener.open.call_args.args[0]
        self.assertTrue(auth.validate_request('POST',URL,request.data,policy()['identities'][auth.channel(D,SCOPE)]['http'][0]))

    def test_binding_mismatches_refuse_and_provider_text_is_not_leaked(self):
        for changes in ({'oid':CLIENT},{'tid':CLIENT},{'appid':TENANT},{'aud':'wrong'}):
            managed=Mock(get_token=Mock(return_value=SimpleNamespace(token=token(auth.EXCHANGE))))
            opener=Mock(open=Mock(return_value=io.BytesIO(json.dumps({'access_token':token(appid=CLIENT,**{k:v for k,v in changes.items() if k!='appid'}) if 'appid' not in changes else token(appid=TENANT)}).encode())))
            with configured(policy()), self.assertRaisesRegex(RuntimeError,'^FEDERATED_READER_TOKEN_UNAVAILABLE_OR_BINDING_MISMATCH$'):
                auth.Tokens(D,managed=managed,opener=opener).get_token(SCOPE)
        with self.assertRaisesRegex(RuntimeError,'^FEDERATED_READER_TOKEN_UNAVAILABLE_OR_BINDING_MISMATCH$'):
            auth.Tokens(D,managed=Mock(get_token=Mock(side_effect=ValueError('SECRET')))).get_token(SCOPE)

    def test_wrong_managed_subject_never_dispatches(self):
        opener=Mock()
        with self.assertRaises(RuntimeError):
            auth.Tokens(D,managed=Mock(get_token=Mock(return_value=SimpleNamespace(token=token(auth.EXCHANGE,oid=CLIENT)))),opener=opener).get_token(SCOPE)
        opener.open.assert_not_called()

    def test_unapproved_scope_or_secret_field_refused(self):
        with self.assertRaises(ValueError):auth.validate(dict(D,client_secret='never'))
        managed=Mock()
        with self.assertRaises(ValueError):auth.Tokens(D,managed=managed).get_token('https://graph.microsoft.com/.default')
        managed.get_token.assert_not_called()

    def test_gateway_rejects_foreign_assertion_and_secret_grant(self):
        grant=policy()['identities'][auth.channel(D,SCOPE)]['http'][0]
        body={'client_id':CLIENT,'scope':SCOPE,'grant_type':'client_credentials','client_assertion_type':auth.ASSERTION_TYPE,'client_assertion':token(auth.EXCHANGE)}
        self.assertTrue(auth.validate_request('POST',URL,urlencode(body),grant))
        for change in ({'client_secret':'secret'},{'scope':'https://graph.microsoft.com/.default'},
                       {'client_assertion':token(auth.EXCHANGE,oid=CLIENT)},{'grant_type':'password'}):
            self.assertFalse(auth.validate_request('POST',URL,urlencode(body|change),grant))

    def test_manifest_routes_source_sql_and_native_through_same_application(self):
        from investigator.adapters.estate_installation import configuration
        from investigator.adapters.vault_user_cache import credential,provider
        m=cloud_manifest();o=m['adapters'][0]['options'];f=o['fabric']
        o['sql']['auth']=dict(D,account='synthetic-worker')
        f['auth']=dict(D,python='python');f['native_reader']['mode']=auth.MODE
        f['sql_reader']=dict(D,account='synthetic-worker',server=f['sql_reader']['server'])
        for identity in m['identities']:identity['credential_reference']=auth.reference(D)
        config=configuration(m)
        self.assertEqual(credential(config['sql']['auth']),D)
        self.assertEqual(credential(config['fabric']['auth']),D)
        with patch('azure.identity.ManagedIdentityCredential',return_value=Mock()):
            self.assertIsInstance(provider(D),auth.Tokens)
        f['native_reader']['principal_id']=CLIENT
        with self.assertRaises(ValueError):configuration(m)

    def test_authentication_control_is_not_estate_permission_proof(self):
        from platform_federated_preflight import run
        result=run([{'authentication':D,'scope':SCOPE}],factory=Mock(return_value=Mock(get_token=Mock(return_value=token(appid=CLIENT)))))
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['estate_reads'],0)
        self.assertIn('no estate query permission',result['limitation'])
        failed=run([{'authentication':D,'scope':SCOPE}],factory=Mock(return_value=Mock(get_token=Mock(return_value=token(appid=TENANT)))))
        self.assertEqual(failed['status'],'FAIL')

    def test_failure_retains_safe_stage_and_code_but_not_provider_secrets(self):
        from platform_federated_preflight import run
        provider=auth.Tokens(D,managed=Mock(get_token=Mock(side_effect=ValueError('AADSTS70021 SECRET-VALUE'))))
        result=run([{'authentication':D,'scope':SCOPE}],factory=Mock(return_value=provider))
        self.assertEqual(result['checks'][0]['stage'],'MANAGED_ASSERTION')
        self.assertEqual(result['checks'][0]['provider_code'],'AADSTS70021')
        self.assertNotIn('SECRET-VALUE',json.dumps(result))


if __name__=='__main__':unittest.main()

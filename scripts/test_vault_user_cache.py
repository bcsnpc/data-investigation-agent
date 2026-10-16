"""No real credentials, model calls or estate requests."""
import copy
import io
import json
import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace

from investigator.adapters import vault_user_cache as auth
from test_managed_identity_auth import IDENTITY, TENANT, CLIENT, PRINCIPAL, MODEL, WORKSPACE, token

D = {'mode':auth.MODE,'tenant_id':TENANT,'client_id':CLIENT,'principal_id':PRINCIPAL,
     'account':'reader@example.test','scope':auth.PBI,
     'reference':{'vault_url':'https://synthetic.vault.azure.net','secret_name':'reader-cache',
                  'secret_version':'a'*32,'identity':IDENTITY}}
A = {'realm':TENANT,'local_account_id':PRINCIPAL,'username':D['account'],
     'environment':'login.microsoftonline.com','home_account_id':'synthetic-home','authority_type':'MSSTS'}
CACHE = {'version':1,'cache':{'Account':{'one':A},'AppMetadata':{},'RefreshToken':{'one':{
    'client_id':CLIENT,'environment':A['environment'],'home_account_id':A['home_account_id'],
    'credential_type':'RefreshToken','secret':'synthetic-refresh-value'}}}}


class CacheTests(unittest.TestCase):
    def app(self, access=None):
        app=Mock()
        app.get_accounts.return_value=[A]
        app.acquire_token_silent.return_value={'access_token':access or token()}
        return app

    def test_in_memory_silent_only_and_no_disk_or_secret_output(self):
        application=Mock(return_value=self.app())
        with patch('builtins.open',side_effect=AssertionError('No cache disk writes')), patch('subprocess.run',side_effect=AssertionError('No CLI')):
            provider=auth.Tokens(D,loader=Mock(return_value=json.dumps(CACHE)),application=application)
            self.assertEqual(provider.get_token(auth.PBI),token())
        kwargs=application.call_args.kwargs
        self.assertFalse(kwargs['instance_discovery'])
        application.return_value.acquire_token_silent.assert_called_once_with([auth.PBI],account=A)
        self.assertFalse(application.return_value.acquire_token_interactive.called)
        self.assertEqual(set(json.loads(kwargs['token_cache'].serialize())),set(CACHE['cache']))

    def test_unknown_scope_fails_before_key_vault(self):
        loader=Mock()
        with self.assertRaisesRegex(ValueError,'AUDIENCE_UNDECLARED'):
            auth.Tokens(D,loader=loader).get_token(auth.SQL)
        loader.assert_not_called()

    def test_wrong_cache_identity_client_or_extra_credentials_refuse(self):
        changes=[('Account','local_account_id',CLIENT),('Account','realm',CLIENT),
                 ('Account','username','other@example.test'),('RefreshToken','client_id',TENANT),
                 ('RefreshToken','home_account_id','different')]
        for section,key,value in changes:
            cache=copy.deepcopy(CACHE);cache['cache'][section]['one'][key]=value
            with self.assertRaises(ValueError):auth.cache_payload(json.dumps(cache),D)
        cache=copy.deepcopy(CACHE);cache['cache']['AccessToken']={}
        with self.assertRaisesRegex(ValueError,'MINIMAL'):auth.cache_payload(json.dumps(cache),D)

    def test_wrong_token_claims_or_provider_error_never_exposes_secrets(self):
        for claims in ({'tid':CLIENT},{'oid':CLIENT},{'aud':'https://evil.invalid'},{'upn':'admin@example.test'}):
            with self.assertRaisesRegex(RuntimeError,'BINDING_MISMATCH') as error:
                auth.Tokens(D,loader=lambda _,**kw:json.dumps(CACHE),application=Mock(return_value=self.app(token(**claims)))).get_token(auth.PBI)
            self.assertNotIn('synthetic-refresh',str(error.exception))
        with self.assertRaisesRegex(RuntimeError,'BINDING_MISMATCH') as error:
            auth.Tokens(D,loader=Mock(side_effect=ValueError('raw-secret')),application=Mock()).get_token(auth.PBI)
        self.assertNotIn('raw-secret',str(error.exception))

    def test_versioned_secret_read_calls_gateway(self):
        from investigator.adapters import managed_identity as mi
        response=io.BytesIO(json.dumps({'id':auth.reference(D),'value':json.dumps(CACHE)}).encode())
        with patch('investigator.live_gateway.open_http',return_value=response) as gate:
            raw=mi.secret(D['reference'],tokens=Mock(get_token=Mock(return_value='synthetic-token')))
        self.assertEqual(json.loads(raw),CACHE)
        self.assertEqual(gate.call_args.args[1].full_url,auth.reference(D)+'?api-version=7.4')

    def test_refresh_http_is_exact_and_gateway_checked(self):
        url='https://login.microsoftonline.com/'+TENANT+'/oauth2/v2.0/token'
        data={'grant_type':'refresh_token','client_id':CLIENT,'scope':auth.PBI+' openid offline_access','refresh_token':'synthetic'}
        grant={'tenant_id':TENANT,'client_id':CLIENT,'scope':auth.PBI}
        from urllib.parse import urlencode
        self.assertTrue(auth.validate_refresh_request('POST',url,urlencode(data).encode(),grant))
        for updates in ({'grant_type':'password'},{'scope':auth.SQL},{'client_id':TENANT},{'client_secret':'bad'}):
            self.assertFalse(auth.validate_refresh_request('POST',url,urlencode(data|updates),grant))
        response=Mock();response.__enter__=Mock(return_value=response);response.__exit__=Mock(return_value=False)
        response.code=200;response.headers={};response.read.return_value=b'{"access_token":"synthetic"}'
        with patch('investigator.live_gateway.open_http',return_value=response) as gate:
            self.assertEqual(auth.Http(D).post(url,data=data).json()['access_token'],'synthetic')
        gate.assert_called_once()
        with self.assertRaises(ValueError):auth.Http(D).get('https://evil.invalid')

    def test_native_dax_binds_existing_user_not_vault_worker(self):
        import run_native_diagnostic as native
        reader={'mode':'isolated_reader','tenant_id':TENANT,'principal_id':PRINCIPAL,
                'account':D['account'],'model_ids':[MODEL]}
        request={'workspace':WORKSPACE,'native_model_id':MODEL,'query':'EVALUATE ROW("value", 7)'}
        with patch.object(auth,'Tokens',return_value=Mock(get_token=Mock(return_value=token()))) as factory, \
                patch('investigator.live_gateway.open_http',return_value=io.BytesIO(b'{"results":[]}')):
            result=json.loads(native.execute(request,TENANT,reader,D|{'python':'python'}))
        factory.assert_called_once_with(D)
        self.assertEqual(result['_native_execution']['account'],D['account'])
        self.assertEqual(result['_native_execution']['mode'],'isolated_reader')
        with self.assertRaisesRegex(ValueError,'binding differs'):
            native.execute(request,TENANT,reader,D|{'account':'admin@example.test'})

    def test_sql_worker_retains_guards_using_cached_user_provider(self):
        import managed_sql_worker as worker
        from test_managed_sql_worker import Cursor
        declaration=D|{'scope':auth.SQL}
        cursor=Cursor();connection=Mock();connection.cursor.return_value=cursor
        payload={'server':'synthetic','database':'synthetic','authentication':declaration,
                 'query':'SELECT SUM(quantity) AS value FROM dbo.movements','parameters':[],
                 'read_only_objects':['dbo.movements'],'max_rows':2,'result_columns':['value'],'require_read_only':True}
        with patch('investigator.live_gateway.authorize_sql_payload',side_effect=lambda x:x), \
                patch.object(auth,'provider',return_value=Mock(get_token=Mock(return_value='synthetic-token'))) as factory:
            result=worker.execute(payload,connect=Mock(return_value=connection))
        factory.assert_called_once_with(declaration)
        self.assertTrue(result['read_only_verified']);self.assertEqual(len(cursor.calls),4)
        self.assertNotIn('synthetic-token',json.dumps(result))

    def test_closed_config_and_worker_projection(self):
        from metadata_config import validate_config, worker_configuration
        from test_managed_identity_auth import cloud_manifest
        options=cloud_manifest()['adapters'][0]['options']
        options['fabric']['auth']=D|{'python':'python'}
        options['fabric']['native_reader']={'mode':'isolated_reader','tenant_id':TENANT,
            'principal_id':PRINCIPAL,'account':D['account'],'model_ids':[MODEL]}
        options['fabric']['sql_reader']=D|{'scope':auth.SQL,'server':'synthetic'}
        config=validate_config({'version':1,**options,'storage':{'database':'synthetic.db'}})
        projected=worker_configuration(config,{'workspace':WORKSPACE,'native_model_id':MODEL})
        self.assertEqual(projected['fabric']['auth'],D|{'python':'python'})
        self.assertNotIn('sql_reader',projected['fabric'])
        bad=copy.deepcopy(config);bad['fabric']['auth']['principal_id']=CLIENT
        with self.assertRaisesRegex(ValueError,'binding differs'):validate_config(bad)
        bad=copy.deepcopy(config);bad['fabric']['sql_reader']['scope']=auth.PBI
        with self.assertRaisesRegex(ValueError,'audience'):validate_config(bad)

    def test_real_msal_cache_lookup_and_refresh_use_exact_gateway_endpoints(self):
        from investigator.live_gateway import Gateway
        from urllib.parse import parse_qs
        tenant_url='https://login.microsoftonline.com/'+TENANT
        discovery=tenant_url+'/v2.0/.well-known/openid-configuration'
        token_url=tenant_url+'/oauth2/v2.0/token'
        grant={'method':'POST','url':token_url,'purpose':'auth_refresh',
               'tenant_id':TENANT,'client_id':CLIENT,'scope':auth.PBI}
        gate=Gateway({'version':1,'live_enabled':True,'identities':{'reader':{'http':[
            {'method':'GET','url':discovery,'purpose':'metadata'},grant]}}})
        requests=[]
        def opened(opener,request,**kwargs):
            gate.http('reader',request.get_method(),request.full_url,request.data)
            requests.append(request)
            body=({'authorization_endpoint':tenant_url+'/oauth2/v2.0/authorize',
                   'token_endpoint':token_url,'issuer':tenant_url+'/v2.0'} if request.get_method()=='GET'
                  else {'access_token':token(),'expires_in':3600,'token_type':'Bearer','scope':auth.PBI})
            response=io.BytesIO(json.dumps(body).encode());response.code=200;response.headers={}
            return response
        with patch.dict('os.environ',{'DIA_LIVE_ACCESS_DISABLED':'0'}), \
                patch('investigator.live_gateway.open_http',side_effect=opened):
            self.assertEqual(auth.Tokens(D,loader=lambda _,**kw:json.dumps(CACHE)).get_token(auth.PBI),token())
        self.assertEqual([r.full_url for r in requests],[discovery,token_url])
        self.assertEqual(parse_qs(requests[1].data.decode())['grant_type'],['refresh_token'])

    def test_metadata_bridge_never_falls_back_to_cli_for_cached_reader(self):
        from metadata_auth import WorkerTransport
        with patch('subprocess.run') as run:
            with self.assertRaisesRegex(ValueError,'UNDECLARED'):
                WorkerTransport('python',TENANT,'worker.py',authentication=D).invoke({'endpoint':'workspaces'})
        run.assert_not_called()


if __name__=='__main__':unittest.main()

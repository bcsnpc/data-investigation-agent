import base64
import copy
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from cloud_dax_authorization import run
from run_native_diagnostic import execute

TENANT='10000000-0000-0000-0000-000000000001'
PRINCIPAL='10000000-0000-0000-0000-000000000002'
CLIENT='10000000-0000-0000-0000-000000000003'
WORKSPACE='10000000-0000-0000-0000-000000000004'
MODEL='10000000-0000-0000-0000-000000000005'
READER={'mode':'federated_reader','tenant_id':TENANT,'principal_id':PRINCIPAL,'account':'synthetic-reader','model_ids':[MODEL]}
AUTH={'mode':'federated_reader','tenant_id':TENANT,'principal_id':PRINCIPAL,'client_id':CLIENT}
REQUEST={'workspace':WORKSPACE,'native_model_id':MODEL,'query':'EVALUATE ROW("quantity",SUM(\'Activity\'[units]))','requires_native_reader':True}


def token(**changes):
    claims={'aud':'https://analysis.windows.net/powerbi/api','tid':TENANT,'oid':PRINCIPAL,'appid':CLIENT,'azp':CLIENT,
            'secret_extension':'must-never-be-retained','roles':['Dataset.Read.All']}
    claims.update(changes)
    return 'header.'+base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip('=')+'.secret-signature'


class NativeIdentityObserverTests(unittest.TestCase):
    def test_only_whitelisted_claims_after_binding_before_query(self):
        seen=[];bearer=token()
        provider=Mock(get_token=Mock(return_value=bearer))
        def open_http(*args,**kwargs):
            self.assertEqual(len(seen),1)
            return io.BytesIO(b'{"results":[]}')
        with patch('investigator.adapters.vault_user_cache.credential',return_value=AUTH),patch('investigator.adapters.vault_user_cache.provider',return_value=provider),patch('investigator.live_gateway.open_http',side_effect=open_http):
            result=execute(REQUEST,TENANT,READER,AUTH,identity_observer=seen.append)
        self.assertEqual(set(seen[0]),{'aud','tid','oid','appid','azp'})
        self.assertNotIn(bearer,json.dumps(seen));self.assertNotIn('must-never',json.dumps(seen))
        self.assertIn('_native_execution',result)

    def test_wrong_principal_never_observed_or_dispatched(self):
        observer=Mock();provider=Mock(get_token=Mock(return_value=token(oid=CLIENT)))
        with patch('investigator.adapters.vault_user_cache.credential',return_value=AUTH),patch('investigator.adapters.vault_user_cache.provider',return_value=provider),patch('investigator.live_gateway.open_http') as http:
            with self.assertRaisesRegex(ValueError,'Native reader principal differs'):
                execute(REQUEST,TENANT,READER,AUTH,identity_observer=observer)
        observer.assert_not_called();http.assert_not_called()

    def test_observer_requires_reader_before_credential_acquisition(self):
        with patch('run_native_diagnostic.FabricCliTokens') as tokens:
            with self.assertRaisesRegex(ValueError,'observer requires a bound reader'):
                execute(REQUEST,TENANT,identity_observer=Mock())
        tokens.assert_not_called()


class FakeMeter:
    def __init__(self,state,budget,limit):
        self.limit=limit;self.used=0;self.closed=False
        self.usage=SimpleNamespace(snapshot=lambda:{'physical_requests':self.used})
    def __call__(self,call):self.used+=1;return call()
    def close(self):self.closed=True


class AuthorizationCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.request=Path(self.tmp.name)/'request.json';self.request.write_bytes(json.dumps(REQUEST).encode())
        self.plan={'manifest':'retained-estate.json','options':{'request':str(self.request),'request_sha256':hashlib.sha256(self.request.read_bytes()).hexdigest(),'budget':{'environment':'synthetic'}}}
        self.config={'fabric':{'workspace_id':WORKSPACE,'native_reader':copy.deepcopy(READER),'auth':AUTH}}
        self.records=[];self.context=SimpleNamespace(record=lambda kind,value:self.records.append((kind,value)))
        for target,value in [('investigator.estate_manifest.load',{}),('investigator.adapters.estate_installation.configuration',self.config),('metadata_config.worker_configuration',self.config),('investigator.shared_state.configured_state',object())]:
            p=patch(target,return_value=value);p.start();self.addCleanup(p.stop)
        p=patch('scan_estate_graph.Meter',FakeMeter);p.start();self.addCleanup(p.stop)

    def test_401_keeps_actual_claims_exact_target_and_status_no_model(self):
        def native(request,tenant,reader,auth,*,identity_observer):
            self.assertEqual(request,REQUEST);self.assertEqual(reader,READER)
            identity_observer({'aud':'https://analysis.windows.net/powerbi/api','tid':TENANT,'oid':PRINCIPAL,'appid':CLIENT})
            raise HTTPError('https://api.powerbi.com/fixed',401,'Unauthorized',{},io.BytesIO(b'{"error":{"code":"PowerBINotAuthorizedException"}}'))
        with patch('run_native_diagnostic.execute',side_effect=native) as call:
            result=run(self.plan,self.context)
        call.assert_called_once();self.assertEqual(result['http_status'],401)
        self.assertEqual(result['error']['service_error_code'],'PowerBINotAuthorizedException')
        self.assertFalse(result['error']['completion_uncertain']);self.assertEqual(result['model_calls'],0)
        self.assertEqual(result['physical_requests'],1)
        self.assertEqual(result['target']['url'],f'https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE}/datasets/{MODEL}/executeQueries')
        self.assertEqual(self.records[-2][0],'native-token-claims')
        self.assertEqual(result['actual_token_claims'][0]['tid'],TENANT)

    def test_hash_mismatch_before_credential_or_reader(self):
        self.request.write_bytes(b'{}')
        with patch('run_native_diagnostic.execute') as call:
            with self.assertRaisesRegex(ValueError,'REQUEST_BYTES_DIFFER'):run(self.plan,self.context)
        call.assert_not_called();self.assertEqual(self.records,[])

    def test_wrong_identity_mode_refuses_no_alternative_identity(self):
        self.config['fabric']['native_reader']['mode']='isolated_reader'
        with patch('run_native_diagnostic.execute') as call:
            with self.assertRaisesRegex(ValueError,'FEDERATED_READER_REQUIRED'):run(self.plan,self.context)
        call.assert_not_called()

    def test_forbidden_extra_claim_never_persisted(self):
        def native(*args,identity_observer,**kwargs):identity_observer({'aud':'a','access_token':'do-not-retain'})
        with patch('run_native_diagnostic.execute',side_effect=native):result=run(self.plan,self.context)
        self.assertEqual(result['status'],'FAILED');self.assertEqual(result['actual_token_claims'],[])
        self.assertNotIn('do-not-retain',json.dumps(self.records));self.assertNotIn('access_token',json.dumps(self.records))

    def test_success_retains_exact_provider_response(self):
        response='{"results":[{"tables":[{"rows":[{"[quantity]":8765}]}]}]}'
        with patch('run_native_diagnostic.execute',return_value=response):result=run(self.plan,self.context)
        self.assertEqual(result['status'],'SUCCEEDED');self.assertEqual(result['response'],response)
        self.assertEqual(result['physical_requests'],1)


if __name__=='__main__':unittest.main()

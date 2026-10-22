import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch, Mock

from investigator.access_check import check, configured, expiry_checks, load, table
from investigator.adapters.access_probes import LiveProbes, NotTestable
from investigator.live_gateway import GatewayDenied


def mapping():
    return {'version':'dia-permission-map-v1', 'identities':{'investigator':{'principal_id':'reader'}},
            'checks':[{'id':'model', 'identity':'investigator', 'resource':'model-1', 'action':'ReadExplore',
                       'scopes':['fixture'], 'probe':{'kind':'http'}}]}


class AccessTests(unittest.TestCase):
    def test_map_never_grants_itself_a_pass(self):
        result=check(mapping(),bindings={},now='2026-10-22T00:00:00Z')
        self.assertEqual(result['status'],'INCOMPLETE')
        self.assertEqual(result['rows'][0]['status'],'NOT_TESTABLE')
        self.assertIn('NO_ACTUAL_IDENTITY_PROBE_BINDING',table(result))

    def test_actual_identity_and_resource_bound_receipt_required(self):
        for wrong in (True, {'permission_observed':True,'identity':'owner','resource':'model-1','receipt':{'status':200}},
                      {'permission_observed':True,'identity':'investigator','resource':'other','receipt':{'status':200}}):
            with self.subTest(wrong=wrong):
                self.assertEqual(check(mapping(),backend=SimpleNamespace(probe=lambda *_:wrong))['status'],'FAIL')
        proof={'permission_observed':True,'identity':'investigator','resource':'model-1','receipt':{'status':200}}
        self.assertEqual(check(mapping(),backend=SimpleNamespace(probe=lambda *_:proof))['status'],'PASS')

    def test_route_scoping_does_not_probe_other_estate_or_owner(self):
        data=mapping();data['checks'].append({**data['checks'][0],'id':'billing-model','scopes':['billing']})
        calls=[]
        def probe(row,_):
            calls.append(row['id']);raise NotTestable('recorded test')
        result=check(data,scope='fixture',backend=SimpleNamespace(probe=probe))
        self.assertEqual(calls,['model']);self.assertEqual(len(result['rows']),1)

    def test_denial_of_guard_is_hard_not_a_warning(self):
        def deny(*_):raise GatewayDenied('read-only policy')
        with self.assertRaises(GatewayDenied):check(mapping(),backend=SimpleNamespace(probe=deny))

    def test_provider_error_is_sanitized(self):
        def error(*_):raise RuntimeError('secret password must not be recorded')
        result=check(mapping(),backend=SimpleNamespace(probe=error))
        self.assertEqual(result['rows'][0]['reason'],'RuntimeError')
        self.assertNotIn('password',json.dumps(result))

    def test_expiry_warns_seven_days_and_fails_at_expiry(self):
        metadata=[{'credential_key_id':'key','expires_at_utc':'2026-11-21T00:59:55Z'}]
        self.assertFalse(expiry_checks(metadata,'2026-11-13T00:59:55Z')[0]['warning'])
        self.assertTrue(expiry_checks(metadata,'2026-11-14T00:59:55Z')[0]['warning'])
        self.assertEqual(expiry_checks(metadata,'2026-11-21T00:59:55Z')[0]['status'],'FAIL')

    def test_monthly_owner_reminder_from_twenty_fifth_without_mutating_accounts(self):
        data={**mapping(),'checks':[]}
        self.assertEqual(check(data,now='2026-10-24T00:00:00Z')['rows'],[])
        result=check(data,now='2026-12-25T00:00:00Z')
        self.assertEqual(result['rows'][0]['resource'],'2027-01')
        self.assertIn('worker has no INSERT',result['rows'][0]['reason'])

    def test_complete_map_retains_all_identity_roles_and_fixed_connections(self):
        data=load(Path(__file__).resolve().parents[1]/'config/permission-map.yaml')
        self.assertTrue({'owner','investigator','scanner','worker','graph-scan','smoke'}<=data['identities'].keys())
        self.assertGreaterEqual(len(data['checks']),60)
        connection=next(r for r in data['checks'] if r['id']=='fixture-fixed-connection')
        self.assertIn('SSO None',connection['action'])
        self.assertEqual(len({r['id'] for r in data['checks']}),len(data['checks']))

    def test_backend_never_substitutes_owner_for_reader(self):
        bindings={'identities':{'investigator':{'mode':'managed_identity','principal_id':'owner'}},'probes':{'model':{}}}
        # Even an empty binding is not permission evidence.
        bindings['probes']['model']={'url':'https://example.invalid'}
        result=check(mapping(),bindings=bindings)
        self.assertEqual(result['rows'][0]['reason'],'ACTUAL_IDENTITY_BINDING_MISMATCH')

    def test_http_probes_gateway_and_meter_and_never_emit_raw_body(self):
        auth={'mode':'managed_identity','principal_id':'reader'}
        binding={'url':'https://example.invalid/models/id','scope':'declared','channel':'reader'}
        backend=LiveProbes({'identities':{'investigator':auth},'probes':{'model':binding}})
        backend._count=lambda fn:fn()
        class Response(io.BytesIO):status=200
        raw=b'{"metadata":"sensitive-raw-value"}'
        with patch('investigator.adapters.vault_user_cache.provider') as provider,patch('investigator.live_gateway.open_http',return_value=Response(raw)) as gateway:
            provider.return_value.get_token.return_value='not-logged-token'
            result=check(mapping(),backend=backend)
        self.assertEqual(result['status'],'PASS');gateway.assert_called_once()
        self.assertNotIn('sensitive-raw-value',json.dumps(result));self.assertNotIn('not-logged-token',json.dumps(result))

    def test_fixed_connection_setting_is_checked_not_just_http_200(self):
        auth={'mode':'managed_identity','principal_id':'reader'}
        binding={'url':'https://example.invalid/connections/id','scope':'declared','channel':'reader',
                 'expect':{'credentialDetails.singleSignOnType':'None'}}
        backend=LiveProbes({'identities':{'investigator':auth},'probes':{'model':binding}});backend._count=lambda fn:fn()
        class Response(io.BytesIO):status=200
        with patch('investigator.adapters.vault_user_cache.provider'),patch('investigator.live_gateway.open_http',return_value=Response(b'{"credentialDetails":{"singleSignOnType":"Sso"}}')):
            result=check(mapping(),backend=backend)
        self.assertEqual(result['rows'][0]['reason'],'DECLARED_RESOURCE_SETTING_DIFFERS')

    def test_sql_different_served_principal_refuses(self):
        auth={'mode':'managed_identity','principal_id':'reader','tenant_id':'tenant'}
        backend=LiveProbes({'identities':{'investigator':auth},'probes':{'model':{'server':'server','database':'db','account':'reader'}}},
                           sql=lambda *_:{'status':'REACHABLE','surface_report':{'identity':'owner','object':'db'}})
        backend._count=lambda fn:fn()
        data=mapping();data['checks'][0]['probe']={'kind':'sql'}
        self.assertEqual(check(data,backend=backend)['rows'][0]['reason'],'SQL_SERVED_IDENTITY_OR_DATABASE_DIFFERS')

    def test_runner_records_warning_and_still_dispatches_build_phase(self):
        from investigator.unified_runner import run
        with tempfile.TemporaryDirectory() as folder:
            config={'version':'dia-runner-estate-v1','manifest':'/inputs/estate.json','image':'reg/worker@sha256:'+'a'*64,
                    'capture':{},'checks':{'A':{'kind':'investigation','options':{}}},'output_root':folder}
            seen=[];captured={}
            run(config,'A',registry={'investigation':lambda *_:seen.append('read')},put=lambda k,v:captured.setdefault(k,v))
            self.assertEqual(seen,['read'])
            self.assertTrue(any('admission-warning' in k for k in captured))

    def test_daily_smoke_invokes_access_check_and_retains_incomplete(self):
        from investigator.daily_smoke import run_smoke
        from investigator.shared_state import SharedState
        with tempfile.TemporaryDirectory() as folder:
            state=SharedState.offline(Path(folder)/'state.db');state.migrate()
            context=SimpleNamespace(step=lambda name,fn:fn())
            auth={'principal_id':'reader'}
            config={'version':1,'run_id':'daily','reader_authentication':auth,'gold_payload':{'authentication':auth},
                    'platform_blob':{},'demo_earned':False}
            with patch('investigator.daily_smoke.validate_gold_payload'),patch('investigator.access_check.configured',return_value={'status':'INCOMPLETE','rows':[]}) as access:
                result=run_smoke(config,context,state=state,sign_in=lambda:{},gold_read=lambda _: {},blob_roundtrip=lambda *_:{})
            access.assert_called_once();self.assertEqual(result['status'],'INCOMPLETE')


if __name__=='__main__':unittest.main()

"""Synthetic connector tests: transport selection changes no reasoning or grants."""
import base64
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch
from gateway_test_support import allow_native
from investigator.adapters.investigative_native import NativeQueries
from investigator.adapters import xmla_query
from investigator.live_gateway import GatewayDenied
from metadata_config import worker_configuration
from run_native_diagnostic import execute

W='11111111-1111-4111-8111-111111111111'
M='22222222-2222-4222-8222-222222222222'
P='33333333-3333-4333-8333-333333333333'
T='44444444-4444-4444-8444-444444444444'


def setting():
    return dict(mode='xmla',library='.local/synthetic/client.dll',workspace_id=W,
                workspace_name='Practice fixture',models={M:'Practice quantity'})


def reader():
    return dict(mode='isolated_reader',tenant_id=T,principal_id=P,account='reader@example.test',model_ids=[M])


def token(**overrides):
    claims=dict(oid=P,tid=T,aud='https://analysis.windows.net/powerbi/api',exp=9999999999)
    claims.update(overrides)
    return 'header.'+base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip('=')+'.signature'


class XmlaConnectorTests(unittest.TestCase):
    def request(self):return dict(workspace=W,native_model_id=M,query='EVALUATE ROW("ok", 1)')

    def test_engine_route_passes_only_installed_setting_and_default_stays_rest(self):
        dax=Mock(return_value={'results':[{'tables':[{'rows':[{'[ok]':1}]}]}]})
        config={'fabric':{'auth':{'tenant_id':T},'native_reader':reader()}}
        route=dict(kind='DAX',workspace=W,model=M,asset_ids=['measure'],config=config)
        native=NativeQueries({'semantic':route},source=Mock(),fabric=Mock(),dax=dax,offline=True)
        bound=dict(query=self.request()['query'],asset_ids=['measure'])
        self.assertEqual(native('semantic',bound,timeout_seconds=30)['rows'],[{'[ok]':1}])
        self.assertNotIn('transport_config',dax.call_args.kwargs)
        route['config']['fabric']['dax_transport']=setting()
        native=NativeQueries({'semantic':route},source=Mock(),fabric=Mock(),dax=dax,offline=True)
        native('semantic',bound,timeout_seconds=30)
        self.assertEqual(dax.call_args.kwargs['transport_config'],setting())

    def test_worker_projection_keeps_transport_and_rejects_unknown_fields(self):
        config=dict(version=1,fabric=dict(workspace_id=W,auth=dict(mode='fabric_cli',tenant_id=T,python='python'),
                    native_reader=reader(),dax_transport=setting()),storage=dict(database='.local/synthetic/catalog.sqlite'))
        projected=worker_configuration(config,self.request())
        self.assertEqual(projected['fabric']['dax_transport'],setting())
        for alteration in (dict(mode='rest'),dict(effective_user='owner'),dict(models={}),dict(library='../bad.dll')):
            bad=deepcopy(config);bad['fabric']['dax_transport'].update(alteration)
            with self.subTest(alteration=alteration),self.assertRaises(ValueError):worker_configuration(bad,self.request())

    def test_real_executor_selects_xmla_preserves_decimal_and_identity_no_rest_fallback(self):
        from investigator.native_identity import require
        raw='{"results":[{"tables":[{"rows":[{"[amount]":123456.123456789}]}]}]}'
        with patch('connect_fixture_reader.application'),patch('connect_fixture_reader.token',return_value=token()),\
             patch.object(xmla_query,'read',return_value=raw) as read,patch('investigator.live_gateway.open_http') as rest:
            result=execute(self.request(),T,reader(),transport_config=setting())
            from decimal import Decimal
            result=json.loads(result,parse_float=Decimal)
            require(result,self.request(),reader())
            self.assertEqual(result['results'][0]['tables'][0]['rows'][0]['[amount]'],Decimal('123456.123456789'))
            read.assert_called_once();rest.assert_not_called()
            read.side_effect=RuntimeError('unavailable')
            with self.assertRaises(RuntimeError):execute(self.request(),T,reader(),transport_config=setting())
            rest.assert_not_called()

    def test_wrong_principal_tenant_or_audience_never_dispatches(self):
        for claims in (dict(oid=W),dict(tid=W),dict(aud='https://database.windows.net/')):
            with self.subTest(claims=claims),patch('connect_fixture_reader.application'),\
                 patch('connect_fixture_reader.token',return_value=token(**claims)),patch.object(xmla_query,'read') as read:
                with self.assertRaises(ValueError):execute(self.request(),T,reader(),transport_config=setting())
                read.assert_not_called()

    def test_gateway_and_model_scope_reject_before_subprocess(self):
        run=Mock()
        with allow_native('XMLA_EVALUATE',workspace=W,model=M):
            for req in (dict(self.request(),query='REFRESH model'),dict(self.request(),native_model_id=W),dict(self.request(),workspace=M)):
                with self.subTest(req=req),self.assertRaises((ValueError,GatewayDenied)):
                    xmla_query.read(setting(),req,'never-used',timeout_seconds=30,run=run)
        run.assert_not_called()

    def test_rows_bounds_errors_and_secret_stdin_only(self):
        with tempfile.TemporaryDirectory() as folder:
            library=Path(folder)/'client.dll';library.touch()
            runner=Mock(return_value=SimpleNamespace(returncode=0,stdout='{"results":[{"tables":[{"rows":[{"[ok]":1}]}]}]}'))
            with patch('sys.platform','win32'),patch('fabric_sql_auth.profile_path',return_value=library),allow_native('XMLA_EVALUATE',workspace=W,model=M):
                result=xmla_query.read(setting(),self.request(),'secret-token',timeout_seconds=30,run=runner)
                self.assertEqual(json.loads(result)['results'][0]['tables'][0]['rows'],[{'[ok]':1}])
                self.assertNotIn('secret-token',str(runner.call_args.args))
                self.assertEqual(json.loads(runner.call_args.kwargs['input'])['access_token'],'secret-token')
                for output in ('{}','{"results":[{"error":"failure"}]}',json.dumps({'results':[{'tables':[{'rows':[{}]*10001}]}]})):
                    runner.return_value.stdout=output
                    with self.subTest(output=output[:40]),self.assertRaises(ValueError):
                        xmla_query.read(setting(),self.request(),'secret-token',timeout_seconds=30,run=runner)
                runner.return_value=SimpleNamespace(returncode=1,stdout='secret-token',stderr='secret-token')
                with self.assertRaisesRegex(RuntimeError,'^XMLA native query failed$'):
                    xmla_query.read(setting(),self.request(),'secret-token',timeout_seconds=30,run=runner)

    def test_native_script_uses_token_property_no_impersonation_or_password(self):
        script=(Path(__file__).resolve().parents[1]/'infra/scripts/Read-XmlaQuery.ps1').read_text()
        self.assertIn('$connection.AccessToken',script)
        self.assertIn('DbConnectionStringBuilder',script)
        for prohibited in ('EffectiveUserName','Password','Roles','ExecuteNonQuery','Invoke-ASCmd'):
            self.assertNotIn(prohibited,script)

    def test_linux_uses_pinned_dotnet_client_and_no_powershell_or_local_dll(self):
        runner=Mock(return_value=SimpleNamespace(returncode=0,stdout='{"results":[{"tables":[{"rows":[{"[ok]":1}]}]}]}'))
        with patch('sys.platform','linux'),patch.object(Path,'is_file',return_value=True),allow_native('XMLA_EVALUATE',workspace=W,model=M):
            xmla_query.read(setting(),self.request(),'secret-token',timeout_seconds=30,run=runner)
        self.assertEqual(runner.call_args.args[0],['dotnet','/opt/dia/xmla-reader/Dia.XmlaReader.dll'])
        self.assertEqual(json.loads(runner.call_args.kwargs['input'])['library'],'')

    def test_cloud_probe_has_fixed_query_and_uses_real_engine_port(self):
        from probe_native_dax import probe, QUERY
        config=dict(version=1,fabric=dict(workspace_id=W,auth=dict(mode='fabric_cli',tenant_id=T,python='python'),
                    native_reader=reader(),dax_transport=setting()),storage=dict(database='.local/synthetic/catalog.sqlite'))
        with patch('investigator.adapters.investigative_native.NativeQueries') as native:
            native.return_value.return_value={'rows':[{'[ok]':1}]}
            self.assertEqual(probe(config,M)['status'],'PASS')
            self.assertEqual(native.return_value.call_args.args[1]['query'],QUERY)
            self.assertEqual(QUERY,'EVALUATE ROW("ok", 1)')
            with self.assertRaises(ValueError):probe(config,W)

    @unittest.skipUnless(Path('/opt/dia/xmla-reader/Dia.XmlaReader.dll').is_file(),'native Linux image dependency check')
    def test_linux_image_loads_adomd_without_network_or_credentials(self):
        import subprocess
        result=subprocess.run(['dotnet','/opt/dia/xmla-reader/Dia.XmlaReader.dll','--self-test'],
                              capture_output=True,text=True,check=True,timeout=30)
        self.assertEqual(json.loads(result.stdout)['status'],'PASS')


if __name__=='__main__':unittest.main()


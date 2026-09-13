"""Reusable connector tests use alternate targets and injected credentials/transports."""
import base64
import sys
from unittest.mock import patch
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from metadata_config import ROOT, load_config
from metadata_auth import MetadataHttp, AzureCredentialTokens, PowerShellSqlCatalog
from metadata_connectors import SqlMetadataConnector, FabricMetadataConnector, PowerBIMetadataConnector, UnsupportedCapability


class ConnectorTests(unittest.TestCase):
    def test_parity_ignores_acquisition_time_but_detects_definition_change(self):
        from metadata_inventory import Inventory
        from compare_metadata_scans import compare
        with tempfile.TemporaryDirectory() as temp:
            database=Path(temp)/'inventory.sqlite'
            runs=[]
            for expression in ['SUM(a)', 'SUM(a)', 'SUM(b)']:
                store=Inventory(database)
                store.asset('db','SqlDatabase','db','catalog',{'captured_at':str(len(runs))})
                store.asset('measure','Measure','Sales','api',{'expression':expression})
                runs.append(store.scan)
                store.finish(); store.db.close()
            self.assertEqual(compare(database,runs[0],runs[1])['status'],'PASS')
            self.assertEqual(compare(database,runs[0],runs[2])['changed'],['measure'])

    def test_local_auth_rejects_wrong_tenant(self):
        from metadata_auth import FabricCliTokens
        payload = base64.urlsafe_b64encode(json.dumps({'tid':'wrong-tenant'}).encode()).decode().rstrip('=')
        fake = SimpleNamespace(FabAuth=lambda: SimpleNamespace(get_access_token=lambda *a,**kw: 'header.'+payload+'.signature'))
        with patch.dict(sys.modules, {'fabric_cli.core.fab_auth':fake}):
            with self.assertRaises(RuntimeError): FabricCliTokens('expected-tenant').get_token('scope')

    def test_configuration_alternate_targets_and_secret_rejection(self):
        config = json.loads((ROOT/'infra/metadata/development.json').read_text(encoding='utf-8-sig'))
        config['sql']['server'] = 'another.database.windows.net'
        config['sql']['database'] = 'other_database'
        config['fabric']['workspace_id'] = '11111111-1111-1111-1111-111111111111'
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'config.json'
            path.write_text(json.dumps(config))
            loaded = load_config(path)
            self.assertEqual(loaded['sql']['server'], 'another.database.windows.net')
            self.assertTrue(Path(loaded['sql']['auth']['credential_file']).is_absolute())
            config['sql']['auth']['password'] = 'must-not-be-in-config'
            path.write_text(json.dumps(config))
            with self.assertRaises(ValueError): load_config(path)

    def test_sql_connector_uses_injected_reader(self):
        calls = []
        def reader(*args):
            calls.append(args)
            return {'objects': []}
        connector = SqlMetadataConnector({'server':'other.host','database':'otherdb','visibility_schema':'sales'}, reader)
        self.assertEqual(connector.discover_assets(), {'objects':[]})
        self.assertEqual(calls, [('other.host','otherdb','sales')])
        with self.assertRaises(UnsupportedCapability): connector.get_refresh_history({})

    def test_local_sql_adapter_passes_values_as_arguments(self):
        def runner(command, **kwargs):
            self.assertEqual(command[command.index('-Database')+1], 'name;with delimiter')
            self.assertEqual(command[command.index('-VisibilitySchema')+1], 'sales')
            Path(command[command.index('-OutputPath')+1]).write_text('{"objects":[]}')
            return SimpleNamespace(returncode=0)
        adapter = PowerShellSqlCatalog('reader.ps1','credential.xml',runner)
        self.assertEqual(adapter('other.host','name;with delimiter','sales'), {'objects':[]})

    def test_fabric_and_powerbi_use_configured_workspace(self):
        calls = []
        def transport(endpoint, **kwargs):
            calls.append((endpoint,kwargs.get('audience')))
            return {'text':{'value':[]}}
        connector = FabricMetadataConnector('another-workspace',transport,lambda *a: {})
        connector.discover_assets()
        connector.get_refresh_history({'id':'notebook'})
        PowerBIMetadataConnector(connector).get_refresh_history({'type':'SemanticModel','id':'model'})
        self.assertEqual(calls, [('workspaces/another-workspace/items','fabric'),
            ('workspaces/another-workspace/items/notebook/jobs/instances','fabric'),
            ('groups/another-workspace/datasets/model/refreshes','powerbi')])

    def test_http_uses_injected_credential_and_blocks_mutations(self):
        scopes=[]
        credential=SimpleNamespace(get_token=lambda scope: (scopes.append(scope) or SimpleNamespace(token='test-token')))
        class Response(io.BytesIO):
            status=200
            headers={}
        class Opener:
            def open(self, request, **kwargs):
                self.request=request
                return Response(b'{"value":[]}')
        opener=Opener()
        http=MetadataHttp(AzureCredentialTokens(credential),opener)
        self.assertEqual(http('groups/w/datasets',audience='powerbi')['status_code'],200)
        self.assertEqual(scopes,['https://analysis.windows.net/powerbi/api/.default'])
        self.assertEqual(opener.request.full_url,'https://api.powerbi.com/v1.0/myorg/groups/w/datasets')
        for endpoint,method in [('https://evil.example','get'),('items/x','delete'),('items/x/updateDefinition','post')]:
            with self.assertRaises(ValueError): http(endpoint,method)
        self.assertEqual(len(scopes),1)

    def test_onelake_fallback_receives_dynamic_item(self):
        def unavailable(*args, **kwargs): raise RuntimeError('unsupported')
        calls=[]
        def fallback(workspace,item):
            calls.append((workspace,item['id']))
            return {'tables':[], 'source':'OneLake'}
        c=FabricMetadataConnector('other-workspace',unavailable,fallback)
        self.assertTrue(c.get_tables({'id':'other-lakehouse'})['column_schema'])
        self.assertEqual(calls,[('other-workspace','other-lakehouse')])


if __name__ == '__main__': unittest.main()

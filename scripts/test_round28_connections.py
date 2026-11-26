"""Synthetic offline named-database routing; no estate data or expectations."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
from investigator.adapters.sql_connections import entries, for_asset, for_request, root
from investigator.adapters.estate_installation import configuration
from investigator import estate_config
from test_round28_configuration import draft

ROOT = Path(__file__).resolve().parents[1]


def sql(database, account='reader'):
    return dict(server='source.example.test', database=database, visibility_schema='app',
                auth=dict(mode='dpapi_file', credential_file='unused.xml', account=account))


class NamedConnectionTests(unittest.TestCase):
    def bundle(self):
        from test_estate_manifest import ManifestTests
        manifest=ManifestTests().fixture()
        options=manifest['adapters'][0]['options']
        options.pop('sql', None)
        options['sql_connections']={'first':sql('first'), 'second':sql('second','other-reader')}
        # Use only synthetic application declarations; no fixture semantics involved.
        manifest['layers']=[];manifest['resources']=[];manifest['system_of_record']=None
        manifest['pipelines']=[];manifest['lineage']['source_delivery']=None
        for name,connection in options['sql_connections'].items():
            manifest['identities'].append(dict(id='reader-'+name,principal=connection['auth']['account'],
                credential_reference='unused.xml',scopes=[]))
            address=root(connection)+'/object/1'
            manifest['layers'].append(dict(id=name,asset_id=address,role='APPLICATION',business_name='application',
                reachable=True,reach=dict(adapter=manifest['adapters'][0]['id'],address=address,reader='reader-'+name,connection=name)))
        return manifest

    def test_native_bundle_has_independent_readers_and_exact_layer_bindings(self):
        m=self.bundle()
        with patch('socket.socket.connect', side_effect=AssertionError('NETWORK_FORBIDDEN')):
            config=configuration(m)
        self.assertNotIn('sql',config)
        for name in ('first','second'):
            selected=for_asset(config, m['layers'][('first','second').index(name)]['asset_id'],name)
            self.assertEqual(selected['sql']['database'],name)
            self.assertEqual(selected['sql']['auth']['account'],'reader' if name=='first' else 'other-reader')
        bad=deepcopy(m);bad['layers'][0]['reach']['connection']='second'
        with self.assertRaisesRegex(ValueError,'outside declared'):configuration(bad)
        bad=deepcopy(m);bad['layers'][0]['reach']['reader']='reader-second'
        with self.assertRaisesRegex(ValueError,'account differs'):configuration(bad)

    def test_request_cannot_default_or_cross_databases(self):
        config={'sql_connections':{'first':sql('first'),'second':sql('second')}}
        first=root(sql('first'))+'/object/1';second=root(sql('second'))+'/object/1'
        self.assertEqual(for_request(config,{'asset_ids':[second]})['sql']['database'],'second')
        for request in ({},{'asset_ids':[first,second]},{'asset_ids':['sql://other/db/object/1']}):
            with self.assertRaises(ValueError):for_request(config,request)
        self.assertNotIn('sql',config)
        old={'sql':sql('only')};self.assertIs(for_request(old,{}),old)

    def test_closed_native_validation_refuses_duplicates_unknown_fields_and_mixed_defaults(self):
        from metadata_config import validate_config
        config=configuration(self.bundle())
        # configuration adds _estate; validate just its original worker fields.
        config={key:value for key,value in config.items() if key in ('version','sql_connections','fabric','storage')}
        validate_config(deepcopy(config))
        for mutation in (lambda c:c.update(sql=sql('first')),
                         lambda c:c['sql_connections'].update(second=sql('first')),
                         lambda c:c['sql_connections']['first']['auth'].update(password='forbidden')):
            bad=deepcopy(config);mutation(bad)
            with self.assertRaises(ValueError):validate_config(bad)

    def test_outer_identity_secrets_and_layer_references_are_checked(self):
        value=draft();value['connections']={'first':dict(server='source.example.test',database='first',identity='reader',secret_refs=['model-key'])}
        value['connectors'][0]['connection']='first';value['layers']['source']['connections']=['first']
        estate_config.validate(value)
        for mutation in (lambda v:v['connections']['first'].update(identity='unknown'),
                         lambda v:v['connections']['first'].update(secret_refs=['unknown']),
                         lambda v:v['layers']['source'].update(connections=['unknown']),
                         lambda v:v['connectors'][0].update(connection='unknown')):
            bad=deepcopy(value);mutation(bad)
            with self.assertRaises(ValueError):estate_config.validate(bad)

    def test_source_worker_receives_selected_database_and_credential_only(self):
        from run_source_diagnostic import read_once
        config={'sql_connections':{'first':sql('first'),'second':sql('second','other-reader')}}
        request={'asset_ids':[root(sql('second'))+'/object/1'],'query':'SELECT 1'}
        runner=Mock(return_value=Mock(stdout='{"value":"1"}',returncode=0))
        with patch('investigator.physical_reads.run',runner):read_once(config,request)
        payload=json.loads(runner.call_args.kwargs['input'])
        self.assertEqual(payload['database'],'second');self.assertEqual(payload['credential_file'],'unused.xml')
        self.assertNotIn('sql_connections',payload)

    def test_catalog_opens_both_database_routes_with_distinct_configs(self):
        from investigator.adapters.ai_native_catalog import NativeCatalog
        from test_round23_native_catalog import asset
        assets=[];nodes=[]
        for name in ('first','second'):
            parent=root(sql(name));identity=parent+'/object/1'
            assets.extend([asset(parent,'SqlDatabase',None,name,{}),asset(identity,'SqlObject',parent,'Fact',{'name':'Fact','schema_name':'app'})])
            nodes.append({'id':name,'properties':{'asset_id':identity}})
        config={'sql_connections':{'first':sql('first'),'second':sql('second','other-reader')}}
        catalog=NativeCatalog(assets=assets,graph_nodes=nodes,configuration=config,endpoint=Mock(),sql_read=Mock(),record=Mock())
        self.assertEqual({r['database'] for r in catalog.routes.values()},{'first','second'})
        for route in catalog.routes.values():self.assertEqual(route['database'],route['config']['sql']['database'])

    def test_deployment_drafts_stay_disabled_and_practice_is_single_connection(self):
        path=ROOT/'config/estates/healthnet.json'
        if not path.exists():self.skipTest('Deployment files excluded from public image')
        with patch('socket.socket.connect',side_effect=AssertionError('NETWORK_FORBIDDEN')):
            value=estate_config.load(path)
            self.assertEqual(estate_config.dry_run(value)['status'],'DRAFT_DISABLED')
            with self.assertRaisesRegex(ValueError,'ESTATE_DISABLED'):estate_config.engine_manifest(value)
        self.assertEqual(len(value['connections']),2)
        self.assertEqual(len(estate_config.load(ROOT/'config/estates/practice-fixture.json')['connections']),1)

    def test_metadata_discovery_uses_each_named_reader_and_retains_both_roots(self):
        from test_enterprise_discovery import DiscoveryTests
        from investigator.discovery_collect import Collector
        fixture=DiscoveryTests();fixture.setUp()
        try:
            config=deepcopy(fixture.config);base=config.pop('sql')
            config['sql_connections']={'first':deepcopy(base),'second':dict(deepcopy(base),database='second')}
            readers={}
            for name,connection in config['sql_connections'].items():
                def read(server,database,schema,connection=connection):
                    self.assertEqual((server,database,schema),(connection['server'],connection['database'],connection['visibility_schema']))
                    return dict(fixture.sql(),server=server,database=database)
                readers[name]=Mock(side_effect=read)
            batch=Collector(config,fixture.transport,readers).run()
            found={a['id'] for a in batch['assets'] if a['kind']=='SqlDatabase'}
            self.assertEqual(found,{root(c) for c in config['sql_connections'].values()})
            for reader in readers.values():reader.assert_called_once()
        finally:fixture.tearDown()

    def test_named_secret_references_validate_offline_without_fetching(self):
        from metadata_config import validate_config
        from investigator.adapters.vault_user_cache import SQL
        config=configuration(self.bundle())
        config={k:v for k,v in config.items() if k in ('version','sql_connections','fabric','storage')}
        identity='11111111-1111-4111-8111-111111111111'
        for name,connection in config['sql_connections'].items():
            connection['auth']=dict(mode='key_vault_user_cache',tenant_id=identity,client_id=identity,
                principal_id=identity,account=name+'@example.test',scope=SQL,
                reference=dict(vault_url='https://test-vault.vault.azure.net',secret_name=name+'-reader-cache',secret_version='a'*32,identity=dict(mode='managed_identity',tenant_id=identity,client_id=identity,principal_id=identity)))
        with patch('socket.socket.connect',side_effect=AssertionError('NETWORK_FORBIDDEN')):
            validate_config(config)
        self.assertNotEqual(config['sql_connections']['first']['auth']['reference'],config['sql_connections']['second']['auth']['reference'])

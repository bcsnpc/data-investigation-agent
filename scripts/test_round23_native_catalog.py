import unittest
from copy import deepcopy
from unittest.mock import Mock,patch
from investigator.adapters.ai_native_catalog import NativeCatalog


def asset(identity,kind,parent,name,metadata):
    return {'id':identity,'kind':kind,'parent_id':parent,'name':name,'metadata':metadata,
            'content_hash':'a'*64,'availability':'CURRENT','provenance':'DISCOVERED'}


class NativeCatalogTests(unittest.TestCase):
    def test_literal_directlake_route_requires_native_ownership_not_matching_names(self):
        import json
        model='fabric://workspace/model';table=model+'/table/Activity';endpoint='fabric://workspace/endpoint'
        self.assets += [asset(model,'SemanticModel','fabric://workspace','Model',{}),
            asset(table,'SemanticTable',model,'Activity',{'name':'Activity','partitions':[{'mode':'directLake','source':{'type':'entity','schemaName':'dbo','entityName':'Items','expressionSource':'Source'}}]}),
            asset(model+'/bim','DefinitionPart',model,'model.bim',{'content':json.dumps({'model':{'expressions':[{'name':'Source','expression':'let S = Sql.Database("fabric-server", "endpoint") in S'}]}})})]
        self.nodes.append({'id':'semantic-table','properties':{'asset_id':table}})
        path={'nodes':[self.nodes[-1]]}
        self.assertEqual(self.build().declared_continuations(path),[])
        witness=asset(model+'/native-relation/one','NativeItemRelationMetadata',model,'Native relation',{
            'endpoint_asset_hash':'a'*64,'container_asset_hash':'a'*64,
            'relation':{'source':endpoint,'target':self.parent,'relation':'NATIVE_CASCADEDELETE','provenance':'DISCOVERED',
                        'evidence':[{'scope':model,'source_api':'fabric_item_relations_beta'}]}})
        self.assets.append(witness)
        value=self.build().declared_continuations(path)
        self.assertEqual(value[0]['physical_table'],self.table)
        self.assertEqual(value[0]['graph_nodes'],['table-node']);self.read.assert_not_called()
        witness['metadata']['container_asset_hash']='b'*64
        self.assertEqual(self.build().declared_continuations(path),[])

    def test_practice_application_report_references_existing_model_and_no_saved_filters(self):
        import json,base64
        from fixture.guided_report import application_report
        visual={'visual':{'query':{'queryState':{'Values':{'projections':[{'field':{'Measure':{
            'Property':'Handled Quantity','Expression':{'SourceRef':{'Entity':'Activity'}}}}}]}}}}}
        documents={'.platform':{'metadata':{'displayName':'Template'}},
            'definition/pages/p/page.json':{'displayName':'Template','filterConfig':{}},
            'definition/pages/p/visuals/25189fcc5fe05539b3b6/visual.json':visual,
            'definition/pages/p/visuals/unrelated/visual.json':visual,
            'definition/report.json':{'filterConfig':{}},
            'definition.pbir':{'datasetReference':{'byConnection':{'connectionString':'model=${ITEM_4};workspace=${WORKSPACE_NAME}'}}}}
        template={'parts':[{'path':p,'content':json.dumps(d)} for p,d in documents.items()]}
        result=application_report(template,workspace_name='Fixture',model_name='Application',model_id='existing-model',logical_id='logical',record_fields=('warehouse_id','product_id','units'))
        parts={p['path']:json.loads(base64.b64decode(p['payload'])) for p in result['parts']}
        visuals=[v for p,v in parts.items() if p.endswith('/visual.json') and v['visual'].get('visualType')!='tableEx']
        self.assertEqual(len(visuals),1)
        field=visuals[0]['visual']['query']['queryState']['Values']['projections'][0]['field']['Measure']
        self.assertEqual(field['Property'],'Movement Units');self.assertEqual(field['Expression']['SourceRef']['Entity'],'Movements')
        self.assertIn('existing-model',json.dumps(parts['definition.pbir']))
        self.assertFalse(any('filterConfig' in p for p in parts.values()))
        table=next(v for p,v in parts.items() if '/round23records/' in p)
        fields=table['visual']['query']['queryState']['Values']['projections']
        self.assertEqual([p['field']['Column']['Property'] for p in fields],['warehouse_id','product_id','units'])
        self.assertNotIn('movement_id',json.dumps(table))

    def test_security_reads_existing_scope_and_retained_roles_are_not_current_memberships(self):
        import json
        from investigator.adapters.guided_security import Security
        parent='fabric://workspace/model'
        assets=[asset(parent,'SemanticModel','fabric://workspace','Model',{}),
                asset(parent+'/bim','DefinitionPart',parent,'model.bim',{'content':json.dumps({'model':{'roles':[{'name':'North','tablePermissions':[{'name':'Items','filterExpression':'Items[region]="North"'}]}]}})})]
        http=Mock(return_value={'status_code':403,'text':'denied'})
        result=Security(assets=assets,nodes=[{'id':'model','properties':{'asset_id':parent}}],http=http)('model')
        http.assert_called_once_with('workspaces/workspace/items/model/connections')
        self.assertEqual(result['checks'][0]['state'],'RETAINED_SNAPSHOT')
        self.assertEqual(result['checks'][0]['roles'][0]['name'],'North')
        self.assertEqual(result['checks'][1]['state'],'BLOCKED_PENDING_OWNER')
        self.assertTrue(result['no_impersonation'])

    def test_view_schema_topup_is_exact_readonly_catalog_control(self):
        from investigator.adapters.binding_catalog import request_many,compiled_control_objects
        objects=[{'connection':'server','database':'database','catalog':{'metadata':{'schema_name':'dbo','name':'View'}}}]
        old=request_many(objects);new=request_many(objects,include_views=True)
        self.assertIn('JOIN sys.tables AS o',old['query'])
        self.assertIn("o.type IN ('U','V')",new['query'])
        payload={**new,'server':'server','database':'database'}
        self.assertEqual(compiled_control_objects(payload),['[dbo].[View]'])
        payload['query']=payload['query'].replace("('U','V')","('U','V','P')")
        self.assertIsNone(compiled_control_objects(payload))

    def test_cloud_metadata_uses_full_auth_not_short_native_reader_profile(self):
        from cloud_guided_investigator import metadata_tokens
        from test_federated_reader import D
        profile={k:v for k,v in D.items() if k!='managed_identity'}
        config={'fabric':{'auth':deepcopy(D),'native_reader':profile}}
        with patch('investigator.adapters.vault_user_cache.provider') as provider:
            self.assertIs(metadata_tokens(config),provider.return_value)
        provider.assert_called_once_with(D)
        self.assertNotIn('managed_identity',profile)

    def setUp(self):
        self.config={'sql':{'server':'server','database':'application'},
                     'fabric':{'sql_reader':{'server':'fabric-server','account':'reader'}}}
        self.parent='fabric://workspace/lakehouse'
        self.table=self.parent+'/table/Items'
        self.assets=[asset(self.parent,'Lakehouse','fabric://workspace','Bronze',{}),
                     asset(self.table,'LakehouseTable',self.parent,'Items',{'name':'Items'}),
                     asset('fabric://workspace/endpoint','SQLEndpoint','fabric://workspace','Bronze SQL',{})]
        self.endpoint=Mock(return_value={'id':'lakehouse','properties':{
            'sqlEndpointProperties':{'id':'endpoint','connectionString':'fabric-server'}}})
        self.read=Mock(return_value={'read_only_verified':True,'rows':[
            {'schema_name':'dbo','table_name':'Items','column_name':'quantity',
             'data_type':'bigint','collation_name':None}]})
        self.nodes=[{'id':'table-node','properties':{'asset_id':self.table}}]

    def build(self):
        return NativeCatalog(assets=self.assets,graph_nodes=self.nodes,configuration=self.config,
                             endpoint=self.endpoint,sql_read=self.read,record=Mock())

    def test_no_schema_read_until_layer_opened_then_native_types_and_cache(self):
        catalog=self.build();self.read.assert_not_called();self.endpoint.assert_not_called()
        identity=next(iter(catalog.routes));result=catalog.prepare(identity)
        self.assertEqual(result['database'],'Bronze SQL')
        self.assertEqual(result['objects'][0]['metadata']['columns'][0]['data_type'],'bigint')
        self.assertEqual(self.read.call_args.args[2]['read_only_objects'],['[dbo].[Items]'])
        catalog.prepare(identity);self.read.assert_called_once()

    def test_endpoint_is_exact_declared_parent_and_known_reader(self):
        for changed in ({'id':'other','properties':{}},
                        {'id':'lakehouse','properties':{'sqlEndpointProperties':{'id':'endpoint','connectionString':'other'}}},
                        {'id':'lakehouse','properties':{'sqlEndpointProperties':{'id':'unknown','connectionString':'fabric-server'}}}):
            with self.subTest(changed=changed):
                self.endpoint.return_value=changed;catalog=self.build()
                with self.assertRaises(ValueError):catalog.prepare(next(iter(catalog.routes)))
        self.read.assert_not_called()

    def test_only_graph_known_tables_enter_routes(self):
        self.nodes=[];self.assertEqual(self.build().routes,{})

    def test_column_only_lineage_opens_its_containing_native_table(self):
        column=self.table+'/column/quantity'
        self.assets.append(asset(column,'LakehouseColumn',self.table,'quantity',{'name':'quantity'}))
        self.nodes.append({'id':'column-node','properties':{'asset_id':column}})
        catalog=self.build();identity=next(iter(catalog.routes))
        self.assertIn('column-node',catalog.routes[identity]['path_nodes'])
        self.assertEqual(len(catalog.prepare(identity,['column-node'])['objects']),1)

    def test_source_and_dax_use_retained_actual_schema_without_query_compiler(self):
        source='sql://server/application';table=source+'/object/1'
        model='fabric://workspace/model';semantic=model+'/table/Activity'
        self.assets += [asset(source,'SqlDatabase',None,'application',{}),
            asset(table,'SqlObject',source,'Items',{'schema_name':'dbo','name':'Items','type_desc':'USER_TABLE',
                                                 'columns':[{'name':'quantity','data_type':'int'}]}),
            asset(model,'SemanticModel','fabric://workspace','Model',{}),
            asset(semantic,'SemanticTable',model,'Activity',{'name':'Activity'}),
            asset(semantic+'/measures/Quantity','Measure',semantic,'Quantity',{'expression':'SUM(Activity[quantity])'})]
        self.nodes += [{'id':'source-node','properties':{'asset_id':table}},
                       {'id':'model-node','properties':{'asset_id':semantic}}]
        catalog=self.build()
        for identity,route in catalog.routes.items():
            if route['kind']=='SOURCE_SQL':
                self.assertEqual(catalog.prepare(identity)['objects'][0]['metadata']['columns'][0]['name'],'quantity')
            if route['kind']=='DAX':
                self.assertEqual(catalog.prepare(identity)['model'],'model')
                self.assertTrue(any(a['kind']=='Measure' for a in route['objects']))
        self.read.assert_not_called()

    def test_semantic_schema_opens_path_tables_and_related_dimensions_only(self):
        parent='fabric://workspace/model'
        self.assets += [asset(parent,'SemanticModel','fabric://workspace','Model',{})]
        for name in ('Activity','Locations','Unrelated'):
            self.assets += [asset(parent+'/table/'+name,'SemanticTable',parent,name,{'name':name}),
                asset(parent+'/table/'+name+'/column/q','SemanticColumn',parent+'/table/'+name,'q',{'name':'q'})]
            self.nodes.append({'id':name,'properties':{'asset_id':parent+'/table/'+name}})
        self.assets.append(asset(parent+'/relationship/r','SemanticRelationship',parent,'r',{'fromTable':'Activity','toTable':'Locations'}))
        catalog=self.build();identity=next(i for i,r in catalog.routes.items() if r['kind']=='DAX')
        result=catalog.prepare(identity,['Activity'])
        self.assertEqual({a['name'] for a in result['objects'] if a['kind']=='SemanticTable'},{'Activity','Locations'})
        self.assertEqual({a['name'] for a in catalog.prepare(identity,['Unrelated'])['objects'] if a['kind']=='SemanticTable'},{'Activity','Locations','Unrelated'})


if __name__=='__main__':unittest.main()

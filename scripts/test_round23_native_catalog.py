import unittest
from copy import deepcopy
from unittest.mock import Mock,patch
from investigator.adapters.ai_native_catalog import NativeCatalog


def asset(identity,kind,parent,name,metadata):
    return {'id':identity,'kind':kind,'parent_id':parent,'name':name,'metadata':metadata,
            'content_hash':'a'*64,'availability':'CURRENT','provenance':'DISCOVERED'}


class NativeCatalogTests(unittest.TestCase):
    def test_declared_manifest_source_and_producer_are_opened_only_after_delivery(self):
        source='sql://server/application/object/10';pipeline='fabric://workspace/pipeline'
        self.assets += [asset('sql://server/application','SqlDatabase','sql://server','application',{}),asset(source,'SqlObject','sql://server/application','Source',{'name':'Source','schema_name':'app','columns':[]}),asset(pipeline,'DataPipeline','fabric://workspace','Copy',{})]
        self.nodes += [{'id':'source-node','properties':{'asset_id':source}},{'id':'job-node','properties':{'asset_id':pipeline}}]
        self.config['_estate']={'layers':[{'id':'app','asset_id':source},{'id':'landing','asset_id':self.table}],
            'lineage':{'bindings':[{'from_layer':'app','to_layer':'landing','provenance':'DECLARED_BY_DEFINITION'}]},
            'pipelines':[{'from_layer':'app','to_layer':'landing','producer_asset_id':pipeline,'audit':{'status':'ABSENT'}}]}
        c=self.build()
        self.assertEqual(c.declared_continuations({'nodes':[]}),[])
        result=c.declared_continuations({'nodes':[self.nodes[0]]})
        self.assertEqual(result[0]['confidence'],'DECLARED')
        self.assertEqual(result[0]['graph_nodes'],['job-node','source-node'])
        self.assertEqual(result[0]['source_asset'],source)
        self.config['_estate']['lineage']['bindings']=[]
        self.assertEqual(self.build().declared_continuations({'nodes':[self.nodes[0]]}),[])
        self.read.assert_not_called()

    def test_literal_model_binding_does_not_depend_on_inventory_root_parent(self):
        import json
        from investigator.adapters.estate_graph_static import StaticGraph
        from investigator.adapters.native_catalog_projection import native_parent
        report='fabric://workspace/report';model='fabric://workspace/model'
        assets=[asset(report,'Report','fabric://workspace','Report',{}),
            asset(model,'SemanticModel',None,'Model',{}),
            asset(report+'/part/definition.pbir','DefinitionPart',report,'definition.pbir',
                {'content':json.dumps({'datasetReference':{'byConnection':{'connectionString':'semanticmodelid=model'}}})})]
        for item in assets:item.pop('content_hash')
        graph=StaticGraph('fixture','owner','2026-10-27T00:00:00Z',assets,lambda _:None)
        self.assertEqual(graph.model_for_report(report),model)
        self.assertEqual(native_parent(assets[1]),'fabric://workspace')
        assets[1]['id']='fabric://different-workspace/model'
        graph=StaticGraph('fixture','owner','2026-10-27T00:00:00Z',assets,lambda _:None)
        self.assertIsNone(graph.model_for_report(report))
    def test_context_excludes_sibling_visual_bodies_but_preserves_global_scope_and_originals(self):
        report='fabric://workspace/report';selected=report+'/selected';sibling=report+'/sibling'
        self.assets += [asset(report,'Report','fabric://workspace','Report',{}),
            asset(selected,'DefinitionPart',report,'definition/pages/p/visuals/a/visual.json',{'content':'selected filter'}),
            asset(sibling,'DefinitionPart',report,'definition/pages/p/visuals/b/visual.json',{'content':'unrelated visual'}),
            asset(report+'/global','DefinitionPart',report,'definition/report.json',{'content':'global filters'})]
        self.nodes += [{'id':'selected-visual','properties':{'asset_id':selected}}]
        catalog=self.build();context=catalog.context({'nodes':[self.nodes[-1]]},{})
        definitions={a['id']:a for a in context['retained_native_definitions']}
        self.assertIn(selected,definitions);self.assertIn(report+'/global',definitions)
        self.assertNotIn(sibling,definitions)
        self.assertEqual(context['off_path_visual_definition_index'][0]['id'],sibling)
        self.assertEqual(catalog.assets[sibling]['metadata']['content'],'unrelated visual')
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
        original=deepcopy(self.assets)
        for a in self.assets:
            for key in ('content_hash','availability','provenance'):a.pop(key,None)
        value=self.build().declared_continuations(path)
        self.assertEqual(value[0]['physical_table'],self.table)
        self.assertIn('Unavailable inventory digest',value[0]['native_ownership'][0]['inventory_digest_qualification'])
        self.assets=original;witness=self.assets[-1]
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
    def test_retained_catalog_without_inventory_availability_has_routes_and_warning(self):
        for item in self.assets:item.pop('availability',None)
        catalog=self.build();self.assertTrue(catalog.routes)
        warnings=catalog.context({'nodes':self.nodes},{})['warnings']
        self.assertTrue(any('current inventory availability' in w for w in warnings))
        self.assertNotIn('availability',next(iter(catalog.assets.values())))
        for item in self.assets:item['availability']='UNAVAILABLE'
        self.assertEqual(self.build().routes,{})
    def test_catalog_wire_missing_inventory_hash_and_provenance_gets_explicit_derived_metadata_digest(self):
        import json,hashlib
        for item in self.assets:
            for key in ('content_hash','provenance','availability'):item.pop(key,None)
        original=deepcopy(self.assets);catalog=self.build();self.assertTrue(catalog.routes)
        item=catalog.assets[self.table]
        expected=hashlib.sha256(json.dumps(item['metadata'],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        self.assertEqual(item['content_hash'],expected)
        self.assertEqual(item['content_hash_basis'],'DERIVED_RETAINED_METADATA_CANONICAL_JSON')
        self.assertEqual(item['provenance']['source'],'RETAINED_ASSET_CATALOG')
        self.assertNotIn('observed_at',item['provenance'])
        self.assertEqual(self.assets,original)
    def test_all_inventory_bookkeeping_is_optional_and_unknown_bookkeeping_never_leaks(self):
        for item in self.assets:
            for key in ('content_hash','provenance','availability','parent_id'):item.pop(key,None)
            item.update(scan_id='scan',created_at='old',collector_private_field={'unused':'bookkeeping'})
        catalog=self.build();self.assertTrue(catalog.routes)
        for item in catalog.assets.values():
            self.assertFalse({'scan_id','created_at','collector_private_field'}&set(item))
        self.assertTrue(catalog.catalog_warnings)

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

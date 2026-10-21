import copy,json,unittest
from test_estate_graph_static import StaticTests,asset,part
from investigator.adapters.estate_graph_static import retained_lakehouse_endpoint_assets

W='fabric://00000000-0000-0000-0000-000000000001'
C='00000000-0000-0000-0000-000000000002'
M=W+'/00000000-0000-0000-0000-000000000003'
E='00000000-0000-0000-0000-000000000004'
NOW='2026-10-13T01:00:00Z'
class DirectLakeTests(unittest.TestCase):
    build=StaticTests.build
    def fixture(self,lakehouse=False):
        self.doc={'model':{'expressions':[{'name':'Origin','kind':'m','expression':
            'let renamed = Sql.Database("server.example.invalid", "'+(E if lakehouse else C)+'") in renamed'}],
            'tables':[{'name':'Semantic renamed','columns':[{'name':'Friendly amount','sourceColumn':'raw_amount'}],
                'partitions':[{'mode':'directLake','source':{'type':'entity','expressionSource':'Origin','schemaName':'dbo','entityName':'physical_table'}}]}]}}
        assets=[asset(W,'Workspace','Workspace'),asset(M,'SemanticModel','Model',W),
            asset(M+'/t','SemanticTable','Semantic renamed',M),asset(M+'/t/c','SemanticColumn','Friendly amount',M+'/t'),
            asset(W+'/'+C,'Lakehouse' if lakehouse else 'Warehouse','Arbitrary renamed container',W),
            asset(W+'/'+C+'/t','LakehouseTable' if lakehouse else 'WarehouseTable','physical_table' if lakehouse else 'dbo.physical_table',W+'/'+C,
                  {'location':'abfss://'+W.split('/')[-1]+'@onelake.dfs.fabric.microsoft.com/'+C+'/Tables/physical_table'}),
            asset(W+'/'+C+'/t/c','LakehouseColumn' if lakehouse else 'WarehouseColumn','raw_amount',W+'/'+C+'/t')]
        return assets
    def graph(self,assets):return self.build(assets+[part('bim',M,'model.bim',self.doc)])
    def bindings(self,g):return [e for e in g['edges'] if e['properties'].get('binding_kind')=='DIRECTLAKE_ENTITY']
    def test_literal_warehouse_and_column_bind_with_native_provenance(self):
        assets=self.fixture();g=self.graph(assets);edges=self.bindings(g)
        self.assertEqual(len(edges),2)
        self.assertTrue(all(e['confidence']=='DECLARED' for e in edges))
        self.assertEqual({e['properties'].get('source_column') for e in edges},{None,'raw_amount'})
        self.assertEqual(edges[0]['properties']['catalog_id'],C)
    def test_renamed_and_duplicate_container_labels_do_not_change_binding(self):
        assets=self.fixture();before=self.bindings(self.graph(assets));assets.append(asset(W+'/'+E,'Warehouse','Arbitrary renamed container',W))
        assets[4]['name']='Completely different';after=self.bindings(self.graph(assets))
        self.assertEqual([(e['source'],e['target']) for e in before],[(e['source'],e['target']) for e in after])
    def test_unknown_expression_duplicate_expression_and_multiple_partitions_refuse(self):
        for change in ('unknown','duplicate','partitions','dynamic','import'):
            assets=self.fixture();model=self.doc['model']
            if change=='unknown':model['tables'][0]['partitions'][0]['source']['expressionSource']='Missing'
            elif change=='duplicate':model['expressions'].append(copy.deepcopy(model['expressions'][0]))
            elif change=='partitions':model['tables'][0]['partitions']*=2
            elif change=='dynamic':model['expressions'][0]['expression']='let x = Sql.Database(server, catalog) in x'
            else:model['tables'][0]['partitions'][0]['mode']='import'
            g=self.graph(assets);self.assertEqual(self.bindings(g),[],change)
            self.assertTrue(any(n['confidence']=='UNKNOWN' and n['label'].startswith('DirectLake') for n in g['nodes']))
    def test_missing_source_column_never_uses_semantic_display_name(self):
        assets=self.fixture();self.doc['model']['tables'][0]['columns'][0]['sourceColumn']='Missing'
        g=self.graph(assets);self.assertEqual(len(self.bindings(g)),1)
        self.assertTrue(any('sourceColumn' in n['label'] for n in g['nodes']))
    def test_lakehouse_requires_retained_endpoint_binding_not_shared_labels(self):
        assets=self.fixture(True);self.assertEqual(self.bindings(self.graph(assets)),[])
        receipt=[{'request':{'workspace':W.split('/')[-1],'lakehouse':C},'response':{'id':C,'workspaceId':W.split('/')[-1],
            'type':'Lakehouse','properties':{'sqlEndpointProperties':{'id':E,'connectionString':'server.example.invalid'}}}}]
        evidence=retained_lakehouse_endpoint_assets(json.dumps(receipt).encode(),observed_at=NOW)
        self.assertEqual(evidence[0]['metadata']['observed_at'],'2026-10-13T01:00:00.000000Z')
        self.assertEqual(len(self.bindings(self.graph(assets+evidence))),2)
        evidence[0]['metadata']['response']['properties']['sqlEndpointProperties']['connectionString']='other.example.invalid'
        self.assertEqual(self.bindings(self.graph(assets+evidence)),[])
    def test_conflicting_endpoint_containers_refuse(self):
        assets=self.fixture(True)
        for container in (C,'00000000-0000-0000-0000-000000000005'):
            if container!=C:assets.append(asset(W+'/'+container,'Lakehouse','Other',W))
            assets.append(asset('proof/'+container,'LakehouseEndpointMetadata','Evidence',W+'/'+container,{'request':{'workspace':W.split('/')[-1],'lakehouse':container},'response':{
                'id':container,'workspaceId':W.split('/')[-1],'type':'Lakehouse','properties':{'sqlEndpointProperties':{'id':E,'connectionString':'server.example.invalid'}}}}))
        self.assertEqual(self.bindings(self.graph(assets)),[])
    def test_conflicting_responses_for_one_container_are_not_cherry_picked(self):
        assets=self.fixture(True)
        for number,server in enumerate(('server.example.invalid','other.example.invalid')):
            assets.append(asset('evidence/'+str(number),'LakehouseEndpointMetadata','Evidence',W+'/'+C,{
                'request':{'workspace':W.split('/')[-1],'lakehouse':C},'response':{'id':C,'workspaceId':W.split('/')[-1],
                'type':'Lakehouse','properties':{'sqlEndpointProperties':{'id':E,'connectionString':server}}}}))
        self.assertEqual(self.bindings(self.graph(assets)),[])

    def test_calculated_columns_are_not_bound_from_source_column(self):
        assets=self.fixture();self.doc['model']['tables'][0]['columns'][0]['expression']='1+1'
        self.assertEqual(len(self.bindings(self.graph(assets))),1)

if __name__=='__main__':unittest.main()

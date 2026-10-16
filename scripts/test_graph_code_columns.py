import unittest
import test_estate_graph_static as static_tests
asset,part=static_tests.asset,static_tests.part


class CodeColumnsTests(unittest.TestCase):
    def build(self,assets):return static_tests.StaticTests().build(assets)
    def notebook(self):
        code="""from pyspark.sql import functions as F
a = spark.read.format('delta').load('store/a')
b = spark.read.format('delta').load('store/b')
c = a.join(b, ['key'], 'left').withColumn('value', F.col('units') * F.col('rate'))
c.write.format('delta').mode('overwrite').save('store/c')
"""
        assets=[asset('lake','Lakehouse','Lake'),asset('book','Notebook','Book'),part('code','book','code.py',code)]
        for table,cols in [('a',['key','units']),('b',['key','rate']),('c',[])]:
            assets.append(asset(table,'LakehouseTable',table,'lake',{'location':'store/'+table}))
            assets.extend(asset(table+'/'+col,'LakehouseColumn',col,table,{'type_name':'integer'}) for col in cols)
        return assets
    def test_existing_reader_derives_exact_columns_and_retains_join_semantics(self):
        graph=self.build(self.notebook());nodes={n['id']:n for n in graph['nodes']}
        value=next(n for n in nodes.values() if n['label']=='value')
        edges=[e for e in graph['edges'] if e['source']==value['id']]
        self.assertEqual({nodes[e['target']]['label'] for e in edges if e['kind']=='COMPUTED_FROM'},{'units','rate'})
        self.assertEqual(value['properties']['schema_evidence'],'CODE_DECLARED_NOT_OBSERVED')
        step=nodes[next(e['target'] for e in edges if e['kind']=='DERIVED_IN_STEP')]
        self.assertFalse(step['properties']['execution_established'])
        self.assertEqual(step['properties']['relation']['input']['kind'],'JOIN')
    def test_same_name_different_location_does_not_bind(self):
        assets=self.notebook();next(a for a in assets if a['id']=='c')['metadata']['location']='other/c'
        graph=self.build(assets)
        self.assertFalse(any(n['label']=='value' for n in graph['nodes']))
        self.assertTrue(any('storage-location' in n['label'] for n in graph['nodes']))
    def scripts(self,texts):
        activity={'name':'Build','type':'Script','linkedService':{'properties':{'typeProperties':{'workspaceId':'ws','artifactId':'warehouse'}}},
            'typeProperties':{'scripts':[{'text':text} for text in texts]}}
        return [asset('w','Warehouse','Warehouse',metadata={'id':'warehouse','workspaceId':'ws'}),
            asset('s','WarehouseTable','app.source','w'),asset('s/c','WarehouseColumn','amount','s'),
            asset('p','DataPipeline','Build'),part('p/d','p','pipeline-content.json',{'properties':{'activities':[activity]}})]
    def test_script_create_view_then_table_resolves_code_schema_without_observation_claim(self):
        graph=self.build(self.scripts(['CREATE VIEW app.v AS SELECT amount AS revenue FROM app.source;',
            'CREATE TABLE app.destination AS SELECT revenue FROM app.v;']))
        nodes={n['id']:n for n in graph['nodes']}
        deps=[e for e in graph['edges'] if e['kind']=='COMPUTED_FROM' and nodes[e['source']]['kind']=='COLUMN']
        self.assertEqual(len(deps),2)
        self.assertTrue(all(e['confidence']=='DECLARED' for e in deps))
        self.assertTrue(all(nodes[e['source']]['properties']['schema_evidence']=='CODE_DECLARED_NOT_OBSERVED' for e in deps))
    def test_script_procedure_is_retained_with_exact_span_and_unknown(self):
        text='CREATE PROCEDURE app.p AS BEGIN DELETE FROM app.source; END;'
        graph=self.build(self.scripts([text]))
        node=next(n for n in graph['nodes'] if n['properties'].get('expression')==text)
        self.assertEqual(node['provenance']['span']['path'],'/properties/activities/0/typeProperties/scripts/0/text')
        self.assertTrue(any(e['source']==node['id'] and e['confidence']=='UNKNOWN' for e in graph['edges']))
    def test_script_unknown_warehouse_never_binds_same_name_objects(self):
        assets=self.scripts(['CREATE VIEW app.v AS SELECT amount FROM app.source;']);assets[0]['metadata']['id']='other'
        graph=self.build(assets)
        self.assertFalse(any(n['label']=='app.v' for n in graph['nodes']))
        self.assertTrue(any('Warehouse binding' in n['label'] for n in graph['nodes']))
    def test_script_cross_database_uses_retained_sql_reader_schema_not_default_guess(self):
        assets=self.scripts(['CREATE VIEW app.v AS SELECT amount FROM Bronze.dbo.source;'])
        assets.extend([asset('lake','Lakehouse','Bronze',metadata={'workspaceId':'ws'}),
            asset('t','LakehouseTable','source','lake',{'reader_schema':{'schema_name':'dbo'}}),
            asset('t/c','LakehouseColumn','amount','t')])
        graph=self.build(assets);nodes={n['id']:n for n in graph['nodes']}
        self.assertTrue(any(e['kind']=='COMPUTED_FROM' and nodes[e['target']]['properties'].get('asset_id')=='t/c' for e in graph['edges']))
        assets[-2]['metadata']['reader_schema']={}
        graph=self.build(assets)
        self.assertTrue(any('source table is unresolved' in n['label'] for n in graph['nodes']))
    def test_retained_external_asset_keeps_its_original_observation_time(self):
        graph=static_tests.StaticTests().build([asset('w','Warehouse','Warehouse')],
            source_observations={'w':'2026-10-01T00:00:00Z'})
        self.assertEqual(graph['nodes'][0]['provenance']['observed_at'],static_tests.c.timestamp('2026-10-01T00:00:00Z'))
        self.assertEqual(graph['observed_at'],static_tests.c.timestamp(static_tests.NOW))
        with self.assertRaisesRegex(ValueError,'OBSERVATION_ASSET_NOT_RETAINED'):
            static_tests.StaticTests().build([asset('w','Warehouse','Warehouse')],source_observations={'absent':static_tests.NOW})


if __name__=='__main__':unittest.main()


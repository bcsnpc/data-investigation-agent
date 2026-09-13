"""Adversarial lineage contracts: scope, ambiguity, unsupported code and traversal."""
import json,tempfile,unittest
from pathlib import Path
from lineage_notebook import StaticNotebook
from lineage_graph import Graph,build


def asset(id,kind,name,parent=None,meta=None):
    return {'id':id,'kind':kind,'name':name,'parent':parent,'meta':meta or {},'hash':'test-hash'}


class LineageTests(unittest.TestCase):
    def test_persisted_graph_retains_edges_and_gaps(self):
        from metadata_inventory import Inventory
        from lineage_graph import persist,load_graph
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'inventory.sqlite'
            store=Inventory(path)
            for name in ['a','b']:store.asset(name,'Test',name,'fixture',{})
            scan=store.scan;store.finish();store.db.close()
            graph=Graph([asset(x,'Test',x) for x in ['a','b']])
            graph.edge('a','b','data','a',{'line':3})
            graph.gap('b','Missing evidence',{})
            run=persist(path,scan,graph,{'records':[]})
            loaded=load_graph(path,run)
            self.assertEqual(loaded.edges,graph.edges)
            self.assertEqual(loaded.traverse('b')['unresolved'],graph.gaps)

    def test_page_filter_is_inherited_by_visual(self):
        model_id='aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
        reference={'Column':{'Expression':{'SourceRef':{'Entity':'Sales'}},'Property':'amount'}}
        assets=[asset('m','SemanticModel','m',meta={'id':model_id}),asset('t','SemanticTable','Sales','m'),
                asset('c','SemanticColumn','amount','t'),asset('r','Report','report'),
                asset('p','ReportPage','page','r',{'filterConfig':reference}),asset('v','ReportVisual','visual','p'),
                asset('part','DefinitionPart','definition.pbir','r',{'content':json.dumps({'datasetReference':{'byConnection':{'connectionString':'semanticmodelid='+model_id}}})})]
        graph=build(assets,{'records':[]})
        self.assertIn(('c','v','context'),graph.edges)
        self.assertFalse(graph.gaps)

    def test_sql_cte_and_join_are_not_physical_cte_tables(self):
        code='''a=spark.read.load("abfss://w@host/l/Tables/orders")
a.createOrReplaceTempView("src")
b=spark.read.load("abfss://w@host/l/Tables/refunds")
b.createOrReplaceTempView("refunds")
df=spark.sql("WITH filtered AS (SELECT * FROM src) SELECT * FROM filtered f JOIN refunds r ON f.id=r.id")
df.write.save("abfss://w@host/g/Tables/output")'''
        writes,gaps=StaticNotebook(code).analyze()
        self.assertFalse(gaps)
        self.assertEqual(set(writes[0]['sources']),{'abfss://w@host/l/Tables/orders','abfss://w@host/l/Tables/refunds'})

    def test_published_intermediate_is_preserved(self):
        code='''a=spark.read.load("abfss://w@host/l/Tables/source")
a.createOrReplaceTempView("s")
b=spark.sql("SELECT * FROM s")
b.createOrReplaceTempView("intermediate")
c=spark.sql("SELECT * FROM intermediate")
b.withColumn("_run",F.lit("r")).write.save("abfss://w@host/g/Tables/first")
c.withColumn("_run",F.lit("r")).write.save("abfss://w@host/g/Tables/second")'''
        writes,gaps=StaticNotebook(code).analyze()
        self.assertEqual(writes[1]['sources'],['abfss://w@host/g/Tables/first'])

    def test_sibling_projections_do_not_invent_materialized_dependency(self):
        code='''a=spark.read.load("abfss://w@host/l/Tables/source")
a.createOrReplaceTempView("s")
df=spark.sql("SELECT * FROM s")
df.select("a").write.save("abfss://w@host/g/Tables/first")
df.select("b").write.save("abfss://w@host/g/Tables/second")'''
        writes,_=StaticNotebook(code).analyze()
        self.assertEqual(writes[1]['sources'],['abfss://w@host/l/Tables/source'])

    def test_dynamic_writes_and_conditional_inputs_are_unresolved(self):
        code='''df=spark.read.load("abfss://w@host/l/Tables/source")
if runtime_flag:
 df=spark.read.load("abfss://w@host/l/Tables/other")
df.write.save("abfss://w@host/g/Tables/output")'''
        writes,gaps=StaticNotebook(code).analyze()
        self.assertTrue(gaps)
        self.assertTrue(any(x.startswith('unresolved-control:') for x in writes[0]['sources']))

    def test_unknown_transform_is_not_silently_accepted(self):
        writes,gaps=StaticNotebook('df=spark.read.load("source")\ndf.magic().write.save("out")').analyze()
        self.assertTrue(gaps)
        self.assertTrue(any(x.startswith('unresolved-operation:') for x in writes[0]['sources']))

    def test_notebook_code_is_never_executed(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'must-not-exist'
            StaticNotebook(f'from pathlib import Path\nPath({str(target)!r}).write_text("unsafe")').analyze()
            self.assertFalse(target.exists())

    def test_dax_strings_and_comments_do_not_create_dependencies(self):
        assets=[asset('m','SemanticModel','m'),asset('t','SemanticTable','Sales','m'),
                asset('c','SemanticColumn','amount','t'),asset('a','Measure','Total','t',{'expression':'SUM(Sales[amount]) + IF(TRUE(), 0, "[fake]") // [missing]'} )]
        graph=build(assets,{'records':[]})
        self.assertIn(('c','a','data'),graph.edges)
        self.assertFalse(graph.gaps)

    def test_ambiguous_measure_reference_is_not_guessed(self):
        assets=[asset('m','SemanticModel','m'),asset('t','SemanticTable','Sales','m'),asset('u','SemanticTable','Other','m'),
                asset('a','Measure','Total','t'),asset('b','Measure','Total','u'),asset('x','Measure','Result','t',{'expression':'[Total]'})]
        graph=build(assets,{'records':[]})
        self.assertTrue(any(x['asset']=='x' for x in graph.gaps))
        self.assertNotIn(('a','x','data'),graph.edges)

    def test_traversal_is_cycle_safe_and_separates_filter_edges(self):
        graph=Graph([asset(x,'Test',x) for x in 'abcd'])
        for a,b,k in [('a','b','data'),('b','a','data'),('b','c','binding'),('d','c','filter')]:graph.edge(a,b,k,'a',{})
        self.assertEqual({a['id'] for a in graph.traverse('c')['assets']},{'a','b','c'})
        self.assertIn('d',{a['id'] for a in graph.traverse('c',kinds={'data','binding','filter'})['assets']})
        self.assertEqual({a['id'] for a in graph.traverse('a','downstream')['assets']},{'a','b','c'})

    def test_loop_values_are_discovered_not_named_by_rules(self):
        code='''base="abfss://w@host/l"
for name in ["unseen_one","unseen_two"]:
 df=spark.read.load(f"{base}/Tables/{name}")
 df.select("id").write.save(f"abfss://w@host/g/Tables/{name}_clean")'''
        writes,gaps=StaticNotebook(code).analyze()
        self.assertFalse(gaps)
        self.assertEqual([w['destination'].split('/')[-1] for w in writes],['unseen_one_clean','unseen_two_clean'])


if __name__=='__main__':unittest.main()

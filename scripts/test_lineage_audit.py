import unittest
from lineage_graph import Graph,build
from audit_lineage import audit
from lineage_notebook import StaticNotebook
from pathlib import Path


class AuditTests(unittest.TestCase):
    def fixture(self):
        assets=[{'id':name,'kind':kind,'name':name,'parent':None,'hash':'hash','meta':{}} for name,kind in
                [('source','SqlObject'),('measure','Measure'),('visual','ReportVisual'),('text','ReportVisual')]]
        graph=Graph(assets)
        graph.edge('measure','visual','binding','measure',{})
        return graph

    def test_missing_source_path_is_not_success(self):
        result=audit(self.fixture())
        self.assertEqual(result['status'],'PARTIAL')
        self.assertEqual(result['source_paths_found'],0)

    def test_paths_and_unbound_visuals_are_separate(self):
        graph=self.fixture();graph.edge('source','measure','data','measure',{})
        result=audit(graph)
        self.assertEqual(result['source_paths_found'],1)
        self.assertEqual(result['visuals_without_discovered_binding'],['text'])

    def test_gap_prevents_resolved_status(self):
        graph=self.fixture();graph.edge('source','measure','data','measure',{})
        graph.gap('measure','Unsupported expression',{})
        result=audit(graph)
        self.assertEqual(result['status'],'PARTIAL')
        self.assertEqual(result['source_paths_found'],0)

    def test_empty_graph_is_not_resolved(self):
        self.assertEqual(audit(Graph([]))['status'],'PARTIAL')

    def test_reviewed_pinned_reader_resolves_only_its_bound_paths(self):
        helper=(Path(__file__).resolve().parents[1]/'infra/fabric/read_pinned_bronze.py').read_text()
        binding={'status':'BOUND_INPUTS','tables':[{'source_table':str(i),'destination':'snapshot/'+str(i)} for i in range(10)]}
        code=helper+'\nB='+repr(binding)+"\nframes=read_pinned_bronze(spark,DeltaTable,B)\nframes['1'].write.save('silver')"
        writes,gaps=StaticNotebook(code).analyze()
        self.assertEqual(writes[0]['sources'],['snapshot/1'])
        self.assertFalse(gaps)
        changed=code.replace("return frames","return {}")
        self.assertTrue(StaticNotebook(changed).analyze()[1])

    def test_shadowed_pinned_reader_not_trusted(self):
        helper=(Path(__file__).resolve().parents[1]/'infra/fabric/read_pinned_bronze.py').read_text()
        code=helper+"\nread_pinned_bronze=other\nframes=read_pinned_bronze(spark,DeltaTable,{})"
        self.assertTrue(StaticNotebook(code).analyze()[1])

    def test_snapshot_mapping_resolves_exact_parent_and_destination(self):
        assets=[{'id':'sql','parent':'sql://server/db','kind':'SqlObject','name':'app.orders','meta':{},'hash':'sqlhash'},
                {'id':'bronze','parent':'fabric://workspace/lakehouse','kind':'LakehouseTable','name':'snapshot.orders','meta':{},'hash':'tablehash'}]
        mapping={'sql_parent':'sql://server/db','sql_table':'app.orders',
                 'destination':'abfss://workspace@onelake.dfs.fabric.microsoft.com/lakehouse/Tables/snapshot/orders',
                 'bronze_proof_sha256':'proof','delta_version':0}
        graph=build(assets,{'records':[],'snapshot_mappings':[mapping]})
        self.assertIn(('sql','bronze','data'),graph.edges)
        self.assertEqual(graph.edges[('sql','bronze','data')][0]['detail']['verified_snapshot_mapping'],mapping)
        mapping['sql_parent']='sql://another/db'
        graph=build(assets,{'records':[],'snapshot_mappings':[mapping]})
        self.assertFalse(graph.edges)
        self.assertTrue(graph.gaps)


if __name__=='__main__':unittest.main()

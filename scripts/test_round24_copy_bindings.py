import unittest,copy
from investigator.adapters.graph_copy_bindings import resolve,activities
class CopyTests(unittest.TestCase):
 def test_invoked_copy_job_uses_workspace_and_item_uuid(self):
  from test_estate_graph_static import StaticTests,asset,part
  pipeline='fabric://workspace/pipeline';job='fabric://workspace/job'
  doc={'properties':{'activities':[{'name':'Invoke','type':'InvokeCopyJob','typeProperties':{'workspaceId':'workspace','copyJobId':'job'}}]}}
  graph=StaticTests().build([asset(pipeline,'DataPipeline','Pipeline'),asset(job,'CopyJob','Job'),part('definition',pipeline,'pipeline-content.json',doc)])
  ids={n['properties'].get('asset_id'):n['id']for n in graph['nodes']}
  self.assertTrue(any(e['source']==ids[pipeline]and e['target']==ids[job]and e['kind']=='COMPUTED_FROM'for e in graph['edges']))
 def test_nested_native_columns_keep_parent_json_pointer(self):
  from test_estate_graph_static import StaticTests,asset
  graph=StaticTests().build([asset('table','SqlObject','app.items',metadata={'columns':[{'name':'amount','data_type':'int'}]})])
  column=next(n for n in graph['nodes']if n['kind']=='COLUMN')
  self.assertEqual(column['provenance']['source_id'],'table');self.assertEqual(column['provenance']['span']['path'],'/columns/0')
 def test_https_onelake_schema_path_binds_without_display_name_guessing(self):
  from test_directlake_bridge import DirectLakeTests,W,C,M,E,NOW
  from test_estate_graph_static import asset
  from investigator.adapters.estate_graph_static import retained_native_relation_assets
  h=DirectLakeTests();assets=h.fixture(True);context=h.native_context(assets)
  physical=next(a for a in assets if a['kind']=='LakehouseTable');physical['metadata']={'storage_location':'https://onelake.dfs.fabric.microsoft.com/'+W.split('/')[-1]+'/'+C+'/Tables/dbo/physical_table'}
  evidence=retained_native_relation_assets(context,observed_at=NOW,model_ids=[M])
  self.assertEqual(len(h.bindings(h.graph(assets+evidence))),2)
 def test_schema_only_ddl_is_not_a_row_producing_dependency(self):
  from test_graph_code_columns import CodeColumnsTests
  helper=CodeColumnsTests();graph=helper.build(helper.scripts(['CREATE TABLE app.result (amount int)']))
  nodes={n['id']:n for n in graph['nodes']}
  steps={n['id']for n in nodes.values()if n['properties'].get('definition_only')}
  self.assertTrue(steps);self.assertFalse(any(e['kind']=='DERIVED_IN_STEP'and e['target']in steps for e in graph['edges']))
 def test_sql_script_producer_carries_its_exact_source_table(self):
  from test_graph_code_columns import CodeColumnsTests
  helper=CodeColumnsTests();graph=helper.build(helper.scripts(['CREATE VIEW app.result AS SELECT amount FROM app.source']))
  nodes={n['id']:n for n in graph['nodes']}
  self.assertTrue(any(e['kind']=='COMPUTED_FROM'and nodes[e['source']]['label']=='Declared SQL script'and nodes[e['target']]['properties'].get('asset_id')=='s'for e in graph['edges']))
 def test_notebook_write_links_table_to_its_real_producer(self):
  from test_graph_code_columns import CodeColumnsTests
  helper=CodeColumnsTests();graph=helper.build(helper.notebook())
  output=next(n for n in graph['nodes']if n.get('properties',{}).get('asset_id')=='c')
  self.assertTrue(any(e['source']==output['id']and e['kind']=='DERIVED_IN_STEP'for e in graph['edges']))
 def test_connection_uuid_and_destination_uuid_are_both_required(self):
  assets={a['id']:a for a in [
   {'id':'connection','kind':'SourceConnection','metadata':{'id':'uuid','connectionDetails':{'type':'SQL','path':'server;db'}}},
   {'id':'source','kind':'SqlObject','parent_id':'sql://server/db','metadata':{'schema_name':'app','name':'items'}},
   {'id':'target','kind':'LakehouseTable','parent_id':'fabric://workspace/lakehouse','name':'items','metadata':{}}]}
  props={'source':{'datasetSettings':{'externalReferences':{'connection':'uuid'},'typeProperties':{'schema':'app','table':'items'}}},'sink':{'datasetSettings':{'typeProperties':{'table':'items'},'linkedService':{'properties':{'typeProperties':{'workspaceId':'workspace','artifactId':'lakehouse'}}}}}}
  result=resolve(assets,props);self.assertEqual((result['source_asset'],result['destination_asset']),('source','target'))
  wrong=copy.deepcopy(props);wrong['source']['datasetSettings']['externalReferences']['connection']='same-display-name';self.assertIsNone(resolve(assets,wrong))
  wrong=copy.deepcopy(props);wrong['sink']['datasetSettings']['linkedService']['properties']['typeProperties']['artifactId']='other';self.assertIsNone(resolve(assets,wrong))
 def test_copyjob_activity_objects_are_merged_with_connection_declaration(self):
  doc={'properties':{'source':{'connectionSettings':{'externalReferences':{'connection':'uuid'}}},'destination':{'connectionSettings':{'typeProperties':{'artifactId':'id'}}}},'activities':[{'id':'activity','properties':{'source':{'datasetSettings':{'schema':'app','table':'items'}},'destination':{'datasetSettings':{'table':'items'}}}}]}
  rows=activities(doc,'CopyJob');self.assertEqual(rows[0]['typeProperties']['source']['datasetSettings']['table'],'items');self.assertEqual(rows[0]['typeProperties']['source']['connectionSettings']['externalReferences']['connection'],'uuid')
if __name__=='__main__':unittest.main()

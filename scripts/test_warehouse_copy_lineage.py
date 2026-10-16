"""Native Warehouse and embedded Copy declarations stay scoped and unverified."""
import copy,json,unittest
from types import SimpleNamespace
from unittest.mock import patch
from lineage_graph import build
from investigator.adapters.code_verification import resolve_objects
from investigator.adapters.microsoft_process import MicrosoftProcessAdapter

WS='00000000-0000-0000-0000-000000000001'
WID='00000000-0000-0000-0000-000000000002'
P='fabric://'+WS

def asset(id,kind,name,parent=None,meta=None):
 return {'id':id,'kind':kind,'name':name,'parent':parent,'meta':meta or {},'hash':'sealed'}
def adapted(a):
 return {'id':a['id'],'kind':a['kind'],'name':a['name'],'parent_id':a['parent'],'metadata':a['meta'],'content_hash':a['hash'],'availability':'CURRENT'}
class NativeTests(unittest.TestCase):
 def setUp(self):
  self.w=P+'/'+WID;self.model=P+'/model';self.table=self.w+'/table/gold.events'
  self.partition={'mode':'directLake','source':{'type':'entity','schemaName':'gold','entityName':'events','expressionSource':'Source'}}
  self.document={'model':{'expressions':[{'name':'Source','expression':'let db = Sql.Database("host", "'+WID+'") in db'}],
    'tables':[{'name':'Activity','partitions':[self.partition]}]}}
  self.assets=[asset(self.w,'Warehouse','serving',P,{'id':WID,'properties':{'connectionString':'host'}}),
    asset(self.table,'WarehouseTable','gold.events',self.w,{'schema_name':'gold','name':'events','type_desc':'USER_TABLE','columns':[{'name':'units','data_type':'bigint'}]}),
    asset(self.model,'SemanticModel','model',P),asset(self.model+'/table','SemanticTable','Activity',self.model),
    asset(self.model+'/def','DefinitionPart','model.bim',self.model,{'content':json.dumps(self.document)})]
  self.context={'assets':[adapted(a) for a in self.assets],'graph':{'edges':[]}}
  self.config={'fabric':{'workspace_id':WS,'sql_reader':{'server':'host','account':'reader'}}}
 def test_warehouse_partition_requires_item_server_and_workspace_match(self):
  g=build(self.assets,{'records':[]});self.assertIn((self.table,self.model+'/table','data'),g.edges)
  for field,value in [('connectionString','other')]:
   changed=copy.deepcopy(self.assets);changed[0]['meta']['properties'][field]=value
   self.assertNotIn((self.table,self.model+'/table','data'),build(changed,{'records':[]}).edges)
  changed=copy.deepcopy(self.assets);changed[0]['parent']='fabric://other'
  self.assertNotIn((self.table,self.model+'/table','data'),build(changed,{'records':[]}).edges)
 def test_runtime_warehouse_declared_source_and_filtered_refusal(self):
  model={'context':{'model_assets':[{'id':self.model,'kind':'SemanticModel'}]}}
  adapter=MicrosoftProcessAdapter(object(),self.config,model,None,None)
  metadata={'assets':[{'id':self.model+'/table','kind':'SemanticTable','metadata':{'partitions':[self.partition]}}]}
  with patch('investigator.adapters.microsoft_process.context_search.latest',return_value=self.context):
   binding=adapter._partition_binding(metadata)
   self.assertEqual(binding['status'],'RESOLVED');self.assertEqual(binding['asset']['id'],self.table)
   self.assertEqual(binding['relation_cross_check']['status'],'WAREHOUSE_DECLARATION_MATCHED')
   layer={'id':self.table,'binding':binding,'semantic_column':'units','declared_columns':[{'name':'units','sourceColumn':'units','dataType':'int64'}]}
   quantity,reason=adapter._lower_quantity(layer,{'filters':[],'dimension_ids':[]})
   self.assertIsNone(reason);self.assertEqual(quantity['database'],'serving');self.assertIn('[gold].[events]',quantity['query'])
   self.assertIn('filtered scope',adapter._lower_quantity(layer,{'filters':[{}]})[1])
 def test_warehouse_verifier_uses_retained_exact_identity_and_types(self):
  process=SimpleNamespace(config=self.config,read_endpoint=lambda _:self.fail('No inferred Lakehouse lookup'))
  objects,gaps=resolve_objects(process,self.context,{self.table:{'units':'long'}})
  self.assertFalse(gaps);self.assertEqual(objects[self.table]['database'],'serving')
  self.assertEqual(objects[self.table]['catalog']['metadata']['columns'][0]['data_type'],'bigint')
  objects,gaps=resolve_objects(process,self.context,{self.table:{'units':'double'}})
  self.assertFalse(objects);self.assertIn('schema differs',gaps[0]['reason'])
  changed=copy.deepcopy(self.context);changed['assets'][0]['metadata']['properties']['connectionString']='other'
  self.assertFalse(resolve_objects(process,changed,{self.table:{'units':'long'}})[0])
 def test_explicit_tsql_language_reaches_tsql_parser_and_keeps_append_refusal(self):
  from investigator.transformation_sql import extract_statement
  from investigator.code_static import Unsupported
  plan=extract_statement('CREATE TABLE [gold].[target] AS SELECT [units] FROM [silver].[source]',{'silver.source':{'units':'long'}},dialect='tsql')
  self.assertIn('gold.target',plan)
  from investigator.code_sources import normalize
  from investigator.transformation_reader import propose
  unit=normalize('definition.sql',b'CREATE TABLE [gold].[target] AS SELECT [units] FROM [silver].[source]')
  unit['cells'][0]['language']='tsql'
  result=propose(unit,schemas={'silver.source':{'units':'long'}},boundary={'from_layer':'source','to_layer':'target'},item='pipeline',target_table='gold.target',layers=[{'id':'source'},{'id':'target'}])
  self.assertEqual(len(result['proposals']),1);self.assertEqual(result['proposals'][0]['extractor'],'STATIC')
  with self.assertRaises(Unsupported):extract_statement('INSERT INTO [gold].[target] SELECT [units] FROM [silver].[source]',{'silver.source':{'units':'long'}},dialect='tsql')
  with self.assertRaises(Unsupported):extract_statement('CREATE TABLE x AS SELECT units FROM s',{},dialect='guessed')
 def copy_assets(self):
  src='sql://server/db';dest=P+'/lake';pipe=P+'/pipe'
  activity={'name':'copy','type':'Copy','typeProperties':{'source':{'type':'AzureSqlSource','sqlReaderQuery':'SELECT units FROM app.events','datasetSettings':{'typeProperties':{'schema':'app','table':'events'},'externalReferences':{'connection':'conn'}}},'sink':{'type':'LakehouseTableSink','datasetSettings':{'typeProperties':{'table':'events'},'linkedService':{'properties':{'typeProperties':{'workspaceId':WS,'artifactId':'lake'}}}}}}}
  cols=[{'name':'units','data_type':'bigint','computed_definition':None}]
  assets=[asset(src+'/obj','SqlObject','app.events',src,{'columns':cols}),asset(dest+'/table/events','LakehouseTable','events',dest,{'columns':cols}),asset(pipe,'DataPipeline','load',P),asset(pipe+'/part','DefinitionPart','pipeline-content.json',pipe,{'content':json.dumps({'properties':{'activities':[activity]}})})]
  records={'records':[{'status':'AVAILABLE','data':{'id':'conn','connectionDetails':{'path':'server;db'}}}]}
  return assets,records,activity
 def test_embedded_copy_graph_retains_inferred_not_verified_mapping(self):
  assets,records,_=self.copy_assets();g=build(assets,records)
  proof=g.edges[(assets[0]['id'],assets[1]['id'],'data')][0]['detail']['mapping']
  self.assertEqual(proof['verification'],'UNVERIFIED');self.assertEqual(proof['provenance'],'INFERRED_FROM_CODE')
 def test_embedded_copy_missing_connection_or_ambiguous_destination_is_gap(self):
  assets,records,_=self.copy_assets()
  self.assertTrue(any(x['reason']=='Embedded Copy mapping unavailable' for x in build(assets,{'records':[]}).gaps))
  duplicate=copy.deepcopy(assets[1]);duplicate['id']+='-other';assets.append(duplicate)
  g=build(assets,records);self.assertFalse(g.edges);self.assertIn('ambiguous',g.gaps[0]['detail']['reason'])
if __name__=='__main__':unittest.main()

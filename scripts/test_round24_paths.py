import unittest
from copy import deepcopy
from unittest.mock import Mock
from investigator.guided_investigator_installation import Factory
from investigator.adapters.ai_native_catalog import NativeCatalog
from investigator.investigation_read_tools import ReadTools
from test_round23_intake_queries import graph,request
class PathTests(unittest.TestCase):
 def test_one_measure_does_not_open_its_storage_siblings_or_transitive_relationship_tables(self):
  import test_round23_native_catalog as f
  h=f.NativeCatalogTests();h.setUp();model='fabric://workspace/model';home=model+'/table/Home';input=model+'/table/Input';other=model+'/table/Other'
  h.assets += [f.asset(model,'SemanticModel','fabric://workspace','Model',{}),f.asset(home,'SemanticTable',model,'Home',{}),f.asset(input,'SemanticTable',model,'Input',{}),f.asset(other,'SemanticTable',model,'Other',{}),f.asset(home+'/m','Measure',home,'Selected',{'expression':'SUM(Input[units])'}),f.asset(home+'/sibling','Measure',home,'Unrelated',{'expression':'SUM(Other[amount])'}),f.asset(home+'/c','SemanticColumn',home,'Unused',{}),f.asset(input+'/c','SemanticColumn',input,'units',{}),f.asset(other+'/c','SemanticColumn',other,'amount',{}),f.asset(model+'/r','SemanticRelationship',model,'Relationship',{'fromTable':'Input','toTable':'Other'})]
  h.nodes += [{'id':name,'kind':kind,'properties':{'asset_id':identity}}for name,kind,identity in [('model','MODEL',model),('home','TABLE',home),('input','TABLE',input),('other','TABLE',other),('measure','MEASURE',home+'/m'),('sibling','MEASURE',home+'/sibling'),('column','COLUMN',input+'/c')]]
  tail=model+'/table/Tail';h.assets.extend([f.asset(tail,'SemanticTable',model,'Tail',{}),f.asset(tail+'/c','SemanticColumn',tail,'unused',{}),f.asset(model+'/r2','SemanticRelationship',model,'Further relationship',{'fromTable':'Other','toTable':'Tail'})]);h.nodes.append({'id':'tail','kind':'TABLE','properties':{'asset_id':tail}})
  c=h.build();identity=next(i for i,r in c.routes.items()if r['kind']=='DAX');projected=c.prepare(identity,{'measure','column'})
  ids={a['id']for a in projected['objects']};self.assertEqual(ids,{home,input,other,home+'/m',input+'/c',other+'/c'});self.assertNotIn(tail,ids)
  opened=c.prepare(identity,{'other'});self.assertIn(other+'/c',{a['id']for a in opened['objects']})
 def test_producing_native_expression_keeps_its_literal_pipeline_owner_for_run_reads(self):
  c=NativeCatalog.__new__(NativeCatalog);c.assets={'part':{'kind':'DefinitionPart','parent_id':'pipeline'},'pipeline':{'kind':'DataPipeline','parent_id':'workspace'}}
  c.graph_nodes={'job':{'id':'job','kind':'PIPELINE','properties':{'asset_id':'pipeline'}},'other':{'id':'other','kind':'PIPELINE','properties':{'asset_id':'unrelated'}}}
  node={'id':'step','kind':'QUERY_STEP','properties':{'expression':'INSERT ... SELECT ...'},'provenance':{'source_id':'part'}}
  self.assertEqual([n['id']for n in c.associated_nodes({'nodes':[node]})],['job'])
  node['provenance']['source_id']='missing';self.assertEqual(c.associated_nodes({'nodes':[node]}),[])
 def factory(self):
  f=Factory.__new__(Factory);f.associated_nodes=None;f.definition_for=None;f.graph=Mock();f.graph.allowed={'model','physical','job','source'};f.graph.intake_catalog.return_value={'nodes':[{'id':'job','kind':'PIPELINE'}]};return f
 def test_measure_home_is_not_a_physical_data_dependency(self):
  c=NativeCatalog.__new__(NativeCatalog);c.assets={'measure':{'id':'measure','kind':'Measure','parent_id':'home'},'home':{'id':'home','kind':'SemanticTable','parent_id':'model'},'model':{'id':'model','kind':'SemanticModel','parent_id':'workspace'}}
  c.graph_nodes={k:{'id':k,'kind':kind,'properties':{'asset_id':asset}}for k,kind,asset in [('m','MEASURE','measure'),('h','TABLE','home'),('model','MODEL','model')]}
  extra=c.associated_nodes({'nodes':[c.graph_nodes['m']]})
  self.assertEqual([n['id']for n in extra],['model'])
 def test_declared_bridges_resolve_until_closure_on_every_expansion(self):
  f=self.factory()
  def path(root):return {'nodes':[{'id':root,'kind':'TABLE'}],'edges':[]}
  f.graph.path_to_source.side_effect=path;f.graph.calculation_path.side_effect=path
  def bridges(p):
   ids={n['id']for n in p['nodes']};result=[]
   if 'model'in ids:result.append({'confidence':'DECLARED','graph_nodes':['physical','job']})
   if 'physical'in ids:result.append({'confidence':'DECLARED','graph_nodes':['source']})
   return result
  f.declared_continuations=bridges
  r=f.resolve_path(path('model'));self.assertEqual({n['id']for n in r['nodes']},{'model','physical','job','source'});self.assertEqual(len(r['declared_route_bridges']),2);self.assertIn(unittest.mock.call('job'),f.graph.calculation_path.call_args_list)
 def test_unique_named_measure_never_expands_sibling_visual_paths(self):
  f=self.factory();catalog=graph();f.graph.intake_catalog.return_value=catalog;f.routes={};f.graph.path_to_source.return_value={'nodes':[{'id':'measure','kind':'MEASURE'}],'edges':[]}
  item=request();item.pop('visual');item['description']='What is Measure calculated from?';r=f.target_path(item)
  f.graph.path_to_source.assert_called_once_with('measure');self.assertIn('no visual selected',r['target_selection'])
 def test_retained_measure_dax_requires_no_info_query_or_native_api(self):
  c=NativeCatalog.__new__(NativeCatalog);c.graph_nodes={'node':{'properties':{'asset_id':'measure'},'provenance':{'source':'STATIC_DEFINITION'}}};c.assets={'measure':{'id':'measure','name':'Quantity','kind':'Measure','metadata':{'expression':'SUM(Items[quantity])'},'content_hash':'a'*64,'provenance':'DISCOVERED'}}
  r=c.definition('node');self.assertEqual(r['content'],'SUM(Items[quantity])');self.assertFalse(r['current_native_fetch_performed']);self.assertEqual(r['basis'],'RETAINED_NATIVE_DEFINITION')
 def test_code_lineage_uses_calculation_port_and_search_never_activates_candidate(self):
  g=Mock();g.calculation_path.return_value={'nodes':[],'edges':[]};g.explore.return_value={'nodes':[{'id':'column','kind':'COLUMN'}],'edges':[]}
  expand=Mock(return_value={});port=ReadTools(graph=g,path={'nodes':[{'id':'job','kind':'PIPELINE'}]},queries=Mock(),intake={'report':'r'},job_runs=Mock(),refresh_history=Mock(),expand=expand)
  port.lineage({'node':'job'});g.calculation_path.assert_called_once_with('job');expand.reset_mock();port.lineage({'operation':'SEARCH','words':'quantity'});expand.assert_not_called();self.assertIn('column',port.visible)
if __name__=='__main__':unittest.main()

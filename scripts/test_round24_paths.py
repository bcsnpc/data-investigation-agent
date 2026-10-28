import unittest
from copy import deepcopy
from unittest.mock import Mock
from investigator.guided_investigator_installation import Factory
from investigator.adapters.ai_native_catalog import NativeCatalog
from investigator.investigation_read_tools import ReadTools
from test_round23_intake_queries import graph,request
class PathTests(unittest.TestCase):
 def factory(self):
  f=Factory.__new__(Factory);f.associated_nodes=None;f.definition_for=None;f.graph=Mock();f.graph.allowed={'model','physical','job','source'};f.graph.intake_catalog.return_value={'nodes':[{'id':'job','kind':'PIPELINE'}]};return f
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

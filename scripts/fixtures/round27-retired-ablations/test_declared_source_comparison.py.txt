"""A declared reachable comparator must actually exist in the read toolbox."""
from copy import deepcopy
from unittest.mock import Mock
import unittest
from investigator.guided_investigator_installation import Factory
from investigator.regression_features import configured

class DeclaredSourceComparisonTests(unittest.TestCase):
 def fixture(self):
  f=Factory.__new__(Factory);f.graph=Mock();f.graph.allowed={'target','source'}
  source={'id':'source','kind':'TABLE','label':'Application records','properties':{'asset_id':'native-source'}}
  f.graph.intake_catalog.return_value={'nodes':[source],'edges':[]}
  route={'path_nodes':['source'],'asset_ids':['native-source'],'objects':[],
         'dialect':'T-SQL','label':'Application'}
  f.routes={'sql':deepcopy(route)}
  def prepare(identity,nodes):
   self.assertEqual(identity,'sql');self.assertEqual(nodes,{'target','source'})
   return {**route,'objects':[{'id':'native-source','metadata':{'name':'Records'}}]}
  f.prepare=Mock(side_effect=prepare)
  path={'nodes':[{'id':'target','kind':'TABLE','label':'Landing'}],'edges':[]}
  context={'system_of_record':{'declared':True,'reachable':True,'layer':'sql','asset_id':'native-source'}}
  return f,path,context,{},{}
 def test_exact_existing_binding_is_available_without_inventing_lineage(self):
  f,path,c,available,layers=self.fixture();before=deepcopy(path)
  node=f.prepare_declared_source_comparison(path,c,available,layers)
  self.assertEqual(path,before);self.assertEqual(node['id'],'source')
  self.assertEqual(layers['sql']['objects'][0]['id'],'native-source')
  self.assertTrue(c['system_of_record']['admitted_in_case'])
  self.assertFalse(c['declared_source_comparisons'][0]['lineage_established'])
  self.assertFalse(c['declared_source_comparisons'][0]['quantity_read_performed_by_activation'])
 def test_same_name_different_asset_or_ambiguous_node_never_activates(self):
  for mode in ['different-asset','duplicate-node','outside-scope','unregistered-asset','missing-properties']:
   f,path,c,a,l=self.fixture();nodes=f.graph.intake_catalog.return_value['nodes']
   if mode=='different-asset':nodes[0]['properties']['asset_id']='other-native-source'
   if mode=='duplicate-node':nodes.append({**deepcopy(nodes[0]),'id':'other-source'})
   if mode=='outside-scope':f.graph.allowed={'target'}
   if mode=='unregistered-asset':f.routes['sql']['asset_ids']=['other-native-source']
   if mode=='missing-properties':nodes[0]['properties']=None;c['warnings']=None
   with self.subTest(mode=mode):
    self.assertIsNone(f.prepare_declared_source_comparison(path,c,a,l));f.prepare.assert_not_called()
    self.assertFalse(c['system_of_record']['reachable']);self.assertEqual(l,{})
 def test_explicitly_unreachable_or_undeclared_source_is_preserved(self):
  for key in ['reachable','declared']:
   f,path,c,a,l=self.fixture();c['system_of_record'][key]=False
   self.assertIsNone(f.prepare_declared_source_comparison(path,c,a,l));f.prepare.assert_not_called()
 def test_existing_active_object_is_not_prepared_again(self):
  f,path,c,a,l=self.fixture();l['sql']={'objects':[{'id':'native-source'}]}
  self.assertIsNone(f.prepare_declared_source_comparison(path,c,a,l));f.prepare.assert_not_called()
  self.assertTrue(c['system_of_record']['admitted_in_case'])
 def test_flag_reproduces_old_advertised_but_inactive_case(self):
  f,path,c,a,l=self.fixture()
  with configured({'r27_declared_source_comparison':False}):
   self.assertIsNone(f.prepare_declared_source_comparison(path,c,a,l))
  self.assertTrue(c['system_of_record']['reachable']);self.assertEqual(l,{})
 def test_real_factory_exposes_source_in_tool_enums_without_changing_target_path(self):
  from tempfile import TemporaryDirectory
  from pathlib import Path
  from types import SimpleNamespace
  from investigator.shared_state import SharedState
  from test_round23_intake_queries import graph,request,sql_objects
  with TemporaryDirectory()as folder:
   state=SharedState.offline(Path(folder)/'state.sqlite');state.migrate()
   catalog=graph();landing={'id':'landing','kind':'TABLE','label':'Landing','properties':{'asset_id':'native-landing'}}
   source={'id':'source-node','kind':'TABLE','label':'Application','properties':{'asset_id':'native-source'}}
   catalog['nodes'].extend([landing,source]);g=Mock();g.allowed={n['id']for n in catalog['nodes']}
   g.intake_catalog.return_value=catalog
   card=next(n for n in catalog['nodes']if n['id']=='card');path={'nodes':[card,landing],'edges':[]}
   original=deepcopy(path);routes={}
   for identity,node,asset in [('landing','landing','native-landing'),('source','source-node','native-source')]:
    objects=sql_objects();objects[0]['id']=asset
    routes[identity]={'kind':'SOURCE_SQL','path_nodes':[node],'asset_ids':[asset],
                      'objects':objects,'dialect':'T-SQL','label':identity}
   native=Mock(spec=[]);prepare=Mock(side_effect=lambda identity,nodes:deepcopy(routes[identity]))
   factory=Factory(state=state,graph=g,routes=routes,native=native,
       context_for=lambda *a:{'system_of_record':{'declared':True,'reachable':True,'layer':'source','asset_id':'native-source'}},
       triage_for=lambda *a:SimpleNamespace(run=lambda:{'facts':[]}),model_for=lambda _:Mock(),
       reserve=Mock(),persist=Mock(),job_runs=Mock(),refresh_history=Mock(),prepare_route=prepare,checkpoint_for=lambda _:Mock())
   factory.target_path=Mock(return_value=deepcopy(path));factory.resolve_path=lambda value:value
   engine=factory({'id':'comparison-case','estate':'estate','intake':request()})
   self.assertIn('source',engine.queries.layers)
   sql=next(t for t in engine.tools if t['name']=='run_sql')
   self.assertIn('source',sql['input_schema']['properties']['layer']['enum'])
   definition=next(t for t in engine.tools if t['name']=='get_definition')
   self.assertIn('source-node',definition['input_schema']['properties']['node']['enum'])
   self.assertEqual(engine.context['path'],original)
   self.assertEqual(engine.context['explicit_target']['visual'],'card')
   native.assert_not_called()

if __name__=='__main__':unittest.main()

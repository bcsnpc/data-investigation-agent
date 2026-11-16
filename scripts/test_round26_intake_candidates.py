from copy import deepcopy
from unittest.mock import Mock
import unittest
from investigator.guided_intake import Catalog
from investigator.guided_intake_candidates import resolve,check_origin

class CandidateTests(unittest.TestCase):
 def setUp(self):
  self.text='Handled Quantity shows 7.'
  self.catalog=Catalog({'nodes':[{'id':m,'kind':'MEASURE','label':'Handled Quantity'}for m in ('m1','m2')],'edges':[]})
  self.mapped={'status':'NEEDS_INPUT','prefilled':{'version':'IntakeRequest/1','issue_type':'DATA_LOOKS_OLD','description':self.text,'details':{'measure':'Handled Quantity'},'reported_figure':{'state':'NUMBER','value':'7','precision':'EXACT'},'compared_with':{'kind':'NOTHING'}},'resolution_candidates':[{'via':m,'basis':'CATALOG_CONTAINMENT_OF_NAMED_MEASURE'}for m in ('m1','m2')],'source':{'kind':'MAPPED_TEXT','text':self.text,'provenance':{'reported_figure':[4,4]},'figure_mentions':[{'role':'PRIMARY','reference':[4,4]}]},'question':{'text':'Which report?','fields':[]}}
 def probe(self,values):
  return Mock(side_effect=lambda m,_:{'status':'SUCCEEDED','query_id':'query:'+m,'value':values[m]})
 def test_unique_exact_native_match_targets_only_measure_with_original_span_validation(self):
  probe=self.probe({'m1':7,'m2':8});result=resolve(self.text,self.mapped,self.catalog,probe)
  self.assertEqual(result['status'],'READY');self.assertEqual(result['intake']['measure'],'m1');self.assertNotIn('visual',result['intake']);self.assertNotIn('report',result['intake']);self.assertEqual(probe.call_count,2)
  self.assertEqual(check_origin(result['source'],result['intake'],self.catalog,result)['status'],'READY')
  with self.assertRaisesRegex(ValueError,'DIRECT_TARGET_UNRESOLVED'):check_origin(result['source'],result['intake'],self.catalog)
  forged=deepcopy(result['intake']);forged['reported_figure']['value']='9'
  with self.assertRaises(ValueError):check_origin(result['source'],forged,self.catalog,result)
 def test_equal_values_or_a_failed_candidate_never_authorize_arbitrary_selection(self):
  for probe in (self.probe({'m1':7,'m2':7}),Mock(side_effect=[{'status':'SUCCEEDED','query_id':'q','value':7},{'status':'UNAVAILABLE'}])):
   result=resolve(self.text,self.mapped,self.catalog,probe);self.assertEqual(result['status'],'NEEDS_INPUT');self.assertEqual(len(result['candidate_checks']),2)
 def test_named_visual_filters_and_declared_report_are_never_dropped(self):
  for changes in ({'report':'r1'},{'visual':'v1'},{'details':{'measure':'Handled Quantity','filters':[{'field':'warehouse','value':1}]}}):
   mapped=deepcopy(self.mapped);mapped['prefilled'].update(changes);probe=self.probe({'m1':7,'m2':8});self.assertEqual(resolve(self.text,mapped,self.catalog,probe)['status'],'NEEDS_INPUT');probe.assert_not_called()
  probe=self.probe({'m1':7,'m2':8});resolve('The Handled Quantity card shows 7.',self.mapped,self.catalog,probe);probe.assert_not_called()
 def test_invalid_primary_span_still_refuses_after_native_match(self):
  mapped=deepcopy(self.mapped);mapped['source']['provenance']['reported_figure']=[1,1]
  self.assertEqual(resolve(self.text,mapped,self.catalog,self.probe({'m1':7,'m2':8}))['status'],'NEEDS_INPUT')
 def test_omitted_model_shortlist_candidate_is_still_checked(self):
  self.mapped['resolution_candidates']=self.mapped['resolution_candidates'][:1]
  probe=self.probe({'m1':7,'m2':7});self.assertEqual(resolve(self.text,self.mapped,self.catalog,probe)['status'],'NEEDS_INPUT');self.assertEqual(probe.call_count,2)
 def test_bounded_partial_inventory_cannot_authorize_a_match(self):
  self.catalog.nodes.update({m:{'id':m,'kind':'MEASURE','label':'Handled Quantity'}for m in ('m3','m4')});self.mapped['resolution_candidates'] +=[{'via':m,'basis':'CATALOG_CONTAINMENT_OF_NAMED_MEASURE'}for m in ('m3','m4')];probe=self.probe({'m1':7,'m2':8,'m3':9,'m4':10});result=resolve(self.text,self.mapped,self.catalog,probe);self.assertEqual(result['status'],'NEEDS_INPUT');self.assertEqual(probe.call_count,3)

class NativeProbeTests(unittest.TestCase):
 def test_probe_uses_the_bound_measure_route_and_preserves_original_query_record(self):
  from types import SimpleNamespace
  from investigator.guided_intake_candidates import probe_measure
  objects=[{'id':'table','kind':'SemanticTable','name':'Activity'},{'id':'metric','kind':'Measure','name':'Handled Quantity','parent_id':'table'}]
  factory=SimpleNamespace(target_path=lambda _: {'nodes':[{'id':'m1'}]},resolve_path=lambda x:x,
      routes={'model':{'dialect':'DAX','path_nodes':['m1']}},prepare=lambda *_:{'dialect':'DAX','objects':objects,'label':'Model'})
  catalog=Catalog({'nodes':[{'id':'m1','kind':'MEASURE','label':'Handled Quantity'}],'edges':[]});execute=Mock(return_value={'rows':[{'[value]':7}]});saved=[];events=[]
  observed=probe_measure(factory,catalog,'m1',{},execute,events.append,saved)
  self.assertEqual(observed['status'],'SUCCEEDED');self.assertEqual(observed['value'],7);self.assertEqual(len(saved),1);self.assertEqual(observed['query_id'],saved[0]['id']);execute.assert_called_once();self.assertEqual(execute.call_args.args[0],'model');self.assertEqual(execute.call_args.args[1]['validator_version'],'bounded-dax-v1')
  self.assertEqual(saved[0]['text'],'EVALUATE ROW("value", [Handled Quantity])')
  repeated=probe_measure(factory,catalog,'m1',{},execute,events.append,saved);self.assertEqual(repeated['query_id'],observed['query_id']);self.assertEqual(len(saved),1);execute.assert_called_once();self.assertTrue(any(e.get('event')=='INTAKE_CANDIDATE_ALREADY_HAVE'for e in events))
 def test_intake_queries_count_towards_the_existing_action_allowance_and_reuse_cache(self):
  from test_round23_reasoning import LoopTests,tool
  h=LoopTests();loop=h.assemble([]);query='SELECT SUM(quantity) AS total FROM dbo.Items';q=loop.queries.run('gold',query,kind='sql',purpose='recreate');loop.initial_tools_used=1
  again=loop.queries.run('gold',query,kind='sql',purpose='recreate');self.assertEqual(again['already_have'],q['id']);h.execute.assert_called_once()
  h.model.complete.side_effect=None
  h.model.complete.return_value=tool('submit_finding',{'verdict':'observed value','cause':'The checked value is7.','numbers':[7],'checked':['gold'],'evidence_ids':[q['id']]})
  out=loop.run();self.assertEqual(out['status'],'ANSWERED');self.assertEqual(out['tools_used'],2);h.execute.assert_called_once()

if __name__=='__main__':unittest.main()

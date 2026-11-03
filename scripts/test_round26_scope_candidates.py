"""Native scoped candidates: exact definitions, exhaustive checks, no cell swaps."""
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock
import unittest
from investigator.guided_intake import Catalog
from investigator.guided_intake_candidates import resolve, probe_target
from investigator.guided_text_resolver import Resolver
from investigator.adapters.intake_candidate_scope import compile_scope, plan
from test_round23_text_resolver import reference

class ScopeCandidatesTests(unittest.TestCase):
 def fixture(self):
  from test_declared_predicate_adapter import DeclaredPredicateAdapterTests
  f=DeclaredPredicateAdapterTests();f.setUp();self.addCleanup(f.doCleanups);return f
 def test_native_filters_are_composed_and_not_inferred_from_the_reported_value(self):
  f=self.fixture();out=compile_scope(f.model,f.measure['id'],f.visual['id'])
  self.assertIn('TREATAS({"North"}',out['query']);self.assertNotIn('Coastal',out['query'])
  self.assertEqual(out['scope_evidence']['cell']['mode'],'UNGROUPED')
  entries=out['scope_evidence']['inventory']['entries']
  self.assertEqual(sum(e['disposition']=='ACTIVE'for e in entries),3)
  self.assertTrue(out['scope_evidence']['definition_evidence']['conditional_declarations'])
 def test_unsupported_native_filter_and_unaddressed_matrix_never_become_totals(self):
  f=self.fixture();f.model['context']['model_assets'].append({'id':'segment','parent_id':f.dimension['id'],'kind':'SemanticColumn','name':'Segment','metadata':{'dataType':'string'}});f.modify(f.visual,lambda d:d['visual'].update(visualType='pivotTable'));f.modify(f.visual,lambda d:d['visual']['query']['queryState'].update(
      Rows={'projections':[{'field':{'Column':{'Expression':{'SourceRef':{'Entity':'Customers'}},'Property':'Segment'}}}]}))
  with self.assertRaisesRegex(ValueError,'MISSING_CELL_KEYS'):
   compile_scope(f.model,f.measure['id'],f.visual['id'])
  out=compile_scope(f.model,f.measure['id'],f.visual['id'],total=True)
  self.assertEqual(out['scope_evidence']['cell']['mode'],'TOTAL')
  f.modify(f.page,lambda d:d.update(filterConfig={'filters':[{'type':'Unsupported','filter':{'Unknown':True}}]}))
  with self.assertRaises(ValueError):compile_scope(f.model,f.measure['id'],f.visual['id'])
 def test_native_plan_resolves_literal_model_and_definition_addresses_only(self):
  from urllib.parse import quote
  f=self.fixture();model_id='fabric://'+f.model['workspace']+'/'+f.model['native_id']
  report=f.report['report'];report.update(kind='Report',parent_id='fabric://'+f.model['workspace'],metadata={'datasetId':f.model['native_id']})
  model={'id':model_id,'kind':'SemanticModel','name':'Model','parent_id':report['parent_id'],'metadata':{}}
  f.table['parent_id']=model_id;f.dimension['parent_id']=model_id
  for p in f.parts:p['parent_id']=report['id']
  assets={a['id']:a for a in [report,model,*f.model['context']['model_assets'],*f.parts]}
  nodes=[{'id':'r','kind':'REPORT','label':'Report','properties':{'asset_id':report['id']}},
     {'id':'p','kind':'PAGE','label':'Page'},
     {'id':'v','kind':'VISUAL','label':'Revenue card','properties':{'asset_id':report['id']+'/visual/'+quote(f.visual['name'],safe='')}},
     {'id':'m','kind':'MEASURE','label':'Revenue','properties':{'asset_id':f.measure['id']}}]
  edges=[{'source':a,'target':b,'kind':k}for a,b,k in [('r','p','CONTAINS'),('p','v','CONTAINS'),('v','m','COMPUTED_FROM')]]
  catalog=Catalog({'nodes':nodes,'edges':edges});native=SimpleNamespace(assets=assets,routes={'dax':{'container':model_id,'dialect':'DAX'}})
  for target in ('r','p','v'):
   out=plan(native,catalog,target,{'description':'Report Revenue card shows 999','details':{'measure':'Revenue'}})
   self.assertEqual(out['intake']['visual'],'v');self.assertIn('TREATAS',out['query']);self.assertNotIn('999',out['query'])
  report['metadata']['datasetId']='not-the-native-model'
  with self.assertRaisesRegex(ValueError,'EXPLICIT_MODEL_BINDING_ABSENT'):
   plan(native,catalog,'v',{'description':'Report Revenue card'})
 def setup_candidates(self,field='visual'):
  from test_round26_catalog_resolution import CatalogResolutionTests
  self.catalog=CatalogResolutionTests().catalog();self.catalog.nodes['card']['label']='Regional summary'
  self.catalog.nodes.update({'p2':{'id':'p2','kind':'PAGE','label':'Other page'},'v2':{'id':'v2','kind':'VISUAL','label':'Whole summary'}})
  self.catalog.edges.extend([{'source':'report','target':'p2','kind':'CONTAINS'},
      {'source':'p2','target':'v2','kind':'CONTAINS'},{'source':'v2','target':'measure','kind':'COMPUTED_FROM'}])
  self.text='Billing Overview Net Revenue card shows 7.'
  span=reference(self.text,'7');visual=reference(self.text,'Net Revenue')
  args={'proposal':{'version':'IntakeRequest/1','report':'report','page':'page','visual':'card',
      'description':self.text,'issue_type':'NUMBER_LOOKS_WRONG','reported_figure':{'state':'NUMBER','value':'7','precision':'EXACT'},
      'compared_with':{'kind':'NOTHING'}},'provenance':{'visual':visual,'reported_figure':span},
      'figure_mentions':[{'role':'PRIMARY','reference':span}]}
  self.mapped=Resolver(catalog=self.catalog,model=None,record=lambda _:None).check(self.text,args)
  self.assertEqual(self.mapped['status'],'NEEDS_INPUT')
  if field=='page':self.mapped['question']['fields']=[{'field':'page','choices':[]}]
 def test_visual_tie_checks_each_scope_and_unique_match_is_origin_checked(self):
  self.setup_candidates();probe=Mock(side_effect=lambda key,p:{'status':'SUCCEEDED','query_id':key,'value':7 if key=='v2'else 8})
  out=resolve(self.text,self.mapped,self.catalog,probe)
  self.assertEqual(probe.call_count,2);self.assertEqual(out['status'],'READY')
  self.assertEqual(out['intake']['visual'],'v2');self.assertEqual(out['intake']['page'],'p2')
  self.assertEqual(out['source'],self.mapped['source'])
 def test_page_tie_checks_each_and_retains_ambiguous_results(self):
  self.setup_candidates('page');probe=Mock(return_value={'status':'SUCCEEDED','query_id':'q','value':7})
  out=resolve(self.text,self.mapped,self.catalog,probe)
  self.assertEqual(probe.call_count,2);self.assertEqual(out['status'],'NEEDS_INPUT')
  self.assertEqual(out['question']['fields'][0]['field'],'page');self.assertEqual(len(out['candidate_checks']),2)
 def test_exact_named_visual_is_not_swapped_for_matching_value(self):
  self.setup_candidates();self.text='Billing Overview Regional summary Net Revenue shows 7.'
  self.mapped['source']['text']=self.text
  probe=Mock(return_value={'status':'SUCCEEDED','query_id':'q','value':8})
  out=resolve(self.text,self.mapped,self.catalog,probe)
  self.assertEqual(probe.call_count,1);self.assertEqual(probe.call_args.args[0],'card')
  self.assertEqual(out['status'],'NEEDS_INPUT')
 def test_failed_native_candidate_prevents_unique_selection_and_keeps_error(self):
  self.setup_candidates();probe=Mock(side_effect=[{'status':'SUCCEEDED','query_id':'q','value':7},
     {'status':'UNAVAILABLE','error':'native read failed'}])
  out=resolve(self.text,self.mapped,self.catalog,probe)
  self.assertEqual(out['status'],'NEEDS_INPUT');self.assertEqual(out['candidate_checks'][1]['error'],'native read failed')
 def test_scoped_port_runs_compiled_query_and_reuses_saved_result(self):
  self.setup_candidates();objects=[{'id':'t','kind':'SemanticTable','name':'Sales'},
      {'id':'m','kind':'Measure','name':'Revenue','parent_id':'t'}]
  compiled={'layer':'model','query':'EVALUATE ROW("value", [Revenue])','scope':'retained',
      'scope_evidence':{'retained':'definition'},'intake':{'report':'report','page':'page','visual':'card'}}
  factory=SimpleNamespace(candidate_query_for=Mock(return_value=compiled),
      prepare=lambda *_:{'dialect':'DAX','objects':objects,'label':'Semantic'})
  execute=Mock(return_value={'rows':[{'[value]':7}]});saved=[];events=[]
  for _ in range(2):
   out=probe_target(factory,self.catalog,'card',{},execute,events.append,saved)
   self.assertEqual(out['value'],7);self.assertEqual(out['scope_evidence'],compiled['scope_evidence'])
  execute.assert_called_once();self.assertEqual(len(saved),1)

if __name__=='__main__':unittest.main()

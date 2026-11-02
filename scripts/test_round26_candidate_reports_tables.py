from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock
import unittest
from investigator.guided_intake import Catalog
from investigator.guided_intake_candidates import resolve,probe_target
from test_round23_text_resolver import reference


class CandidatesTests(unittest.TestCase):
 def setup(self,kind):
  self.text='Rows shows 7.'if kind=='TABLE'else'Revenue shows 7.'
  self.nodes=[{'id':i,'kind':kind,'label':'Rows'if kind=='TABLE'else'Revenue '+i}for i in ('a','b')]
  self.edges=[]
  if kind=='REPORT':
   for i in ('a','b'):
    self.nodes.extend([{'id':'p'+i,'kind':'PAGE','label':'Overview'},{'id':'v'+i,'kind':'VISUAL','label':'Revenue'},
                       {'id':'m'+i,'kind':'MEASURE','label':'Revenue'}])
    self.edges.extend([{'source':i,'target':'p'+i,'kind':'CONTAINS'},{'source':'p'+i,'target':'v'+i,'kind':'CONTAINS'},
                       {'source':'v'+i,'target':'m'+i,'kind':'COMPUTED_FROM'}])
  self.catalog=Catalog({'nodes':self.nodes,'edges':self.edges})
  span=reference(self.text,'7')
  self.mapped={'status':'NEEDS_INPUT','prefilled':{'version':'IntakeRequest/1','description':self.text,
     'issue_type':'NUMBER_LOOKS_WRONG','reported_figure':{'state':'NUMBER','value':'7','precision':'EXACT'},'compared_with':{'kind':'NOTHING'}},
     'source':{'kind':'MAPPED_TEXT','text':self.text,'provenance':{'reported_figure':span},'figure_mentions':[{'role':'PRIMARY','reference':span}]}}
 def test_two_reports_are_checked_before_a_unique_native_match_resolves(self):
  self.setup('REPORT');probe=Mock(side_effect=lambda key,p:{'status':'SUCCEEDED','query_id':'q'+key,'value':7 if key=='a' else 8})
  result=resolve(self.text,self.mapped,self.catalog,probe)
  self.assertEqual(probe.call_count,2);self.assertEqual(result['status'],'READY');self.assertEqual(result['intake']['report'],'a')
  self.assertNotIn('visual',result['intake'])
 def test_two_tables_are_checked_and_none_or_multiple_fits_keep_the_findings(self):
  self.setup('TABLE')
  for values in [(7,7),(8,9)]:
   probe=Mock(side_effect=[{'status':'SUCCEEDED','query_id':'same','value':v}for v in values])
   result=resolve(self.text,self.mapped,self.catalog,probe)
   self.assertEqual(result['status'],'NEEDS_INPUT');self.assertEqual(len(result['candidate_checks']),2)
   self.assertEqual(result['question']['fields'][0]['field'],'table');self.assertTrue(result['candidate_checks_exhaustive'])
 def test_three_probe_bound_never_selects_from_an_incomplete_inventory(self):
  self.setup('TABLE')
  for i in ('c','d'):self.catalog.nodes[i]={'id':i,'kind':'TABLE','label':'Rows'}
  probe=Mock(return_value={'status':'SUCCEEDED','query_id':'one','value':7})
  result=resolve(self.text,self.mapped,self.catalog,probe)
  self.assertEqual(probe.call_count,3);self.assertFalse(result['candidate_checks_exhaustive']);self.assertEqual(result['status'],'NEEDS_INPUT')
 def test_explicit_visual_never_changes_to_a_matching_candidate(self):
  self.setup('REPORT');self.mapped['prefilled']['visual']='va';probe=Mock()
  self.assertEqual(resolve(self.text,self.mapped,self.catalog,probe)['status'],'NEEDS_INPUT');probe.assert_not_called()
 def test_loose_card_is_not_replaced_by_an_unfiltered_report_probe(self):
  self.setup('REPORT');execute=Mock()
  result=probe_target(None,self.catalog,'a',{'description':'Revenue card shows7'},execute,lambda _:None,[])
  self.assertEqual(result['status'],'UNAVAILABLE');self.assertIn('NO_UNFILTERED_SUBSTITUTION',result['error']);execute.assert_not_called()
 def test_table_probe_executes_only_the_exact_native_column_and_record_key(self):
  self.setup('TABLE');self.catalog.nodes['a']['properties']={'asset_id':'asset:a'}
  obj={'id':'asset:a','metadata':{'schema_name':'app','name':'Rows','type_desc':'USER_TABLE',
       'columns':[{'name':'units','data_type':'INT'},{'name':'row_id','data_type':'INT'}]}}
  route={'dialect':'T-SQL','asset_ids':['asset:a'],'objects':[obj],'label':'Source'}
  factory=SimpleNamespace(routes={'source':route},prepare=lambda i,n:deepcopy(route))
  execute=Mock(return_value={'rows':[{'value':7}]});events=[];saved=[]
  proposal={'description':'row_id 42 has7 units','details':{'measure':'units','record':'row_id 42'}}
  result=probe_target(factory,self.catalog,'a',proposal,execute,events.append,saved)
  self.assertEqual(result['value'],7);self.assertEqual(len(saved),1);self.assertIn('WHERE [row_id] = 42',result['query'])
  args=execute.call_args.args;self.assertEqual(args[0],'source');self.assertEqual(args[1]['asset_ids'],['asset:a'])
  self.assertTrue(args[1]['query'].startswith('SELECT TOP'));self.assertEqual(execute.call_args.kwargs['timeout_seconds'],30)
  proposal['details']['filters']=[{'field':'region','value':'West'}];execute.reset_mock()
  result=probe_target(factory,self.catalog,'a',proposal,execute,events.append,saved)
  self.assertEqual(result['status'],'UNAVAILABLE');execute.assert_not_called();self.assertIn('NO_FILTER',result['error'])

if __name__=='__main__':unittest.main()

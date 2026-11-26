"""A real read must not be reported unread merely because its proof shape differs."""
from copy import deepcopy
import unittest
from investigator.grounded_answers import finding
from investigator.regression_features import configured
from test_round23_answers_native import case

class ConsistencyFeedbackTests(unittest.TestCase):
 def fixture(self):
  c=case();c['context'].update(layers={'gold':{'label':'Serving'},'source':{'label':'Application'}},system_of_record={'declared':True,'reachable':True,'layer':'source','asset_id':'source-table'})
  q=deepcopy(c['queries'][0]);q.update(id='source-q',layer='source',asset_ids=['source-table']);c['queries'].append(q)
  c['evidence']['definition']={'tool':'get_definition','result':{'content':'Retained direct quantity definition','provenance':{'source':'retained'}}}
  a={'verdict':'consistent to source','cause':'The cited native quantities agree.','numbers':[7],'checked':['gold','source'],'evidence_ids':['q','source-q','definition']}
  return c,a
 def test_same_scalar_reads_still_deliver(self):
  c,a=self.fixture();self.assertIn('consistent to source',finding(a,c)['business'])
 def test_cited_multirow_or_multicolumn_reads_are_not_called_unread(self):
  for rows in ([{'quantity':7,'record_id':1}],[{'quantity':7},{'quantity':9}],[]):
   c,a=self.fixture()
   for q in c['queries']:q['result']['rows']=deepcopy(rows)
   with self.subTest(rows=rows),self.assertRaises(ValueError)as error:finding(a,c)
   self.assertIn('read layers without a comparable one-cell value',str(error.exception))
   self.assertNotIn('unread layers',str(error.exception))
   self.assertIn('same selected value and scope',str(error.exception))
 def test_uncited_source_read_is_not_reported_unqueried(self):
  c,a=self.fixture();a['evidence_ids'].remove('source-q')
  with self.assertRaisesRegex(ValueError,'source object was read.*not cited; cite source-q'):finding(a,c)
 def test_other_read_but_uncited_layer_names_existing_query(self):
  c,a=self.fixture();a['evidence_ids'].remove('q')
  with self.assertRaises(ValueError)as error:finding(a,c)
  self.assertIn('read but not cited layers: gold',str(error.exception))
  self.assertIn('query evidence q',str(error.exception))
  self.assertNotIn('unread layers',str(error.exception))
 def test_truly_unread_source_still_refuses(self):
  c,a=self.fixture();c['queries'].pop();a['evidence_ids'].remove('source-q')
  with self.assertRaisesRegex(ValueError,'declared source object was not queried'):finding(a,c)
 def test_a_truly_unread_required_layer_is_named_separately(self):
  c,a=self.fixture();c['context']['layers']['landing']={'label':'Landing'}
  with self.assertRaises(ValueError)as error:finding(a,c)
  self.assertIn('unread layers (no successful native result): landing',str(error.exception))
  self.assertNotIn('unread layers (no successful native result): gold',str(error.exception))
 def test_different_native_scalars_still_refuse(self):
  c,a=self.fixture();c['queries'][1]['result']['rows']=[{'quantity':9}]
  with self.assertRaisesRegex(ValueError,'compared native values differ'):finding(a,c)
 def test_failed_read_cannot_become_proof(self):
  c,a=self.fixture();c['queries'][1].update(status='ERROR',error='native read failed')
  with self.assertRaisesRegex(ValueError,'FAILED_QUERY'):finding(a,c)
 def test_flag_restores_original_feedback_without_allowing_finding(self):
  c,a=self.fixture()
  for q in c['queries']:q['result']['rows']=[{'quantity':7,'record_id':1}]
  with configured({'r27_source_consistency_feedback':False}),self.assertRaisesRegex(ValueError,'unread layers'):finding(a,c)

"""Native DAX headers and declared numeric SQL encodings must interoperate honestly."""
import unittest
from copy import deepcopy
from types import SimpleNamespace
from decimal import Decimal
from investigator.adapters.analysis_projection import project
from investigator.bounded_analysis import row_diff,contribution,comparison_cell
from investigator.investigation_read_tools import ReadTools
from investigator.regression_features import configured

def record(identity,rows,types=None,**more):
 return {'id':identity,'status':'SUCCEEDED','asset_ids':['table'],'result':{'rows':rows,**({'column_types':types}if types else{})},**more}
def layer():
 return {'dialect':'DAX','objects':[{'id':'table','kind':'SemanticTable','name':'Facts','metadata':{'columns':[{'name':'id'},{'name':'units'}]}}]}
def fixture():
 a=record('sql-q',[{'id':'7','units':'20'}],{'id':'Int64','units':'Int64'})
 b=record('dax-q',[{'Facts[id]':7,'Facts[units]':20}])
 return a,b
class ProjectionTests(unittest.TestCase):
 def views(self,a,b):return project(a,{'dialect':'T-SQL'},['id','units'])[0],project(b,layer(),['id','units'])[0]
 def test_native_sql_and_dax_readtools_diff_preserves_original_records(self):
  a,b=fixture();before=deepcopy((a,b));tools=ReadTools.__new__(ReadTools)
  tools.queries=SimpleNamespace(layers={'sql':{'dialect':'T-SQL'},'model':layer()},run=lambda identity,*args,**kwargs:a if identity=='sql'else b)
  args={'left':{'layer':'sql','kind':'sql','query':'SELECT id, units FROM approved_table'},'right':{'layer':'model','kind':'dax','query':'EVALUATE Facts'},'keys':['id'],'compare_fields':['units']}
  value=tools.analyze(args,'row_diff')
  self.assertEqual((value['missing_count'],value['extra_count'],value['changed_count']),(0,0,0));self.assertEqual(value['query_ids'],['sql-q','dax-q'])
  self.assertEqual(value['native_column_bindings']['right'],{'id':'Facts[id]','units':'Facts[units]'})
  self.assertEqual((a,b),before)
  with configured({'r27_analysis_native_projection':False}),self.assertRaisesRegex(ValueError,'KEY_COLUMN_MISSING'):tools.analyze(args,'row_diff')
 def test_named_aliases_need_no_guessed_table_binding(self):
  a,b=fixture();b['result']['rows']=[{'[id]':7,'[units]':20}];right,mapping=project(b,{'dialect':'DAX','objects':[]},['id','units'])
  left=self.views(a,b)[0];self.assertEqual(row_diff(left,right,keys=['id'],compare_fields=['units'],typed_values=True)['changed_count'],0)
  self.assertEqual(mapping,{'id':'[id]','units':'[units]'})
 def test_qualified_columns_require_exact_declared_and_referenced_parent(self):
  a,b=fixture()
  for context in ({'dialect':'DAX','objects':[]},layer()):
   bad=deepcopy(b);bad['asset_ids']=[]
   right,_=project(bad,context,['id','units'])
   with self.assertRaisesRegex(ValueError,'KEY_COLUMN_MISSING'):row_diff(a,right,keys=['id'],compare_fields=['units'],typed_values=True)
 def test_ambiguous_native_labels_are_never_picked_by_order(self):
  for extra in ('id','[id]'):
   a,b=fixture();b['result']['rows'][0][extra]=7
   with self.assertRaisesRegex(ValueError,'AMBIGUOUS_OUTPUT_COLUMN'):project(b,layer(),['id'])
 def test_numeric_looking_text_keys_are_not_coerced(self):
  a,b=fixture();a['result']['rows'][0]['id']='007';a['result']['column_types']['id']='String';left,right=self.views(a,b)
  value=row_diff(left,right,keys=['id'],compare_fields=['units'],typed_values=True);self.assertEqual((value['missing_count'],value['extra_count']),(1,1))
 def test_unknown_string_keys_remain_distinct_from_native_numbers(self):
  a,b=fixture();a['result'].pop('column_types');left,right=self.views(a,b)
  value=row_diff(left,right,keys=['id'],compare_fields=['units'],typed_values=True);self.assertEqual(value['missing_count'],1)
 def test_exact_numbers_do_not_round_large_values_or_decimal_scale(self):
  self.assertEqual(comparison_cell('9007199254740993','integer'),comparison_cell(9007199254740993))
  self.assertNotEqual(comparison_cell('9007199254740992','integer'),comparison_cell(9007199254740993))
  self.assertEqual(comparison_cell('20.2000','number'),comparison_cell(Decimal('20.2')))
  self.assertNotEqual(comparison_cell('999999999999999999999999999999999999.01','number'),comparison_cell(Decimal('999999999999999999999999999999999999.02')))
 def test_boolean_and_null_never_become_numeric_one_or_zero(self):
  self.assertEqual(comparison_cell('true','boolean'),comparison_cell(True))
  self.assertNotEqual(comparison_cell(True),comparison_cell(1));self.assertNotEqual(comparison_cell(None,'integer'),comparison_cell(0))
 def test_invalid_integer_and_nonfinite_cells_are_refused(self):
  for value,kind in (('7.1','integer'),('NaN','number'),('Infinity','number'),('not a number','number'),('perhaps','boolean')):
   with self.subTest(value=value),self.assertRaises(ValueError):comparison_cell(value,kind)
 def test_literal_dates_do_not_acquire_an_assumed_timezone(self):
  self.assertNotEqual(comparison_cell('2026-01-01T00:00:00','literal'),comparison_cell('2026-01-01T00:00:00Z','literal'))
 def test_duplicate_keys_are_detected_after_numeric_representation_alignment(self):
  a,b=fixture();a['result']['rows'].append({'id':'7.0','units':'20'});left,right=self.views(a,b)
  with self.assertRaisesRegex(ValueError,'NOT_UNIQUE'):row_diff(left,right,keys=['id'],compare_fields=['units'],typed_values=True)
 def test_truncation_never_earns_complete_absence_counts(self):
  a,b=fixture();a['truncated']=True;b['result']['rows']=[];left,right=self.views(a,b)
  value=row_diff(left,right,keys=['id'],compare_fields=['units'],typed_values=True);self.assertIsNone(value['missing_count']);self.assertFalse(value['complete_returned_scopes'])
 def test_contributions_share_typed_group_keys_but_keep_exact_arithmetic(self):
  a,b=fixture();a['result']['rows'][0]['units']='20.20';a['result']['column_types']['units']='Decimal128(38, 2)';b['result']['rows'][0]['Facts[units]']=20.2;left,right=self.views(a,b)
  value=contribution(left,right,dimensions=['id'],value_field='units',typed_values=True);self.assertEqual(value['total_slices'],1);self.assertEqual(Decimal(value['net_difference']),0)
 def test_changed_samples_keep_the_observed_values(self):
  a,b=fixture();b['result']['rows'][0]['Facts[units]']=21;left,right=self.views(a,b)
  value=row_diff(left,right,keys=['id'],compare_fields=['units'],typed_values=True);self.assertEqual(value['changed_sample'][0]['fields']['units'],{'before':'20','after':21})
 def test_missing_row_fields_are_not_filled_with_null(self):
  a,b=fixture();b['result']['rows'].append({'Facts[units]':20});left,right=self.views(a,b)
  with self.assertRaisesRegex(ValueError,'KEY_COLUMN_MISSING'):row_diff(left,right,keys=['id'],compare_fields=['units'],typed_values=True)

 def test_unknown_metadata_does_not_hide_an_actual_native_numeric_type(self):
  a,b=fixture();a['result']['rows'][0]={'id':7,'units':20};a['result']['column_types']={'id':'Unknown','units':'Unknown'};left,right=self.views(a,b)
  value=row_diff(left,right,keys=['id'],compare_fields=['units'],typed_values=True);self.assertEqual((value['missing_count'],value['changed_count']),(0,0))
 def test_same_layer_refusal_still_precedes_any_read(self):
  tools=ReadTools.__new__(ReadTools);calls=[];tools.queries=SimpleNamespace(layers={'one':layer()},run=lambda *a,**k:calls.append(a))
  args={'left':{'layer':'one','kind':'dax','query':'EVALUATE Facts'},'right':{'layer':'one','kind':'dax','query':'EVALUATE Facts'},'keys':['id'],'compare_fields':['units']}
  with self.assertRaisesRegex(ValueError,'DIFFERENT_LAYERS'):tools.analyze(args,'row_diff')
  self.assertEqual(calls,[])

 def test_optional_metadata_does_not_prevent_declared_column_binding(self):
  a,b=fixture();context={'dialect':'DAX','objects':[None,{'id':'table','kind':'SemanticTable','name':'Facts','metadata':None},{'id':'id-column','kind':'SemanticColumn','parent_id':'table','name':'id','metadata':None},{'id':'units-column','kind':'SemanticColumn','parent_id':'table','name':'units'}]}
  right,mapping=project(b,context,['id','units']);left=project(a,{'dialect':'T-SQL'},['id','units'])[0]
  self.assertEqual(mapping,{'id':'Facts[id]','units':'Facts[units]'});self.assertEqual(row_diff(left,right,keys=['id'],compare_fields=['units'],typed_values=True)['changed_count'],0)
 def test_malformed_optional_type_metadata_never_coerces_numeric_text(self):
  a,b=fixture();a['result']['column_types']=['Int64'];left,right=self.views(a,b)
  self.assertEqual(row_diff(left,right,keys=['id'],compare_fields=['units'],typed_values=True)['missing_count'],1)

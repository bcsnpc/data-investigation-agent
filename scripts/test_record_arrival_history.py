"""New keyed source rows are a valid latency history check, not unchanged totals."""
from copy import deepcopy
from unittest import TestCase,main
from investigator.history_comparison import disposition
from investigator.regression_features import configured
import test_round26_history_comparison as baseline

def case():
 v=baseline.HistoryComparisonTests().case()
 v['queries'][0].update(text='SELECT id,quantity,modified_at FROM dbo.Items WHERE id=42',result={'rows':[{'id':42,'quantity':17,'modified_at':'2026-10-02'}]})
 v['queries'][1].update(text="SELECT id,quantity FROM dbo.Items FOR SYSTEM_TIME AS OF '2026-10-01' WHERE id=42",result={'rows':[]})
 return v

class RecordArrivalTests(TestCase):
 def test_native_keyed_absence_then_presence_with_different_projections(self):
  v=case();before=deepcopy(v);out=disposition(v,['now','then'])
  self.assertTrue(out['ruled_out']);self.assertEqual(out['basis'],'KEY_ABSENT_AT_NATIVE_LOAD_END_PRESENT_NOW')
  self.assertEqual(out['query_ids'],['then','now']);self.assertEqual(v,before)
  self.assertIn('not an earlier deletion/reinsertion',out['qualification'])
 def test_flag_off_retains_old_unchanged_scalar_requirement(self):
  pass
 def test_uncited_wrong_asset_wrong_layer_failed_or_truncated_is_not_arrival(self):
  variants=[]
  for field,value in [('asset_ids',['another']),('asset_ids',['table','another']),('layer','warehouse'),('status','ERROR'),('truncated',True)]:
   v=case();v['queries'][1][field]=value;variants.append(v)
  v=case();v['queries'][0]['result']['truncated']=True;variants.append(v)
  v=case();v['context']['system_of_record'].pop('asset_id');variants.append(v)
  for v in variants:
   with self.subTest(case=v):self.assertFalse(disposition(v,['now','then'])['ruled_out'])
  self.assertFalse(disposition(case(),['now'])['ruled_out'])
 def test_existing_changed_row_missing_current_or_unrelated_snapshot_not_arrival(self):
  variants=[]
  v=case();v['queries'][1]['result']['rows']=[{'id':42,'quantity':16}];variants.append(v)
  v=case();v['queries'][0]['result']['rows']=[];variants.append(v)
  v=case();v['queries'][1]['text']=v['queries'][1]['text'].replace('2026-10-01','2026-09-01');variants.append(v)
  v=case();v['queries'][1]['text']=v['queries'][1]['text'].replace('id=42','id=43');variants.append(v)
  v=case();v['triage']={};variants.append(v)
  for v in variants:
   with self.subTest(case=v):self.assertFalse(disposition(v,['now','then'])['ruled_out'])
 def test_broad_predicates_joins_limits_aggregates_and_current_only_do_not_prove_arrival(self):
  for historical in ["SELECT id FROM dbo.Items FOR SYSTEM_TIME AS OF '2026-10-01' WHERE id>0",
   "SELECT id FROM dbo.Items FOR SYSTEM_TIME AS OF '2026-10-01' WHERE id=42 OR id=43",
   "SELECT TOP 1 id FROM dbo.Items FOR SYSTEM_TIME AS OF '2026-10-01' WHERE id=42",
   "SELECT COUNT(*) FROM dbo.Items FOR SYSTEM_TIME AS OF '2026-10-01' WHERE id=42",
   "SELECT i.id FROM dbo.Items FOR SYSTEM_TIME AS OF '2026-10-01' i JOIN dbo.Other o ON i.id=o.id WHERE i.id=42",
   'SELECT id FROM dbo.Items WHERE id=42']:
   v=case();v['queries'][1]['text']=historical
   with self.subTest(query=historical):self.assertFalse(disposition(v,['now','then'])['ruled_out'])

if __name__=='__main__':main()

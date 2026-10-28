import unittest,json
from datetime import datetime,timezone
from unittest.mock import patch
from investigator import build_phase as b

class Aggregation(unittest.TestCase):
 def test_all_statuses_environments_missing_allocations_and_reset_preserved(self):
  now=datetime(2026,10,28,tzinfo=timezone.utc).timestamp();reset=datetime.fromisoformat(b.POLICY['restoration_reset']['effective_at']).timestamp()
  retained=[];alloc=[];groups={}
  for i in range(12000):
   category=('SCAN','INVESTIGATION','RESTORATION')[i%3];created=reset-1 if i%2 else reset+1
   key={'environment':str(i%4),'session_id':str(i),'reservation_key':'key'}
   retained.append({**key,'reserved':json.dumps({'cloud_calls':1}),'created':created,'status':('RESERVED','UNCERTAIN','SETTLED')[i%3]})
   if i%7:alloc.append({**key,'purpose':category})
   else:category='INVESTIGATION'
   bucket=(category,created);groups[bucket]=groups.get(bucket,0)+1
  projections=[{'category':k[0],'created':k[1],'cloud_calls':v,'invalid':0}for k,v in groups.items()]
  a,c=b.physical_group_rows(projections)
  self.assertLessEqual(len(a),6);self.assertEqual(b.physical_status(a,c,now),b.physical_status(retained,alloc,now))
  for category in b.PURPOSES:
   def admission(r,a):
    try:return b.admit_physical(r,a,now,category)
    except Exception as e:return type(e).__name__,str(e)
   self.assertEqual(admission(a,c),admission(retained,alloc))
 def test_unknown_category_is_not_discarded_even_with_zero_count(self):
  now=datetime(2026,10,28,tzinfo=timezone.utc).timestamp();a,c=b.physical_group_rows([{'category':'BAD','created':now,'cloud_calls':0}])
  with self.assertRaisesRegex(ValueError,'CATEGORY_UNKNOWN'):b.physical_status(a,c,now)
 def test_malformed_aggregate_falls_back_to_unmodified_raw_contract(self):
  from types import SimpleNamespace
  state=SimpleNamespace(backend='postgresql');raw=[{'original':'kept'}];alloc=[{'original':'allocation'}]
  with patch('investigator.shared_usage.rows',side_effect=[[{'invalid':1}],raw,alloc])as read:
   self.assertEqual(b.shared_physical_rows(state,object(),datetime(2026,10,28,tzinfo=timezone.utc).timestamp()),(raw,alloc))
   self.assertEqual(read.call_count,3)
if __name__=='__main__':unittest.main()

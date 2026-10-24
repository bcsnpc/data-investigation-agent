import json,unittest
from investigator import build_phase as b
from test_build_phase import instant
from investigator.usage_governance import UsageHold

class ScanReallocationTests(unittest.TestCase):
    def test_owner_reallocation_preserves_total_reserve_and_usage(self):
        now=instant('2026-10-24')+2*3600
        rows=[{'environment':'x','session_id':'scan','reservation_key':'one','reserved':json.dumps({'cloud_calls':817}),'created':now}]
        alloc=[{'environment':'x','session_id':'scan','reservation_key':'one','purpose':'SCAN'}]
        value=b.physical_status(rows,alloc,now)
        self.assertEqual(value['limits'],{'INVESTIGATION':3905,'SCAN':2000,'RESTORATION':95})
        self.assertEqual(value['total_limit'],6000)
        self.assertEqual(sum(value['limits'].values()),6000)
        self.assertEqual(value['used']['SCAN'],817)
        self.assertEqual(value['restoration_remaining'],95)
        self.assertNotIn('SCAN_MONTHLY_80_PERCENT',value['warnings'])

    def test_historical_clock_keeps_original_policy_for_replay(self):
        now=instant('2026-10-23')
        self.assertEqual(b.physical_status([],[],now)['limits'],{'INVESTIGATION':4905,'SCAN':1000,'RESTORATION':95})

    def test_updated_categories_still_refuse_at_their_ceilings(self):
        now=instant('2026-10-25')
        for purpose,count in [('SCAN',2000),('INVESTIGATION',3905),('RESTORATION',95)]:
            rows=[{'environment':'x','session_id':'x','reservation_key':'one','reserved':json.dumps({'cloud_calls':count}),'created':now}]
            alloc=[{'environment':'x','session_id':'x','reservation_key':'one','purpose':purpose}]
            with self.subTest(purpose=purpose),self.assertRaisesRegex(UsageHold,purpose+'_EXHAUSTED'):
                b.admit_physical(rows,alloc,now,purpose)
        self.assertEqual(b.physical_status([],[],instant('2026-11-02'))['limits']['SCAN'],2000)

if __name__=='__main__':unittest.main()

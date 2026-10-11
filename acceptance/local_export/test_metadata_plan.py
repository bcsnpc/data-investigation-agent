import unittest
from metadata_plan import request
class PlanTests(unittest.TestCase):
 def test_native_worker_attests_only_once(self):
  c={'surface':'FABRIC_SQL','database':'fixture','item_id':'fixture://id'};r=request(c,'SELECT COLUMNS FROM INFORMATION_SCHEMA.COLUMNS')
  self.assertNotIn('__surface_',r['query']);self.assertEqual(len(r['result_columns']),9)
  with self.assertRaisesRegex(ValueError,'DUPLICATE'):request(c,'SELECT __surface_identity FROM t')
 def test_source_catalog_route_required_before_admission(self):
  with self.assertRaisesRegex(ValueError,'ROUTE'):request({'surface':'AZURE_SQL','database':'billingapp'},'SELECT metadata')
  r=request({'surface':'AZURE_SQL','database':'billingapp','item_id':'sql://server/billingapp/catalog'},'SELECT metadata',source=True);self.assertEqual(r['result_columns'][-1],'object_id')
if __name__=='__main__':unittest.main()

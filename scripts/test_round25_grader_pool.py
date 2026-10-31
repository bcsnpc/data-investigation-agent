import copy,json,unittest
from round25_grader_pool import encode,decode
class LosslessPoolTests(unittest.TestCase):
 def test_literal_queries_rows_prose_and_unicode_round_trip(self):
  prefix='SELECT SUM(CAST(quantity AS bigint)) FROM [app].'
  value={'protocol':'scored-evaluation-v1','case_id':'synthetic','purpose':'GRADE_GUIDED_ANSWER','expected':{'cause':'unchanged — €','value':17},'delivered':{'queries':[{'sql':prefix+'[movements] WHERE movement_id=900701','rows':[{'quantity':17}]},{'sql':prefix+'[other_movements] WHERE movement_id=900701','rows':[{'quantity':None}]}],'business':'The recorded value is 17; the other result is empty.'}}
  original=copy.deepcopy(value);packed=encode(value,minimum_string=40,minimum_slice=20)
  self.assertEqual(decode(packed),original);self.assertEqual(value,original)
 def test_shorter_exact_slices_reduce_repeated_query_material(self):
  common='source_modified_at_utc AS observation_time, SUM(quantity) AS quantity FROM '
  value={'delivered':{'queries':[common+'[native_'+str(i)+'] WHERE quantity > 0' for i in range(25)]}}
  packed=encode(value,minimum_string=40,minimum_slice=20)
  self.assertEqual(decode(packed),value)
  self.assertLess(len(json.dumps(packed)),len(json.dumps(value)))
 def test_invalid_minimum_refused(self):
  with self.assertRaisesRegex(ValueError,'LOSSLESS_POOL_MINIMUMS'):encode({'delivered':{}},minimum_string=0)

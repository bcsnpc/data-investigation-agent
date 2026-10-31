import copy,json,unittest
from round25_grader_pool import encode,decode,fit_task
class LosslessPoolTests(unittest.TestCase):
 def test_legacy_native_prefix_field_is_not_misread_as_new_transport_metadata(self):
  value={'delivered':{'pool_reference_prefix':'native literal','rows':[{'units':17}]*3}}
  self.assertEqual(decode(encode(value)),value)
  with self.assertRaisesRegex(ValueError,'METADATA_COLLISION'):encode(value,string_references=True)
 def test_fitting_keeps_all_literal_fields_and_does_not_raise_the_bound(self):
  value={'protocol':'scored-evaluation-v1','case_id':'synthetic','purpose':'GRADE_GUIDED_ANSWER','expected':{'cause':'unchanged'},'delivered':{'rows':[{'units':17,'sql':'SELECT quantity FROM approved_table WHERE id=17'}]*80}}
  original=copy.deepcopy(value);packed=fit_task(value,maximum_characters=2000)
  self.assertEqual(decode(packed),original);self.assertEqual(value,original)
  self.assertLessEqual(len(json.dumps(packed,sort_keys=True,separators=(',',':'),ensure_ascii=False)),2000)
  with self.assertRaisesRegex(ValueError,'GRADER_INPUT_BOUND'):fit_task(value,maximum_characters=24001)
  with self.assertRaisesRegex(ValueError,'DOES_NOT_FIT'):fit_task(value,maximum_characters=1)
 def test_already_fitting_tasks_are_byte_stable(self):
  value={'delivered':{'business':'literal €','rows':[{'units':17}]}}
  before=json.dumps(value,ensure_ascii=False)
  self.assertIs(fit_task(value),value);self.assertEqual(json.dumps(value,ensure_ascii=False),before)
 def test_v2_references_preserve_literal_markers_and_reference_shaped_data(self):
  value={'case_id':'fixed','expected':{'number':17},'delivered':{'literal_markers':['@0','@@1','@@@2'],'literal_object':{'p':1},'rows':[{'units':17,'label':'unchanged €'}]*12}}
  original=copy.deepcopy(value);packed=encode(value,string_references=True,minimum_string=40,minimum_slice=20)
  self.assertEqual(decode(packed),original);self.assertEqual(value,original)
  self.assertEqual(packed['delivered']['pool_reference_prefix'],'@@@@')
 def test_v2_reduces_reference_overhead_and_old_packets_still_replay(self):
  value={'delivered':{'rows':[{'units':17,'label':'literal unchanged result'}]*80}}
  old=encode(value);new=encode(value,string_references=True)
  self.assertEqual(decode(old),value);self.assertEqual(decode(new),value)
  self.assertLess(len(json.dumps(new)),len(json.dumps(old)))
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

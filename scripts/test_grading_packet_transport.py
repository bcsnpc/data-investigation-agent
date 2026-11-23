import unittest,json,copy
from round25_grader_pool import encode,decode
from round25_grader_pool import fit_task,decode as multi_decode
def restore_fields(value):return value
from grading_packet_transport import unpool_for_refit
class GraderTransportTests(unittest.TestCase):
 def test_nested_pool_is_decoded_before_refitting_without_mutation(self):
  v={'case_id':'synthetic','expected':{'number':17},'delivered':{'business':'The recorded units are 17.','queries':[{'text':'SELECT units FROM approved_table WHERE id=17','rows':[{'units':17}]}]*80}}
  packed=encode(v);before=copy.deepcopy(packed)
  self.assertIn('verbatim_pool',packed['delivered'])
  decoded=unpool_for_refit(packed);self.assertEqual(decoded,v);self.assertEqual(packed,before)
  again=fit_task(decoded,maximum_characters=2000)
  self.assertEqual(restore_fields(multi_decode(again)),v)
  self.assertLessEqual(len(json.dumps(again,sort_keys=True,separators=(',',':'),ensure_ascii=False)),2000)
 def test_plain_packets_are_unchanged(self):
  v={'delivered':{'business':'unchanged','rows':[{'units':17}]}}
  self.assertIs(unpool_for_refit(v),v)
 def test_unknown_literal_metadata_not_interpreted(self):
  v={'delivered':{'pool_encoding':'native metadata','verbatim_pool':['literal']}}
  self.assertIs(unpool_for_refit(v),v)

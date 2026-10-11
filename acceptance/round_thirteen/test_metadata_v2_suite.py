import unittest
import test_replay_suite as legacy
class Tests(unittest.TestCase):
 def setUp(self):legacy.Tests.setUp(self)
 def tearDown(self):legacy.Tests.tearDown(self)
 def metadata(self,op,dispatcher):
  op.update(dispatcher=dispatcher,operation='billing_metadata_collection',capture_support={'metadata_capture.py':op['catalog'],'replay_metadata.py':op['catalog']},after_artifacts={'catalog-after.sqlite':op['catalog'],'inventory-after.sqlite':op['inventory']})
 def pin(self,name):self.suite['consumer_hashes'][name]={'git_blob_sha256':'b'*64,'checkout_sha256':{'LF':'b'*64,'CRLF':'c'*64}}
 def test_new_sql_protocol_class_requires_three_explicit_consumers(self):
  self.metadata(self.suite['operations'][0],legacy.M['METADATA_V2_DISPATCHER'])
  with self.assertRaisesRegex(ValueError,'CANONICAL_CONSUMER_SET'):legacy.M['validate'](self.suite)
  for n in legacy.M['METADATA_V2_CONSUMERS']:self.pin(n)
  self.assertIs(legacy.M['validate'](self.suite),self.suite)
 def test_original_v1_negative_and_new_v2_are_distinct_manifest_operations(self):
  self.metadata(self.suite['operations'][0],legacy.M['METADATA_DISPATCHER']);self.suite['operations'][0].update(expected_status='REPLAY_BLOCKED',expected_blocker='TAPE_EVENT_DIFFERS:CLOCK:AUTH_STATE')
  self.metadata(self.suite['operations'][1],legacy.M['METADATA_V2_DISPATCHER'])
  for n in legacy.M['METADATA_V2_CONSUMERS']|{'acceptance/round_thirteen/metadata_revision.py'}:self.pin(n)
  legacy.M['validate'](self.suite)
  self.assertEqual(self.suite['operations'][0]['expected_blocker'],'TAPE_EVENT_DIFFERS:CLOCK:AUTH_STATE');self.assertNotEqual(self.suite['operations'][0]['dispatcher'],self.suite['operations'][1]['dispatcher'])
if __name__=='__main__':unittest.main()

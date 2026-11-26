"""A mismatched descriptive lookup key is not native evidence of absence."""
import unittest
from unittest.mock import Mock
from investigator.investigation_read_tools import ReadTools
from investigator.regression_features import configured

class RecordKeyAlignmentTests(unittest.TestCase):
 def run_trace(self,rows,key='42',**record):
  tools=ReadTools.__new__(ReadTools);tools.queries=Mock()
  tools.queries.run.return_value={'id':'q','status':'SUCCEEDED','result':{'rows':rows},**record}
  args={'key':key,'queries':[{'layer':'native-layer','kind':'sql','query':'SELECT id FROM dbo.Items WHERE id=42','key_field':'id'}]}
  value=tools.record_trace(args)['layers'][0]
  tools.queries.run.assert_called_once_with('native-layer',args['queries'][0]['query'],kind='sql',purpose='record')
  return value
 def test_descriptive_or_other_key_does_not_prove_absence(self):
  for key in ['id=42, group=9','different-key']:
   with self.subTest(key=key):
    v=self.run_trace([{'id':42}],key)
    self.assertEqual(v['presence'],'UNESTABLISHED_KEY_MISMATCH')
    self.assertIn('literal',v['reason']);self.assertFalse(v['duplicate_observed'])
 def test_exact_key_preserves_observed_duplicates(self):
  v=self.run_trace([{'id':42},{'id':42}])
  self.assertEqual(v['presence'],'PRESENT');self.assertEqual(v['matching_rows'],2)
  self.assertTrue(v['duplicate_observed'])
 def test_empty_complete_lookup_can_establish_absence(self):
  self.assertEqual(self.run_trace([])['presence'],'ABSENT')
 def test_truncated_nonmatch_remains_unestablished(self):
  for rows in [[],[{'id':9}]]:
   self.assertEqual(self.run_trace(rows,truncated=True)['presence'],'UNESTABLISHED_IN_TRUNCATED_RESULT')
 def test_failed_read_never_becomes_absence(self):
  self.assertEqual(self.run_trace([],status='FAILED')['presence'],'UNAVAILABLE')
 def test_missing_key_column_is_not_absence(self):
  v=self.run_trace([{'other':42}]);self.assertEqual(v['presence'],'UNAVAILABLE')
  self.assertEqual(v['reason'],'RESULT_MISSING_KEY_COLUMN')
 def test_independent_flag_preserves_prior_behavior(self):
  with configured({'r27_record_key_alignment':False}):
   self.assertEqual(self.run_trace([{'id':42}],'id=42')['presence'],'ABSENT')

if __name__=='__main__':unittest.main()

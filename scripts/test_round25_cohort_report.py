import unittest
from round25_cohort_report import summarize,verdict_class
class CohortReviewTests(unittest.TestCase):
 def test_authored_verdict_groups_preserve_legacy_and_direct_labels(self):
  self.assertEqual(verdict_class({'expected':{'verdict':'source changed history'}}),'source changed history')
  self.assertEqual(verdict_class({'verdict':'waiting on job'}),'waiting on job')
  self.assertEqual(verdict_class({'cause':'not a verdict'}),'ORACLE_VERDICT_UNDECLARED')
 def case(self):
  grade={'verdict_match':True,'layer_match':True,'cause_match':True,'harmful':False,'handoff_quality':0,'failing_step':'none','partial':False,'reason':'a'}
  return {'ticket':'fixture','class':'as designed','primary':grade,'secondary':{**grade,'handoff_quality':2}}
 def test_missing_review_is_pending_and_operator_review_refused(self):
  case=self.case();report=summarize([case],'g2');self.assertFalse(report['raw_review_complete'])
  case['raw_review']={'winner':'primary','grade':case['primary'],'reason':'operator choice','raw_outcome_sha256':'a'*64}
  with self.assertRaisesRegex(ValueError,'OPERATOR_MUST_NOT'):summarize([case],'g2')
 def test_independent_review_does_not_change_official_or_strict(self):
  case=self.case();case['raw_review']={'winner':'neither','grade':{**case['primary'],'cause_match':False},'reason':'native result does not support cause','raw_outcome_sha256':'a'*64,'independent_fresh_call':True,'operator_judgment_supplied':False}
  report=summarize([case],'g4');self.assertEqual(report['official_primary']['all_three']['correct'],1);self.assertEqual(report['strict']['all_three']['correct'],1);self.assertEqual(report['raw_reviewed']['all_three']['correct'],0)

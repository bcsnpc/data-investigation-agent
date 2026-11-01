import unittest
from round25_cohort_report import summarize,verdict_class,load_saved_outcome,established_intake_exception,original_split_scores
class CohortReviewTests(unittest.TestCase):
 def test_original_splits_keep_denominators_and_do_not_change_grades(self):
  from copy import deepcopy
  a=self.case();a['secondary']=dict(a['primary']);a['ticket']='dev-a'
  b=deepcopy(a);b['ticket']='held-b';b['primary']['cause_match']=False;b['secondary']['cause_match']=False
  cases=[a,b];before=deepcopy(cases)
  result=original_split_scores(cases,{'dev':['dev-a','dev-pending'],'heldout':['held-b']})
  self.assertEqual(result['dev']['requested'],2)
  self.assertEqual(result['dev']['official_primary']['all_three']['correct'],1)
  self.assertEqual(result['dev']['official_primary']['all_three']['total'],1)
  self.assertEqual(result['heldout']['official_primary']['all_three']['correct'],0)
  self.assertEqual(cases,before)
  with self.assertRaisesRegex(ValueError,'OVERLAPPING'):original_split_scores(cases,{'dev':['dev-a'],'heldout':['dev-a','held-b']})
  with self.assertRaisesRegex(ValueError,'UNBOUND'):original_split_scores(cases,{'dev':['dev-a']})
 def test_only_exact_established_intake_failures_can_be_classified_automatically(self):
  exit_record={'exit_code':1,'reason':'UNDELIVERED_EXCEPTION','last_step':'guided-investigation'}
  self.assertTrue(established_intake_exception({'error_type':'ValueError','message':'COMPARISON_DETAILS_REQUIRED'},exit_record))
  for failure in ({'error_type':'HTTPError','message':'HTTP404'},{'error_type':'ValueError','message':'READ_ONLY_VIOLATION'},{'error_type':'ProviderHTTPError','message':'429'},{'error_type':'SpendHold','message':'MONTHLY_MODEL_EXHAUSTED'}):
   self.assertFalse(established_intake_exception(failure,exit_record))
  self.assertFalse(established_intake_exception({'error_type':'ValueError','message':'COMPARISON_DETAILS_REQUIRED'},{**exit_record,'exit_code':0}))
 def test_native_exception_preserves_original_bytes_and_unknown_usage(self):
  import tempfile,json
  from pathlib import Path
  with tempfile.TemporaryDirectory()as folder:
   error={'error':{'type':'ValueError','message':'COMPARISON_DETAILS_REQUIRED'},'execution':{'status':'Failed'}}
   p=Path(folder)/'g2-fixture-terminal-error.json';raw=json.dumps(error,indent=2).encode();p.write_bytes(raw)
   source,saved,wrapped=load_saved_outcome(folder,'g2','fixture')
   self.assertEqual((source,saved),(p,raw));self.assertTrue(wrapped['reporting_only_native_exception'])
   self.assertEqual(wrapped['result']['status'],'UNDELIVERED_NATIVE_EXCEPTION')
   self.assertIsNone(wrapped['result']['physical_requests']);self.assertNotIn('charged_microdollars',wrapped['result']['cost'])
   self.assertEqual(wrapped['result']['native_error'],error);self.assertFalse(wrapped['result']['outputs'])
 def test_sealed_result_always_takes_precedence_over_error_metadata(self):
  import tempfile,json
  from pathlib import Path
  with tempfile.TemporaryDirectory()as folder:
   p=Path(folder)/'g2-fixture-result.json';raw=b'{"result":{"status":"ANSWERED"}}';p.write_bytes(raw)
   (Path(folder)/'g2-fixture-terminal-error.json').write_text('{}')
   source,saved,wrapped=load_saved_outcome(folder,'g2','fixture')
   self.assertEqual((source,saved),(p,raw));self.assertNotIn('reporting_only_native_exception',wrapped)
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

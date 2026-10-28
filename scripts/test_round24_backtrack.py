import unittest
from investigator.failure_backtrack import report,sample_ids,markdown
class BacktrackTests(unittest.TestCase):
 def test_corrected_query_error_is_not_automatically_first_wrong_step(self):
  row={'id':'dev','outcome':{'case':{'queries':[{'status':'ERROR','error':'bad name'}]}},'grade':{'verdict_match':True,'layer_match':True,'cause_match':False,'harmful':False,'failing_step':'wrong conclusion','reason':'The conclusion exceeds its evidence.'}}
  out=report([row],pass_id='dev01');self.assertEqual(out['zeros'][0]['first_wrong_step'],'conclusion');self.assertEqual(out['correctness']['layer_match'],1);self.assertEqual(out['score'],0);self.assertFalse(out['scores_or_expectations_changed'])
 def test_sample_is_repeatable_and_final_is_full(self):
  ids=[str(i)for i in range(40)];self.assertEqual(len(sample_ids(ids,'pass')),10);self.assertEqual(sample_ids(ids,'pass'),sample_ids(ids,'pass'));self.assertEqual(len(sample_ids(ids,'pass',final=True)),40)
 def test_walkthrough_renders_saved_steps_without_changing_grade(self):
  grade={'verdict_match':True,'layer_match':False,'cause_match':False,'harmful':False,'failing_step':'target','reason':'Wrong native path.'}
  trace={k:k+' retained'for k in ('intake','target','triage','tool_decisions','queries','final_answer','sealed_expected')};trace['checkpoint_sha256']='a'*64
  row={'id':'dev','outcome':{},'grade':grade,'saved_trace':trace};out=report([row],pass_id='dev01');text=markdown(out)
  for label in trace.values():self.assertIn(label,text)
  self.assertEqual(out['score'],0);self.assertEqual(grade,row['grade']);self.assertEqual(out['estate_reads'],0);self.assertEqual(out['model_calls'],0)
if __name__=='__main__':unittest.main()

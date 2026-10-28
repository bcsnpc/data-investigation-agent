import unittest
from investigator.failure_backtrack import report,sample_ids
class BacktrackTests(unittest.TestCase):
 def test_corrected_query_error_is_not_automatically_first_wrong_step(self):
  row={'id':'dev','outcome':{'case':{'queries':[{'status':'ERROR','error':'bad name'}]}},'grade':{'verdict_match':True,'layer_match':True,'cause_match':False,'harmful':False,'failing_step':'wrong conclusion','reason':'The conclusion exceeds its evidence.'}}
  out=report([row],pass_id='dev01');self.assertEqual(out['zeros'][0]['first_wrong_step'],'conclusion');self.assertEqual(out['correctness']['layer_match'],1);self.assertEqual(out['score'],0);self.assertFalse(out['scores_or_expectations_changed'])
 def test_sample_is_repeatable_and_final_is_full(self):
  ids=[str(i)for i in range(40)];self.assertEqual(len(sample_ids(ids,'pass')),10);self.assertEqual(sample_ids(ids,'pass'),sample_ids(ids,'pass'));self.assertEqual(len(sample_ids(ids,'pass',final=True)),40)
if __name__=='__main__':unittest.main()

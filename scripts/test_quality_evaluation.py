"""Evaluation boundaries: a selected model must be frozen; reads aren't correctness."""
import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from acceptance.unknown_domain.run_ticket import verify_model_settings
from acceptance.unknown_domain.score_run import score
from challenge_freeze import sha


class QualityEvaluationTests(unittest.TestCase):
    def test_unfrozen_or_changed_model_settings_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'model.json';path.write_text('{"deployment":"test"}')
            manifest={'files':{},'policy_files':{str(path.resolve()):sha(path.read_bytes())}}
            verify_model_settings(manifest,path)
            path.write_text('{"deployment":"different"}')
            with self.assertRaises(ValueError):verify_model_settings(manifest,path)
            with self.assertRaises(ValueError):verify_model_settings({'files':{},'policy_files':{}},path)

    def test_successful_read_is_not_graded_as_correct_answer(self):
        result=score({'session':{'observations':[{'status':'COMPLETED','tool':'bounded_sql','test_purpose':'TEST_CONTRIBUTION'},
                                                 {'status':'COMPLETED','tool':'bounded_dax','test_purpose':'REPRODUCE_MEASURE'}],
                              'outcome':{'classification':'LIKELY_TECHNICAL_DEFECT'}}})
        self.assertEqual(result['completed_reads'],2)
        self.assertEqual((result['measure_reproductions'],result['contribution_tests']),(1,1))
        self.assertEqual(result['business_correctness'],'NOT_GRADED')


if __name__=='__main__':unittest.main()

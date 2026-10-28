import json
import unittest
from unittest.mock import patch
from round25_quality import wilson, accuracy_table, score, verify_freeze, audit_failure, restored_job_status


class MeasurementTests(unittest.TestCase):
    def test_wilson_known_intervals_and_empty_sample(self):
        result=wilson(18,20)
        self.assertAlmostEqual(result['lower'], .6989663547715127)
        self.assertAlmostEqual(result['upper'], .9721335187862319)
        self.assertAlmostEqual(wilson(0,20)['upper'], .16112515805281938)
        self.assertEqual(wilson(20,20)['upper'],1)
        self.assertIsNone(wilson(0,0)['accuracy'])
        for args in ((-1,4),(5,4),(1,0),(True,1)):
            with self.assertRaises(ValueError):wilson(*args)

    def test_score_keeps_all_three_and_reports_dimensions_separately(self):
        rows=[dict(verdict_match=True,layer_match=True,cause_match=True,harmful=False),
              dict(verdict_match=True,layer_match=False,cause_match=True,harmful=False)]
        table=accuracy_table(rows)
        self.assertEqual(table['all_three']['correct'],1)
        self.assertEqual(table['verdict_match']['correct'],2)
        self.assertEqual(table['layer_match']['correct'],1)
        self.assertEqual(table['harmful']['correct'],0)
        self.assertIsNotNone(table['harmful']['upper'])
        with self.assertRaises(ValueError):score(dict(rows[0],cause_match=1))

    @patch('round25_quality.subprocess.check_output')
    def test_freeze_uses_git_filtered_identity_and_refuses_changed_engine(self, call):
        receipt={'engine_files':{'scripts/investigator/example.py':{'git_canonical_blob':'abc'}},
                 'commit':'frozen','worker_image':'same-image'}
        call.return_value='abc\n'
        self.assertTrue(verify_freeze(receipt)['runtime_unchanged'])
        self.assertIn('--stdin-paths',call.call_args.args[0])
        call.return_value='different\n'
        with self.assertRaisesRegex(ValueError,'FROZEN_ENGINE_CHANGED'):verify_freeze(receipt)

    def test_failure_audit_keeps_full_answer_and_original_grade(self):
        grade=dict(verdict_match=False,layer_match=True,cause_match=True,harmful=False,reason='Original reason')
        wrapped={'result':{'status':'ANSWERED','business':'Full delivered answer',
                           'outputs':{'technical':'Entire technical text'},'handoff':{'cause':'retained'}}}
        raw=json.dumps(wrapped).encode();audit=audit_failure(wrapped,grade,outcome_bytes=raw)
        self.assertEqual(audit['raw_answer']['business'],'Full delivered answer')
        self.assertEqual(audit['raw_answer']['technical'],'Entire technical text')
        self.assertEqual(audit['original_grade'],grade)
        self.assertIsNone(audit['checker_defect'])
        self.assertFalse(audit['engine_rerun_allowed'])
        self.assertFalse(audit['expectation_change_allowed'])
        self.assertEqual(audit['raw_review_status'],'REVIEW_REQUIRED')
        audit['original_grade']['reason']='New audit note'
        audit['raw_answer']['handoff']['cause']='Audit annotation'
        self.assertEqual(grade['reason'],'Original reason')
        self.assertEqual(wrapped['result']['handoff']['cause'],'retained')

    def test_postscore_fixture_reporting_preserves_native_failure_and_rejects_other_causes(self):
        native={'status':'Failed','failureReason':{'errorCode':'2011','message':"There is already an object named 'bronze' in the database. CREATE SCHEMA failed due to previous errors."}}
        before=json.dumps(native,sort_keys=True)
        self.assertEqual(restored_job_status('failed-billing',native),'ORIGINAL_EXISTING_BILLING_BOOTSTRAP_FAILED_2011')
        self.assertEqual(json.dumps(native,sort_keys=True),before)
        self.assertEqual(restored_job_status('failed-fixture',{'status':'Completed'}),'ORIGINAL_JOB_COMPLETED')
        with self.assertRaises(ValueError):restored_job_status('failed-fixture',native)
        native['failureReason']['message']='An unrelated SQL permission failure'
        with self.assertRaises(ValueError):restored_job_status('failed-billing',native)


if __name__=='__main__':unittest.main()

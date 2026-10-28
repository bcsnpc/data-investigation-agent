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


class CohortTests(unittest.TestCase):
    def test_raw_review_requires_evidence_and_keeps_official_score(self):
        from round25_quality import three_scores
        good=dict(verdict_match=True,layer_match=True,cause_match=True,harmful=False,handoff_quality=2)
        bad=dict(good,cause_match=False,harmful=True,handoff_quality=1)
        case={'ticket':'disputed','primary':good,'secondary':bad}
        value=three_scores([case])
        self.assertEqual(value['strict']['all_three']['correct'],0)
        self.assertEqual(value['raw_review_pending'],['disputed'])
        self.assertEqual(value['raw_reviewed']['all_three']['total'],0)
        case['raw_review']={'winner':'secondary','grade':bad,'raw_outcome_sha256':'a'*64,'reason':'Saved queries omit history.'}
        value=three_scores([case])
        self.assertTrue(value['raw_review_complete'])
        self.assertEqual(value['official_primary']['all_three']['correct'],1)
        self.assertEqual(value['raw_reviewed']['all_three']['correct'],0)
        self.assertEqual(value['raw_reviewed']['harmful']['correct'],1)
        self.assertEqual(case['primary'],good)
        self.assertEqual(case['secondary'],bad)
        case['raw_review']['grade']=good
        with self.assertRaises(ValueError):three_scores([case])
        case['raw_review']['winner']='primary'
        value=three_scores([case])
        self.assertEqual(value['strict']['all_three']['correct'],0)
        self.assertEqual(value['raw_reviewed']['all_three']['correct'],1)
        self.assertEqual(value['official_primary']['all_three']['correct'],1)

    def test_partial_cohorts_and_disagreements_stay_explicit(self):
        from round25_quality import cohort_metrics
        good=dict(verdict_match=True,layer_match=True,cause_match=True,harmful=False,reason='native facts')
        bad=dict(good,cause_match=False,reason='cause not established')
        cases=[{'ticket':'one','class':'defined','primary':good,'secondary':bad}]
        value=cohort_metrics(cases)
        self.assertEqual(value['completed_graded'],1)
        self.assertEqual(value['primary']['all_three']['correct'],1)
        self.assertEqual(value['secondary']['all_three']['correct'],0)
        self.assertEqual(value['agreement']['correct'],0)
        self.assertEqual(value['disagreements'],cases)
        self.assertEqual(value['per_class']['defined']['primary']['all_three']['total'],1)
        self.assertIsNone(cohort_metrics([])['primary']['all_three']['accuracy'])

class NativeProbeRouteTests(unittest.TestCase):
    def test_a_probe_uses_only_its_existing_estate_route(self):
        from round25_quality import require_existing_probe_route
        route={'server':'reader-endpoint','database':'billing','objects':['[gold].[invoices]'],'read_only':True}
        base={'environment':{'DIA_PLATFORM_GATEWAY_POLICY':json.dumps({'identities':{'investigation':{'sql':[route]}}})}}
        before=json.dumps(base,sort_keys=True);config={'fabric':{'sql_reader':{'server':'reader-endpoint'}}}
        self.assertTrue(require_existing_probe_route(base,config,'billing',['[gold].[invoices]']))
        self.assertEqual(json.dumps(base,sort_keys=True),before)
        with self.assertRaises(ValueError):require_existing_probe_route(base,config,'fixture',['[gold].[invoices]'])
        with self.assertRaises(ValueError):require_existing_probe_route(base,config,'billing',['[gold].[other]'])
        route['read_only']=False;base['environment']['DIA_PLATFORM_GATEWAY_POLICY']=json.dumps({'identities':{'investigation':{'sql':[route]}}})
        with self.assertRaises(ValueError):require_existing_probe_route(base,config,'billing',['[gold].[invoices]'])

class FactReferenceTests(unittest.TestCase):
    def test_root_and_descendant_container_labels_resolve_only_to_supplied_facts(self):
        from round25_quality import fact_reference_known
        facts={'target_bindings':{'reports':{'report-one':{'binding':'model-one'}}},'baseline':{'value':16}}
        before=json.dumps(facts,sort_keys=True)
        self.assertTrue(fact_reference_known('target_bindings.reports',facts))
        self.assertTrue(fact_reference_known('reports',facts))
        self.assertTrue(fact_reference_known('native_facts.baseline',facts))
        self.assertFalse(fact_reference_known('invented_namespace',facts))
        self.assertFalse(fact_reference_known('binding.model-two',facts))
        self.assertEqual(json.dumps(facts,sort_keys=True),before)

class ReplacementTests(unittest.TestCase):
    def test_only_undelivered_plumbing_can_be_replaced_once(self):
        from round25_quality import plumbing_replacement_label
        self.assertEqual(plumbing_replacement_label(error_type='LockNotAvailable',delivered=False,replacements_used=0),'-replacement01')
        for options in ({'error_type':'LockNotAvailable','delivered':True,'replacements_used':0},
                        {'error_type':'OperationalError','delivered':False,'replacements_used':0},
                        {'error_type':'WRONG_VERDICT','delivered':False,'replacements_used':0},
                        {'error_type':'CAPTURE_LOSS','delivered':False,'replacements_used':1}):
            with self.assertRaises(ValueError):plumbing_replacement_label(**options)

class WaveTests(unittest.TestCase):
    def test_no_concurrent_wave_can_consume_restore_headroom(self):
        from round25_quality import static_wave_width
        self.assertEqual(static_wave_width(59),0)
        self.assertEqual(static_wave_width(60),1)
        self.assertEqual(static_wave_width(100),2)
        self.assertEqual(static_wave_width(140),3)
        # A restored, read-only static wave needs no additional mutation cushion.
        self.assertEqual(static_wave_width(39,restore_headroom=0),0)
        self.assertEqual(static_wave_width(40,restore_headroom=0),1)
        self.assertEqual(static_wave_width(80,restore_headroom=0),2)
        for available in range(200):
            width=static_wave_width(available)
            if width:self.assertLessEqual(width*40+20,available)
        with self.assertRaises(ValueError):static_wave_width(-1)

if __name__=='__main__':unittest.main()

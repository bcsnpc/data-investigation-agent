"""A returned investigation is not proof that the earned smoke outcome held."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from investigator.daily_smoke import run_smoke
from investigator.daily_smoke import ledger_demo_matches


class SmokeDemoExpectationTests(unittest.TestCase):
    def test_next_month_reminder_needs_actual_read_and_keeps_original_table(self):
        import copy
        from investigator.daily_smoke import monthly_budget_advisory
        access={'status':'INCOMPLETE','rows':[
            {'id':'reader','status':'PASS'},
            {'id':'next-month-budget','status':'NOT_TESTABLE','warning':True,'resource':'2026-11'}]}
        before=copy.deepcopy(access)
        state=Mock();state.snapshot.return_value={'identity':'model-microdollars:2026-11','unit':'MICRODOLLARS'}
        result=monthly_budget_advisory(access,state)
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['result'],before);self.assertEqual(access,before)
        state.snapshot.assert_called_once_with('model-microdollars:2026-11')
        self.assertFalse(result['resolved_advisories'][0]['account_created'])
        state.put.assert_not_called();state.reserve.assert_not_called()

    def test_missing_or_wrong_month_account_cannot_resolve_reminder(self):
        from investigator.daily_smoke import monthly_budget_advisory
        access={'status':'INCOMPLETE','rows':[
            {'id':'next-month-budget','status':'NOT_TESTABLE','warning':True,'resource':'2026-11'}]}
        for observed in ({'identity':'model-microdollars:2026-10','unit':'MICRODOLLARS'},
                         {'identity':'model-microdollars:2026-11','unit':'REQUESTS'}):
            state=Mock();state.snapshot.return_value=observed
            self.assertEqual(monthly_budget_advisory(access,state)['status'],'INCOMPLETE')
        state=Mock();state.snapshot.side_effect=KeyError('missing')
        self.assertEqual(monthly_budget_advisory(access,state)['status'],'INCOMPLETE')

    def test_other_failed_or_untestable_probes_are_never_hidden(self):
        from investigator.daily_smoke import monthly_budget_advisory
        for status in ('FAIL','NOT_TESTABLE'):
            access={'status':'INCOMPLETE','rows':[
                {'id':'reader','status':status},
                {'id':'next-month-budget','status':'NOT_TESTABLE','warning':True,'resource':'2026-11'}]}
            state=Mock()
            self.assertEqual(monthly_budget_advisory(access,state)['status'],'INCOMPLETE')
            state.snapshot.assert_not_called()

    def smoke(self, classification, *, expected='TRANSFORMATION_LOGIC', state='FINDINGS_SHARED'):
        config = dict(version=1, run_id='synthetic', reader_authentication={},
                      gold_payload={'authentication': {}}, platform_blob={}, demo_earned=True)
        if expected is not None:
            config['demo_expected_classification'] = expected
        result = {'demo': {'ticket': {'state': state, 'findings': {
            'classification': classification, 'warnings': ['SNAPSHOT_UNVERIFIED']}}}}
        context = SimpleNamespace(step=lambda name, fn: fn())
        storage = Mock()
        storage.get.return_value = {'revision': 1, 'body': {
            'kind': 'DAILY_SMOKE', 'run_id': 'synthetic',
            'challenge': __import__('hashlib').sha256(b'synthetic').hexdigest()}}
        with patch('investigator.daily_smoke.validate_gold_payload'), patch(
                'investigator.access_check.configured', return_value={'status': 'PASS'}):
            return run_smoke(config, context, state=storage, sign_in=lambda: {},
                             gold_read=lambda _: {}, blob_roundtrip=lambda *_: {}, demo=lambda: result)

    def test_retained_no_comparable_path_cannot_pass_the_earned_demo(self):
        result = self.smoke('NO_COMPARABLE_PATH')
        self.assertEqual(result['status'], 'FAIL')
        check = result['checks']['family_a_demo']
        self.assertEqual(check['reason'], 'SMOKE_DEMO_EXPECTATION_NOT_MET')
        self.assertEqual(check['result']['demo']['ticket']['findings']['classification'], 'NO_COMPARABLE_PATH')

    def test_correct_delivered_outcome_with_warning_still_passes(self):
        self.assertEqual(self.smoke('TRANSFORMATION_LOGIC')['status'], 'PASS')

    def test_missing_expectation_or_undelivered_outcome_cannot_pass(self):
        self.assertEqual(self.smoke('TRANSFORMATION_LOGIC', expected=None)['status'], 'FAIL')
        self.assertEqual(self.smoke('TRANSFORMATION_LOGIC', state='HELD')['status'], 'FAIL')
        self.assertEqual(self.smoke(None)['status'], 'FAIL')

    def test_new_engine_must_keep_earned_native_finding_boundary_and_both_values(self):
        import copy
        expected={'verdict':'as designed','native_classification':'TRANSFORMATION_LOGIC',
            'boundary':{'downstream':'gold','upstream':'silver'},'values':{'gold':'8765','silver':'7661'}}
        bundle={'verdict':'as designed','outputs':{'business':'implemented join','technical':'bounded evidence'},'evidence':{
            'g':{'kind':'READ','value':{'subject':'gold','state':'VALUE','value':'8765','read_only_verified':True,'route_admitted':True}},
            's':{'kind':'READ','value':{'subject':'silver','state':'VALUE','value':'7661','read_only_verified':True,'route_admitted':True}},
            'definition':{'kind':'DESIGN_CHECK','subjects':['gold','silver'],'value':{'checked':True,'business_correctness_claim':False,'native_assessment':{'classification':'TRANSFORMATION_LOGIC'}}}}}
        self.assertTrue(ledger_demo_matches(bundle,expected))
        for mutate in (lambda b:b['evidence'].pop('definition'),lambda b:b['evidence']['s']['value'].update(value='8765'),
            lambda b:b.update(status='blocked'),lambda b:b['evidence']['definition']['value']['native_assessment'].update(classification='NO_COMPARABLE_PATH')):
            wrong=copy.deepcopy(bundle);mutate(wrong);self.assertFalse(ledger_demo_matches(wrong,expected))


if __name__ == '__main__': unittest.main()

"""A returned investigation is not proof that the earned smoke outcome held."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from investigator.daily_smoke import run_smoke


class SmokeDemoExpectationTests(unittest.TestCase):
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


if __name__ == '__main__': unittest.main()

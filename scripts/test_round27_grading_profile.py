import unittest
from investigator.adapters.evaluation_anthropic import request_for


class Round27GradingTests(unittest.TestCase):
    def test_profile_changes_rubric_not_sealed_record(self):
        expected={'verdict':'as designed','cause':'Retained sum rule.'}
        task={'protocol':'scored-evaluation-v1','purpose':'GRADE_GUIDED_ANSWER','case_id':'dev-only',
              'expected':{'grading_profile':'round27','sealed_expected_record':expected},'delivered':{}}
        system=request_for(task,'0'*64)['params']['system']
        self.assertIn('bare clarification',system)
        self.assertIn('useful handoff',system)
        self.assertIn('true incidental layer difference',system)
        self.assertIn('do not defer to its',system)
        self.assertEqual(task['expected']['sealed_expected_record'],expected)

    def test_historical_profiles_are_unchanged(self):
        task={'protocol':'scored-evaluation-v1','purpose':'GRADE_GUIDED_ANSWER','case_id':'old',
              'expected':{},'delivered':{}}
        self.assertNotIn('Round27 grading profile',request_for(task,'0'*64)['params']['system'])


if __name__=='__main__':unittest.main()

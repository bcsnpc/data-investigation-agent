import unittest
from copy import deepcopy

from investigator.free_dev_grading import disposition, gradeable_result, metrics


class FreeDevGradingTests(unittest.TestCase):
    def test_physical_cap_interruption_is_a_scored_failure(self):
        value = {'result': {'status': 'INTERRUPTED',
                            'stop': 'UsageHold: GUIDED_PHYSICAL_CAP_REACHED'}}
        self.assertTrue(gradeable_result(value))
        self.assertEqual(disposition(value), 'SCORED_BUDGET_STOP')

    def test_engine_crash_is_not_mislabelled_environmental(self):
        value = {'status': 'INTERRUPTED', 'stop': 'KeyError: model_calls'}
        self.assertTrue(gradeable_result(value))
        self.assertEqual(disposition(value), 'SCORED_ENGINE_INTERRUPTION')

    def test_proven_provider_unavailability_is_unscored(self):
        for stop in (
            'ProviderUnavailable: NVIDIA_TRANSPORT_UNAVAILABLE_ENVIRONMENT_AFFECTED',
            'ProviderUnavailable: NVIDIA_ASYNC_RESULT_PENDING_ENVIRONMENT_AFFECTED',
        ):
            with self.subTest(stop=stop):
                self.assertFalse(gradeable_result({'status': 'INTERRUPTED', 'stop': stop}))

    def test_normal_incomplete_answers_stay_in_the_score(self):
        for status in ('ANSWERED', 'UNRESOLVED', 'NEEDS_INPUT', 'BLOCKED'):
            with self.subTest(status=status):
                self.assertTrue(gradeable_result({'status': status}))

    def test_environment_word_alone_does_not_exclude_a_failure(self):
        self.assertTrue(gradeable_result({'status': 'INTERRUPTED',
                                         'stop': 'ValueError: invalid environment field'}))

    def test_explicit_unestablished_and_environment_statuses(self):
        for status in ('UNESTABLISHED', 'ENVIRONMENT_AFFECTED'):
            self.assertFalse(gradeable_result({'status': status}))

    def test_partial_metrics_are_unknown_not_zero(self):
        value = {'result': {'status': 'INTERRUPTED', 'physical_requests': 40,
                            'cost': {'charged_microdollars': 0},
                            'timing': {'wall_seconds': 218.17}}}
        before = deepcopy(value)
        actual = metrics(value)
        self.assertEqual(actual['physical_requests'], 40)
        self.assertEqual(actual['investigator_cost_usd'], 0)
        self.assertEqual(actual['engine_wall_seconds'], 218.17)
        for key in ('model_calls', 'model_seconds', 'native_query_seconds'):
            self.assertIsNone(actual[key])
        self.assertEqual(value, before)

    def test_complete_metrics_and_bad_optional_values(self):
        actual = metrics({'physical_requests': 0, 'model_calls': 3,
                          'cost': {'charged_microdollars': 125000},
                          'timing': {'wall_seconds': 2, 'model_seconds': 1,
                                     'native_query_sum_seconds': .5}})
        self.assertEqual(actual, {'physical_requests': 0, 'model_calls': 3,
                                 'investigator_cost_usd': .125, 'engine_wall_seconds': 2,
                                 'model_seconds': 1, 'native_query_seconds': .5})
        for value in (True, -1, float('inf'), float('nan'), 'unknown', 10 ** 1000):
            self.assertIsNone(metrics({'model_calls': value})['model_calls'])
        self.assertIsNone(metrics({'cost': True})['investigator_cost_usd'])
        self.assertIsNone(metrics({'timing': ['unknown']})['engine_wall_seconds'])


if __name__ == '__main__':
    unittest.main()

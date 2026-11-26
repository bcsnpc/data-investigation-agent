"""Sequential native checks must not erase a failure read in the same refresh."""
import unittest
from copy import deepcopy
from unittest.mock import Mock
from investigator.guided_live_facts import PathFacts
from investigator.regression_features import configured


class RefreshObservationTests(unittest.TestCase):
    def refreshed(self, seconds=35):
        current = ['2026-11-23T14:00:00Z']
        facts = []
        ledger = Mock()
        ledger.read.side_effect = lambda *a, **kw: {'facts': deepcopy(facts)}
        def fact(subject, at, status):
            return {'subject': subject, 'kind': 'JOB_RUN', 'state': 'OBSERVED',
                    'freshness': 'CURRENT', 'collected_at': at,
                    'value': {'run_id': subject + '-run', 'status': status}}
        def collect(*args, **kwargs):
            facts.extend([fact('failed', '2026-11-23T14:00:00Z', 'FAILED'),
                          fact('probe', '2026-11-23T14:00:34Z', 'SUCCEEDED'),
                          fact('old', '2026-11-23T13:59:59Z', 'FAILED'),
                          fact('future', '2026-11-23T15:00:00Z', 'FAILED')])
            from datetime import datetime, timedelta, timezone
            current[0] = (datetime(2026, 11, 23, 14, tzinfo=timezone.utc)
                          + timedelta(seconds=seconds)).isoformat()
            return {'status': 'PATH_NATIVE_HISTORY_CHECKED'}
        port = PathFacts(ledger=ledger, estate='synthetic',
                         path={'nodes': [{'id': x, 'kind': 'PIPELINE'}
                                         for x in ('failed', 'probe', 'old', 'future')]},
                         collector=collect, now=lambda: current[0])
        return port

    def test_failed_first_subject_and_successful_second_subject_both_retained(self):
        port = self.refreshed()
        result = port.refresh('JOB_RUNS', [])
        self.assertEqual({f['subject'] for f in result['value']}, {'failed', 'probe'})
        self.assertEqual(result['observed_at'], '2026-11-23T14:00:00Z')
        self.assertEqual(result['value'][0]['value']['status'], 'FAILED')
        self.assertEqual(result['value'][0]['collected_at'], '2026-11-23T14:00:00Z')

    def test_unrelated_checks_can_refresh_once_without_erasing_first_job(self):
        port = self.refreshed()
        with self.assertRaisesRegex(ValueError, 'FRESH_PATH_FACT_NOT_AVAILABLE'):
            port.refresh('MODEL_REFRESH', [])
        result = port.lookup('JOB_RUNS', [])
        self.assertEqual(len(result['value']), 2)

    def test_flag_reproduces_loss_of_first_observation(self):
        self.assertEqual([f['subject'] for f in result['value']], ['probe'])

    def test_old_collection_is_not_relabelled_current(self):
        port = self.refreshed(seconds=1000)
        with self.assertRaisesRegex(ValueError, 'FRESH_PATH_FACT_NOT_AVAILABLE'):
            port.refresh('JOB_RUNS', [])


if __name__ == '__main__':
    unittest.main()

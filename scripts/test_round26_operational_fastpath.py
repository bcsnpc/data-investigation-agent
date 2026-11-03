from unittest.mock import Mock
import unittest
from investigator.operational_intake import admit
from investigator.operational_fastpath import run


class OperationalFastpathTests(unittest.TestCase):
    def admission(self):
        return admit({'text': 'Did Daily Billing Load fail? It affects 950 versus 900.'},
                     {'candidates': [{'id': 'job', 'kind': 'PIPELINE', 'label': 'Daily Billing Load'}]})

    def history(self, state):
        return {'facts': [{'subject': 'job', 'kind': 'JOB_RUN', 'state': 'OBSERVED', 'observed_at': '2026-11-01T01:00:00Z',
                'value': {'status': state, 'run_id': 'run-1', 'start': '2026-11-01T00:00:00Z',
                          'end': None, 'error': 'synthetic failure' if state == 'FAILED' else None}}]}

    def test_named_job_with_numbers_does_not_require_report(self):
        admission = self.admission()
        self.assertEqual(admission['status'], 'READY')
        history = Mock(return_value=self.history('FAILED'))
        answer = run(admission, history, record=Mock())
        self.assertEqual(answer['technical']['verdict'], 'failed job')
        self.assertIn('Daily Billing Load', answer['business'])
        self.assertIn('run-1', answer['business'])
        self.assertEqual(answer['model_calls'], 0)

    def test_waiting_is_rechecked_at_answer_time(self):
        history = Mock(side_effect=[self.history('RUNNING'), self.history('COMPLETED')])
        answer = run(self.admission(), history, record=Mock())
        self.assertEqual(history.call_count, 2)
        self.assertFalse(answer['technical']['waiting_fixture_still_active'])
        self.assertEqual(answer['technical']['answer_status'], 'COMPLETED')

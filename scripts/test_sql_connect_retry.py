import subprocess
import unittest
from unittest.mock import Mock
from sql_connect_retry import read_with_retry
from cross_layer_investigation import metric_observation


FAILURE = dict(error='SQL_READ_FAILED', stage='connect', sql_error_number=40613)
SUCCESS = dict(values={'order_count': '100000'}, query='fixed query', captured_at='now')


class RetryTests(unittest.TestCase):
    def test_resume_recovery_and_evidence(self):
        read = Mock(side_effect=[FAILURE, FAILURE, SUCCESS])
        sleep = Mock()
        result = read_with_retry(read, sleep)
        self.assertEqual(result['values'], SUCCESS['values'])
        self.assertEqual([a['status'] for a in result['connection_attempts']], ['FAILED','FAILED','SUCCEEDED'])
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [10,20])
        observation = metric_observation('sql', 'order_count', result, 'USD', None, 'sql')
        self.assertEqual(observation['connection_attempts'], result['connection_attempts'])
        self.assertIsNone(observation['source_snapshot'])

    def test_exhaustion_stays_unavailable(self):
        read = Mock(return_value=FAILURE)
        result = read_with_retry(read, Mock())
        self.assertEqual(read.call_count, 3)
        self.assertEqual(result['connection_attempts'][-1]['retry_delay_seconds'], 0)
        observation = metric_observation('sql','order_count',result,'USD',None,'sql')
        self.assertEqual(observation['status'], 'UNAVAILABLE')
        self.assertEqual(len(observation['connection_attempts']), 3)

    def test_auth_query_and_other_errors_are_not_retried(self):
        for failure in [dict(FAILURE, sql_error_number=18456), dict(FAILURE, stage='query'),
                        dict(FAILURE, sql_error_number=40615), dict(FAILURE, sql_error_number=None)]:
            read = Mock(return_value=failure); sleep = Mock()
            read_with_retry(read, sleep)
            self.assertEqual(read.call_count, 1)
            sleep.assert_not_called()

    def test_timeout_or_invalid_response_not_retried(self):
        for error in [subprocess.TimeoutExpired('hidden', 150), ValueError('private text')]:
            read = Mock(side_effect=error)
            result = read_with_retry(read, Mock())
            self.assertEqual(read.call_count, 1)
            self.assertNotIn('private', str(result))
            self.assertEqual(result['connection_attempts'][0]['status'], 'FAILED')

    def test_first_success_does_not_sleep(self):
        sleep = Mock()
        result = read_with_retry(Mock(return_value=SUCCESS), sleep)
        self.assertEqual(len(result['connection_attempts']), 1)
        sleep.assert_not_called()


if __name__ == '__main__': unittest.main()

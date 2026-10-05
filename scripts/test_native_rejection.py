"""A service rejection is deterministic; only genuinely uncertain completion is uncertain."""
import io
import json
import subprocess
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import run_native_diagnostic as native
from investigator import flexible_tools


def http_error(code, body=b'{"error":{"code":"DatasetExecuteQueriesError","message":"query text 12345"}}'):
    return HTTPError('https://example.invalid', code, 'x', {}, io.BytesIO(body))


class WorkerClassificationTests(unittest.TestCase):
    def test_client_rejection_is_not_uncertain(self):
        failure = native.worker_failure(http_error(400))
        self.assertEqual(failure, {'error': 'HTTPError', 'http_status': 400,
                                   'service_error_code': 'DatasetExecuteQueriesError', 'completion_uncertain': False})

    def test_rejection_never_carries_the_response_body(self):
        self.assertNotIn('12345', json.dumps(native.worker_failure(http_error(400))))

    def test_server_error_stays_uncertain(self):
        for code in (500, 502, 503, 504):
            self.assertTrue(native.worker_failure(http_error(code))['completion_uncertain'], code)

    def test_transport_failure_and_timeout_stay_uncertain(self):
        self.assertTrue(native.worker_failure(URLError('reset'))['completion_uncertain'])
        self.assertTrue(native.worker_failure(TimeoutError())['completion_uncertain'])

    def test_other_errors_are_not_uncertain(self):
        self.assertFalse(native.worker_failure(ValueError('bad'))['completion_uncertain'])

    def test_unparseable_or_hostile_error_code_is_dropped(self):
        for body in (b'not json', b'{"error":{"code":"a b; drop"}}', b'{"error":"x"}'):
            self.assertNotIn('service_error_code', native.worker_failure(http_error(400, body)))


class TransportTests(unittest.TestCase):
    from test_reader_execution import config as reader_config, WORKSPACE, MODEL
    CONFIG = reader_config()
    CONFIG['fabric'].pop('native_reader')
    REQUEST = {'workspace': WORKSPACE, 'native_model_id': MODEL}

    def run_with(self, failure):
        completed = subprocess.CompletedProcess([], 1, json.dumps(failure), '')
        with patch('run_native_diagnostic.subprocess.run', return_value=completed):
            native.transport(self.CONFIG, self.REQUEST)

    def test_rejection_raises_a_deterministic_error_not_a_timeout(self):
        with self.assertRaises(native.NativeRejected) as caught:
            self.run_with({'error': 'HTTPError', 'http_status': 400, 'service_error_code': 'X',
                           'completion_uncertain': False})
        self.assertNotIsInstance(caught.exception, TimeoutError)
        self.assertEqual((caught.exception.http_status, caught.exception.service_error_code), (400, 'X'))

    def test_uncertain_failure_is_still_a_timeout(self):
        with self.assertRaises(TimeoutError):
            self.run_with({'error': 'HTTPError', 'http_status': 503, 'completion_uncertain': True})


class ReceiptTests(unittest.TestCase):
    def test_rejection_is_failed_not_interrupted_and_records_status(self):
        request = {'tool': 'bounded_dax'}
        with patch.object(flexible_tools, 'build', return_value=request), \
             patch('investigator.flexible_tools.require'):
            import sqlite3, tempfile, os
            folder = tempfile.mkdtemp(); path = os.path.join(folder, 'receipts.sqlite')
            class Store:
                def connect(self):
                    return sqlite3.connect(path)
            with patch('investigator.receipt_integrity.seal'):
                result = flexible_tools.run(Store(), {'model_id': 'm'}, {'fabric': {'native_reader': {}}}, 'bounded_dax',
                                            lambda request: (_ for _ in ()).throw(native.NativeRejected(400, 'X')))
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(result['result']['error_type'], 'NativeRejected')
        self.assertEqual((result['result']['http_status'], result['result']['service_error_code']), (400, 'X'))


if __name__ == '__main__':
    unittest.main()

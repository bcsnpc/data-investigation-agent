import subprocess
import unittest
from unittest.mock import MagicMock, patch

from run_source_diagnostic import transport, SourceReadError, SourceReadTimeout
from sql_connect_retry import read_with_retry
from investigator.source_diagnostics import run
import test_source_diagnostics as source_fixture


class RuntimeTransportTests(unittest.TestCase):
    def setUp(self):
        self.sleep=MagicMock()
        patcher=patch('run_source_diagnostic.read_with_retry',side_effect=lambda read:read_with_retry(read,self.sleep))
        patcher.start();self.addCleanup(patcher.stop)
        self.success={'value':'5','row_count':'5','nonblank_count':'5'}

    def test_only_connect_40613_retries_and_keeps_attempts(self):
        failure={'error':'SQL_READ_FAILED','stage':'connect','sql_error_number':40613}
        with patch('run_source_diagnostic.read_once',side_effect=[failure,self.success]) as call:
            result=transport({}, {})
        self.assertEqual(call.call_count,2);self.sleep.assert_called_once_with(10)
        self.assertEqual([a['status'] for a in result['connection_attempts']],['FAILED','SUCCEEDED'])

    def test_query_error_and_login_failure_never_repeat_read(self):
        for stage,number in [('query',40613),('connect',18456),('connect',40615),('unknown',40613)]:
            with self.subTest(stage=stage,number=number):
                with patch('run_source_diagnostic.read_once',return_value={'error':'SQL_READ_FAILED','stage':stage,'sql_error_number':number}) as call:
                    with self.assertRaises(SourceReadError):transport({}, {})
                call.assert_called_once()
        self.sleep.assert_not_called()

    def test_worker_timeout_is_uncertain_and_not_retried(self):
        with patch('run_source_diagnostic.read_once',side_effect=subprocess.TimeoutExpired('worker',90)) as call:
            with self.assertRaises(SourceReadTimeout):transport({}, {})
        call.assert_called_once();self.sleep.assert_not_called()

    def test_connection_exhaustion_has_three_attempts(self):
        with patch('run_source_diagnostic.read_once',return_value={'error':'SQL_READ_FAILED','stage':'connect','sql_error_number':40613}) as call:
            with self.assertRaises(SourceReadError) as captured:transport({}, {})
        self.assertEqual(call.call_count,3);self.assertEqual(len(captured.exception.connection_attempts),3)
        self.assertEqual([c.args[0] for c in self.sleep.call_args_list],[10,20])

    def test_successful_attempt_metadata_is_persisted_with_source_observation(self):
        helper=source_fixture.SourceTests();helper.setUp();self.addCleanup(helper.doCleanups)
        with patch('run_source_diagnostic.read_once',return_value=self.success):
            result=run(helper.store,helper.plan,helper.config,lambda req:transport(helper.config,req))
        self.assertEqual(result['status'],'COMPLETED')
        self.assertEqual(result['result']['connection_attempts'][0]['status'],'SUCCEEDED')

    def test_untrusted_attempt_text_is_not_persisted(self):
        helper=source_fixture.SourceTests();helper.setUp();self.addCleanup(helper.doCleanups)
        result=run(helper.store,helper.plan,helper.config,lambda req:dict(self.success,connection_attempts=[{'error_message':'secret'}]))
        self.assertEqual(result['status'],'FAILED');self.assertNotIn('secret',str(result))


if __name__=='__main__':unittest.main()

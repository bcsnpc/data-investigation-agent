import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from unittest.mock import patch
import tempfile
from pathlib import Path

from investigator.disk_hygiene import require_laptop_headroom


class DiskHygieneTests(unittest.TestCase):
    def test_local_cli_checks_before_loading_estate_or_starting_docker(self):
        from investigator.unified_runner import main
        with patch('investigator.disk_hygiene.require_laptop_headroom',
                   side_effect=ValueError('LAPTOP_DISK_HEADROOM_LOW:D:/')):
            with self.assertRaisesRegex(ValueError, 'HEADROOM_LOW'):
                main(SimpleNamespace(runtime='local'))

    def test_direct_launch_blocks_before_any_azure_request(self):
        from investigator.adapters.runner_deployment import launch
        execute = Mock()
        with patch('investigator.disk_hygiene.require_laptop_headroom',
                   side_effect=ValueError('LAPTOP_DISK_HEADROOM_LOW:D:/')):
            with self.assertRaisesRegex(ValueError, 'HEADROOM_LOW'):
                launch({}, 'ticket', execute=execute)
        execute.assert_not_called()

    def test_harness_blocks_new_submission_but_can_recover_existing_outcome(self):
        from investigator.investigator_harness import CaseLog, RunHarness
        with tempfile.TemporaryDirectory() as folder:
            ticket = {'target': 'example'}
            user, admit = Mock(), Mock()
            log = CaseLog(Path(folder)/'case.jsonl')
            with patch('investigator.disk_hygiene.require_laptop_headroom',
                       side_effect=ValueError('LAPTOP_DISK_HEADROOM_LOW:C:/')):
                with self.assertRaisesRegex(ValueError, 'HEADROOM_LOW'):
                    RunHarness(user, log, admit=admit).run(ticket)
                admit.assert_not_called()
                user.submit.assert_not_called()
                # A saved outcome must remain recoverable even when the disk is low.
                log.append('OUTCOME', {'result': {'saved': True}})
                self.assertEqual(RunHarness(user, log, admit=admit).run(ticket), {'saved': True})

    def test_both_windows_drives_must_pass_at_exact_decimal_thresholds(self):
        usage = Mock(side_effect=[SimpleNamespace(free=40_000_000_000),
                                  SimpleNamespace(free=80_000_000_000)])
        result = require_laptop_headroom(platform='nt', disk_usage=usage)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual([call.args[0] for call in usage.call_args_list], ['C:/', 'D:/'])

    def test_either_drive_below_floor_blocks(self):
        for values in ((39_999_999_999, 100_000_000_000),
                       (60_000_000_000, 79_999_999_999)):
            with self.subTest(values=values), self.assertRaisesRegex(ValueError, 'HEADROOM_LOW'):
                require_laptop_headroom(platform='nt', disk_usage=Mock(
                    side_effect=[SimpleNamespace(free=x) for x in values]))

    def test_missing_drive_is_not_a_pass(self):
        with self.assertRaisesRegex(ValueError, 'HEADROOM_UNESTABLISHED'):
            require_laptop_headroom(platform='nt', disk_usage=Mock(side_effect=OSError()))

    def test_linux_does_not_probe_windows_drives(self):
        usage = Mock(side_effect=AssertionError('must not probe'))
        self.assertEqual(require_laptop_headroom(platform='posix', disk_usage=usage)['status'],
                         'NOT_APPLICABLE')
        usage.assert_not_called()

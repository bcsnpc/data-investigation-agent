import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
from investigator.worker_launch import options
from investigator import tape_worker


class WorkerLaunchTests(unittest.TestCase):
    def test_tape_git_integrity_and_revision_checks_share_no_console_policy(self):
        from investigator.process_tape import Tape, TapeError
        bootstrap = {'entry_point': 'workspace', 'context_identity': 'synthetic-context',
                     'config': {}, 'profile': {}, 'usage_policy': {},
                     'engine_hash': 'synthetic-engine', 'state': {}}
        revision = 'a' * 40
        with tempfile.TemporaryDirectory() as folder, \
                patch('investigator.worker_launch.options',
                      side_effect=lambda kw: {**kw, 'creationflags': 123}) as policy, \
                patch('subprocess.check_output', side_effect=['', revision]) as check:
            tape = Tape(Path(folder) / 'clean.json', bootstrap)
            self.assertEqual(tape.engine_revision, revision)
            self.assertEqual(policy.call_count, 1)
            self.assertEqual(check.call_count, 2)
            for call in check.call_args_list:
                self.assertEqual(call.kwargs['creationflags'], 123)
            self.assertEqual(check.call_args_list[0].args[0][:2], ['git', 'status'])
            self.assertEqual(check.call_args_list[1].args[0], ['git', 'rev-parse', 'HEAD'])
        with tempfile.TemporaryDirectory() as folder, \
                patch('subprocess.check_output', return_value=' M scripts/investigator/a.py') as check:
            with self.assertRaisesRegex(TapeError, 'TAPE_UNCOMMITTED_ENGINE'):
                Tape(Path(folder) / 'dirty.json', bootstrap)
            self.assertEqual(check.call_count, 1)

    def test_windows_pipe_worker_never_requires_a_console(self):
        original = {'stdin': 1, 'stdout': 2, 'creationflags': 0x200}
        self.assertEqual(options(original, platform='nt'), {
            **original, 'creationflags': 0x08000200})
        self.assertEqual(original['creationflags'], 0x200)
        self.assertEqual(options({}, platform='nt')['creationflags'], 0x08000000)

    def test_nonwindows_and_explicit_detachment_are_unchanged(self):
        self.assertEqual(options({}, platform='posix'), {})
        for flags in (8, 16, 8 | 0x200):
            value = {'creationflags': flags}
            self.assertEqual(options(value, platform='nt'), value)

    def test_bounded_and_streaming_dispatch_share_launch_policy(self):
        with patch.object(tape_worker, 'ACTIVE', Mock(get=Mock(return_value=None))), \
                patch('investigator.worker_launch.options', side_effect=lambda kw: {**kw, 'creationflags': 123}) as policy, \
                patch.object(tape_worker.subprocess, 'Popen') as popen, \
                patch.object(tape_worker.subprocess, 'run') as run:
            tape_worker.popen(['worker'], worker_timeout=3, stdout=2)
            popen.assert_called_once_with(['worker'], stdout=2, creationflags=123)
            tape_worker.run(['worker'], input='{}', timeout=3, stdout=2)
            run.assert_called_once_with(['worker'], input='{}', timeout=3, stdout=2, creationflags=123)
            self.assertEqual(policy.call_count, 2)


if __name__ == '__main__':
    unittest.main()

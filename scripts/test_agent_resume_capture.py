import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from investigator import process_tape as journal
from investigator.agent_ticket import AgentTicket
import test_process_tape as fixtures


class ResumeCaptureTests(unittest.TestCase):
    def record(self, folder, version):
        path = Path(folder) / 'tape.json'
        bootstrap = fixtures.AgentTapeVersionTests().workspace(folder)
        with patch.object(journal, 'VERSION', version), patch('subprocess.check_output', side_effect=['', 'a'*40]):
            tape = journal.Tape(path, bootstrap)
        start = {'name': 'agent_resume', 'args': ['ticket'], 'kwargs': {'revision': 2, 'comment_id': 'real-user'}}
        tape.event('OPERATION_START', journal.bytes_of(start))
        tape.event('CONFIGURATION', journal.bytes_of({'config': {}, 'profile': {}, 'usage_policy': {}}))
        tape.event('OPERATION_END', journal.bytes_of({'name': 'agent_resume', 'error': None}))
        final = {'operation': 'agent_resume', 'error': None, 'outputs': None, 'status': None,
                 'result': {'ticket': {'state': 'HELD'}, 'revision': 3}}
        return path, tape, start, final

    def test_resume_is_current_contract_only_and_legacy_seals_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            _, tape, _, final = self.record(folder, 'bounded-worker-tape-v11')
            with self.assertRaisesRegex(journal.TapeError, 'TAPE_OPERATION_FIELDS'): tape.finish(final)
        with tempfile.TemporaryDirectory() as folder:
            path, tape, start, final = self.record(folder, 'bounded-worker-tape-v12')
            tape.finish(final); original = path.read_bytes(); replay = journal.Tape(path)
            replay.event('OPERATION_START', journal.bytes_of(start))
            replay.event('CONFIGURATION', journal.bytes_of({'config': {}, 'profile': {}, 'usage_policy': {}}))
            replay.event('OPERATION_END', journal.bytes_of({'name': 'agent_resume', 'error': None}))
            replay.finish(final)
            self.assertEqual(path.read_bytes(), original)

    def test_offline_dispatcher_invokes_actual_resume_entry_with_retained_ids(self):
        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root / 'acceptance/unknown_domain'))
        import process_replay
        with tempfile.TemporaryDirectory() as folder:
            path, tape, _, final = self.record(folder, 'bounded-worker-tape-v12'); tape.finish(final)
            controller = Mock()
            workspace = Mock()
            workspace.smart_intake = controller
            with patch.object(process_replay, 'ModelStore'), patch.object(process_replay, 'Runtime'), \
                 patch.object(process_replay, 'AdaptiveRuntime') as adaptive, \
                 patch.object(process_replay, 'Workspace', return_value=workspace), \
                 patch('investigator.smart_intake.SmartIntake', return_value=controller), \
                 patch.object(AgentTicket, 'resume', return_value=final['result']) as resume:
                adaptive.return_value.config = {}; adaptive.return_value.planner_profile = {}; adaptive.return_value.governor = SimpleNamespace(policy={})
                result = process_replay.replay(path, Path(folder) / 'replay', allow_engine_drift=True)
            self.assertTrue(result['matched']); self.assertEqual(result['network_requests'], 0)
            resume.assert_called_once_with('ticket', revision=2, comment_id='real-user')

    def test_recording_uses_installed_smart_policy_not_a_private_shadow(self):
        controller = SimpleNamespace(configuration={'must_confirm': []}, ownership={'business': [], 'technical': []}, auto_start=True)
        ticket = AgentTicket(SimpleNamespace(smart_intake=controller))
        self.assertIs(ticket.configuration, controller.configuration)
        self.assertIs(ticket.ownership, controller.ownership)
        self.assertTrue(ticket.auto_start)
        self.assertTrue(hasattr(AgentTicket.resume, '__wrapped__'))

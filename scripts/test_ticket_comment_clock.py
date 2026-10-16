"""A discussion timestamp cannot make an otherwise exact replay drift."""
import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from investigator.process_tape import Tape, active
from investigator.ticket_state import Tickets
from investigator.ticket_comments import append
import test_investigator_workspace as fixture


class CommentClockTests(unittest.TestCase):
    def workspace(self):
        helper = fixture.WorkspaceTests()
        helper.setUp()
        self.addCleanup(helper.doCleanups)
        return SimpleNamespace(smart_intake=SimpleNamespace(tickets=Tickets(helper.store)))

    def test_comment_replays_with_a_different_wall_clock_and_unchanged_tape(self):
        workspace = self.workspace()
        replay_workspace = self.workspace()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'comment.json'
            bootstrap = {'entry_point': 'synthetic', 'context_identity': 'retained',
                         'config': {}, 'profile': {}, 'usage_policy': {},
                         'engine_hash': 'synthetic', 'state': {}}
            tape = Tape(path, bootstrap)
            def execute(workspace):
                saved = workspace.smart_intake.tickets.submit({'text': 'A question'}, 'ticket')
                request = {'ticket_id': saved['ticket']['id'], 'revision': saved['revision'],
                           'request_key': 'question', 'text': 'Which figure?',
                           'attachment_id': None, 'review_id': None}
                result = append(workspace, request, actor='AGENT')
                # A duplicate must return the original comment without another clock.
                self.assertEqual(append(workspace, copy.deepcopy(request), actor='AGENT'), result)
                return result
            with active(tape):
                recorded = execute(workspace)
                tape.finish(recorded)
            original = path.read_bytes()
            replay = Tape(path)
            with active(replay), patch('time.time', return_value=1):
                observed = execute(replay_workspace)
                replay.finish(observed)
            self.assertEqual(observed, recorded)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(sum(e['kind'] == 'CLOCK' for e in tape.events), 1)


if __name__ == '__main__':
    unittest.main()

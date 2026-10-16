"""Draft development pushes must not dispatch unbudgeted provider evaluations."""
import unittest
from pathlib import Path


class DraftIntakeCITests(unittest.TestCase):
    def test_provider_job_waits_until_pr_is_ready_but_manual_and_scheduled_remain(self):
        workflow=(Path(__file__).resolve().parents[1]/'.github/workflows/current-intake-evaluation.yml').read_text()
        self.assertIn("if: github.event_name != 'pull_request' || github.event.pull_request.draft == false",workflow)
        self.assertIn('workflow_dispatch:',workflow)
        self.assertIn('schedule:',workflow)


if __name__=='__main__':unittest.main()

"""Draft development pushes must not dispatch unbudgeted provider evaluations."""
import unittest
from pathlib import Path


class DraftIntakeCITests(unittest.TestCase):
    def test_contract_job_waits_until_pr_is_ready_but_manual_and_scheduled_remain(self):
        workflow=(Path(__file__).resolve().parents[1]/'.github/workflows/current-intake-evaluation.yml').read_text()
        self.assertIn("if: github.event_name != 'pull_request' || github.event.pull_request.draft == false",workflow)
        self.assertIn('workflow_dispatch:',workflow)
        self.assertIn('schedule:',workflow)

    def test_hosted_ci_cannot_dispatch_retired_azure_profile_or_unbudgeted_live_calls(self):
        workflow=(Path(__file__).resolve().parents[1]/'.github/workflows/current-intake-evaluation.yml').read_text()
        self.assertNotIn('AZURE_OPENAI_',workflow)
        self.assertNotIn('secrets.',workflow)
        self.assertNotIn('run_current_intake_eval.py --',workflow)
        self.assertIn('DIA_LIVE_ACCESS_DISABLED: "1"',workflow)
        for module in ('test_calculation_intake','test_round24_runtime_anthropic','test_round24_gateway_components'):
            self.assertIn(module,workflow)
        self.assertIn('NOT a live quality score',workflow)


if __name__=='__main__':unittest.main()

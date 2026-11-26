import unittest
from datetime import datetime,timezone
from cloud_guided_investigator import model_budget_purpose
from investigator.reasoning_budget import ai_step
from investigator.provider_budget import check_credit
from investigator.model_spend import SpendHold


class GuidedSmokePurposeTests(unittest.TestCase):
    def test_nested_guided_steps_keep_trusted_smoke_and_restore_normal_context(self):
        now=datetime(2026,11,22,tzinfo=timezone.utc).timestamp()
        for step in ('INTAKE','INVESTIGATOR','EVALUATOR','SCREENSHOT'):
            with self.subTest(step=step):
                self.assertEqual(model_budget_purpose(step),step)
                with ai_step('SMOKE'):
                    purpose=model_budget_purpose(step)
                    self.assertEqual(purpose,'SMOKE')
                    # Latest owner scope is grading-only, including trusted smoke contexts.
                    with self.assertRaisesRegex(SpendHold,'PURPOSE_NOT_APPROVED'):
                        check_credit('openai',now,owner='round27-release-smokes',purpose=purpose)
                    with self.assertRaisesRegex(SpendHold,'PURPOSE_NOT_APPROVED'):
                        check_credit('anthropic',now,owner='round27-release-smokes',purpose=purpose)
                self.assertEqual(model_budget_purpose(step),step)
        with self.assertRaisesRegex(SpendHold,'PURPOSE_NOT_APPROVED'):
            check_credit('openai',now,owner='round27-dev',purpose=model_budget_purpose('INVESTIGATOR'))

    def test_untrusted_ticket_cannot_set_accounting_purpose(self):
        # The helper accepts only the installed step; no ticket or spec field is read.
        with ai_step('INVESTIGATOR'):
            self.assertEqual(model_budget_purpose('INTAKE'),'INTAKE')
            self.assertEqual(model_budget_purpose('EVALUATOR'),'EVALUATOR')


if __name__=='__main__':unittest.main()

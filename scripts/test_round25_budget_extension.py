import unittest
from unittest.mock import Mock,patch
from investigator.enrichment_job import EnrichmentSpendBudget
class BudgetExtensionTests(unittest.TestCase):
 def test_extended_october_policy_keeps_grading_in_monthly_account(self):
  state=Mock();state.get.return_value={'body':{'total_limit':15500,'default_total_limit':9000}}
  with patch('investigator.build_phase.ensure_model_account',return_value='model-microdollars:2026-10'):
   budget=EnrichmentSpendBudget(state,owner='grader',price=lambda a,b:1)
  self.assertTrue(budget.monthly)
  self.assertEqual(budget.account,'model-microdollars:2026-10')
  state.totals.assert_not_called()

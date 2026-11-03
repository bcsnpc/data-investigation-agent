import unittest
from unittest.mock import Mock,patch
from investigator.enrichment_job import EnrichmentSpendBudget
from investigator import build_phase
from datetime import datetime, timezone
class BudgetExtensionTests(unittest.TestCase):
 def test_owner_october_extension_and_explicit_round26_november_override(self):
  october=build_phase.round24_limits(datetime(2026,10,31,tzinfo=timezone.utc).timestamp())
  november=build_phase.round24_limits(datetime(2026,11,1,tzinfo=timezone.utc).timestamp())
  self.assertEqual((october['model_microdollars'],october['total_limit'],october['limits']),
   (206000000,17000,{'SCAN':2500,'INVESTIGATION':14405,'RESTORATION':95}))
  self.assertEqual((november['model_microdollars'],november['total_limit'],november['limits']),
   (150000000,14500,{'SCAN':2500,'INVESTIGATION':11905,'RESTORATION':95}))
 def test_extended_october_policy_keeps_grading_in_monthly_account(self):
  state=Mock();state.get.return_value={'body':{'total_limit':15500,'default_total_limit':9000}}
  with patch('investigator.build_phase.ensure_model_account',return_value='model-microdollars:2026-10'):
   budget=EnrichmentSpendBudget(state,owner='grader',price=lambda a,b:1)
  self.assertTrue(budget.monthly)
  self.assertEqual(budget.account,'model-microdollars:2026-10')
  state.totals.assert_not_called()

import unittest,tempfile
from pathlib import Path
from datetime import datetime,timezone
from investigator.shared_state import SharedState
from investigator.reasoning_budget import TicketBudget,RateCard
from investigator.model_spend import SpendHold
from investigator.triage_hints import suggestion,job_hint

class ActualCostTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.state=SharedState.offline(Path(self.tmp.name)/'s.sqlite');self.state.migrate()
  self.rate=RateCard(model='claude-opus-5-5',input_rate='5',base_input_rate='4',cache_read_rate='.20',output_rate='20',source='https://platform.claude.com/docs/en/about-claude/pricing',observed_at='2026-10-27')
  self.budget=TicketBudget(self.state,case_id='x',owner='worker',rate=self.rate,clock=lambda:datetime(2026,11,1,tzinfo=timezone.utc).timestamp(),actual_usage_limit=3000000)
 def test_estimate_and_actual_differ_without_false_violation_monthly_commitment_remains(self):
  key=self.budget.reserve({'model':self.rate.model,'max_tokens':8000},input_tokens_upper_bound=10000)
  before=self.state.snapshot('model-microdollars:2026-11')['reservations'][0]
  self.assertEqual(int(before['reserved']),100000)
  self.assertEqual(before['detail']['maximum_commitment_microdollars'],210000)
  self.budget.settle(key,{'input_tokens':10000,'output_tokens':6000})
  after=self.state.snapshot('model-microdollars:2026-11')
  self.assertFalse(after['violated']);self.assertEqual(after['charged'],'160000')
 def test_unknown_response_keeps_full_monthly_commitment_charged(self):
  key=self.budget.reserve({'model':self.rate.model,'max_tokens':8000},input_tokens_upper_bound=10000)
  self.budget.settle(key)
  self.assertEqual(self.state.totals('model-microdollars:2026-11')['charged'],'210000')
 def test_ticket_not_blocked_by_worst_case_reservation(self):
  with self.state.transaction()as db:
   db.execute('INSERT INTO state_accounts VALUES(?,?,?,?,?,?)',('model-microdollars:2026-11','MICRODOLLARS',150000000,0,0,0))
   import json
   db.execute('INSERT INTO state_reservations VALUES(?,?,?,?,?,?,?)',('model-microdollars:2026-11','old','worker',2999999,2999999,'SETTLED',json.dumps({'case_id':'x'})))
  self.budget.reserve({'model':self.rate.model,'max_tokens':4000},input_tokens_upper_bound=10000)
 def test_pending_maxima_cannot_overbook_monthly_cap(self):
  self.budget.status()
  with self.state.transaction()as db:db.execute('UPDATE state_accounts SET ceiling=300000')
  self.budget.reserve({'model':self.rate.model,'max_tokens':8000},input_tokens_upper_bound=10000)
  with self.assertRaisesRegex(SpendHold,'MONTHLY_MODEL_EXHAUSTED'):self.budget.reserve({'model':self.rate.model,'max_tokens':8000},input_tokens_upper_bound=10000)

class TriageTests(unittest.TestCase):
 def test_old_failed_history_does_not_override_latest_success(self):
  triage={'facts':[{'check':'JOB_RUNS','state':'OBSERVED','source':'native','value':[{'kind':'JOB_RUN','subject':'job','value':{'run_id':'new','status':'Completed'}},{'kind':'RUN_HISTORY','subject':'job','value':{'runs':[{'run_id':'old','status':'Failed'}]}}]}]}
  self.assertEqual(job_hint(triage),[])

 def test_failed_native_run_is_first_hint_and_unavailable_never_becomes_fault(self):
  triage={'facts':[{'check':'JOB_RUNS','state':'OBSERVED','source':'native-history','value':[{'subject':'job','value':{'id':'r','status':'Failed','failureReason':{'message':'native failure'}}}]}]}
  self.assertEqual(job_hint(triage)[0]['subject'],'job');self.assertIn('first',suggestion(triage))
  triage['facts'][0]['state']='UNAVAILABLE';self.assertEqual(job_hint(triage),[])
  self.assertIn('does not establish',suggestion(triage))
if __name__=='__main__':unittest.main()

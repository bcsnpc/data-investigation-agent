import json,unittest,tempfile
from pathlib import Path
from datetime import datetime,timezone
from unittest.mock import patch
from investigator import build_phase as b
from investigator.reasoning_budget import RateCard,TicketBudget
from investigator.shared_state import SharedState
from investigator.model_spend import SpendHold

def at(s):return datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp()

class OwnerAllocationTests(unittest.TestCase):
 def test_october_only_override_preserves_usage_and_november_defaults(self):
  override={'2026-10':{'effective_at':'2026-10-27T00:00:00+00:00','limits':{'SCAN':2500,'INVESTIGATION':6405,'RESTORATION':95}}}
  rows=[{'environment':'e','session_id':'s','reservation_key':'r','reserved':json.dumps({'cloud_calls':2000}),'created':at('2026-10-26')}];alloc=[{'environment':'e','session_id':'s','reservation_key':'r','purpose':'SCAN'}]
  with patch.dict(b.POLICY,monthly_allocation_overrides=override):
   before=b.physical_status(rows,alloc,at('2026-10-26'));after=b.physical_status(rows,alloc,at('2026-10-28'));nov=b.physical_status([],[],at('2026-11-01'))
  self.assertEqual(before['used'],after['used']);self.assertEqual(after['total'],2000)
  self.assertEqual(after['limits'],override['2026-10']['limits']);self.assertEqual(nov['limits'],{'SCAN':2000,'INVESTIGATION':6905,'RESTORATION':95})
 def test_manual_smoke_category_covers_nested_scan_and_restores_after_exit(self):
  with b.operating_mode(category='SCAN'):
   self.assertEqual(b.purpose(),'SCAN')
   with b.manual_smoke_allocation(True):
    self.assertEqual(b.purpose(),'INVESTIGATION')
    with b.operating_mode(category='SCAN'):self.assertEqual(b.purpose(),'INVESTIGATION')
   self.assertEqual(b.purpose(),'SCAN')
 def test_cloud_policy_october_limits_and_default_month_are_both_enforced(self):
  with tempfile.TemporaryDirectory()as d:
   state=SharedState.offline(Path(d)/'state.sqlite');state.migrate();state.put('build_phase_policy','monthly-physical',{'total_limit':9000,'limits_effective_month':'2026-10','limits':{'SCAN':2500,'INVESTIGATION':6405,'RESTORATION':95},'default_limits':{'SCAN':2000,'INVESTIGATION':6905,'RESTORATION':95}})
   with state.transaction()as db:
    for month,limit in [('2026-10',6405),('2026-11',6905)]:
     status={'month_utc':month,'total_limit':9000,'total':limit,'limits':{'INVESTIGATION':6905},'used':{'INVESTIGATION':limit}}
     with self.assertRaisesRegex(Exception,'EXHAUSTED'):b.check_shared_request_policy(state,db,at(month+'-28'),status,'INVESTIGATION')

class ActualDiagnosticTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.state=SharedState.offline(Path(self.tmp.name)/'state.sqlite');self.state.migrate();self.rate=RateCard(model='test',input_rate='5',output_rate='20',source='https://example.test/rate',observed_at='2026-10-27');self.now=lambda:at('2026-11-01');self.b=TicketBudget(self.state,case_id='case',owner='worker',rate=self.rate,clock=self.now,actual_usage_limit=3000000)
 def body(self):return {'model':'test','max_tokens':4000}
 def test_pending_bounds_do_not_replace_case_actuals_but_still_charge_monthly(self):
  with patch.object(self.rate,'price',return_value=2000000):
   first=self.b.reserve(self.body());second=self.b.reserve(self.body())
  self.assertEqual(self.b.status()['charged_microdollars'],0);self.assertEqual(int(self.state.totals('model-microdollars:2026-11')['charged']),4000000)
  self.b.settle(first,{'input_tokens':100,'output_tokens':100});self.assertEqual(self.b.status()['charged_microdollars'],2500)
  self.b.settle(second);self.assertEqual(self.b.status()['charged_microdollars'],2002500)
 def test_actual_limit_stops_next_call_and_never_refunds_uncertain(self):
  with patch.object(self.rate,'price',return_value=3000000):identity=self.b.reserve(self.body())
  self.b.settle(identity)
  with self.assertRaisesRegex(SpendHold,'TICKET_MODEL_EXHAUSTED'):self.b.reserve(self.body())
  self.assertEqual(self.b.status()['charged_microdollars'],3000000)
 def test_monthly_hard_cap_still_refuses_on_reserved_maximum(self):
  self.b.status()
  with self.state.transaction()as db:db.execute('UPDATE state_accounts SET ceiling=100')
  with self.assertRaisesRegex(SpendHold,'MONTHLY_MODEL_EXHAUSTED'):self.b.reserve(self.body())
 def test_other_actual_limit_not_approved(self):
  with self.assertRaises(ValueError):TicketBudget(self.state,case_id='c',owner='w',rate=self.rate,actual_usage_limit=4000000)

if __name__=='__main__':unittest.main()

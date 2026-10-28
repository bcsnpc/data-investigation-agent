"""Round24 dated policy and combined-cap regressions, entirely offline."""
import json,tempfile,unittest
from pathlib import Path
from datetime import datetime,timezone
from investigator.shared_state import SharedState
from investigator import build_phase as b
from investigator.anthropic_credit import admit
from investigator.model_spend import SpendHold

class PolicyTests(unittest.TestCase):
 def test_october_raise_and_november_reset_preserve_usage(self):
  at=lambda value:datetime.fromisoformat(value).replace(tzinfo=timezone.utc).timestamp()
  row={'environment':'x','session_id':'x','reservation_key':'x','created':at('2026-10-27'),'reserved':json.dumps({'cloud_calls':8294})}
  allocation={k:row[k]for k in ('environment','session_id','reservation_key')};allocation['purpose']='INVESTIGATION'
  october=b.physical_status([row],[allocation],at('2026-10-29'))
  self.assertEqual(october['total'],8294);self.assertEqual(october['total_limit'],12000)
  self.assertEqual(october['limits'],{'SCAN':2500,'INVESTIGATION':9405,'RESTORATION':95})
  november=b.physical_status([row],[allocation],at('2026-11-01'))
  self.assertEqual(november['total'],0);self.assertEqual(november['total_limit'],9000)
  self.assertEqual(november['limits'],{'SCAN':2500,'INVESTIGATION':6405,'RESTORATION':95})
  self.assertEqual(b.model_ceiling(at('2026-10-29')),146000000)
  self.assertEqual(b.model_ceiling(at('2026-11-01')),150000000)
 def test_new_batches_use_monthly_combined_account_without_erasing_old_usage(self):
  from investigator.enrichment_job import EnrichmentSpendBudget
  from investigator.adapters.evaluation_anthropic import request_for
  with tempfile.TemporaryDirectory()as folder:
   state=SharedState.offline(Path(folder)/'s.sqlite');state.migrate()
   state.put('build_phase_policy','monthly-physical',{'total_limit':12000,'default_total_limit':9000})
   with state.transaction()as db:db.execute('INSERT INTO state_accounts VALUES(?,?,?,?,?,?)',('enrichment:round-twenty-one','MICRODOLLARS',25000000,0,9000000,0))
   budget=EnrichmentSpendBudget(state,owner='grader',price=lambda i,o:100)
   self.assertTrue(budget.monthly);self.assertTrue(budget.account.startswith('model-microdollars:'))
   request=request_for({'protocol':'scored-evaluation-v1','purpose':'GRADE_GUIDED_ANSWER','case_id':'case','expected':{},'delivered':{}},'a'*64)
   budget.reserve(request,'one');budget.settle('one',{'input_tokens':10,'output_tokens':10})
   row=state.snapshot(budget.account)['reservations'][0]
   self.assertEqual(row['detail']['purpose'],'GRADING');self.assertEqual(state.totals('enrichment:round-twenty-one')['charged'],'9000000')
 def test_november_combines_only_month_tagged_auxiliary_usage(self):
  from investigator.anthropic_credit import status
  with tempfile.TemporaryDirectory()as folder:
   state=SharedState.offline(Path(folder)/'s.sqlite');state.migrate()
   with state.transaction()as db:
    for name in ('model-microdollars:2026-11','enrichment:round-twenty-one'):
     db.execute('INSERT INTO state_accounts VALUES(?,?,?,?,?,?)',(name,'MICRODOLLARS',150000000,0,0,0))
    for key,month,cost in [('old','2026-10',9000000),('new','2026-11',2000000)]:
     db.execute('INSERT INTO state_reservations VALUES(?,?,?,?,?,?,?)',('enrichment:round-twenty-one',key,'worker',cost,cost,'SETTLED',json.dumps({'month_utc':month})))
   report=status(state,datetime(2026,11,2,tzinfo=timezone.utc).timestamp())
   self.assertEqual(report['charged_microdollars'],2000000)
   self.assertEqual(report['remaining_microdollars'],148000000)
   self.assertEqual(sum(report['by_ai_step_microdollars'].values()),2000000)
 def test_combined_cap_includes_grading_and_protects_its_margin(self):
  with tempfile.TemporaryDirectory()as folder:
   state=SharedState.offline(Path(folder)/'s.sqlite');state.migrate()
   for name in ('model','grading'):
    with state.transaction()as db:db.execute('INSERT INTO state_accounts VALUES(?,?,?,?,?,?)',(name,'MICRODOLLARS',999999999,0,0,0))
   month=datetime.now(timezone.utc).strftime('%Y-%m')
   state.put('anthropic_credit',month,{'model_account':'model','grading_account':'grading','baseline_model_charged':0,'baseline_grading_charged':0,'baseline_higher_microdollars':90000000,'normalized_ceiling_microdollars':146000000,'protected_grading_microdollars':3000000})
   state.reserve('model','one','worker',53000000)
   with self.assertRaisesRegex(SpendHold,'COMBINED_ANTHROPIC'):state.reserve('model','too','worker',1)
   state.reserve('grading','grade','reviewer',3000000)
   with self.assertRaisesRegex(SpendHold,'COMBINED_ANTHROPIC'):state.reserve('grading','too','reviewer',1)
   self.assertEqual(state.totals('model')['charged'],'53000000')
   self.assertEqual(state.totals('grading')['charged'],'3000000')

if __name__=='__main__':unittest.main()

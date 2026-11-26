"""Saved native schedule regression; no estate or provider calls."""
from copy import deepcopy
from unittest import TestCase,main
from unittest.mock import Mock
from investigator.adapters.runtime_facts_microsoft import future_job_schedule,MicrosoftRuntimeFacts
from investigator.regression_features import configured
from test_runtime_facts_microsoft import retained,WS,ITEM

NOW='2026-11-22T06:41:40Z'
def schedule():
 return {'id':'schedule1','enabled':True,'configuration':{'type':'Cron','interval':60,'localTimeZoneId':'UTC',
  'startDateTime':'2026-11-23T18:38:43','endDateTime':'2026-11-23T18:39:43'}}

class FutureScheduleTests(TestCase):
 def test_saved_utc_naive_producer_fields_establish_first_due_not_run(self):
  body={'value':[schedule()]};before=deepcopy(body);v=future_job_schedule(body,NOW)
  self.assertEqual(v['next_due'],'2026-11-23T18:38:43Z');self.assertTrue(v['enabled'])
  self.assertEqual(v['due_basis'],'DECLARED_FUTURE_FIRST_SLOT_NOT_OBSERVED_RUN');self.assertEqual(body,before)
  self.assertNotIn('status',v);self.assertNotIn('run_id',v)
 def test_disabled_and_empty_do_not_schedule(self):
  row=schedule();row['enabled']=False
  for body in ({'value':[row]},{'value':[]}):
   v=future_job_schedule(body,NOW);self.assertIsNone(v['next_due']);self.assertFalse(v['enabled'])
 def test_multiple_known_future_schedules_choose_earliest(self):
  row=schedule();later=deepcopy(row);later['configuration'].update(startDateTime='2026-11-24T12:00:00Z',endDateTime='2026-11-25T12:00:00Z')
  self.assertEqual(future_job_schedule({'value':[later,row]},NOW)['next_due'],'2026-11-23T18:38:43Z')
 def test_already_started_does_not_invent_phase_from_start(self):
  with self.assertRaisesRegex(ValueError,'PHASE_UNESTABLISHED'):future_job_schedule({'value':[schedule()]},'2026-11-23T18:39:00Z')
 def test_partial_unknown_or_bad_enabled_schedule_never_becomes_global_next(self):
  bodies=[{'value':[schedule()],'continuationToken':'more'}]
  for patch in ({'type':'Weekly'},{'localTimeZoneId':'Central Standard Time'},{'interval':True},{'interval':0},{'endDateTime':None},{'endDateTime':'2026-11-21T00:00:00Z'}):
   row=schedule();row['configuration'].update(patch);bodies.append({'value':[schedule(),row]})
  row=schedule();row['enabled']='true';bodies.append({'value':[row]})
  for body in bodies:
   with self.subTest(body=body),self.assertRaises(ValueError):future_job_schedule(body,NOW)
 def test_expired_window_not_future_but_enabled_not_rewritten_disabled(self):
  v=future_job_schedule({'value':[schedule()]},'2026-11-24T00:00:00Z')
  self.assertIsNone(v['next_due']);self.assertTrue(v['enabled'])
 def test_adapter_keeps_native_evidence_and_flag_off_behavior(self):
  raw={'value':[schedule()]}
  def http(path,audience):return {'status_code':200,'text':deepcopy(raw) if path.endswith('/schedules') else {'value':[]}}
  for on in (True,False):
   with self.subTest(on=on):
    adapter=MicrosoftRuntimeFacts({'job':{'kind':'JOB','workspace':WS,'item':ITEM,'job_type':'Pipeline'}},http=Mock(side_effect=http),retain=retained)
    adapter.list_changes(['job']);facts=adapter.fetch('job',now=NOW)
    fact=next(f for f in facts if f['kind']=='SCHEDULE')
    self.assertEqual(fact['value']['native_schedules'],raw);self.assertTrue(fact['provenance']['evidence_ids'])
    self.assertEqual(fact['value']['next_due'],'2026-11-23T18:38:43Z' if on else None)
    self.assertFalse(any(f['kind']=='OVERDUE' for f in facts))

if __name__=='__main__':main()

import json,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
from investigator.shared_state import SharedState
from investigator.build_phase import operating_mode
from investigator.usage_governance import UsageHold
from scan_estate_graph import Meter

class ControlMeterTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.state=SharedState.offline(Path(self.tmp.name)/'state.sqlite');self.state.migrate();self.at=datetime(2026,10,23,tzinfo=timezone.utc).timestamp()
  self.state.put('usage_policy','test',{'policy':{'environment':'test','daily_limits':{'cloud_calls':1,'planner_calls':1,'input_characters':1,'output_tokens':8000},'max_inflight_planners':1,'no_progress_limit':2},'round_policy':{'id':'historical'}})
 def test_reporting_failure_cannot_prevent_settlement_or_remove_authoritative_charge(self):
  with operating_mode(category='INVESTIGATION'),patch('investigator.shared_usage.SharedUsage.mirror',side_effect=RuntimeError('unused reporting mirror stalled'))as reporting:
   meter=Meter(self.state,{'environment':'test'},1,clock=lambda:self.at,reporting_mirror=False);self.addCleanup(meter.close);self.assertEqual(meter(lambda:17),17);self.assertEqual(meter.used,1);reporting.assert_not_called()
   self.assertEqual(meter.local.execute('SELECT COUNT(*) FROM adaptive_usage').fetchone()[0],0)
   self.assertEqual(meter.usage.snapshot()['monthly']['used']['INVESTIGATION'],1)
  with self.state.transaction()as db:
   row=db.execute('SELECT status,owner FROM state_usage').fetchone();self.assertEqual(row[0],'SETTLED');self.assertEqual(row[1],meter.owner)
 def test_lost_reservation_commit_ack_reuses_key_and_dispatches_once(self):
  from investigator import build_phase
  original=build_phase.shared_reserve;keys=[]
  def reserve(*args,**kwargs):
   keys.append(args[3]);result=original(*args,**kwargs)
   if len(keys)==1:raise ConnectionError('lost commit acknowledgement')
   return result
  operation=Mock(return_value=17)
  with operating_mode(category='INVESTIGATION'):
   meter=Meter(self.state,{'environment':'test'},1,clock=lambda:self.at,reporting_mirror=False);self.addCleanup(meter.close)
   with patch('investigator.build_phase.shared_reserve',side_effect=reserve),patch('time.sleep')as sleep:
    self.assertEqual(meter(operation),17)
   sleep.assert_called_once_with(30);self.assertEqual(len(set(keys)),1);operation.assert_called_once()
   self.assertEqual(meter.usage.snapshot()['monthly']['total'],1);self.assertEqual(len(meter.reservation_retries),1)
  with self.state.transaction()as db:
   self.assertEqual(db.execute('SELECT status FROM state_usage').fetchall(),[('SETTLED',)])
 def test_reservation_transport_retries_are_bounded_and_policy_refusals_never_retry(self):
  for error,attempts in ((ConnectionError('transport'),3),(UsageHold('MONTHLY_PHYSICAL_SCAN_EXHAUSTED'),1),(ValueError('query error'),1)):
   with self.subTest(error=type(error).__name__),operating_mode(category='INVESTIGATION'):
    meter=Meter(self.state,{'environment':'test'},1,clock=lambda:self.at,reporting_mirror=False);self.addCleanup(meter.close);operation=Mock()
    with patch('investigator.build_phase.shared_reserve',side_effect=error)as reserve,patch('time.sleep')as sleep:
     with self.assertRaises(type(error)):meter(operation)
     self.assertEqual(reserve.call_count,attempts);self.assertEqual(sleep.call_count,attempts-1)
    operation.assert_not_called();self.assertEqual(meter.used,0)
 def test_postgres_authentication_and_query_errors_are_not_transport_retries(self):
  from scan_estate_graph import reservation_connection_failure
  import psycopg
  for error in (psycopg.errors.InvalidPassword('auth'),psycopg.errors.InsufficientPrivilege('permission'),psycopg.errors.SyntaxError('query')):
   self.assertFalse(reservation_connection_failure(error))
  self.assertTrue(reservation_connection_failure(psycopg.errors.IdleInTransactionSessionTimeout('idle')))
 def test_real_shared_monthly_limit_still_refuses_before_dispatch_without_reporting_mirror(self):
  reserved=json.dumps({'cloud_calls':1,'planner_calls':0,'input_characters':0,'output_tokens':0})
  with self.state.transaction()as db:
   db.executemany('INSERT INTO state_usage VALUES(?,?,?,?,?,?,?,?,?,?,?)',[('test','old'+str(i),'one','2026-10-23','cloud',reserved,'{}','SETTLED','historic',self.at,'old'+str(i))for i in range(1000)])
   db.executemany('INSERT INTO state_read_allocations VALUES(?,?,?,?,?)',[('test','old'+str(i),'one',None,'SCAN')for i in range(1000)])
  operation=Mock()
  with operating_mode(category='SCAN'):
   meter=Meter(self.state,{'environment':'test'},1,clock=lambda:self.at,reporting_mirror=False);self.addCleanup(meter.close)
   with self.assertRaisesRegex(UsageHold,'MONTHLY_PHYSICAL_SCAN_EXHAUSTED'):meter(operation)
  operation.assert_not_called();self.assertEqual(meter.used,0)
 def test_control_report_skips_legacy_snapshot_and_counts_other_environments_and_pending_reads(self):
  reserved=json.dumps({'cloud_calls':1,'planner_calls':0,'input_characters':0,'output_tokens':0})
  with self.state.transaction()as db:
   db.execute('INSERT INTO state_usage VALUES(?,?,?,?,?,?,?,?,?,?,?)',('other-estate','pending','one','2026-10-23','cloud',reserved,None,'RESERVED','historic',self.at,'other'))
   db.execute('INSERT INTO state_read_allocations VALUES(?,?,?,?,?)',('other-estate','pending','one',None,'INVESTIGATION'))
   db.execute('INSERT INTO state_usage VALUES(?,?,?,?,?,?,?,?,?,?,?)',('other-estate','historical','old','2026-10-01','cloud',reserved,'{}','SETTLED','historic',datetime(2026,10,1,tzinfo=timezone.utc).timestamp(),'other'))
  with operating_mode(category='INVESTIGATION'),patch('investigator.shared_usage.SharedUsage.snapshot',side_effect=RuntimeError('legacy historical report stalled'))as legacy:
   meter=Meter(self.state,{'environment':'test'},1,clock=lambda:self.at,reporting_mirror=False);self.addCleanup(meter.close)
   self.assertEqual(meter.before['monthly']['total'],1);self.assertEqual(meter.before['monthly']['used']['INVESTIGATION'],1)
   meter(lambda:17);self.assertEqual(meter.usage.snapshot()['monthly']['total'],2);legacy.assert_not_called()
 def test_exact_tape_legacy_and_invalid_flags_cannot_disable_their_mirror(self):
  with operating_mode(category='INVESTIGATION'),patch('investigator.process_tape.ACTIVE')as active:
   active.get.return_value=SimpleNamespace(replaying=False)
   with self.assertRaisesRegex(ValueError,'UNTAPED_BUILD_CONTROL'):Meter(self.state,{'environment':'test'},1,reporting_mirror=False)
  with patch('investigator.build_phase.active',return_value=False):
   with self.assertRaisesRegex(ValueError,'UNTAPED_BUILD_CONTROL'):Meter(self.state,{'environment':'test'},1,reporting_mirror=False)
  with self.assertRaisesRegex(ValueError,'BOOLEAN'):Meter(self.state,{'environment':'test'},1,reporting_mirror='false')

 def test_admission_period_query_preserves_all_current_charges_and_originals(self):
  from investigator.build_phase import shared_physical_rows,physical_status
  reserved=json.dumps({'cloud_calls':1,'planner_calls':0,'input_characters':0,'output_tokens':0})
  cases=[('old',self.at-86400*10,'SETTLED','SCAN'),('pending',self.at,'RESERVED','SCAN'),('uncertain',self.at,'UNCERTAIN','INVESTIGATION'),('future',datetime(2026,11,1,tzinfo=timezone.utc).timestamp(),'RESERVED','RESTORATION')]
  with self.state.transaction() as db:
   for key,created,status,purpose in cases:
    db.execute('INSERT INTO state_usage VALUES(?,?,?,?,?,?,?,?,?,?,?)',('other',key,'one','recorded','cloud',reserved,None,status,'historic',created,'other-owner'))
    db.execute('INSERT INTO state_read_allocations VALUES(?,?,?,?,?)',('other',key,'one',None,purpose))
   # Legacy reservations without allocation must still count, as investigation.
   db.execute('INSERT INTO state_usage VALUES(?,?,?,?,?,?,?,?,?,?,?)',('unclassified','legacy','one','recorded','cloud',reserved,None,'RESERVED','historic',self.at,'another-owner'))
   cursor=db.execute('SELECT environment,session_id,reservation_key,reserved,created FROM state_usage');all_rows=[dict(zip([x[0]for x in cursor.description],r))for r in cursor.fetchall()]
   cursor=db.execute('SELECT environment,session_id,reservation_key,purpose FROM state_read_allocations');all_alloc=[dict(zip([x[0]for x in cursor.description],r))for r in cursor.fetchall()]
   kept,allocations=shared_physical_rows(self.state,db,self.at)
   self.assertEqual(physical_status(kept,allocations,self.at),physical_status(all_rows,all_alloc,self.at))
   self.assertEqual({x['session_id']for x in kept},{'pending','uncertain','legacy'})
   self.assertEqual(len(allocations),2)
  with operating_mode(category='INVESTIGATION'):
   meter=Meter(self.state,{'environment':'test'},1,clock=lambda:self.at,reporting_mirror=False);self.addCleanup(meter.close)
   meter(lambda:17);self.assertEqual(meter.usage.snapshot()['monthly']['total'],4)
  with self.state.transaction()as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM state_usage').fetchone()[0],6)

if __name__=='__main__':unittest.main()

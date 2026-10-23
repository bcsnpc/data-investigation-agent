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
 def test_exact_tape_legacy_and_invalid_flags_cannot_disable_their_mirror(self):
  with operating_mode(category='INVESTIGATION'),patch('investigator.process_tape.ACTIVE')as active:
   active.get.return_value=SimpleNamespace(replaying=False)
   with self.assertRaisesRegex(ValueError,'UNTAPED_BUILD_CONTROL'):Meter(self.state,{'environment':'test'},1,reporting_mirror=False)
  with patch('investigator.build_phase.active',return_value=False):
   with self.assertRaisesRegex(ValueError,'UNTAPED_BUILD_CONTROL'):Meter(self.state,{'environment':'test'},1,reporting_mirror=False)
  with self.assertRaisesRegex(ValueError,'BOOLEAN'):Meter(self.state,{'environment':'test'},1,reporting_mirror='false')

if __name__=='__main__':unittest.main()

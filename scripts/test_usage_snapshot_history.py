"""Snapshot observes one instant; older sealed clock sequences remain exact."""
import concurrent.futures,json,sqlite3,tempfile,types,unittest
from datetime import datetime,timezone
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
from investigator import process_tape,read_allowance
from investigator.usage_governance import UsageGovernor
from test_process_tape import bootstrap
import test_adaptive_investigation as fixture

class SnapshotHistoryTests(unittest.TestCase):
 def owner(self,n):
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row;self.addCleanup(db.close)
    db.execute('CREATE TABLE adaptive_usage(environment,session_id,reservation_key,day,kind,reserved,actual,status,policy_hash,created)')
    read_allowance.initialize(db);now=1791663000.0;day=datetime.fromtimestamp(now,timezone.utc).date().isoformat()
    amount={'planner_calls':0,'input_characters':0,'output_tokens':0,'cloud_calls':1}
    db.executemany('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,?,?,?,?)',[('test','s'+str(i),'k',day,'cloud',json.dumps(amount),None,'SETTLED','hash',now-1) for i in range(n)])
    calls=[]
    def clock():calls.append(now);return process_tape.clock('snapshot-fixed',lambda:now)
    owner=UsageGovernor.__new__(UsageGovernor);owner.environment='test';owner.hash='hash';owner.runtime=types.SimpleNamespace(db=lambda:db);owner.clock=clock;owner.policy={'daily_limits':{'cloud_calls':10000}}
    return owner,calls,now
 def test_8000_rows_observe_one_instant_and_preserve_totals(self):
    owner,calls,_=self.owner(8000);result=owner.snapshot()
    self.assertEqual(len(calls),1);self.assertEqual(result['charged_today']['cloud_calls'],8000)
    self.assertTrue(all(v==0 for v in result['active_reservations'].values()))
 def test_v6_sealed_snapshot_clock_sequence_replays_without_changing_bytes(self):
    owner,calls,now=self.owner(3);expected=owner.snapshot();calls.clear()
    with tempfile.TemporaryDirectory() as folder:
     path=Path(folder)/'v6.json'
     with patch.object(process_tape,'VERSION','bounded-worker-tape-v6'):
      tape=process_tape.Tape(path,bootstrap())
      with process_tape.active(tape):
       # Actual pre-v7 snapshot sequence: rolling clock, one clock per row,
       # then returned day. The original seal must remain byte-identical.
       for _ in range(5):process_tape.clock('snapshot-fixed',lambda:now)
       tape.finish(expected)
     before=path.read_bytes();replay=process_tape.Tape(path)
     with process_tape.active(replay):
      actual=owner.snapshot();replay.finish(actual)
     self.assertEqual(actual,expected);self.assertEqual(len(calls),5);self.assertEqual(path.read_bytes(),before)
 def test_new_snapshot_counts_share_a_read_transaction_without_changing_v6_queries(self):
    owner,_,_=self.owner(3);db=owner.runtime.db();db.commit();queries=[];db.set_trace_callback(queries.append)
    owner.snapshot();self.assertEqual(queries.count('BEGIN'),1)
    queries.clear();token=process_tape.ACTIVE.set(types.SimpleNamespace(replaying=True,version='bounded-worker-tape-v6'))
    try:
     with patch('investigator.process_tape.clock',side_effect=lambda name,fn:fn()):owner.snapshot()
    finally:process_tape.ACTIVE.reset(token)
    self.assertNotIn('BEGIN',queries)
 def governor(self):
    helper=fixture.AdaptiveTests();helper.setUp();self.addCleanup(helper.doCleanups);helper.store.environment='development'
    policy={'environment':'development','daily_limits':{'planner_calls':100,'cloud_calls':100,'input_characters':100000,'output_tokens':100000},'max_inflight_planners':4,'no_progress_limit':2}
    return helper,UsageGovernor(helper.runtime,policy,lambda:1000)
 def test_concurrent_writer_cannot_mix_allowance_and_row_views(self):
    helper,governor=self.governor()
    with helper.runtime.db() as db:db.execute('PRAGMA journal_mode=WAL')
    governor.metered_read('first','read',lambda:None)
    original=read_allowance.snapshot
    def interleaved(db,*args,**kwargs):
     result=original(db,*args,**kwargs)
     with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
      pool.submit(governor.metered_read,'second','read',lambda:None).result()
     return result
    with patch('investigator.read_allowance.snapshot',side_effect=interleaved):result=governor.snapshot()
    self.assertEqual(result['read_allowance']['ordinary_charged'],1);self.assertEqual(result['reservation_states'],{'SETTLED':1})
    self.assertEqual(governor.snapshot()['reservation_states'],{'SETTLED':2})
 def test_snapshot_does_not_commit_or_roll_back_caller_owned_transaction(self):
    helper,governor=self.governor()
    with helper.runtime.db() as db:
     db.execute('BEGIN IMMEDIATE');governor.reserve(db,'caller','pending','planner',100,output_tokens=500)
     @contextmanager
     def caller_connection():yield db
     with patch.object(helper.runtime,'db',caller_connection):result=governor.snapshot()
     self.assertTrue(db.in_transaction);self.assertEqual(result['active_reservations']['planner_calls'],1)
     db.rollback()
    self.assertEqual(governor.snapshot()['reservation_states'],{})
 def test_future_v8_is_not_mistaken_for_legacy_clock_ordering(self):
    owner,calls,_=self.owner(8000)
    token=process_tape.ACTIVE.set(types.SimpleNamespace(replaying=True,version='bounded-worker-tape-v8'))
    try:
     with patch('investigator.process_tape.clock',side_effect=lambda name,fn:fn()):owner.snapshot()
    finally:process_tape.ACTIVE.reset(token)
    self.assertEqual(len(calls),1)
 def test_v8_registry_keeps_v6_and_v7_in_every_supported_feature_class(self):
    self.assertEqual(process_tape.VERSION,'bounded-worker-tape-v8')
    for versions in (process_tape.SUPPORTED_VERSIONS,process_tape.PINNED_VERSIONS,process_tape.ACCOUNTED_VERSIONS,process_tape.SMART_VERSIONS,process_tape.CODE_VERSIONS):
     self.assertIn('bounded-worker-tape-v6',versions);self.assertIn('bounded-worker-tape-v7',versions);self.assertIn('bounded-worker-tape-v8',versions)
 def test_four_concurrent_reservations_with_history_have_no_counter_leaks(self):
    helper=fixture.AdaptiveTests();helper.setUp();self.addCleanup(helper.doCleanups);helper.store.environment='development'
    policy={'environment':'development','daily_limits':{'planner_calls':100,'cloud_calls':100,'input_characters':100000,'output_tokens':100000},'max_inflight_planners':4,'no_progress_limit':2}
    governor=UsageGovernor(helper.runtime,policy,helper.clock)
    amount=json.dumps({'planner_calls':1,'cloud_calls':0,'input_characters':1,'output_tokens':1})
    with helper.runtime.db() as db:
     db.executemany('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,?,?,?,?)',[('development','historic-'+str(i),'model','1900-01-01','planner',amount,json.dumps({'input_tokens':0,'output_tokens':1}),'SETTLED','history',helper.clock()-172800) for i in range(8000)])
    def work(i):
     session='parallel-'+str(i)
     with helper.runtime.db() as db:
      db.execute('BEGIN IMMEDIATE');governor.reserve(db,session,'model','planner',100,output_tokens=500)
     with helper.runtime.db() as db:
      db.execute('BEGIN IMMEDIATE');governor.settle(db,session,'model',{'input_tokens':25,'output_tokens':10})
     return governor.metered_read(session,'read',lambda:i)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:self.assertEqual(list(pool.map(work,range(4))),list(range(4)))
    result=governor.snapshot();self.assertEqual(result['reserved_today'],{'planner_calls':4,'cloud_calls':4,'input_characters':400,'output_tokens':2000});self.assertEqual(result['charged_today']['output_tokens'],40);self.assertTrue(all(v==0 for v in result['active_reservations'].values()));self.assertEqual(result['reservation_states'],{'SETTLED':8008})
if __name__=='__main__':unittest.main()

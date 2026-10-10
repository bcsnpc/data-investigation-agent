"""Incremental shared inputs conserve history without holding the write lock to serialize it."""
import concurrent.futures,copy,json,sqlite3,tempfile,time,unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
from investigator import budget_delta as delta,process_tape as journal,read_allowance
from investigator.usage_governance import UsageGovernor
from test_process_tape import bootstrap
import test_adaptive_investigation as fixture

class BudgetDeltaTests(unittest.TestCase):
 def setUp(self):
    self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
    self.db=sqlite3.connect(self.root/'live.sqlite');self.addCleanup(self.db.close)
    self.db.execute('CREATE TABLE adaptive_usage(environment TEXT,session_id TEXT,reservation_key TEXT,day TEXT,kind TEXT,reserved TEXT,actual TEXT,status TEXT,policy_hash TEXT,created REAL,PRIMARY KEY(environment,session_id,reservation_key))')
    read_allowance.initialize(self.db);delta.initialize(self.db)
    self.db.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,?,?,?,?)',self.row('external','old'));self.db.commit()
    with closing(sqlite3.connect(self.root/'catalog.sqlite')) as saved:self.db.backup(saved)
    self.boot=bootstrap();self.boot['state']={'budget_checkpoint':'DELTA_V1','artifacts':{'catalog.sqlite':journal.sha((self.root/'catalog.sqlite').read_bytes())}}
 def row(self,session,key,environment='test'):
    return [environment,session,key,'1900-01-01','cloud',json.dumps({'cloud_calls':1}),None,'SETTLED','policy',1000.0]
 def tape(self,name='tape.json'):
    tape=journal.Tape(self.root/name,self.boot);delta.prepare(tape,self.root/'catalog.sqlite','test');return tape
 def snapshot(self,db):
    return {table:[list(r) for r in db.execute('SELECT * FROM '+table+' WHERE environment=? ORDER BY '+','.join(delta.layout(db)[table]['keys']),('test',))] for table in delta.TABLES}
 def test_added_updated_deleted_old_rows_reconstruct_exact_state_and_keep_owned(self):
    tape=self.tape();owned={'owner'}
    self.db.execute('UPDATE adaptive_usage SET actual=?,status=? WHERE session_id=?',('{"rows":4}','UNCERTAIN','external'))
    self.db.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,?,?,?,?)',self.row('external','new'))
    self.db.execute('DELETE FROM adaptive_usage WHERE reservation_key=?',('old',))
    self.db.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,?,?,?,?)',self.row('owner','own'))
    delta.checkpoint(tape,self.db,'test',owned);tape.finish({});expected=self.snapshot(self.db)
    changes=json.loads(journal.validate_event(tape.events[1],2));self.assertEqual(changes['count'],3);self.assertTrue(all('owner' not in str(r) for r in changes['changes']))
    with closing(sqlite3.connect(self.root/'replay.sqlite')) as target:
     with closing(sqlite3.connect(self.root/'catalog.sqlite')) as saved:saved.backup(target)
     target.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,?,?,?,?)',self.row('owner','own'));target.commit()
     replay=journal.Tape(tape.path);delta.prepare(replay,self.root/'catalog.sqlite','test');delta.checkpoint(replay,target,'test',owned);replay.finish({})
     self.assertEqual(self.snapshot(target),expected)
 def test_environment_change_conserves_departure_and_arrival(self):
    tape=self.tape();self.db.execute('UPDATE adaptive_usage SET environment=? WHERE session_id=?',('other','external'))
    delta.checkpoint(tape,self.db,'test',set());tape.finish({})
    body=json.loads(journal.validate_event(tape.events[1],2));self.assertEqual(body['count'],1);self.assertIsNone(body['changes'][0]['after'])
    arrivals=list(self.db.execute("SELECT before_row,after_row FROM budget_mutations WHERE environment='other'"));self.assertEqual(len(arrivals),1);self.assertIsNone(arrivals[0][0]);self.assertEqual(json.loads(arrivals[0][1])[0],'other')
 def test_external_session_primary_key_change_is_conserved(self):
    tape=self.tape();self.db.execute("UPDATE adaptive_usage SET session_id='renamed' WHERE session_id='external'")
    delta.checkpoint(tape,self.db,'test',set());tape.finish({})
    self.assertNotIn(('test','external','old'),tape.budget_delta['states']['adaptive_usage']);self.assertIn(('test','renamed','old'),tape.budget_delta['states']['adaptive_usage'])
 def test_cross_ownership_change_refuses_instead_of_skipping(self):
    tape=self.tape();self.db.execute("UPDATE adaptive_usage SET session_id='owner' WHERE session_id='external'")
    with self.assertRaisesRegex(journal.TapeError,'OWNERSHIP_CHANGE'):delta.checkpoint(tape,self.db,'test',{'owner'})
 def test_missing_capture_trigger_and_journal_pruning_refuse(self):
    tape=self.tape()
    with self.assertRaisesRegex(sqlite3.IntegrityError,'append-only'):self.db.execute('DELETE FROM budget_mutations')
    self.db.execute('DROP TRIGGER budget_delta_adaptive_usage_update')
    with self.assertRaisesRegex(journal.TapeError,'JOURNAL_INCOMPLETE'):delta.checkpoint(tape,self.db,'test',set())
 def test_wrong_trigger_body_under_correct_name_cannot_be_blessed_at_startup(self):
    self.db.execute('DROP TRIGGER budget_delta_adaptive_usage_update')
    self.db.execute('CREATE TRIGGER budget_delta_adaptive_usage_update AFTER UPDATE ON adaptive_usage BEGIN SELECT 1; END')
    with self.assertRaisesRegex(journal.TapeError,'JOURNAL_CHANGED'):delta.initialize(self.db)
    with closing(sqlite3.connect(self.root/'wrong.sqlite')) as saved:self.db.backup(saved)
    tape=journal.Tape(self.root/'wrong.json',bootstrap())
    tape.bootstrap['state']={'budget_checkpoint':'DELTA_V1'}
    with self.assertRaisesRegex(journal.TapeError,'JOURNAL_CHANGED'):delta.prepare(tape,self.root/'wrong.sqlite','test')
 def test_corrupt_delta_before_image_and_owned_rows_are_refused(self):
    tape=self.tape();self.db.execute("UPDATE adaptive_usage SET status='UNCERTAIN' WHERE session_id='external'");delta.checkpoint(tape,self.db,'test',set());tape.finish({})
    body=json.loads(journal.validate_event(tape.events[1],2))
    for corruption,error in [('before','BEFORE_DIFFERS'),('owned','OWNED_ROW'),('count','DELTA_SCOPE')]:
     replay=journal.Tape(tape.path);delta.prepare(replay,self.root/'catalog.sqlite','test');changed=copy.deepcopy(body)
     if corruption=='before':changed['changes'][0]['before'][7]='CORRUPT'
     elif corruption=='owned':changed['owned_sessions']=['owner'];changed['changes'][0]['after'][1]='owner'
     else:changed['count']+=1
     replay.take=lambda kind:journal.bytes_of(changed)
     with self.assertRaisesRegex(journal.TapeError,error):delta.checkpoint(replay,self.db,'test',{'owner'} if corruption=='owned' else set())
 def test_baseline_hash_and_unprepared_pin_refuse(self):
    tape=self.tape();tape.budget_delta=None
    with self.assertRaisesRegex(journal.TapeError,'NOT_PREPARED'):delta.checkpoint(tape,self.db,'test',set())
    self.boot['state']['artifacts']['catalog.sqlite']='bad';fresh=journal.Tape(self.root/'bad.json',self.boot)
    with self.assertRaisesRegex(journal.TapeError,'BASELINE_HASH'):delta.prepare(fresh,self.root/'catalog.sqlite','test')
 def test_memory_baseline_is_never_prepared_under_write_lock(self):
    tape=self.tape();tape.budget_delta=None;self.db.execute('BEGIN IMMEDIATE')
    with self.assertRaisesRegex(journal.TapeError,'INSIDE_TRANSACTION'):delta.prepare_memory(tape,self.db,'test')
 def test_owned_uncommitted_rows_do_not_advance_cursor_on_caller_rollback(self):
    tape=self.tape()
    self.db.execute('BEGIN IMMEDIATE')
    self.db.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,?,?,?,?)',self.row('owner','rolled-back'))
    delta.checkpoint(tape,self.db,'test',{'owner'})
    self.db.rollback()
    self.db.execute('BEGIN IMMEDIATE')
    self.db.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,?,?,?,?)',self.row('owner','committed'))
    delta.checkpoint(tape,self.db,'test',{'owner'});self.db.commit();tape.finish({})
    bodies=[json.loads(journal.validate_event(e,n)) for n,e in enumerate(tape.events,1) if e['kind']=='BUDGET_INPUT']
    self.assertEqual(bodies[0]['from'],bodies[0]['to']);self.assertEqual(bodies[1]['from'],bodies[1]['to'])
    with closing(sqlite3.connect(self.root/'replay.sqlite')) as target:
     with closing(sqlite3.connect(self.root/'catalog.sqlite')) as saved:saved.backup(target)
     replay=journal.Tape(tape.path);delta.prepare(replay,self.root/'catalog.sqlite','test')
     target.execute('BEGIN IMMEDIATE');target.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,?,?,?,?)',self.row('owner','rolled-back'));delta.checkpoint(replay,target,'test',{'owner'});target.rollback()
     target.execute('BEGIN IMMEDIATE');target.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,?,?,?,?)',self.row('owner','committed'));delta.checkpoint(replay,target,'test',{'owner'});target.commit();replay.finish({})
     self.assertEqual(self.snapshot(target),self.snapshot(self.db))
 def test_four_real_tapes_with_8000_history_rows_replay_and_settle_exactly(self):
    helper=fixture.AdaptiveTests();helper.setUp();self.addCleanup(helper.doCleanups);helper.store.environment='development'
    policy={'environment':'development','daily_limits':{'planner_calls':100,'cloud_calls':100,'input_characters':100000,'output_tokens':100000},'max_inflight_planners':4,'no_progress_limit':2}
    gov=UsageGovernor(helper.runtime,policy,lambda:journal.clock('governor',lambda:1000))
    amount=json.dumps({'planner_calls':1,'cloud_calls':0,'input_characters':1,'output_tokens':1})
    with helper.runtime.db() as db:db.executemany('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,?,?,?,?)',[('development','historic-'+str(i),'model','1900-01-01','planner',amount,'{"output_tokens":1}','SETTLED','history',-171800) for i in range(8000)])
    tapes=[]
    for i in range(4):
     root=self.root/str(i);root.mkdir()
     with helper.runtime.db() as db,closing(sqlite3.connect(root/'catalog.sqlite')) as saved:db.backup(saved)
     boot=bootstrap();boot['state']={'budget_checkpoint':'DELTA_V1','artifacts':{'catalog.sqlite':journal.sha((root/'catalog.sqlite').read_bytes())}}
     tape=journal.Tape(root/'tape.json',boot);delta.prepare(tape,root/'catalog.sqlite','development');tapes.append(tape)
    def work(i,governor,runtime,tape):
     session='taped-parallel-'+str(i)
     with journal.active(tape):
      if i==0:
       with runtime.db() as db:
        db.execute('BEGIN IMMEDIATE');governor.reserve(db,session,'caller-rollback','planner',100,output_tokens=500);db.rollback()
      with runtime.db() as db:db.execute('BEGIN IMMEDIATE');governor.reserve(db,session,'model','planner',100,output_tokens=500)
      with runtime.db() as db:db.execute('BEGIN IMMEDIATE');governor.settle(db,session,'model',{'input_tokens':25,'output_tokens':10})
      result=governor.metered_read(session,'read',lambda:i);governor.snapshot();tape.finish({'i':result})
     return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
     self.assertEqual([f.result() for f in [pool.submit(work,i,gov,helper.runtime,tapes[i]) for i in range(4)]],list(range(4)))
    totals=gov.snapshot();self.assertEqual(totals['reserved_today'],{'planner_calls':4,'cloud_calls':4,'input_characters':400,'output_tokens':2000});self.assertEqual(totals['charged_today']['output_tokens'],40);self.assertTrue(all(v==0 for v in totals['active_reservations'].values()));self.assertEqual(totals['reservation_states'],{'SETTLED':8008})
    for i,tape in enumerate(tapes):
     other=fixture.AdaptiveTests();other.setUp();self.addCleanup(other.doCleanups);other.store.environment='development'
     replaygov=UsageGovernor(other.runtime,policy,lambda:journal.clock('governor',lambda:1000))
     with closing(sqlite3.connect(tape.path.parent/'catalog.sqlite')) as saved,other.runtime.db() as db:saved.backup(db)
     before=tape.path.read_bytes();replay=journal.Tape(tape.path);delta.prepare(replay,tape.path.parent/'catalog.sqlite','development')
     self.assertEqual(work(i,replaygov,other.runtime,replay),i);self.assertEqual(tape.path.read_bytes(),before)
     self.assertLess(len(before),100000) # no history serialization in admission events

if __name__=='__main__':unittest.main()

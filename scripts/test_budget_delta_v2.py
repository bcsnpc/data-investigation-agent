"""Lossless v2 journal tests; synthetic SQLite only, no estate/model calls."""
import importlib.util,json,math,random,sqlite3,struct,sys,tempfile,threading,unittest,concurrent.futures
from unittest.mock import patch
from investigator import process_tape as journal
from investigator.usage_governance import UsageGovernor
from test_process_tape import bootstrap
import test_adaptive_investigation as fixture
from pathlib import Path
from contextlib import closing
sys.path.insert(0,'scripts')
from investigator import budget_delta as legacy
from investigator.process_tape import TapeError
from investigator import budget_delta_v2 as v2
ENV='synthetic';VALUE=1791667247.7417014

def schema(db):
 for table in v2.TABLES:db.execute('CREATE TABLE '+table+'(environment TEXT,id TEXT,session_id TEXT,created REAL,expires REAL,status TEXT,PRIMARY KEY(environment,id))')
 legacy.initialize(db);db.commit()
class Tape:
 version='bounded-worker-tape-v8';replaying=False
 def __init__(self):self.bootstrap={'state':{'budget_checkpoint':'DELTA_V2'}};self.events=[]
 def event(self,kind,body):self.events.append((kind,body))
 def peek(self,kind):return None
class LosslessProposalTests(unittest.TestCase):
 def test_all_four_tables_real_slots_are_exact(self):
  with closing(sqlite3.connect(':memory:')) as db:
   schema(db);v2.initialize(db)
   for table in v2.TABLES:db.execute('INSERT INTO '+table+' VALUES(?,?,?,?,?,?)',(ENV,table,'external',VALUE,VALUE+0.1,'RESERVED'))
   for table,b in db.execute('SELECT table_name,after_row FROM budget_mutations_v2'):
    row=v2.decode_row(b);self.assertEqual(row[3],VALUE);self.assertEqual(row[4],VALUE+0.1)
    self.assertIn('$binary64',b)
 def test_random_finite_binary64_roundtrip_10000(self):
  rng=random.Random(45678)
  with closing(sqlite3.connect(':memory:')) as db:
   v2.register_codec(db)
   values=[VALUE,1e300,1e-300,0.1,-0.0]+[struct.unpack('!d',rng.randbytes(8))[0] for _ in range(10000)]
   for value in values:
    if not math.isfinite(value):continue
    wire=db.execute("SELECT json_array(json_object('$binary64',budget_real_hex_v2(?)))",(value,)).fetchone()[0]
    actual=v2.decode_row(wire)[0];self.assertEqual(actual.hex(),value.hex())
 def test_migration_preserves_legacy_journal_and_triggers(self):
  with closing(sqlite3.connect(':memory:')) as db:
   schema(db);db.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?)',(ENV,'a','external',VALUE,VALUE,'RESERVED'));db.commit()
   oldrows=list(db.execute('SELECT * FROM budget_mutations'));oldtriggers=legacy.journal_schema(db)
   v2.initialize(db);db.commit()
   self.assertEqual(list(db.execute('SELECT * FROM budget_mutations')),oldrows);self.assertEqual(legacy.journal_schema(db),oldtriggers)
   self.assertFalse(v2.enabled(type('Old',(),{'version':'bounded-worker-tape-v7','bootstrap':{'state':{'budget_checkpoint':'DELTA_V1'}}})()))
   self.assertTrue(legacy.enabled(type('Old',(),{'version':'bounded-worker-tape-v7','bootstrap':{'state':{'budget_checkpoint':'DELTA_V1'}}})()))
   db.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?)',(ENV,'b','external',VALUE,VALUE,'RESERVED'))
   for table in ('budget_mutations','budget_mutations_v2'):
    with self.assertRaises(sqlite3.IntegrityError):db.execute('DELETE FROM '+table)
 def test_strict_genuine_before_image_drift_refused(self):
  with closing(sqlite3.connect(':memory:')) as db:
   schema(db);v2.initialize(db);db.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?)',(ENV,'a','external',VALUE,VALUE,'RESERVED'));db.commit()
   tape=Tape();v2.prepare_memory(tape,db,ENV)
   cols=tape.budget_delta['schemas']['adaptive_usage']['columns'];k=(ENV,'a');tape.budget_delta['states']['adaptive_usage'][k][cols.index('created')]=math.nextafter(VALUE,math.inf)
   db.execute("UPDATE adaptive_usage SET status='SETTLED' WHERE id='a'");db.commit()
   with self.assertRaisesRegex(TapeError,'TAPE_BUDGET_DELTA_BEFORE_DIFFERS'):v2.checkpoint(tape,db,ENV,{'composer'})
 def test_missing_udf_refuses_write(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'budget.sqlite'
   with closing(sqlite3.connect(path)) as db:schema(db);v2.initialize(db);db.commit()
   with closing(sqlite3.connect(path)) as db:
    with self.assertRaisesRegex(sqlite3.OperationalError,'no such function'):db.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?)',(ENV,'a','external',VALUE,VALUE,'RESERVED'))
 def test_four_thread_fractional_created_expires_checkpoints(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'budget.sqlite'
   with closing(sqlite3.connect(path)) as db:
    schema(db);v2.initialize(db);db.commit();tape=Tape();v2.prepare_memory(tape,db,ENV)
   errors=[]
   def worker(n):
    try:
     with closing(sqlite3.connect(path,timeout=30)) as db:
      v2.register_codec(db)
      for i in range(12):
       table=v2.TABLES[i%4];identity=str(n)+'-'+str(i);created=VALUE+(n*12+i)*0.000002
       db.execute('BEGIN IMMEDIATE');db.execute('INSERT INTO '+table+' VALUES(?,?,?,?,?,?)',(ENV,identity,'external-'+str(n),created,created+0.1234567,'RESERVED'));db.commit()
       db.execute('BEGIN IMMEDIATE');db.execute('UPDATE '+table+" SET status='SETTLED' WHERE id=?",(identity,));db.commit()
    except Exception as exc:errors.append(exc)
   threads=[threading.Thread(target=worker,args=(i,)) for i in range(4)]
   for t in threads:t.start()
   for t in threads:t.join()
   self.assertEqual(errors,[])
   with closing(sqlite3.connect(path)) as db:
    v2.register_codec(db);v2.checkpoint(tape,db,ENV,{'composer'})
    self.assertEqual(len(tape.events),1);body=json.loads(tape.events[0][1]);self.assertEqual(body['count'],96)
    for table in v2.TABLES:
     columns=tape.budget_delta['schemas'][table]['columns']
     for row in db.execute('SELECT * FROM '+table):self.assertEqual(tape.budget_delta['states'][table][(ENV,row[1])],list(row))
 def test_every_actual_declared_real_column_in_four_budget_tables(self):
  from investigator import read_allowance
  with closing(sqlite3.connect(':memory:')) as db:
   db.execute('CREATE TABLE adaptive_usage(environment TEXT,session_id TEXT,reservation_key TEXT,day TEXT,kind TEXT,reserved TEXT,actual TEXT,status TEXT,policy_hash TEXT,created REAL,PRIMARY KEY(environment,session_id,reservation_key))')
   read_allowance.initialize(db)
   columns={table:list(db.execute('PRAGMA table_info('+table+')')) for table in v2.TABLES}
   legacy.initialize(db);v2.initialize(db)
   for table,info in columns.items():
    row=[ENV if r[1]=='environment' else VALUE if r[2].upper()=='REAL' else 3 if r[2].upper()=='INTEGER' else 'synthetic' for r in info]
    db.execute('INSERT INTO '+table+' VALUES('+','.join('?' for _ in row)+')',row)
    wire=db.execute('SELECT after_row FROM budget_mutations_v2 WHERE table_name=?',(table,)).fetchone()[0]
    decoded=v2.decode_row(wire)
    for index,column in enumerate(info):
     if column[2].upper()=='REAL':self.assertEqual(decoded[index],row[index],(table,column[1]))
 def test_recorded_lossless_delta_replays_exact_after_projection_of_codec(self):
  with closing(sqlite3.connect(':memory:')) as db:
   schema(db);v2.initialize(db);db.commit();record=Tape();v2.prepare_memory(record,db,ENV)
   db.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?)',(ENV,'a','external',VALUE,VALUE+0.1,'SETTLED'));db.commit();v2.checkpoint(record,db,ENV,{'composer'})
  class Replay(Tape):
   replaying=True
   def take(self,kind):
    self.assert_kind=kind;return self.body
  with closing(sqlite3.connect(':memory:')) as db:
   schema(db);v2.initialize(db);db.commit();replay=Replay();replay.body=record.events[0][1];v2.prepare_memory(replay,db,ENV);v2.checkpoint(replay,db,ENV,{'composer'})
   self.assertEqual(replay.assert_kind,'BUDGET_INPUT');row=list(db.execute('SELECT * FROM adaptive_usage').fetchone());self.assertEqual(row[3],VALUE);self.assertEqual(row[4],VALUE+0.1)
 def test_projected_version_and_pin_dispatch_preserve_old(self):
  for version,pin,expected in [('privacy-projected-tape-v1','DELTA_V1',False),('privacy-projected-tape-v2','DELTA_V2',True),('bounded-worker-tape-v7','DELTA_V2',False),('bounded-worker-tape-v8','DELTA_V1',False)]:
   self.assertEqual(v2.enabled(type('P',(),{'version':version,'bootstrap':{'state':{'budget_checkpoint':pin}}})()),expected)
 def test_checkpoint_failure_is_retained_and_replays_same_typed_code(self):
  with closing(sqlite3.connect(':memory:')) as db:
   schema(db);v2.initialize(db);db.commit();record=Tape();v2.prepare_memory(record,db,ENV)
   db.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?)',(ENV,'a','external',VALUE,VALUE,'SETTLED'));db.commit()
   record.budget_delta['states']['adaptive_usage'][(ENV,'a')]=[ENV,'a','external',math.nextafter(VALUE,math.inf),VALUE,'SETTLED']
   with self.assertRaisesRegex(TapeError,'DUPLICATE_KEY'):v2.checkpoint(record,db,ENV,{'composer'})
   self.assertEqual(record.events[0][0],'BUDGET_INPUT_FAILURE')
  class Replay(Tape):
   replaying=True
   def peek(self,kind):return self.body if kind=='BUDGET_INPUT_FAILURE' else None
   def take(self,kind):self.taken=kind;return self.body
  with closing(sqlite3.connect(':memory:')) as db:
   replay=Replay();replay.body=record.events[0][1]
   with self.assertRaisesRegex(TapeError,'DUPLICATE_KEY'):v2.checkpoint(replay,db,ENV,{'composer'})
   self.assertEqual(replay.taken,'BUDGET_INPUT_FAILURE')
 def test_all_legacy_versions_remain_dispatchable(self):
  from investigator.process_tape import SUPPORTED_VERSIONS
  from investigator.budget_checkpoint import implementation
  for number in range(1,8):
   version='bounded-worker-tape-v'+str(number);self.assertIn(version,SUPPORTED_VERSIONS)
   tape=type('P',(),{'version':version,'bootstrap':{'state':{'budget_checkpoint':'DELTA_V1'}}})()
   self.assertIs(implementation(tape),legacy if number==7 else None)
 def test_four_real_tapes_with_8000_history_rows_replay_and_settle_exactly(self):
    temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)
    helper=fixture.AdaptiveTests();helper.setUp();self.addCleanup(helper.doCleanups);helper.store.environment='development'
    policy={'environment':'development','daily_limits':{'planner_calls':100,'cloud_calls':100,'input_characters':100000,'output_tokens':100000},'max_inflight_planners':4,'no_progress_limit':2}
    gov=UsageGovernor(helper.runtime,policy,lambda:journal.clock('governor',lambda:1000.123456789))
    amount=json.dumps({'planner_calls':1,'cloud_calls':0,'input_characters':1,'output_tokens':1})
    with helper.runtime.db() as db:db.executemany('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,?,?,?,?)',[('development','historic-'+str(i),'model','1900-01-01','planner',amount,'{"output_tokens":1}','SETTLED','history',-171800) for i in range(8000)])
    tapes=[]
    for i in range(4):
     root=self.root/str(i);root.mkdir()
     with helper.runtime.db() as db,closing(sqlite3.connect(root/'catalog.sqlite')) as saved:db.backup(saved)
     boot=bootstrap();boot['state']={'budget_checkpoint':'DELTA_V2','artifacts':{'catalog.sqlite':journal.sha((root/'catalog.sqlite').read_bytes())}}
     with patch.object(journal,'VERSION','bounded-worker-tape-v8'):tape=journal.Tape(root/'tape.json',boot)
     v2.prepare(tape,root/'catalog.sqlite','development');tapes.append(tape)
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
     replaygov=UsageGovernor(other.runtime,policy,lambda:journal.clock('governor',lambda:1000.123456789))
     with closing(sqlite3.connect(tape.path.parent/'catalog.sqlite')) as saved,other.runtime.db() as db:saved.backup(db)
     before=tape.path.read_bytes();replay=journal.Tape(tape.path);v2.prepare(replay,tape.path.parent/'catalog.sqlite','development')
     self.assertEqual(work(i,replaygov,other.runtime,replay),i);self.assertEqual(tape.path.read_bytes(),before)
     self.assertLess(len(before),100000) # no history serialization in admission events

if __name__=='__main__':unittest.main()

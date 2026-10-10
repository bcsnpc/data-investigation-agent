"""Supported catalog and caller-owned writer codec regression, SQLite only."""
import sqlite3,sys,tempfile,unittest
from pathlib import Path
from contextlib import contextmanager,closing
from types import SimpleNamespace
sys.path.insert(0,'scripts')
from investigator import budget_connection as connection
from investigator import usage_governance as governance
from investigator import budget_delta_v2 as codec
class RawRuntime:
 def __init__(self,path):self.path=path;self.store=SimpleNamespace(environment='synthetic');self.config={}
 @contextmanager
 def db(self):
  with closing(sqlite3.connect(self.path)) as db:
   db.row_factory=sqlite3.Row
   with db:yield db
class WriterTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'catalog.sqlite';self.runtime=RawRuntime(self.path);self.now=1791667247.7417014
  self.policy={'environment':'synthetic','daily_limits':{'planner_calls':20,'cloud_calls':2,'input_characters':100000,'output_tokens':30000},'max_inflight_planners':2,'no_progress_limit':2}
  self.g=governance.UsageGovernor(self.runtime,self.policy,lambda:self.now)
 def test_fresh_raw_caller_reserves_and_settles_under_existing_v2_journal(self):
  with self.runtime.db() as db:self.g.reserve(db,'caller','model','planner',90,output_tokens=500)
  with self.runtime.db() as db:self.g.settle(db,'caller','model',{'input_tokens':30,'output_tokens':40,'total_tokens':70})
  with self.runtime.db() as db:
   row=db.execute('SELECT * FROM adaptive_usage').fetchone();self.assertEqual(row['status'],'SETTLED');self.assertEqual(row['created'],self.now)
   changes=[codec.decode_row(r[0]) for r in db.execute("SELECT after_row FROM budget_mutations_v2 WHERE table_name='adaptive_usage'")]
   self.assertEqual([r[-1] for r in changes],[self.now,self.now])
 def test_fresh_raw_runtime_grant_uses_exact_fractional_expiry(self):
  approval={'environment':'synthetic','batch_id':'approved','approved_by':'synthetic-owner','approval_reference':'synthetic-test','expires_at':self.now+600.0123456789,'runs':[{'session_id':'batch','purpose':'INVESTIGATION','reads':2}]}
  self.g.grant_batch(approval)
  with self.runtime.db() as db:
   row=db.execute('SELECT issued,expires FROM read_batches').fetchone();self.assertEqual(row['issued'],self.now);self.assertEqual(row['expires'],approval['expires_at'])
   self.g.reserve(db,'batch','read','cloud')
   recorded=codec.decode_row(db.execute("SELECT after_row FROM budget_mutations_v2 WHERE table_name='read_batches'").fetchone()[0])
   self.assertEqual(recorded[-2:],[self.now,approval['expires_at']])
 def test_low_level_unprepared_raw_sql_still_refuses(self):
  with self.runtime.db() as db:
   with self.assertRaisesRegex(sqlite3.OperationalError,'no such function: budget_real_hex_v2'):
    db.execute('INSERT INTO read_allocations VALUES(?,?,?,?,?)',('synthetic','raw','r',None,'INVESTIGATION'))
 def test_supported_factory_prepares_every_fresh_connection(self):
  for _ in range(2):
   with closing(connection.connect(self.path)) as db:
    self.assertEqual(db.execute('SELECT budget_real_hex_v2(?)',(self.now,)).fetchone()[0],self.now.hex())
 def test_named_catalog_fresh_connections_allow_actual_journaled_writes(self):
  from read_budget import Catalog
  from ticket_workflow import TicketStore
  from verify_reader_runtime import FixtureStore
  reader=Catalog.__new__(Catalog);reader.path=self.path
  ticket=TicketStore.__new__(TicketStore);ticket.database=self.path
  verifier=FixtureStore.__new__(FixtureStore);verifier.database=self.path
  factories=(reader.db,lambda:closing(ticket.connect()),verifier.connect)
  for i,factory in enumerate(factories):
   for j in range(2):
    with factory() as db:
     self.assertEqual(db.execute('SELECT budget_real_hex_v2(?)',(self.now,)).fetchone()[0],self.now.hex())
     db.execute('INSERT INTO read_allocations VALUES(?,?,?,?,?)',('synthetic','factory',str(i)+':'+str(j),None,'INVESTIGATION'))
     db.commit()
  with self.runtime.db() as db:
   self.assertEqual(db.execute('SELECT count(*) FROM read_allocations').fetchone()[0],6)
   self.assertEqual(db.execute("SELECT count(*) FROM budget_mutations_v2 WHERE table_name='read_allocations'").fetchone()[0],6)
 def test_twenty_fresh_raw_writers_surface_every_thread_failure(self):
  from threading import Thread, Lock
  unexpected=[];admitted=[];refused=[];lock=Lock()
  def attempt(i):
   try:
    with self.runtime.db() as db:
     db.execute('BEGIN IMMEDIATE')
     self.g.reserve(db,'thread-'+str(i),'read','cloud')
    with lock:admitted.append(i)
   except governance.UsageHold:
    with lock:refused.append(i)
   except BaseException as exc:
    with lock:unexpected.append((i,type(exc).__name__,str(exc)))
  threads=[Thread(target=attempt,args=(i,)) for i in range(20)]
  for thread in threads:thread.start()
  for thread in threads:thread.join()
  self.assertEqual(unexpected,[])
  self.assertEqual(len(admitted),2)
  self.assertEqual(len(refused),18)
  self.assertEqual(len(admitted)+len(refused),20)
if __name__=='__main__':unittest.main()

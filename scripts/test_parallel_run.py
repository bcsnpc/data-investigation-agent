import json,sqlite3,tempfile,threading,unittest
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from investigator.parallel_run import run_estates,Concurrency
from investigator.process_tape import ACTIVE


class ParallelRunTests(unittest.TestCase):
    def test_stable_ramp_and_timeout_or_throttle_reduction_do_not_change_policy(self):
        policy=Concurrency();clean=[{'status':'RETURNED','result':{}}]
        self.assertEqual(policy.workers,4)
        self.assertEqual(policy.observe(clean)['after'],6)
        self.assertEqual(policy.observe(clean)['after'],8)
        self.assertEqual(policy.observe(clean)['after'],8)
        self.assertEqual(policy.observe([{'status':'FAILED','error_type':'TimeoutError'}])['after'],7)
        self.assertEqual(policy.observe([{'status':'RETURNED','result':{'http_status':429}}])['after'],6)
        self.assertEqual(policy.observe([{'status':'FAILED','error_type':'ValueError'}])['after'],6)

    def test_external_parallel_budget_checkpoint_replays_without_overwriting_owned_charge(self):
        from investigator.tape_budget import checkpoint,TABLES
        class Journal:
            replaying=False
            index=0
            def __init__(self):self.events=[]
            def event(self,kind,body):self.events.append({'kind':kind,'body':body})
            def take(self,kind):
                event=self.events[self.index];self.index+=1
                if event['kind']!=kind:raise AssertionError('event differs')
                return event['body']
        with closing(sqlite3.connect(':memory:')) as db:
            for table in TABLES:
                db.execute('CREATE TABLE '+table+'(environment TEXT,session_id TEXT,amount INTEGER)')
                db.execute('INSERT INTO '+table+' VALUES(?,?,?)',('estate','own',1))
                db.execute('INSERT INTO '+table+' VALUES(?,?,?)',('estate','other',7))
            tape=Journal();token=ACTIVE.set(tape)
            try:
                checkpoint(SimpleNamespace(environment='estate'),db,'own')
                for table in TABLES:
                    db.execute('UPDATE '+table+' SET amount=99 WHERE session_id="other"')
                    db.execute('UPDATE '+table+' SET amount=2 WHERE session_id="own"')
                tape.replaying=True
                checkpoint(SimpleNamespace(environment='estate'),db,'own')
                for table in TABLES:
                    self.assertEqual(dict(db.execute('SELECT session_id,amount FROM '+table)),{'own':2,'other':7})
            finally:ACTIVE.reset(token)

    def test_four_isolated_contexts_share_atomic_budget_then_switch_estate(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);database=root/'budget.sqlite'
            with closing(sqlite3.connect(database)) as db:
                db.execute('CREATE TABLE charges(id TEXT PRIMARY KEY)');db.commit()
            def factory(slot):
                store=SimpleNamespace(database=database)
                return SimpleNamespace(agent=SimpleNamespace(governor=SimpleNamespace(runtime=SimpleNamespace(store=store))))
            barrier=threading.Barrier(4);seen=[];lock=threading.Lock()
            def execute(workspace,slot):
                self.assertIsNone(ACTIVE.get())
                if slot.estate=='first':barrier.wait(timeout=10)
                else:self.assertEqual(sum(estate=='first' for estate in seen),4)
                token=ACTIVE.set(slot.run_id)
                try:
                    with closing(sqlite3.connect(database,timeout=10)) as db:
                        db.execute('BEGIN IMMEDIATE');db.execute('INSERT INTO charges VALUES(?)',(slot.run_id,));db.commit()
                    self.assertEqual(ACTIVE.get(),slot.run_id)
                    with lock:seen.append(slot.estate)
                    return {'ticket_id':slot.run_id}
                finally:ACTIVE.reset(token)
            outer=ACTIVE.set('caller-tape')
            try:
                result=run_estates([('first',[(str(i),{}) for i in range(4)]),('second',[('x',{})])],root=root/'runs',
                    budget_database=database,workspace_factory=factory,execute=execute)
                self.assertEqual(ACTIVE.get(),'caller-tape')
            finally:ACTIVE.reset(outer)
            self.assertFalse(result['stopped']);self.assertEqual(len(result['results']),5)
            self.assertEqual(len(list((root/'runs').glob('*/control.jsonl'))),5)
            with closing(sqlite3.connect(database)) as db:self.assertEqual(db.execute('SELECT count(*) FROM charges').fetchone()[0],5)

    def test_failure_is_preserved_and_no_replacement_or_next_estate_is_started(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'budget.sqlite'
            def factory(slot):return SimpleNamespace(agent=SimpleNamespace(governor=SimpleNamespace(runtime=SimpleNamespace(store=SimpleNamespace(database=path)))))
            def fail(workspace,slot):raise RuntimeError('retained failure')
            result=run_estates([('one',[('a',{}),('b',{})]),('two',[('c',{})])],root=Path(folder)/'runs',
                budget_database=path,workspace_factory=factory,execute=fail,workers=1)
            self.assertTrue(result['stopped']);self.assertEqual(len(result['results']),1)
            self.assertEqual(result['results'][0]['error_message'],'retained failure')
            recorded=json.loads(next((Path(folder)/'runs').glob('*/result.json')).read_text())
            self.assertEqual(recorded,result['results'][0])

    def test_reused_agent_or_separate_budget_is_refused_before_execution(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'budget.sqlite';called=[]
            workspace=SimpleNamespace(agent=SimpleNamespace(governor=SimpleNamespace(runtime=SimpleNamespace(store=SimpleNamespace(database=path)))))
            result=run_estates([('estate',[('a',{}),('b',{})])],root=Path(folder)/'runs',budget_database=path,
                workspace_factory=lambda slot:workspace,execute=lambda w,s:called.append(s.label),workers=1)
            self.assertEqual(called,['a']);self.assertEqual(result['results'][1]['status'],'FAILED')


if __name__=='__main__':unittest.main()

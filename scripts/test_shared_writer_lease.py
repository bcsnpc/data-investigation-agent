import json,os,subprocess,sys,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from investigator.shared_state import SharedState,StateConflict
from investigator.shared_writer_lease import isolated,acquire,release,require,OWNER_ENV,LEASE_ENV

class WriterLeaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'state.sqlite';self.state=SharedState.offline(self.path);self.state.migrate()
        self.clean=patch.dict(os.environ);self.clean.start();self.addCleanup(self.clean.stop)
        os.environ.pop(LEASE_ENV,None)
        self.args=dict(owner='isolated-job',lease_id='single-attempt-id',expires_at=time.time()+120,approval='Owner test decision')
    def test_foreign_owner_refuses_same_owner_child_inherits(self):
        with isolated(self.state,**self.args):
            self.state.put('test','owner',{'ok':True})
            with patch.dict(os.environ,{OWNER_ENV:'other'}):
                with self.assertRaisesRegex(StateConflict,'OWNED_BY_ANOTHER'):self.state.put('test','other',{})
            command='from investigator.shared_state import SharedState;import sys;s=SharedState.offline(sys.argv[1]);s.put("test","child",{"ok":True})'
            env=dict(os.environ,PYTHONPATH=str(Path(__file__).parent))
            result=subprocess.run([sys.executable,'-c',command,str(self.path)],env=env,capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(self.state.get('test','child')['body'],{'ok':True})
    def test_exception_releases_and_restores_process_owner(self):
        os.environ[OWNER_ENV]='controller'
        with self.assertRaisesRegex(RuntimeError,'primary'):
            with isolated(self.state,**self.args):raise RuntimeError('primary')
        self.assertEqual(os.environ[OWNER_ENV],'controller');self.assertNotIn(LEASE_ENV,os.environ)
        self.assertEqual(self.state.get('application_writer_lease','exclusive')['body']['status'],'RELEASED')
    def test_expiry_refuses_owner_but_control_release_remains_possible(self):
        lease=acquire(self.state,**self.args)
        with patch.dict(os.environ,{OWNER_ENV:lease['owner'],LEASE_ENV:lease['lease_id']}),patch('investigator.shared_writer_lease.time.time',return_value=lease['expires_at']+1):
            with self.assertRaisesRegex(StateConflict,'EXPIRED'):self.state.put('test','late',{})
            release(self.state,lease)
    def test_preflight_requires_exact_live_lease_covering_deadline(self):
        with isolated(self.state,**self.args)as lease:
            declaration={k:lease[k]for k in ('owner','lease_id','expires_at')}
            require(self.state,declaration,deadline=lease['expires_at'])
            with self.assertRaisesRegex(StateConflict,'NOT_COVERED'):require(self.state,declaration,deadline=lease['expires_at']+1)
            with self.assertRaisesRegex(StateConflict,'DECLARATION_DIFFERS'):require(self.state,dict(declaration,lease_id='another'),deadline=0)
    def test_postgres_lock_timeout_rolls_back_and_closes(self):
        class DB:
            def __init__(self):self.queries=[];self.closed=False;self.rolled=False
            def execute(self,query,*args):
                self.queries.append(query)
                if 'pg_advisory_xact_lock'in query:raise TimeoutError('bounded lock timeout')
                return self
            def fetchone(self):return (None,)
            def rollback(self):self.rolled=True
            def close(self):self.closed=True
        db=DB();s=SharedState(lambda:db,backend='postgresql',mode='live')
        with self.assertRaisesRegex(TimeoutError,'bounded'):
            with s.transaction():self.fail('must not enter')
        self.assertTrue(db.closed and db.rolled)
        self.assertLess(db.queries.index("SET LOCAL lock_timeout = '5s'"),db.queries.index('SELECT pg_advisory_xact_lock(183746812)'))
    def test_work_deadline_refuses_before_any_advisory_or_budget_write(self):
        class DB:
            def __init__(self):self.queries=[]
            def execute(self,q,*a):self.queries.append(q);return self
            def fetchone(self):return (1000,)
            def rollback(self):pass
            def close(self):pass
        db=DB();s=SharedState(lambda:db,backend='postgresql',mode='live')
        with patch.dict(os.environ,{'INVESTIGATOR_CLOUD_WORK_DEADLINE':'999'}):
            with self.assertRaisesRegex(StateConflict,'CLOUD_WORK_DEADLINE_EXPIRED'):
                with s.transaction():self.fail('no admission after deadline')
        self.assertFalse(any('pg_advisory_xact_lock'in q for q in db.queries))
    def test_foreign_pg_owner_is_rejected_before_advisory_acquire(self):
        from investigator.shared_state import sha
        value=dict(self.args,issued_at=time.time(),status='ACTIVE')
        class DB:
            def __init__(self):self.query='';self.queries=[]
            def execute(self,q,*a):self.query=q;self.queries.append(q);return self
            def fetchone(self):
                if 'to_regclass'in self.query:return ('state_documents',)
                if 'clock_timestamp'in self.query:return (time.time(),)
                return (json.dumps(value),sha(value))
            def rollback(self):pass
            def close(self):pass
        db=DB();s=SharedState(lambda:db,backend='postgresql',mode='live')
        with self.assertRaisesRegex(StateConflict,'OWNED_BY_ANOTHER'):
            with s.transaction():self.fail('must not enter')
        self.assertFalse(any('pg_advisory_xact_lock'in q for q in db.queries))
    def test_lease_acquired_while_waiting_is_rechecked_after_lock(self):
        from investigator.shared_state import sha
        value=dict(self.args,issued_at=time.time(),status='ACTIVE')
        class DB:
            def __init__(self):self.query='';self.locked=False;self.rolled=False;self.closed=False
            def execute(self,q,*a):
                self.query=q
                if 'pg_advisory_xact_lock'in q:self.locked=True
                return self
            def fetchone(self):
                if 'to_regclass'in self.query:return ('state_documents',)
                if 'clock_timestamp'in self.query:return (time.time(),)
                return (json.dumps(value),sha(value))if self.locked else None
            def rollback(self):self.rolled=True
            def close(self):self.closed=True
        db=DB();s=SharedState(lambda:db,backend='postgresql',mode='live')
        with self.assertRaisesRegex(StateConflict,'OWNED_BY_ANOTHER'):
            with s.transaction():self.fail('must not enter after lease acquisition race')
        self.assertTrue(db.locked and db.rolled and db.closed)

if __name__=='__main__':unittest.main()

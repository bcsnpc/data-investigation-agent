"""Two isolated session catalogs charge one existing ledger; no estate calls."""
from contextlib import contextmanager, closing
from pathlib import Path
from types import SimpleNamespace
import sqlite3
import tempfile
import unittest
from investigator.budget_connection import connect
from investigator.shared_accounting import materialize, qualify
from investigator.usage_governance import UsageGovernor, UsageHold


class Runtime:
    def __init__(self,path,shared=None):
        self.path=path
        self.store=SimpleNamespace(environment='synthetic',shared_accounting=shared)
        self.config={'_estate':{'round':{'starts_at_epoch':0,'physical_requests':3,'restoration_reserved':1}}}
    @contextmanager
    def db(self):
        with closing(connect(self.path,shared_accounting=self.store.shared_accounting)) as db:
            db.row_factory=sqlite3.Row
            with db:yield db


class SharedAccountingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.shared=self.root/'shared.sqlite'
        self.policy={'environment':'synthetic','daily_limits':{'planner_calls':2,'cloud_calls':10,'input_characters':10000,'output_tokens':10000},'max_inflight_planners':2,'no_progress_limit':2}
        self.now=1791757247.0
        original=Runtime(self.shared)
        UsageGovernor(original,self.policy,lambda:self.now)
        with original.db() as db:
            for table in ('models','enterprise_scans','smart_tickets'):
                db.execute('CREATE TABLE '+table+'(id TEXT PRIMARY KEY,body TEXT)')
                db.execute('INSERT INTO '+table+' VALUES(?,?)',('original','immutable'))
        self.a=Runtime(self.root/'a.sqlite',self.shared)
        self.b=Runtime(self.root/'b.sqlite',self.shared)
        self.ga=UsageGovernor(self.a,self.policy,lambda:self.now)
        self.gb=UsageGovernor(self.b,self.policy,lambda:self.now)

    def test_two_catalogs_share_pot_and_daily_cap_without_reset(self):
        self.assertEqual(self.ga.metered_read('a','r',lambda:1),1)
        self.assertEqual(self.gb.metered_read('b','r',lambda:2),2)
        with self.assertRaisesRegex(UsageHold,'round physical'):
            self.ga.metered_read('a','r2',lambda:self.fail('must not execute'))
        for runtime,g,identity in ((self.a,self.ga,'a'),(self.b,self.gb,'b')):
            with runtime.db() as db:
                db.execute('BEGIN IMMEDIATE');g.reserve(db,identity,'m','planner',100,output_tokens=500)
                g.settle(db,identity,'m',{'output_tokens':20})
        with self.a.db() as db:
            with self.assertRaisesRegex(UsageHold,'Daily usage'):
                self.ga.reserve(db,'a','m2','planner',100,output_tokens=500)
        self.assertEqual(self.gb.snapshot()['reserved_today']['planner_calls'],2)
        self.assertEqual(self.ga.snapshot()['reserved_today']['cloud_calls'],2)

    def test_session_and_budget_commit_or_rollback_together(self):
        with self.a.db() as db:db.execute('CREATE TABLE local_session(id TEXT)')
        with self.assertRaisesRegex(RuntimeError,'abort'):
            with self.a.db() as db:
                db.execute('BEGIN IMMEDIATE')
                db.execute("INSERT INTO local_session VALUES('a')")
                self.ga.reserve(db,'a','r','cloud')
                raise RuntimeError('abort')
        with self.a.db() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM local_session').fetchone()[0],0)
            self.assertEqual(db.execute('SELECT count(*) FROM adaptive_usage').fetchone()[0],0)

    def test_concurrent_isolated_catalogs_cannot_over_admit_shared_pot(self):
        from concurrent.futures import ThreadPoolExecutor
        def attempt(number):
            governor=self.ga if number%2 else self.gb
            try:
                governor.metered_read('concurrent-'+str(number),'r',lambda:number)
                return 'admitted'
            except UsageHold:return 'refused'
        with ThreadPoolExecutor(max_workers=4) as pool:
            results=list(pool.map(attempt,range(20)))
        self.assertEqual(results.count('admitted'),2)
        self.assertEqual(results.count('refused'),18)
        self.assertEqual(self.ga.snapshot()['reserved_today']['cloud_calls'],2)

    def test_shared_records_and_reset_operations_are_forbidden(self):
        with self.a.db() as db:
            for sql in ('SELECT * FROM shared_budget.models','SELECT * FROM shared_budget.enterprise_scans',
                        'SELECT * FROM shared_budget.smart_tickets','DELETE FROM adaptive_usage',
                        "UPDATE adaptive_usage SET reserved='{}'",
                        'DROP TABLE shared_budget.adaptive_usage'):
                with self.assertRaises((sqlite3.DatabaseError,ValueError),msg=sql):db.execute(sql)
            with self.assertRaisesRegex(ValueError,'SINGLE_RESERVATION_REQUIRED'):
                db.executemany('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,?,?,?,?)',[])
        with closing(sqlite3.connect(self.shared)) as db:
            for table in ('models','enterprise_scans','smart_tickets'):
                self.assertEqual(db.execute('SELECT * FROM '+table).fetchall(),[('original','immutable')])

    def test_other_catalog_cannot_settle_existing_reservation_or_release_old_charge(self):
        with self.a.db() as db:
            self.ga.reserve(db,'owned-by-a','m','planner',100,output_tokens=500)
        with self.b.db() as db:
            with self.assertRaisesRegex(sqlite3.IntegrityError,'RESERVATION_NOT_OWNED'):
                self.gb.settle(db,'owned-by-a','m',{'output_tokens':0})
        with self.a.db() as db:self.ga.settle(db,'owned-by-a','m',{'output_tokens':20})
        self.assertEqual(self.gb.snapshot()['charged_today']['output_tokens'],20)

    def test_sealed_budget_baseline_replays_without_live_attachment(self):
        from investigator import budget_delta_v2 as v2
        from test_budget_delta_v2 import Tape
        clone=self.root/'replay.sqlite'
        with closing(sqlite3.connect(self.shared)) as db,closing(sqlite3.connect(clone)) as out:db.backup(out)
        self.ga.metered_read('a','r',lambda:1)
        materialize(clone,self.shared)
        before=self.shared.read_bytes()
        tape=Tape();v2.prepare(tape,clone,'synthetic')
        # Replay installation has no shared_accounting option or host ledger.
        runtime=Runtime(clone);g=UsageGovernor(runtime,self.policy,lambda:self.now)
        self.assertEqual(g.snapshot()['reserved_today']['cloud_calls'],1)
        g.metered_read('replay','r',lambda:2)
        self.assertEqual(self.shared.read_bytes(),before)
        self.assertEqual(g.snapshot()['reserved_today']['cloud_calls'],2)

    def test_sql_literals_are_never_rewritten_as_identifiers(self):
        self.assertEqual(qualify("SELECT 'adaptive_usage' FROM adaptive_usage"),"SELECT 'adaptive_usage' FROM shared_budget.adaptive_usage")

    def test_recorded_external_delta_replays_exact_from_materialized_baseline(self):
        from investigator import budget_delta_v2 as v2
        from test_budget_delta_v2 import Tape
        clone=self.root/'sealed.sqlite'
        with closing(sqlite3.connect(self.shared)) as db,closing(sqlite3.connect(clone)) as out:db.backup(out)
        materialize(clone,self.shared)
        recording=Tape();v2.prepare(recording,clone,'synthetic')
        self.ga.metered_read('other-live-session','read',lambda:1)
        with self.a.db() as db:v2.checkpoint(recording,db,'synthetic',{'owner-demo'})
        class Replay(Tape):
            replaying=True
            def take(self,kind):
                if kind!='BUDGET_INPUT':raise AssertionError(kind)
                return recording.events[0][1]
        replay=Replay();v2.prepare(replay,clone,'synthetic')
        host_before=self.shared.read_bytes()
        with closing(connect(clone)) as db:
            v2.checkpoint(replay,db,'synthetic',{'owner-demo'})
            self.assertEqual(db.execute('SELECT session_id FROM adaptive_usage').fetchall(),[('other-live-session',)])
            db.commit()
        self.assertEqual(replay.budget_delta['states'],recording.budget_delta['states'])
        self.assertEqual(self.shared.read_bytes(),host_before)


if __name__=='__main__':unittest.main()

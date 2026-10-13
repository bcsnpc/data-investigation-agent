"""Offline contract tests; PostgreSQL concurrency test is opt-in, not a mock pass."""
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from investigator.shared_state import SharedState, StateConflict, amount
from investigator.shared_tickets import SharedTickets
from investigator.onboarding import Conflict


def source():
    return {'accounts':[{'identity':'pot','unit':'PHYSICAL_REQUESTS','ceiling':'4000','protected':'95','opening':'2839','violated':False},
                        {'identity':'money','unit':'USD','ceiling':'122.932940','protected':'10','opening':'107.957725','violated':False}],
            'provenance':{'source':'synthetic-test','owner_approval':'test'}}


class SharedStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.state=SharedState.offline(Path(self.tmp.name)/'state.sqlite')
        self.state.migrate()

    def test_sqlite_cannot_be_live_even_single_worker(self):
        with self.assertRaisesRegex(ValueError,'LIVE_SHARED_STATE'):
            SharedState(lambda:None,backend='sqlite',mode='live')

    def test_migrations_are_hash_pinned_and_idempotent(self):
        self.state.migrate()
        with self.state.transaction() as db:db.execute("UPDATE state_schema_versions SET sha256='changed'")
        with self.assertRaisesRegex(StateConflict,'SCHEMA_VERSION'):
            self.state.migrate()

    def test_exact_import_preserves_totals_and_never_resets_current_charges(self):
        proof=self.state.import_accounts('one',source())
        self.assertTrue(all(r['matched'] for r in proof['accounts']))
        self.assertEqual(self.state.snapshot('money')['charged'],'107.957725')
        self.state.reserve('money','r1','w1','0.000001')
        self.assertEqual(self.state.import_accounts('one',source()),proof)
        self.assertEqual(self.state.snapshot('money')['charged'],'107.957726')
        changed=source();changed['accounts'][0]['opening']='0'
        with self.assertRaisesRegex(StateConflict,'MIGRATION_SOURCE_CHANGED'):
            self.state.import_accounts('one',changed)

    def test_float_money_refused_and_import_atomic(self):
        invalid=source();invalid['accounts'][1]['opening']=0.1
        with self.assertRaisesRegex(ValueError,'EXACT_AMOUNT'):
            self.state.import_accounts('bad',invalid)
        with self.assertRaises(KeyError):self.state.snapshot('pot')

    def test_concurrent_reservations_cannot_spend_protected_capacity(self):
        limited=source();limited['accounts'][0].update(ceiling='2845',protected='5')
        self.state.import_accounts('one',limited)
        def attempt(number):
            try:self.state.reserve('pot',str(number),'worker'+str(number),1);return True
            except StateConflict:return False
        with ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(attempt,range(16)))
        self.assertEqual(sum(results),1)
        self.assertEqual(self.state.snapshot('pot')['charged'],'2840')

    def test_unknown_usage_retained_owner_checked_and_overrun_latches(self):
        self.state.import_accounts('one',source())
        self.state.reserve('pot','first','owner',1)
        with self.assertRaisesRegex(StateConflict,'OWNER'):
            self.state.settle('pot','first','stranger',0)
        self.state.settle('pot','first','owner')
        self.assertEqual(self.state.snapshot('pot')['charged'],'2840')
        self.state.reserve('pot','second','owner',1)
        self.state.settle('pot','second','owner',2)
        with self.assertRaisesRegex(StateConflict,'LATCHED'):
            self.state.reserve('pot','third','owner',1)

    def test_reusing_admission_never_runs_another_request(self):
        self.state.import_accounts('one',source())
        self.state.reserve('pot','same','owner',1)
        with self.assertRaisesRegex(StateConflict,'ALREADY_ADMITTED'):
            self.state.reserve('pot','same','owner',1)

    def test_case_catalog_readiness_integrity_and_revision(self):
        for namespace in ('case_file','catalog','readiness'):
            self.state.put(namespace,'one',{'evidence':['receipt-id']})
            with self.assertRaises(StateConflict):self.state.put(namespace,'one',{},revision=2)
            self.assertEqual(self.state.get(namespace,'one')['body'],{'evidence':['receipt-id']})
        with self.state.transaction() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM estate_graph_nodes').fetchone()[0],0)
            self.assertEqual(db.execute('SELECT count(*) FROM estate_graph_edges').fetchone()[0],0)

    def test_ticket_contract_restart_idempotency_stale_revision(self):
        tickets=SharedTickets(self.state)
        first=tickets.submit({'text':'Question'},'idempotency')
        self.assertEqual(SharedTickets(self.state).submit({'text':'Question'},'idempotency'),first)
        with self.assertRaises(Conflict):tickets.submit({'text':'Changed'},'idempotency')
        saved=tickets.update(first['ticket']['id'],0,lambda t:t)
        self.assertEqual(saved['revision'],1)
        with self.assertRaises(Conflict):tickets.update(first['ticket']['id'],0,lambda t:t)

    def test_cloud_ticket_factory_uses_shared_repository(self):
        from investigator.ticket_state import Tickets
        with patch('investigator.shared_state.configured_state',return_value=self.state):
            self.assertIsInstance(Tickets(object()),SharedTickets)

    def test_cloud_usage_cannot_fall_back_to_sqlite_authority(self):
        from investigator.usage_governance import UsageGovernor,UsageHold
        with patch('investigator.shared_state.configured_state',return_value=self.state):
            with self.assertRaisesRegex(UsageHold,'POSTGRES_USAGE_GOVERNOR_NOT_MIGRATED'):
                UsageGovernor(None,None,None)


@unittest.skipUnless(os.environ.get('DIA_TEST_POSTGRES_DSN'),'local PostgreSQL DSN not configured')
class PostgreSQLTests(SharedStateTests):
    def setUp(self):
        # A dedicated disposable local test database only, never production.
        import psycopg
        from uuid import uuid4
        self.schema='test_'+uuid4().hex
        dsn=os.environ['DIA_TEST_POSTGRES_DSN']
        with psycopg.connect(dsn) as db:db.execute('CREATE SCHEMA '+self.schema)
        def connect():
            db=psycopg.connect(dsn)
            db.execute('SET search_path TO '+self.schema)
            return db
        self.state=SharedState(connect,backend='postgresql',mode='live');self.state.migrate()
        def cleanup():
            with psycopg.connect(dsn) as db:db.execute('DROP SCHEMA '+self.schema+' CASCADE')
        self.addCleanup(cleanup)


if __name__=='__main__':unittest.main()

from concurrent.futures import ThreadPoolExecutor
import copy
import json
import os
from pathlib import Path
import sqlite3
from unittest.mock import patch
import unittest
from investigator.shared_state import SharedState,StateConflict
from investigator.shared_usage import SharedUsage,export_usage,import_usage
from investigator.usage_governance import UsageGovernor,UsageHold
from read_budget import Catalog
import test_read_budget as read_budget_tests


class SharedReadBudgetTests(read_budget_tests.ReadBudgetTests):
    """Run established read-budget cases through the new authoritative backend."""
    def setUp(self):
        super().setUp()
        self.state=SharedState.offline(self.folder/'shared-state.sqlite');self.state.migrate()
        with self.runtime.db() as db:
            source=export_usage(db,'estate',self.policy,None)
        self.proof=import_usage(self.state,'initial',source)
        self.g.shared=SharedUsage(self.g,self.state,owner='worker-one')

    def test_legacy_rows_count_without_rewriting(self):
        # Legacy means imported history, not deletion from a reporting mirror.
        legacy=Catalog(self.folder/'legacy.sqlite','legacy')
        policy=copy.deepcopy(self.policy);policy['environment']='legacy'
        old=UsageGovernor(legacy,policy,lambda:self.now)
        with legacy.db() as db:
            old.reserve(db,'past','one','cloud');old.settle(db,'past','one')
            db.execute('DELETE FROM read_allocations')
            source=export_usage(db,'legacy',policy,None)
        import_usage(self.state,'legacy',source)
        old.shared=SharedUsage(old,self.state,owner='worker-one')
        self.assertEqual(old.snapshot()['read_allowance']['ordinary_charged'],1)
        with legacy.db() as db:self.assertEqual(export_usage(db,'legacy',policy,None),source)

    def test_actual_governor_factory_uses_postgres_and_requires_import(self):
        mirror=Catalog(self.folder/'new-job.sqlite','estate')
        with patch('investigator.shared_state.configured_state',return_value=self.state),patch.dict(os.environ,{'INVESTIGATOR_WORKER_ID':'fresh-worker'}):
            shared=UsageGovernor(mirror,self.policy,lambda:self.now)
        self.assertIsInstance(shared.shared,SharedUsage)
        self.reserve('from-worker-one')
        with mirror.db() as db:
            shared.reserve(db,'from-fresh-worker','one','cloud')
        with self.assertRaises(UsageHold):self.reserve('over-limit')
        self.assertEqual(shared.snapshot()['read_allowance']['ordinary_charged'],2)

    def test_migration_hash_and_row_conservation(self):
        self.assertTrue(all(t['matched'] and t['sha256_before']==t['sha256_after'] for t in self.proof['tables']))
        with self.runtime.db() as db:source=export_usage(db,'estate',self.policy,None)
        self.assertEqual(import_usage(self.state,'initial',source),self.proof)
        source['policy']['daily_limits']['cloud_calls']=3
        with self.assertRaisesRegex(StateConflict,'SOURCE_CHANGED'):import_usage(self.state,'initial',source)

    def test_settlement_cannot_cross_worker_ownership(self):
        self.reserve('one')
        other=SharedUsage(self.g,self.state,owner='other-worker')
        with self.runtime.db() as db:
            with self.assertRaisesRegex(UsageHold,'owner differs'):other.settle(db,'one','one')
        self.assertEqual(self.g.snapshot()['reservation_states'],{'RESERVED':1})

    def test_private_catalog_rollback_never_refunds_shared_reservation(self):
        with self.assertRaises(RuntimeError):
            with self.runtime.db() as db:
                self.g.reserve(db,'crashed','one','cloud')
                raise RuntimeError('simulate crash after PG commit before local commit')
        self.assertEqual(self.g.snapshot()['read_allowance']['ordinary_charged'],1)
        with self.runtime.db() as db:self.g.shared.mirror(db)
        with self.runtime.db() as db:self.assertEqual(db.execute('SELECT count(*) FROM adaptive_usage').fetchone()[0],1)

    def test_model_overrun_latches_until_explicit_ack_and_preserves_counts(self):
        with self.runtime.db() as db:
            self.g.reserve(db,'model','one','planner',10,output_tokens=1500)
            self.g.settle(db,'model','one',{'output_tokens':2504})
        with self.assertRaisesRegex(UsageHold,'exceeded reservation'):self.reserve('new-read')
        approval={'owner':'test-owner','approved_at':'2026-10-12','reason':'synthetic test correction','corrected_output_tokens':3000}
        self.g.acknowledge_violation('model','one',approval)
        self.reserve('new-read')
        self.assertEqual(self.g.snapshot()['charged_today']['output_tokens'],2504)

    def test_migrating_open_reservation_refuses_instead_of_resetting(self):
        legacy=Catalog(self.folder/'inflight.sqlite','inflight')
        policy=copy.deepcopy(self.policy);policy['environment']='inflight'
        old=UsageGovernor(legacy,policy,lambda:self.now)
        with legacy.db() as db:
            old.reserve(db,'active','one','cloud')
            source=export_usage(db,'inflight',policy,None)
        with self.assertRaisesRegex(StateConflict,'DRAINED_WORKERS'):import_usage(self.state,'inflight',source)

    def test_pot_protects_reserve_and_restoration_consumes_it(self):
        policy=copy.deepcopy(self.policy);policy['environment']='round'
        limits={'starts_at_epoch':0,'physical_requests':3,'restoration_reserved':1}
        runtime=Catalog(self.folder/'round.sqlite','round',{'_estate':{'round':limits}})
        g=UsageGovernor(runtime,policy,lambda:self.now)
        with runtime.db() as db:source=export_usage(db,'round',policy,limits)
        import_usage(self.state,'round',source);g.shared=SharedUsage(g,self.state,owner='round-worker')
        approval=self.approval();approval['environment']='round';approval['runs'][0]['reads']=3
        g.grant_batch(approval)
        with runtime.db() as db:
            g.reserve(db,'trial','one','cloud');g.reserve(db,'trial','two','cloud')
        with self.assertRaisesRegex(UsageHold,'restoration capacity'):
            with runtime.db() as db:g.reserve(db,'trial','three','cloud')
        self.assertEqual(g.restoration_read('restore','one',lambda:'restored'),'restored')
        self.assertEqual(sum(g.snapshot()['reservation_states'].values()),3)


@unittest.skipUnless(os.environ.get('DIA_TEST_POSTGRES_DSN'),'local PostgreSQL DSN not configured')
class PostgreSQLUsageTests(SharedReadBudgetTests):
    def setUp(self):
        # Baseline SQLite is private offline state; authority is real PostgreSQL.
        read_budget_tests.ReadBudgetTests.setUp(self)
        import psycopg
        from uuid import uuid4
        schema='usage_'+uuid4().hex;dsn=os.environ['DIA_TEST_POSTGRES_DSN']
        with psycopg.connect(dsn) as db:db.execute('CREATE SCHEMA '+schema)
        def connect():
            db=psycopg.connect(dsn);db.execute('SET search_path TO '+schema);return db
        self.state=SharedState(connect,backend='postgresql',mode='live');self.state.migrate()
        def cleanup():
            with psycopg.connect(dsn) as db:db.execute('DROP SCHEMA '+schema+' CASCADE')
        self.addCleanup(cleanup)
        with self.runtime.db() as db:source=export_usage(db,'estate',self.policy,None)
        self.proof=import_usage(self.state,'initial',source)
        self.g.shared=SharedUsage(self.g,self.state,owner='worker-one')


if __name__=='__main__':unittest.main()

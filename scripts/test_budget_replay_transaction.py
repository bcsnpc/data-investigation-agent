"""External committed inputs must not disappear in an owned rollback."""
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
from investigator import budget_delta, budget_delta_v2, process_tape as journal
from investigator.budget_connection import connect
from investigator.usage_governance import UsageGovernor
from test_process_tape import bootstrap
import test_adaptive_investigation as fixture


class BudgetReplayTransactionTests(unittest.TestCase):
    def test_committed_external_rows_survive_owned_rollback_in_legacy_and_current_tapes(self):
        for version, module, label in [('bounded-worker-tape-v7', budget_delta, 'DELTA_V1'),
                                       ('bounded-worker-tape-v12', budget_delta_v2, 'DELTA_V2')]:
            with self.subTest(version=version), tempfile.TemporaryDirectory() as folder:
                helper = fixture.AdaptiveTests(); helper.setUp()
                self.addCleanup(helper.doCleanups)
                helper.store.environment = 'development'
                policy = {'environment':'development', 'daily_limits':{
                    'planner_calls':100, 'cloud_calls':100,
                    'input_characters':100000, 'output_tokens':100000},
                    'max_inflight_planners':4, 'no_progress_limit':2}
                governor = UsageGovernor(helper.runtime, policy,
                                        lambda:journal.clock('governor', lambda:1000))
                root = Path(folder)
                with helper.runtime.db() as db, closing(sqlite3.connect(root/'catalog.sqlite')) as saved:
                    db.backup(saved)
                boot = bootstrap()
                boot['state'] = {'budget_checkpoint':label, 'artifacts':{
                    'catalog.sqlite':journal.sha((root/'catalog.sqlite').read_bytes())}}
                with patch.object(journal, 'VERSION', version):
                    tape = journal.Tape(root/'tape.json', boot)
                module.prepare(tape, root/'catalog.sqlite', 'development')
                # Another worker commits after this operation's bootstrap.
                with helper.runtime.db() as db:
                    db.execute('BEGIN IMMEDIATE')
                    governor.reserve(db, 'external', 'model', 'planner', 100, output_tokens=500)
                def work(runtime, gov, tape):
                    with journal.active(tape):
                        with runtime.db() as db:
                            db.execute('BEGIN IMMEDIATE')
                            gov.reserve(db, 'owner', 'rolled-back', 'planner', 100, output_tokens=500)
                            db.rollback()
                        with runtime.db() as db:
                            db.execute('BEGIN IMMEDIATE')
                            gov.reserve(db, 'owner', 'kept', 'planner', 100, output_tokens=500)
                        tape.finish({'complete':True})
                work(helper.runtime, governor, tape)
                before = tape.path.read_bytes()
                other = fixture.AdaptiveTests(); other.setUp()
                self.addCleanup(other.doCleanups); other.store.environment = 'development'
                with closing(sqlite3.connect(root/'catalog.sqlite')) as saved, other.runtime.db() as db:
                    saved.backup(db)
                replay = journal.Tape(tape.path)
                module.prepare(replay, root/'catalog.sqlite', 'development')
                replay_governor = UsageGovernor(other.runtime, policy,
                    lambda:journal.clock('governor', lambda:1000))
                work(other.runtime, replay_governor, replay)
                self.assertEqual(tape.path.read_bytes(), before)
                with other.runtime.db() as db:
                    self.assertEqual([tuple(r) for r in db.execute(
                        'SELECT session_id,reservation_key FROM adaptive_usage ORDER BY session_id')],
                        [('external','model'), ('owner','kept')])

    def test_method_sql_exception_and_close_rollbacks_preserve_only_registered_external_rows(self):
        for route in ('method','sql','context','close'):
            with self.subTest(route=route), tempfile.TemporaryDirectory() as folder:
                path = Path(folder)/'db.sqlite'
                db = connect(path)
                db.execute('CREATE TABLE adaptive_usage(id TEXT PRIMARY KEY,value TEXT)');db.commit()
                db.execute('BEGIN IMMEDIATE')
                db.execute("INSERT INTO adaptive_usage VALUES('owner','uncommitted')")
                db.execute("INSERT INTO adaptive_usage VALUES('external','sealed')")
                db.preserve_external_budget({('adaptive_usage',('external',)):
                    (['id','value'], ['id'], ['external','sealed'])})
                if route == 'method': db.rollback()
                elif route == 'sql': db.execute('ROLLBACK')
                elif route == 'context':
                    with self.assertRaises(ValueError):
                        with db: raise ValueError('synthetic')
                else: db.close()
                if route != 'close': db.close()
                with closing(sqlite3.connect(path)) as check:
                    self.assertEqual(check.execute('SELECT * FROM adaptive_usage').fetchall(),
                                     [('external','sealed')])

    def test_uninstrumented_caller_transaction_refuses_before_external_changes(self):
        from investigator.budget_replay_transaction import preserve
        with closing(sqlite3.connect(':memory:')) as db:
            db.execute('BEGIN')
            with self.assertRaisesRegex(journal.TapeError, 'TRANSACTION_HOOK_REQUIRED'):
                preserve(db, {('adaptive_usage',('x',)):['x']},
                         {'adaptive_usage':{'columns':['id'], 'keys':['id']}})


if __name__ == '__main__': unittest.main()

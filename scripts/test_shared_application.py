"""Shared authority, actual controller wiring, migration and strict tape parity."""
from contextlib import contextmanager, closing
import copy
import json
from pathlib import Path
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from investigator.onboarding import ModelStore, encoded, digest
from investigator.shared_state import SharedState, StateConflict
from investigator import shared_application as app
from investigator.shared_case_file import read as read_case
from investigator.process_tape import Tape, active
from test_process_tape import bootstrap


def store(path, state):
    obj = ModelStore.__new__(ModelStore)
    obj.database=Path(path);obj.environment='synthetic';obj.shared_accounting=None
    obj.shared_catalog=SimpleNamespace(state=state) if state else None
    return obj


class SharedApplicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.authority=SharedState.offline(self.root/'shared.sqlite')
        self.authority.migrate();self.store=store(self.root/'job.sqlite',self.authority)

    def claim(self):
        from investigator.claim_intake import ClaimIntake
        from test_claim_intake import CAT
        workspace=SimpleNamespace(store=self.store,agent=SimpleNamespace(config={},planner_profile={'adapter':'injected'}))
        controller=ClaimIntake(workspace)
        with patch.object(controller,'_catalog',return_value=copy.deepcopy(CAT)):
            result=controller.submit({'request_key':'key','claim':{'metric_phrase':'Quantity','comparator':'NONE',
                'scope':{'kind':'VISUALS','report_id':'report','page_id':'page','visual_ids':['card']}}})
        return controller,result

    def test_actual_claim_controller_writes_shared_rows_and_production_case(self):
        controller,result=self.claim()
        shared=self.authority.get(app.NAMESPACE,app.key('synthetic','claim_intakes'))
        row=shared['body']['rows'][0]
        self.assertEqual(json.loads(row[-2])['id'],result['id'])
        case=read_case(self.authority,'synthetic','claim',result['id'])
        self.assertEqual(case['body']['sections']['claim_intakes']['rows'][0]['record']['body'],row[-2])
        # Destroy the private mirror's claim: the current shared record wins.
        with closing(sqlite3.connect(self.store.database))as db, db:db.execute('DELETE FROM claim_intakes')
        self.assertEqual(controller.get(result['id']),result)
        # Another clean worker reads the same authority, never copied catalog rows.
        second=store(self.root/'second.sqlite',self.authority)
        with second.connect()as db:
            self.assertEqual(db.execute('SELECT body FROM claim_intakes WHERE id=?',(result['id'],)).fetchone()[0],row[-2])

    def test_missing_migration_refuses_existing_rows(self):
        with closing(sqlite3.connect(self.store.database))as db, db:
            db.execute('CREATE TABLE claim_handoffs(claim_id TEXT PRIMARY KEY,body TEXT,hash TEXT)')
            db.execute("INSERT INTO claim_handoffs VALUES('c','{}','hash')")
        with self.assertRaisesRegex(StateConflict,'MIGRATION_REQUIRED'):
            with self.store.connect()as db:db.execute('SELECT * FROM claim_handoffs')

    def test_exact_migration_preserves_json_whitespace_null_real_and_rowids(self):
        with closing(sqlite3.connect(self.store.database))as db, db:
            db.execute('CREATE TABLE adaptive_events(id INTEGER PRIMARY KEY,session_id TEXT,kind TEXT,detail TEXT,created TEXT)')
            db.execute('INSERT INTO adaptive_events VALUES(?,?,?,?,?)',(17,'s','OBSERVED','{ "x": 1 }',None))
            db.execute('CREATE TABLE workspace_jobs(preview_id TEXT PRIMARY KEY,model_id TEXT,session_id TEXT,owner TEXT,status TEXT,created REAL,error TEXT)')
            db.execute('INSERT INTO workspace_jobs VALUES(?,?,?,?,?,?,?)',('p','m',None,'o','HELD',12.125,'retained error'))
        before=app.source(self.store.database,'synthetic');proof=app.migrate(self.authority,'migration',before)
        self.assertTrue(all(p['sha256_before']==p['sha256_after']and p['matched']for p in proof['tables']))
        self.assertEqual(proof,app.migrate(self.authority,'migration',before))
        with self.store.connect()as db:
            self.assertEqual(list(db.execute('SELECT * FROM adaptive_events').fetchone()),[17,'s','OBSERVED','{ "x": 1 }',None])
        self.assertEqual(before,app.source(self.store.database,'synthetic'))
        changed=copy.deepcopy(before);changed['tables']['adaptive_events']['rows'][0][-2]='changed'
        with self.assertRaisesRegex(StateConflict,'SOURCE_CHANGED'):app.migrate(self.authority,'migration',changed)

    def test_concurrent_revision_fences_before_overwriting(self):
        controller,result=self.claim()
        with self.assertRaisesRegex(StateConflict,'REVISION_CHANGED'):
            with self.store.connect()as db:
                db.execute('SELECT * FROM claim_intakes')
                old=self.authority.get(app.NAMESPACE,app.key('synthetic','claim_intakes'))
                self.authority.put(app.NAMESPACE,app.key('synthetic','claim_intakes'),old['body'],revision=old['revision'])
                db.execute('UPDATE claim_intakes SET revision=99')
        self.assertNotEqual(controller.get(result['id'])['revision'],99)

    def test_tape_replays_shared_snapshots_with_zero_authority_calls(self):
        self.claim()
        before=self.root/'before.sqlite'
        with closing(sqlite3.connect(self.store.database))as src,closing(sqlite3.connect(before))as out:src.backup(out)
        b=bootstrap();b['state']['shared_application']=app.VERSION
        def operation(s):
            with s.connect()as db:
                db.execute('BEGIN IMMEDIATE')
                db.execute('CREATE TABLE IF NOT EXISTS v2_cancellations(run_id TEXT PRIMARY KEY,created TEXT)')
                db.execute('INSERT OR IGNORE INTO v2_cancellations VALUES(?,?)',('s','2026-10-13'))
                result=list(db.execute('SELECT * FROM v2_cancellations').fetchone())
            return result
        live=Tape(self.root/'tape.json',b)
        with active(live):live.finish(operation(self.store))
        saved=app.source(self.store.database,'synthetic')
        replay=Tape(live.path)
        with patch.object(self.authority,'transaction',side_effect=AssertionError('Replay network')):
            with active(replay):replay.finish(operation(store(before,None)))
        self.assertEqual(saved,app.source(before,'synthetic'))

    def test_schema_injection_and_blob_cells_refuse(self):
        for sql in ('CREATE TABLE claim_intakes(id TEXT); DROP TABLE x;', 'CREATE TABLE claim_intakes AS SELECT 1'):
            with self.assertRaises(StateConflict):app.validate_table('claim_intakes',{'schema':sql,'columns':['id'],'rows':[]})
        with closing(sqlite3.connect(self.store.database))as db, db:
            db.execute('CREATE TABLE workspace_images(id TEXT,content BLOB)');db.execute('INSERT INTO workspace_images VALUES(?,?)',('i',b'pixels'))
        with self.assertRaisesRegex(StateConflict,'BLOB_MIGRATION'):app.source(self.store.database,'synthetic')

    def test_new_application_table_never_silently_falls_back_to_local_state(self):
        with self.assertRaisesRegex(StateConflict,'NOT_REGISTERED'):
            with self.store.connect()as db:db.execute('CREATE TABLE claim_future_state(id TEXT)')
        with closing(sqlite3.connect(self.store.database))as db:
            self.assertIsNone(db.execute("SELECT 1 FROM sqlite_master WHERE name='claim_future_state'").fetchone())

    def test_projected_capture_cannot_reuse_a_previously_constructed_shared_store(self):
        from investigator.privacy_capture import ACTIVE
        token=ACTIVE.set(object())
        try:
            with self.assertRaisesRegex(StateConflict,'PROJECTED_STATE_NOT_IMPLEMENTED'):
                with self.store.connect():self.fail('raw shared access')
        finally:ACTIVE.reset(token)


if __name__=='__main__':unittest.main()

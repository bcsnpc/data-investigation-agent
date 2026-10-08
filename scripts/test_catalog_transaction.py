import sqlite3,unittest
from investigator.onboarding import ModelStore,Conflict
from test_evidence_synthesis import SynthesisTests


class CatalogTransactionTests(unittest.TestCase):
    def test_fifty_gate_appends_and_admissions_use_one_writer_after_cache_spill(self):
        fixture=SynthesisTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        agent,state=fixture.stopped()
        with agent.runtime.db() as db:
            db.execute('PRAGMA cache_size=2')
            db.execute('BEGIN EXCLUSIVE')
            db.execute('CREATE TABLE gate_append(id INTEGER PRIMARY KEY,body BLOB)')
            for i in range(50):
                db.execute('INSERT INTO gate_append VALUES(?,?)',(i,b'x'*32768))
                loaded=agent.load(db,state['id'])
                agent.admit(loaded,db)
                self.assertTrue(db.in_transaction)
            self.assertEqual(db.execute('SELECT count(*) FROM gate_append').fetchone()[0],50)
        with agent.runtime.db() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM gate_append').fetchone()[0],50)

    def test_borrowed_catalog_does_not_commit_or_close_and_other_paths_do_not_borrow(self):
        fixture=SynthesisTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        store=fixture.f.store
        with store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            with store.catalog_connection(db):
                with store.connect() as nested:self.assertIs(nested,db)
            self.assertTrue(db.in_transaction)
            self.assertEqual(db.execute('SELECT 1').fetchone()[0],1)
        with sqlite3.connect(':memory:') as memory:
            # A different on-disk catalog cannot borrow this writer.
            with store.connect() as disk:
                fake=object.__new__(ModelStore);fake.database=store.database.parent/'different.sqlite'
                with self.assertRaises(Conflict):
                    with fake.catalog_connection(disk):pass


if __name__=='__main__':unittest.main()

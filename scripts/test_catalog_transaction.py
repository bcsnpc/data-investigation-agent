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

    def test_archived_producer_io_shim_appends_fifty_without_changing_values(self):
        import tempfile,importlib.util
        from contextlib import contextmanager,closing
        from pathlib import Path
        from types import SimpleNamespace
        path=Path(__file__).resolve().parents[1]/'acceptance/unknown_domain/catalog_replay.py'
        spec=importlib.util.spec_from_file_location('catalog_replay',path)
        shim=importlib.util.module_from_spec(spec);spec.loader.exec_module(shim)
        class Store:
            def __init__(self,path):self.database=path
            @contextmanager
            def connect(self):
                with closing(sqlite3.connect(self.database,timeout=0.01)) as db:
                    with db:yield db
            def get(self):
                with self.connect() as db:return db.execute('SELECT count(*) FROM records').fetchone()[0]
        class Runtime:
            def __init__(self,store):self.store=store
            @contextmanager
            def db(self):
                with self.store.connect() as db:yield db
        class Agent:
            def __init__(self,store):self.store=store
            def load(self,db):return self.store.get()
            def admit(self):return self.store.get()
        with tempfile.TemporaryDirectory() as directory:
            store=Store(Path(directory)/'catalog.sqlite');runtime=Runtime(store);agent=Agent(store)
            with store.connect() as db:db.execute('CREATE TABLE records(id INTEGER,body BLOB)')
            with shim.install(SimpleNamespace(ModelStore=Store,Runtime=Runtime,AdaptiveRuntime=Agent)):
                with runtime.db() as db:
                    db.execute('PRAGMA cache_size=2');db.execute('BEGIN EXCLUSIVE')
                    for i in range(50):
                        db.execute('INSERT INTO records VALUES(?,?)',(i,b'x'*32768))
                        self.assertEqual(agent.load(db),i+1);self.assertEqual(agent.admit(),i+1)
                        self.assertTrue(db.in_transaction)
            self.assertEqual(store.get(),50)

    def test_borrowed_catalog_does_not_commit_or_close_and_other_paths_do_not_borrow(self):
        fixture=SynthesisTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        store=fixture.f.store
        with store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            with store.catalog_connection(db):
                with store.connect() as nested:self.assertIs(nested,db)
            self.assertTrue(db.in_transaction)
            self.assertEqual(db.execute('SELECT 1').fetchone()[0],1)
        # A different on-disk catalog cannot borrow this writer.
        with store.connect() as disk:
            fake=object.__new__(ModelStore);fake.database=store.database.parent/'different.sqlite'
            with self.assertRaises(Conflict):
                with fake.catalog_connection(disk):pass


if __name__=='__main__':unittest.main()

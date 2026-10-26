import os,sqlite3,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from investigator.shared_state import SharedState,StateConflict
from investigator.shared_writer_lease import isolated,OWNER_ENV,LEASE_ENV

class ReadTransactionTests(unittest.TestCase):
    def test_postgres_reads_use_stable_read_only_snapshot_without_global_writer_lock(self):
        class DB:
            def __init__(self):self.queries=[];self.closed=False;self.committed=False
            def execute(self,query,*args):self.queries.append(query);return self
            def commit(self):self.committed=True
            def rollback(self):pass
            def close(self):self.closed=True
        db=DB();state=SharedState(lambda:db,backend='postgresql',mode='live')
        with patch('investigator.shared_writer_lease.check')as lease:
            result=state._read_transaction(lambda c:c.execute('SELECT 1'))
        self.assertIn('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY',db.queries)
        self.assertFalse(any('pg_advisory'in q for q in db.queries));self.assertTrue(db.closed and db.committed)
        self.assertEqual(lease.call_count,2)
    def test_budget_writers_still_take_exclusive_lock_and_do_not_use_read_only_mode(self):
        class DB:
            def __init__(self):self.queries=[]
            def execute(self,query,*args):self.queries.append(query);return self
            def commit(self):pass
            def rollback(self):pass
            def close(self):pass
        db=DB();state=SharedState(lambda:db,backend='postgresql',mode='live')
        with patch('investigator.shared_writer_lease.check'):
            with state.transaction():pass
        self.assertIn('SELECT pg_advisory_xact_lock(183746812)',db.queries)
        self.assertIn('SET TRANSACTION ISOLATION LEVEL READ COMMITTED',db.queries)
        self.assertFalse(any('READ ONLY'in q for q in db.queries))
    def test_read_callbacks_cannot_mutate_and_foreign_lease_still_blocks_reads(self):
        with tempfile.TemporaryDirectory()as directory:
            state=SharedState.offline(Path(directory)/'state.sqlite');state.migrate();state.put('test','one',{'value':1})
            with self.assertRaisesRegex(sqlite3.OperationalError,'readonly'):
                state._read_transaction(lambda db:db.execute('DELETE FROM state_documents'))
            self.assertEqual(state.get('test','one')['body'],{'value':1})
            with patch.dict(os.environ):
                os.environ.pop(LEASE_ENV,None)
                with isolated(state,owner='read-test-owner',lease_id='read-test',expires_at=time.time()+120,approval='synthetic test'):
                    with patch.dict(os.environ,{OWNER_ENV:'foreign'}):
                        with self.assertRaisesRegex(StateConflict,'OWNED_BY_ANOTHER'):state.get('test','one')
            self.assertEqual(state.get('test','one')['body'],{'value':1})

    def test_replay_read_only_mode_resets_before_the_next_write(self):
        from investigator.shared_usage_replay import MemoryState
        state=MemoryState()
        try:
            state.put('test','one',{'value':1})
            with self.assertRaisesRegex(sqlite3.OperationalError,'readonly'):
                state._read_transaction(lambda db:db.execute('DELETE FROM state_documents'))
            state.put('test','two',{'value':2})
            self.assertEqual(state.get('test','one')['body'],{'value':1})
            self.assertEqual(state.get('test','two')['body'],{'value':2})
        finally:state.connection.close()

if __name__=='__main__':unittest.main()

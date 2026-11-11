from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from investigator.shared_state import SharedState, StateConflict, TRANSACTION_ACTIVE, encoded


class ShortTransactionsTests(unittest.TestCase):
    def test_writer_lock_retry_precedes_body_and_reinstates_transaction_settings(self):
        from unittest.mock import Mock
        class LockTimeout(Exception):sqlstate='55P03'
        db=Mock();attempts=[]
        def execute(sql):
            if 'pg_advisory_xact_lock' in sql:
                attempts.append(sql)
                if len(attempts)==1:raise LockTimeout('busy')
        db.execute.side_effect=execute
        state=SharedState(lambda:None,backend='postgresql',mode='live');check=Mock()
        with patch('time.sleep') as sleep:state._begin_postgres(db,False,False,check)
        self.assertEqual(len(attempts),2);db.rollback.assert_called_once()
        self.assertEqual(check.call_count,2);sleep.assert_called_once_with(30)
        statements=[c.args[0] for c in db.execute.call_args_list]
        self.assertEqual(statements.count("SET LOCAL lock_timeout = '5s'"),2)
        self.assertFalse(state.connection_failures[0]['transaction_body_started'])

    def test_lock_timeout_retries_idempotent_operation_once_without_new_dispatch(self):
        from unittest.mock import Mock
        class LockTimeout(Exception):sqlstate='55P03'
        state=SharedState(lambda:None,backend='postgresql',mode='live')
        operation=Mock(side_effect=[LockTimeout('synthetic'),{'settled':'same-id'}])
        with patch('time.sleep') as sleep:
            self.assertEqual(state._retry_connection_operation('RESERVATION_SETTLEMENT',operation),{'settled':'same-id'})
        self.assertEqual(operation.call_count,2);sleep.assert_called_once_with(30)
        self.assertEqual(state.connection_failures[0]['sqlstate'],'55P03')
        operation=Mock(side_effect=LockTimeout('still held'))
        with patch('time.sleep'),self.assertRaises(LockTimeout):
            state._retry_connection_operation('RESERVATION_SETTLEMENT',operation)
        self.assertEqual(operation.call_count,2)

    def test_graph_reads_do_not_take_shared_writer_transactions(self):
        from investigator.estate_graph_repository import GraphRepository
        from test_estate_graph import graph
        repo = GraphRepository(self.state); repo.migrate(); repo.replace(graph())
        with patch.object(self.state, 'transaction', wraps=self.state.transaction) as transactions:
            repo.records('estate')
            repo.path_records('estate', {'visual'}, {'visual', 'measure', 'column'})
            repo.changes('estate')
        self.assertTrue(transactions.call_args_list)
        self.assertTrue(all(c.kwargs.get('_read_only') is True for c in transactions.call_args_list))

    def test_owner_health_is_one_bounded_read_not_one_connection_per_owner(self):
        from investigator.graph_scan_health import record, unavailable
        for i in range(20):record(self.state, 'e', str(i), '2026-11-01T00:00:00Z', 'UNAVAILABLE', 'synthetic')
        with patch.object(self.state, '_read_transaction', wraps=self.state._read_transaction) as reads, \
             patch.object(self.state, 'get', side_effect=AssertionError('No per-owner connection')):
            result = unavailable(self.state, 'e', {str(i) for i in range(20)})
        self.assertEqual(len(result), 20)
        self.assertEqual(reads.call_count, 1)

    def setUp(self):
        directory = TemporaryDirectory(); self.addCleanup(directory.cleanup)
        self.state = SharedState.offline(Path(directory.name) / 'state.sqlite')
        self.state.migrate()

    def test_serialization_precedes_writer_transaction_and_prior_body_not_loaded(self):
        self.state.put('capture', 'one', {'large': 'original'})
        def serialize(value):
            self.assertFalse(TRANSACTION_ACTIVE.get())
            return encoded(value)
        with patch('investigator.shared_state.encoded', side_effect=serialize), \
             patch.object(self.state, '_get', side_effect=AssertionError('No previous capture decode under lock')):
            self.state.put('capture', 'one', {'large': 'replacement'}, revision=0)
        self.assertEqual(self.state.get('capture', 'one')['revision'], 1)
        with self.assertRaises(StateConflict):
            self.state.put('capture', 'one', {}, revision=0)

    def test_decode_and_hash_happen_after_read_transaction_closes(self):
        self.state.put('capture', 'one', {'large': 'body'})
        from investigator.shared_state import sha
        def checked_hash(value):
            self.assertFalse(TRANSACTION_ACTIVE.get())
            return sha(value)
        with patch('investigator.shared_state.sha', side_effect=checked_hash):
            self.assertEqual(self.state.get('capture', 'one')['body'], {'large': 'body'})

    def test_hash_corruption_still_refuses(self):
        self.state.put('capture', 'one', {'large': 'body'})
        with self.state.transaction() as db:
            db.execute("UPDATE state_documents SET body_hash='wrong'")
        with self.assertRaisesRegex(StateConflict, 'STATE_DOCUMENT_HASH_DIFFERS'):
            self.state.get('capture', 'one')

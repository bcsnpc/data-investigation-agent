from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from investigator.shared_state import SharedState, StateConflict, TRANSACTION_ACTIVE, encoded


class ShortTransactionsTests(unittest.TestCase):
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

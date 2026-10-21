"""Capture egress waits for shared commit/rollback; gateway rule unchanged."""
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from contextlib import closing

from investigator.process_tape import bytes_of
from investigator.run_capture import DurableCapture
from investigator.shared_state import SharedState, TRANSACTION_ACTIVE

HEADER={'entry_point':'runner','context_identity':'fixture-context','config':{},'profile':{},'usage_policy':None,'engine_hash':'fixture-engine','state':{}}


class TrackedConnection(sqlite3.Connection):
    closed=False
    def close(self):
        super().close();self.closed=True


class TransactionPublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.path=self.root/'state.sqlite'
        with closing(sqlite3.connect(self.path)) as db:
            db.execute('CREATE TABLE changes(value INTEGER)');db.commit()
        self.connections=[];self.sent=[];self.fail=False
        def connector():
            db=sqlite3.connect(self.path,factory=TrackedConnection,timeout=.1)
            self.connections.append(db);return db
        self.state=SharedState(connector,backend='sqlite',mode='offline')
        def publish(key,raw):
            self.assertFalse(TRANSACTION_ACTIVE.get())
            if self.connections:self.assertTrue(self.connections[-1].closed)
            # The transaction lock must actually be gone, not merely its flag.
            with closing(sqlite3.connect(self.path,timeout=.1)) as second:
                second.execute('BEGIN IMMEDIATE')
                rows=second.execute('SELECT value FROM changes').fetchall()
            if self.fail:raise OSError('synthetic publication failure')
            self.sent.append((key,raw,rows))
        self.capture=DurableCapture(self.root/'capture',publish,run_id='one',bootstrap=HEADER)

    def test_commit_flushes_after_close_before_return_in_original_order(self):
        with self.state.transaction() as db:
            db.execute('INSERT INTO changes VALUES(16)')
            first=self.capture.record('tape-event',{'ordinal':1})
            second=self.capture.record('tape-event',{'ordinal':2})
            self.assertEqual(len(self.sent),2) # Header and STARTED only.
            self.assertEqual((self.capture.root/'00000003-tape-event.json').read_bytes(),bytes_of({'ordinal':1}))
            self.assertEqual((self.capture.root/'00000004-tape-event.json').read_bytes(),bytes_of({'ordinal':2}))
        self.assertEqual([key for key,_,_ in self.sent][-2:],[first['key'],second['key']])
        self.assertEqual([rows for _,_,rows in self.sent][-2:],[[(16,)],[(16,)]])
        self.capture.record('after',{'committed':True})
        self.capture.seal()
        seal=json.loads(self.sent[-1][1]);self.assertEqual(len(seal['records']),5)
        for ref,(key,raw,_) in zip(seal['records'],self.sent):
            self.assertEqual(ref,{'key':key,'sha256':hashlib.sha256(raw).hexdigest()})
        self.assertEqual(seal['seal'],hashlib.sha256(bytes_of({k:v for k,v in seal.items() if k!='seal'})).hexdigest())

    def test_rollback_also_retains_original_observation_after_close(self):
        error=ValueError('primary rollback')
        with self.assertRaises(ValueError) as caught:
            with self.state.transaction() as db:
                db.execute('INSERT INTO changes VALUES(99)')
                self.capture.record('tape-event',{'observed_before_rollback':True})
                raise error
        self.assertIs(caught.exception,error)
        self.assertEqual(len(self.sent),3)
        self.assertEqual(self.sent[-1][2],[])
        self.assertEqual(json.loads(self.sent[-1][1]),{'observed_before_rollback':True})

    def test_publication_failure_visible_local_records_retained_no_seal(self):
        self.fail=True
        with self.assertRaisesRegex(OSError,'synthetic publication failure'):
            with self.state.transaction() as db:
                db.execute('INSERT INTO changes VALUES(7)')
                self.capture.record('tape-event',{'value':7})
        self.assertEqual((self.capture.root/'00000003-tape-event.json').read_bytes(),bytes_of({'value':7}))
        self.assertEqual(len(self.capture.records),3)
        with self.assertRaisesRegex(RuntimeError,'CAPTURE_PUBLICATION_FAILED_NO_SEAL'):self.capture.seal()
        self.assertFalse((self.capture.root/'run-record.json').exists())

    def test_primary_rollback_error_not_masked_by_publication_failure(self):
        self.fail=True;error=ValueError('original')
        with self.assertRaises(ValueError) as caught:
            with self.state.transaction():
                self.capture.record('tape-event',{'partial':True})
                raise error
        self.assertIs(caught.exception,error)
        self.assertIn('After-transaction publication also failed: OSError',error.__notes__)
        self.assertFalse(TRANSACTION_ACTIVE.get())
        self.assertTrue(self.connections[-1].closed)

    def test_seal_inside_transaction_refuses_without_blob_exception(self):
        with self.state.transaction():
            self.capture.record('tape-event',{'value':1})
            with self.assertRaisesRegex(RuntimeError,'CAPTURE_SEAL_DURING_TRANSACTION'):self.capture.seal()
            self.assertEqual(len(self.sent),2)
        self.assertEqual(len(self.sent),3)
        self.assertFalse((self.capture.root/'run-record.json').exists())

    def test_gateway_network_transaction_guard_remains_enforced(self):
        from investigator.live_gateway import GatewayDenied,_network_unlocked
        from unittest.mock import patch
        with patch.dict('os.environ',{'DIA_GATEWAY_AUDIT_FILE':str(self.root/'denial.jsonl')}):
            with self.state.transaction():
                with self.assertRaisesRegex(GatewayDenied,'NETWORK_DURING_SHARED_STATE_TRANSACTION'):_network_unlocked()


if __name__=='__main__':unittest.main()

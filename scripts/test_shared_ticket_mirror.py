"""Shared authority is never replaced by its per-job replay snapshot."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from investigator.shared_state import SharedState
from investigator.shared_tickets import SharedTickets
from investigator.ticket_state import Tickets
from investigator.onboarding import Conflict
from investigator.process_tape import Tape,active
from investigator.run_recording import backup,has_smart_ticket
from test_process_tape import bootstrap


class Store:
    def __init__(self,path):self.database=Path(path)
    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.database);db.row_factory=sqlite3.Row
        try:
            with db:yield db
        finally:db.close()


class SharedTicketMirrorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.state=SharedState.offline(self.root/'authority.sqlite')
        self.state.migrate();self.store=Store(self.root/'job.sqlite')
        self.tickets=SharedTickets(self.state,replay_store=self.store)

    def test_shared_submit_and_updates_replay_from_separate_private_snapshots(self):
        # Actual ticket-state operations and actual tape events, no transport.
        first=Tape(self.root/'submit.json',bootstrap())
        with active(first):
            saved=self.tickets.submit({'text':'Original form description'},'one-attempt')
            first.finish(saved)
        replay=Tape(self.root/'submit.json')
        with active(replay):
            with patch('investigator.shared_state.configured_state',side_effect=AssertionError('Replay must not connect')):
                local=Tickets(Store(self.root/'replay-submit.sqlite'))
                replay.finish(local.submit({'text':'Original form description'},'one-attempt'))
        identity=saved['ticket']['id']
        for stage in ('attached','finished'):
            snapshot=self.root/(stage+'.sqlite');backup(self.store.database,snapshot)
            def update(ticket):
                ticket['session_id']='session';ticket['mirror_stage']=stage;return ticket
            tape=Tape(self.root/(stage+'.json'),bootstrap())
            with active(tape):
                result=self.tickets.update(identity,saved['revision'],update);tape.finish(result)
            before=tape.path.read_bytes();replay=Tape(tape.path)
            with active(replay):
                with patch('investigator.shared_state.configured_state',side_effect=AssertionError('Replay must not connect')):
                    local=Tickets(Store(snapshot))
                    replay.finish(local.update(identity,saved['revision'],update))
            self.assertEqual(tape.path.read_bytes(),before);saved=result
        self.assertTrue(has_smart_ticket(SimpleNamespace(store=self.store),'session'))
        with self.store.connect() as db:self.assertEqual(Tickets._get(db,identity),saved)

    def test_request_link_lookup_is_not_truncated_to_ui_page(self):
        for i in range(50):SharedTickets(self.state).submit({'n':i},'a'+str(i))
        last=SharedTickets(self.state).submit({'text':'Last'},'z-last')
        self.assertEqual(self.tickets.get(last['ticket']['id']),last)
        with self.store.connect() as db:
            self.assertEqual(db.execute('SELECT request_key FROM smart_tickets').fetchone()[0],'z-last')

    def test_failed_mirror_keeps_commit_and_fails_without_local_fallback(self):
        saved=self.tickets.submit({'text':'q'},'key');identity=saved['ticket']['id']
        with patch.object(self.store,'connect',side_effect=OSError('Mirror unavailable')):
            with self.assertRaisesRegex(OSError,'Mirror unavailable'):
                self.tickets.update(identity,0,lambda t:{**t,'session_id':'s'})
        self.assertEqual(self.state.get('ticket',identity)['revision'],1)
        with self.store.connect() as db:self.assertEqual(Tickets._get(db,identity)['revision'],0)
        with self.assertRaises(Conflict):self.tickets.update(identity,0,lambda t:t)
        current=self.tickets.get(identity)
        self.assertEqual(current['revision'],1)
        with self.store.connect() as db:self.assertEqual(Tickets._get(db,identity),current)

    def test_corrupt_or_ahead_mirror_never_becomes_authority(self):
        saved=self.tickets.submit({'text':'q'},'key');identity=saved['ticket']['id']
        with self.store.connect() as db:db.execute('UPDATE smart_tickets SET revision=8')
        with self.assertRaisesRegex(Conflict,'ahead'):self.tickets.get(identity)
        self.assertEqual(self.state.get('ticket',identity)['revision'],0)


if __name__=='__main__':unittest.main()

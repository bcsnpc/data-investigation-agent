from contextlib import contextmanager
import sqlite3
import tempfile
from pathlib import Path
import unittest
from investigator.ticket_state import Tickets
from investigator import ticket_protocol as protocol
from investigator.onboarding import Conflict
from test_ticket_protocol import question


class Store:
    def __init__(self,path):self.path=path
    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.path)
        try:
            with db:yield db
        finally:db.close()


class TicketStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.store=Store(Path(self.tmp.name)/'catalog.sqlite');self.tickets=Tickets(self.store)

    def test_restart_retains_questions_confirmations_and_history(self):
        saved=self.tickets.submit({'text':'This number looks wrong'},'key');identity=saved['ticket']['id']
        saved=self.tickets.update(identity,0,lambda t:protocol.ask(t,[question('NUMBER')]))
        resumed=Tickets(self.store)
        self.assertEqual(resumed.get(identity),saved)
        saved=resumed.update(identity,1,lambda t:protocol.answer(t,[{'question_id':'number','choice_id':'first'}]))
        self.assertEqual(Tickets(self.store).get(identity)['ticket']['confirmed'],saved['ticket']['confirmed'])
        self.assertEqual(len(saved['ticket']['history']),3)

    def test_idempotency_preserves_work_and_rejects_changed_input(self):
        first=self.tickets.submit({'text':'Question'},'key')
        self.assertEqual(self.tickets.submit({'text':'Question'},'key'),first)
        with self.assertRaises(Conflict):self.tickets.submit({'text':'Different question'},'key')

    def test_stale_reply_cannot_confirm_new_choices(self):
        identity=self.tickets.submit({'text':'Question'},'key')['ticket']['id']
        saved=self.tickets.update(identity,0,lambda t:protocol.ask(t,[question('NUMBER')]))
        with self.assertRaises(Conflict):
            self.tickets.update(identity,0,lambda t:protocol.answer(t,[{'question_id':'number','choice_id':'first'}]))
        self.assertEqual(self.tickets.get(identity),saved)

    def test_retained_evidence_survives_restart_and_scope_changes_miss_cache(self):
        identity=self.tickets.submit({'text':'Question'},'key')['ticket']['id']
        self.tickets.update(identity,0,lambda t:protocol.retain(t,context='pin',scope='North',cell='card',receipt={'id':'sealed'}))
        ticket=Tickets(self.store).get(identity)['ticket']
        self.assertEqual(protocol.reuse(ticket,context='pin',scope='North',cell='card'),{'id':'sealed'})
        self.assertIsNone(protocol.reuse(ticket,context='pin',scope='South',cell='card'))

    def test_projected_ticket_restart_keeps_seals_and_writes_no_raw_value(self):
        from investigator.privacy_capture import Capture
        from investigator.privacy_projection import Projection
        from investigator.privacy_tape import PrivacyTape
        from investigator.onboarding import ModelStore
        root=Path(self.tmp.name)/'projected';root.mkdir()
        column='column://synthetic/person_name';raw='PRIVATE_SYNTHETIC_PERSON'
        policy={'tape_class':'PRIVACY_PROJECTED','version':'estate-privacy-projection-v1',
            'estate_id':'synthetic','key_reference':'secret/synthetic','columns':[column]}
        make=lambda:Projection(policy,lambda _:b'synthetic-in-memory-key-32-bytes!!')
        capture=Capture(make(),[root/'catalog.sqlite',root/'inventory.sqlite'])
        try:
            with capture.active():
                store=ModelStore(root/'catalog.sqlite',root/'inventory.sqlite','synthetic')
                tickets=Tickets(store)
                saved=tickets.submit({'text':raw+' reports a problem','column_id':column,'value':raw},'key')
                identity=saved['ticket']['id']
                tape=PrivacyTape(root/'ticket.tape.json',capture.projection)
                projected=capture.finish(tape,saved)
            for path in root.rglob('*'):
                if path.is_file():self.assertNotIn(raw.encode(),path.read_bytes())
            self.assertNotIn(raw,str(projected))
        finally:capture.close()
        cold=Capture(make(),[root/'catalog.sqlite',root/'inventory.sqlite'])
        try:
            with cold.active():
                store=ModelStore(root/'catalog.sqlite',root/'inventory.sqlite','synthetic')
                self.assertEqual(Tickets(store).get(identity),projected)
        finally:cold.close()


if __name__=='__main__':unittest.main()

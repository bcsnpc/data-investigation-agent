import copy
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from investigator.shared_state import SharedState,StateConflict,sha
from investigator.shared_ticket_migration import export_tickets,import_tickets
from investigator.shared_document_migration import export_documents,import_documents
from investigator.shared_tickets import SharedTickets
from investigator.ticket_state import Tickets
from investigator import ticket_protocol as protocol
from investigator.onboarding import Conflict,ModelStore
from test_ticket_state import Store
from test_ticket_protocol import question


class TicketMigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.folder=Path(self.tmp.name)
        self.store=Store(self.folder/'old.sqlite');self.tickets=Tickets(self.store)
        self.first=self.tickets.submit({'text':'Exact question with retained punctuation.'},'request-key')
        self.id=self.first['ticket']['id']
        self.saved=self.tickets.update(self.id,0,lambda t:protocol.ask(t,[question('NUMBER')]))
        self.saved=self.tickets.update(self.id,1,lambda t:protocol.retain(t,context='pin',scope='North',cell='card',receipt={'id':'sealed'}))
        self.state=SharedState.offline(self.folder/'state.sqlite');self.state.migrate()
        with self.store.connect() as db:self.source=export_tickets(db,'estate')

    def test_exact_case_revision_request_key_and_original_bytes_survive(self):
        source=copy.deepcopy(self.source)
        # Valid historical JSON whitespace is retained, not silently normalized.
        source['rows'][0][3]=json.dumps(json.loads(source['rows'][0][3]),indent=2)
        proof=import_tickets(self.state,'first',source)
        shared=SharedTickets(self.state)
        self.assertEqual(shared.get(self.id),self.saved)
        self.assertEqual(shared.submit(self.first['request'],'request-key'),self.saved)
        self.assertEqual(proof['rows_sha256_before'],proof['rows_sha256_after'])
        self.assertEqual(self.state.get('ticket_import_source','first')['body'],source)
        self.assertTrue(all(p['matched']and p['revision_before']==p['revision_after']for p in proof['tickets']))
        with self.assertRaises(Conflict):shared.update(self.id,0,lambda t:t)
        advanced=shared.update(self.id,2,lambda t:protocol.answer(t,[{'question_id':'number','choice_id':'first'}]))
        self.assertEqual(advanced['revision'],3)
        self.assertEqual(import_tickets(self.state,'first',source),proof)
        self.assertEqual(shared.get(self.id)['revision'],3) # rerun must not reset

    def test_hash_drift_duplicate_identity_and_collision_refuse_atomically(self):
        wrong=copy.deepcopy(self.source);wrong['rows'][0][2]='0'*64
        with self.assertRaisesRegex(StateConflict,'HASH_ID'):import_tickets(self.state,'wrong',wrong)
        self.assertEqual(self.state.list('ticket'),[])
        wrong=copy.deepcopy(self.source);wrong['rows'].append(wrong['rows'][0])
        with self.assertRaisesRegex(StateConflict,'DUPLICATE'):import_tickets(self.state,'wrong',wrong)
        import_tickets(self.state,'first',self.source)
        with self.assertRaisesRegex(StateConflict,'TARGET'):import_tickets(self.state,'second',self.source)
        wrong=copy.deepcopy(self.source);wrong['rows'][0][4]+=1
        with self.assertRaisesRegex(StateConflict,'SOURCE_CHANGED'):import_tickets(self.state,'first',wrong)

    def test_post_write_drift_is_detected_and_rolls_back(self):
        original=self.state._get
        def corrupt(db,namespace,key):
            saved=original(db,namespace,key)
            if namespace=='ticket':saved['revision']+=1
            return saved
        with patch.object(self.state,'_get',side_effect=corrupt):
            with self.assertRaisesRegex(StateConflict,'POST_WRITE'):import_tickets(self.state,'wrong',self.source)
        self.assertEqual(self.state.list('ticket'),[])
        with self.state.transaction() as db:self.assertEqual(db.execute('SELECT count(*) FROM state_migrations').fetchone()[0],0)

    def bundle(self):
        from uuid import uuid4
        catalog=ModelStore(self.store.path,self.folder/'inventory.sqlite','estate')
        if not catalog.list():
            model=catalog.register({'name':'Synthetic model','workspace':str(uuid4()),'model_id':str(uuid4()),'report_ids':[str(uuid4())]},'owner')
            context_id=str(uuid4());context={'id':context_id,'model_id':model['id'],'measures':[]}
            from investigator.onboarding import encoded,digest
            with catalog.connect() as db:
                db.execute('INSERT INTO model_contexts VALUES(?,?,?,?,?,?)',(context_id,model['id'],str(uuid4()),encoded(context),digest(context),'2026-10-12T00:00:00+00:00'))
                db.execute('UPDATE models SET context_id=? WHERE id=?',(context_id,model['id']))
        with closing(sqlite3.connect(self.store.path.as_uri()+'?mode=ro',uri=True)) as db:
            db.row_factory=sqlite3.Row;db.execute('BEGIN')
            return export_documents(db,'estate',[{'version':'route-readiness-v1','unverified':'retained only'}])

    def test_combined_plan_is_offline_and_apply_preserves_component_hashes(self):
        import migrate_shared_documents as cli
        bundle=self.bundle();source=self.folder/'bundle.json';source.write_text(json.dumps(bundle));report=self.folder/'plan.json'
        with patch('migrate_shared_documents.configured_state',side_effect=AssertionError('offline')):
            cli.main(['migrate','--source',str(source),'--expected-sha256',sha(bundle),'--migration-id','one','--report',str(report)])
        self.assertEqual(json.loads(report.read_text())['status'],'PLANNED')
        proof=import_documents(self.state,'one',bundle)
        self.assertEqual(proof['status'],'APPLIED')
        from investigator.shared_catalog import SharedCatalog
        self.assertEqual(SharedCatalog(self.state,'estate').list(),bundle['components'][0]['models'])
        self.assertEqual(proof['components'][-1]['proof']['status'],'RETAINED_NOT_REASSESSED')
        self.assertEqual(SharedTickets(self.state).get(self.id),self.saved)
        wrong=copy.deepcopy(bundle);wrong['components'][1]['rows'][0][4]+=1
        with self.assertRaisesRegex(StateConflict,'BUNDLE_SOURCE_CHANGED'):import_documents(self.state,'one',wrong)

    def test_partial_bundle_resume_cannot_substitute_a_component(self):
        bundle=self.bundle();checkpoints=[]
        with patch('investigator.shared_document_migration.import_tickets',side_effect=RuntimeError('simulated interruption')):
            with self.assertRaises(RuntimeError):import_documents(self.state,'partial',bundle,checkpoint=lambda p:checkpoints.extend(p))
        self.assertEqual([p['component']for p in checkpoints],['catalog'])
        self.assertEqual(SharedTickets(self.state).list(),{'tickets':[]})
        self.assertEqual(import_documents(self.state,'partial',bundle)['status'],'APPLIED')

    def test_export_opens_catalog_read_only_and_changes_no_bytes(self):
        import migrate_shared_documents as cli
        self.bundle();before=self.store.path.read_bytes();output=self.folder/'export.json'
        cli.main(['export','--catalog',str(self.store.path),'--environment','estate','--tape-class','EXACT','--output',str(output)])
        self.assertEqual(self.store.path.read_bytes(),before)
        self.assertEqual(json.loads(output.read_text())['components'][1],self.source)


@unittest.skipUnless(os.environ.get('DIA_TEST_POSTGRES_DSN'),'PostgreSQL DSN not configured')
class PostgreSQLTicketMigrationTests(TicketMigrationTests):
    def setUp(self):
        super().setUp()
        import psycopg
        from uuid import uuid4
        schema='tickets_'+uuid4().hex;dsn=os.environ['DIA_TEST_POSTGRES_DSN']
        with psycopg.connect(dsn) as db:db.execute('CREATE SCHEMA '+schema)
        def connect():
            db=psycopg.connect(dsn);db.execute('SET search_path TO '+schema);return db
        self.state=SharedState(connect,backend='postgresql',mode='live');self.state.migrate()
        def cleanup():
            with psycopg.connect(dsn) as db:db.execute('DROP SCHEMA '+schema+' CASCADE')
        self.addCleanup(cleanup)


if __name__=='__main__':unittest.main()

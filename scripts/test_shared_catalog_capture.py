"""An authoritative two-model result must not replay a six-model stale mirror."""
import sqlite3,tempfile,unittest
from contextlib import closing
from uuid import UUID
from pathlib import Path
from unittest.mock import patch
from investigator import process_tape as journal
from investigator.shared_catalog import SharedCatalog,RecordedCatalog,READ_RESULTS_VERSION,import_catalog
from investigator.onboarding import ModelStore,digest
from investigator.shared_state import SharedState
from investigator.shared_application import bootstrap_replay
from test_process_tape import bootstrap

class CatalogCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.state=SharedState.offline(self.root/'shared.sqlite');self.state.migrate()
        models=[];contexts=[]
        for identity,name in [('billing','Z Billing'),('fixture','A Fixture')]:
            context={'id':'context-'+identity,'model_id':identity,'measures':[]}
            models.append({'environment':'test','id':identity,'name':name,'enabled':True,'context_id':context['id'],'context':context})
            contexts.append({'model_id':identity,'context_id':context['id'],'body':context,'hash':digest(context)})
        self.source={'version':'shared-catalog-import-v1','environment':'test','models':models,'contexts':contexts}
        import_catalog(self.state,'test-source',self.source)
        self.catalog=SharedCatalog(self.state,'test')
        self.path=self.root/'tape.json'
    def tape(self,version=READ_RESULTS_VERSION):
        boot=bootstrap()
        if version is not None:boot['state']['shared_catalog_capture']=version
        return journal.Tape(self.path,boot)
    def stale_store(self):
        with patch('investigator.shared_state.configured_state',return_value=None):
            store=ModelStore(self.root/'private.sqlite',self.root/'inventory.sqlite','test')
        with closing(sqlite3.connect(store.database)) as db,db:
            for i in range(6):db.execute('INSERT INTO models VALUES(?,?,?,?,?,?,?,1,NULL,?)',
                (str(UUID(int=i+1)),'test','workspace','native-'+str(i),'Stale '+str(i),'[]',0,'{}'))
        return store
    def test_exact_live_results_replay_in_order_despite_stale_private_inventory(self):
        stale=self.stale_store();self.assertEqual(len(stale.list(True)),6)
        tape=self.tape()
        with journal.active(tape):
            original=[self.catalog.list(True),self.catalog.get('billing'),self.catalog.context('fixture','context-fixture')]
            tape.finish({'result':original})
        self.assertEqual([m['id'] for m in original[0]],['fixture','billing'])
        # list is one logical read result, not a nested preload or capture of
        # every historical published context. get/context preserve their ports.
        self.assertEqual([e['kind'] for e in tape.events],['BOOTSTRAP','BOUNDED_REQUEST','BOUNDED_RESPONSE',
            'BOUNDED_REQUEST','BOUNDED_RESPONSE','BOUNDED_REQUEST','BOUNDED_RESPONSE','FINAL'])
        replay=journal.Tape(self.path)
        with journal.active(replay),bootstrap_replay(), \
             patch('investigator.shared_state.configured_state',side_effect=AssertionError('No authority connection during replay')):
            store=ModelStore(stale.database,stale.inventory,'test')
            self.assertIsInstance(store.shared_catalog,RecordedCatalog)
            actual=[store.list(True),store.get('billing'),store.context('fixture','context-fixture')]
            self.assertEqual(actual,original);replay.finish({'result':actual})
        with closing(sqlite3.connect(stale.database)) as db:self.assertEqual(db.execute('SELECT count(*) FROM models').fetchone()[0],6)
    def test_request_drift_refuses_instead_of_selecting_a_recorded_result(self):
        tape=self.tape()
        with journal.active(tape):self.catalog.get('billing');tape.finish({})
        replay=journal.Tape(self.path)
        with journal.active(replay),self.assertRaisesRegex(journal.TapeError,'TAPE_REQUEST_BYTES_DIFFER'):
            RecordedCatalog('test').get('fixture')
    def test_old_tapes_keep_private_mirror_without_backfill_or_new_events(self):
        stale=self.stale_store();tape=self.tape(None)
        with journal.active(tape):self.catalog.list(True);tape.finish({})
        self.assertEqual([e['kind'] for e in tape.events],['BOOTSTRAP','FINAL'])
        replay=journal.Tape(self.path)
        with journal.active(replay),bootstrap_replay():
            store=ModelStore(stale.database,stale.inventory,'test')
            self.assertIsNone(store.shared_catalog);self.assertEqual(len(store.list(True)),6)
            replay.finish({})
    def test_unknown_read_contract_refuses_before_authority_read(self):
        tape=self.tape('READ_RESULTS_FUTURE')
        with journal.active(tape),patch.object(self.state,'get',side_effect=AssertionError('Must not read')), \
             self.assertRaisesRegex(journal.TapeError,'SHARED_CATALOG_CAPTURE_VERSION'):
            self.catalog.list(True)

if __name__=='__main__':unittest.main()

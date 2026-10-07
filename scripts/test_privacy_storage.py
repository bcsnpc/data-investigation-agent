import hashlib,json,sqlite3,tempfile,unittest
from contextlib import closing
from pathlib import Path
from investigator.privacy_storage import EvidenceStore,connect
from investigator.privacy_projection import Projection,ProjectionError,canonical
from investigator.privacy_identities import Identities,active
from investigator.onboarding import digest,encoded,ModelStore

COLUMN='column://synthetic/person_name'
POLICY={'tape_class':'PRIVACY_PROJECTED','version':'estate-privacy-projection-v1',
 'estate_id':'synthetic-estate','key_reference':'secret-store/estate','columns':[COLUMN]}
def projection():return Projection(POLICY,lambda _:b'synthetic-in-memory-key-32-bytes!!')


class StorageTests(unittest.TestCase):
    def test_projected_ledger_and_key_fingerprint_rekey_together_no_raw_value_or_digest(self):
        from investigator.privacy_capture import Capture
        from investigator.privacy_tape import PrivacyTape
        from investigator.translation_proposer import key_fingerprint
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);p=projection();capture=Capture(p,[])
            raw='PRIVATE KEY PERSON';normalization={'encoding':'TYPED_JSON'}
            with capture.active():
                keys=key_fingerprint([[raw]],normalization)
                body={'column_id':COLUMN,'value':raw,'keys':keys}
                original_hash=digest(body)
                capture.ledger_append(root/'ledger.json',{'body':body,'hash':original_hash})
                tape=PrivacyTape(root/'tape.json',p);tape.event('RESULT',canonical(body))
                projected=capture.finish(tape,body)
            self.assertNotEqual(projected['keys']['binary_hash'],keys['binary_hash'])
            self.assertEqual(projected['keys']['binary_hash'],key_fingerprint([[p.bind(COLUMN,raw)]],normalization)['binary_hash'])
            for path in root.rglob('*'):
                if path.is_file():
                    self.assertNotIn(raw.encode(),path.read_bytes())
                    self.assertNotIn(original_hash.encode(),path.read_bytes())
            loaded=Capture(projection(),[])
            row=loaded.ledger_rows(root/'ledger.json')[0]
            self.assertEqual(row['hash'],digest(row['body']))

    def test_untrusted_privacy_token_does_not_bypass_business_identifier_rule(self):
        from investigator.business_vocabulary import validate_identifier_form
        from investigator.privacy_capture import Capture
        p=projection();raw='PRIVATE PERSON';token=p.bind(COLUMN,raw)
        with self.assertRaises(ValueError):validate_identifier_form(token)
        with Capture(p,[]).active():
            self.assertEqual(validate_identifier_form(token),token)
            with self.assertRaises(ValueError):validate_identifier_form('privacy_v1_'+'0'*64)

    def test_model_store_uses_memory_before_projection_and_cold_load_validates_identity(self):
        raw='PRIVATE_SYNTHETIC_PERSON'
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'catalog.sqlite';p=projection();vault=EvidenceStore(path,p)
            self.addCleanup(vault.close);identities=Identities(p)
            with active(identities):
                store=ModelStore(path,root/'inventory.sqlite','synthetic')
                body={'column_id':COLUMN,'value':raw}
                child=digest(body);parent={'receipt':body,'receipt_hash':child}
                parent_hash=digest(parent)
                with store.connect() as db:
                    db.execute('CREATE TABLE evidence(body TEXT,hash TEXT)')
                    db.execute('INSERT INTO evidence VALUES(?,?)',(encoded(parent),parent_hash))
                # Including read-only file: URIs never opens a raw disk image.
                with connect(path.resolve().as_uri()+'?mode=ro',uri=True) as db:
                    self.assertIn(raw,db.execute('SELECT body FROM evidence').fetchone()[0])
                    with self.assertRaises(sqlite3.OperationalError):db.execute('DELETE FROM evidence')
            self.assertEqual(list(root.iterdir()),[])
            image=vault.prepare();identities.prepare();identities.rekey();vault.persist(image)
            for file in root.rglob('*'):
                if file.is_file():self.assertNotIn(raw.encode(),file.read_bytes())
            vault.close();loaded=EvidenceStore(path,projection());self.addCleanup(loaded.close)
            with connect(path) as db:
                text,seal=db.execute('SELECT body,hash FROM evidence').fetchone();saved=json.loads(text)
                self.assertEqual(digest(saved),seal)
                self.assertEqual(digest(saved['receipt']),saved['receipt_hash'])
                self.assertNotEqual(seal,parent_hash)
                self.assertNotIn(raw,text)

    def test_raw_existing_store_refuses_and_closed_route_does_not_fall_back(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'raw.sqlite'
            with closing(sqlite3.connect(path)) as db:db.execute('CREATE TABLE evidence(value TEXT)');db.commit()
            with self.assertRaises(ValueError):EvidenceStore(path,projection())
            with self.assertRaisesRegex(ProjectionError,'STORE_CLOSED'):connect(path)

    def test_store_key_and_policy_are_pinned_no_raw_key_in_image(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'evidence.sqlite';p=projection();store=EvidenceStore(path,p)
            with connect(path) as db:db.execute('CREATE TABLE evidence(value INTEGER)')
            store.persist(store.prepare());store.close()
            self.assertNotIn(b'synthetic-in-memory-key',path.read_bytes())
            other=Projection(POLICY,lambda _:b'a-different-in-memory-key-32-bytes!')
            with self.assertRaisesRegex(ProjectionError,'RE_RECORD_REQUIRED'):EvidenceStore(path,other)

    def test_hashes_used_as_map_keys_rekey_but_sensitive_schema_names_still_refuse(self):
        p=projection();identities=Identities(p)
        with active(identities):
            value={'column_id':COLUMN,'value':'PRIVATE_NAME'};key=digest(value)
            body={key:value};outer=digest(body)
        identities.prepare();mapping=identities.rekey();projected=p.project(body)
        self.assertEqual(list(projected),[mapping[key]])
        self.assertEqual(digest(projected),mapping[outer])
        with self.assertRaisesRegex(ProjectionError,'STRUCTURAL_KEY'):
            p.project({COLUMN:'quantity','quantity':12})

    def test_schema_collision_refuses_without_writing_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'evidence.sqlite';p=projection();store=EvidenceStore(path,p);self.addCleanup(store.close)
            with connect(path) as db:db.execute('CREATE TABLE private_table(value TEXT)')
            p.bind(COLUMN,'private_table')
            with self.assertRaisesRegex(ProjectionError,'STORE_SCHEMA'):store.persist(store.prepare())
            self.assertFalse(path.exists())

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import uuid
import sqlite3
from contextlib import closing
from source_snapshot import TABLES, canonical, digest, verify, verify_registered
from ingestion_contract import plan, validate_receipt


class SnapshotContractTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.folder=Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.manifest={'format_version':1,'status':'READY','isolation':'SNAPSHOT',
                       'transaction_completed':True,'snapshot_id':str(uuid.uuid4()),'tables':[]}
        for name in sorted(TABLES):
            path=self.folder/(name+'.jsonl')
            path.write_text(json.dumps(['comma, quote" newline\n unicode é',None])+'\n',encoding='utf-8')
            columns=[{'name':'id','sql_type':'nvarchar','clr_type':'System.String'},
                     {'name':'optional','sql_type':'nvarchar','clr_type':'System.String'}]
            self.manifest['tables'].append({'name':name,'file':path.name,'rows':1,'columns':columns,
                 'sha256':digest(path),'schema_sha256':hashlib.sha256(canonical(columns).encode()).hexdigest()})
        self.write()

    def write(self):
        (self.folder/'manifest.json').write_text(canonical(self.manifest),encoding='utf-8')

    def test_roundtrip_preserves_nulls_and_escaped_strings(self):
        self.assertEqual(verify(self.folder)['rows'],10)

    def test_changed_content_rejected(self):
        (self.folder/'orders.jsonl').write_text('["changed",null]\n')
        with self.assertRaises(ValueError): verify(self.folder)

    def test_expected_manifest_rejects_rewritten_metadata(self):
        expected=digest(self.folder/'manifest.json')
        self.manifest['snapshot_id']=str(uuid.uuid4());self.write()
        with self.assertRaises(ValueError): verify(self.folder,expected)

    def test_missing_duplicate_and_escaping_artifacts(self):
        original=copy.deepcopy(self.manifest)
        for mutate in (lambda m:m['tables'].pop(),lambda m:m['tables'].append(m['tables'][0]),
                       lambda m:m['tables'][0].update(file='../outside.jsonl')):
            self.manifest=copy.deepcopy(original);mutate(self.manifest);self.write()
            with self.assertRaises(ValueError): verify(self.folder)

    def test_failed_transaction_and_inaccurate_count(self):
        self.manifest['transaction_completed']=False;self.write()
        with self.assertRaises(ValueError): verify(self.folder)
        self.manifest['transaction_completed']=True;self.manifest['tables'][0]['rows']=2;self.write()
        with self.assertRaises(ValueError): verify(self.folder)

    def test_pending_is_not_publicly_ready(self):
        (self.folder/'manifest.json').rename(self.folder/'.manifest.pending')
        with self.assertRaises(FileNotFoundError): verify(self.folder)
        self.assertEqual(verify(self.folder,pending=True)['tables'],10)

    def test_publication_needs_exact_complete_version_map(self):
        p=plan(self.folder,digest(self.folder/'manifest.json'),str(uuid.uuid4()),str(uuid.uuid4()))
        receipt={'status':'COMPLETE','source_snapshot_id':p['source_snapshot_id'],
                 'source_manifest_sha256':p['source_manifest_sha256'],
                 'tables':[dict(t,rows=t['expected_rows'],delta_table_id=str(uuid.uuid4()),delta_version=0,content_reconciled=True) for t in p['tables']]}
        self.assertFalse(validate_receipt(p,receipt)['snapshot_proof'])
        for key,value in [('delta_version',True),('delta_version',-1),('content_reconciled',False),('source_sha256','wrong')]:
            bad=copy.deepcopy(receipt);bad['tables'][0][key]=value
            with self.assertRaises(ValueError):validate_receipt(p,bad)
        bad=copy.deepcopy(receipt);bad['tables'].pop()
        with self.assertRaises(ValueError):validate_receipt(p,bad)

    def test_registry_anchors_expected_manifest_hash(self):
        database=self.folder/'registry.sqlite'
        with closing(sqlite3.connect(database)) as db:
            db.execute('CREATE TABLE source_snapshots(snapshot_id TEXT,manifest_sha256 TEXT,directory TEXT)')
            db.execute('INSERT INTO source_snapshots VALUES(?,?,?)',(self.manifest['snapshot_id'],digest(self.folder/'manifest.json'),str(self.folder)))
            db.commit()
        self.assertEqual(verify_registered(database,self.manifest['snapshot_id'])['rows'],10)
        self.manifest['extra']='rewritten';self.write()
        with self.assertRaises(ValueError):verify_registered(database,self.manifest['snapshot_id'])


if __name__=='__main__':unittest.main()

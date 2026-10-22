import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import zipfile

from investigator.onboarding import ModelStore
from prepare_runner_retry_inputs import INPUT_MEMBERS, PREPARED_NAMES, rebuild, sha, selected_parent


class RetryInputsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.prepared=self.root/'prepared';self.prepared.mkdir()
        self.store=ModelStore(self.prepared/'catalog.sqlite',self.prepared/'inventory.sqlite','fixture')
        model=self.store.register({'name':'fixture','workspace':'11111111-1111-1111-1111-111111111111','model_id':'22222222-2222-2222-2222-222222222222','report_ids':['33333333-3333-3333-3333-333333333333']},'test')
        with self.store.connect() as db:
            db.execute('UPDATE models SET revision=85 WHERE id=?',(model['id'],))
            db.execute('CREATE TABLE enterprise_scans(id TEXT,environment TEXT,hash TEXT)')
            db.execute('INSERT INTO enterprise_scans VALUES(?,?,?)',('retained-source','fixture','a'*64))
        self.model=self.store.get(model['id'])
        (self.prepared/'inventory.sqlite').write_bytes(b'fixture-inventory')
        for name in PREPARED_NAMES-{'catalog.sqlite','inventory.sqlite'}:
            (self.prepared/name).write_text(json.dumps(self.model if name=='model.json' else {'fixture':name}))
        self.manifest=self.root/'dependencies.json'
        self.manifest.write_text(json.dumps({'version':'cloud-verifier-cas-dependencies-v1','kind':'prepared','status':'RETAINED','files':[{'name':n,'sha256':sha(self.prepared/n),'bytes':(self.prepared/n).stat().st_size} for n in sorted(PREPARED_NAMES)]}))
        self.source=self.root/'original.zip'
        self.original={n:b'unchanged:'+n.encode() for n in INPUT_MEMBERS}
        self.original.update({'estate.json':json.dumps({'environment':'fixture'}).encode(),'form.json':json.dumps({'request_key':'first','visual':'card'}).encode(),'operator-plan.json':json.dumps({'source_context':'retained-source','source_context_hash':'a'*64,'decision':'original'}).encode()})
        with zipfile.ZipFile(self.source,'w') as z:
            for n,v in self.original.items():z.writestr(n,v)
        self.hashes={p:sha(p) for p in [self.source,self.manifest,*self.prepared.iterdir()]}

    def build(self):
        return rebuild(self.source,self.hashes[self.source],self.manifest,self.hashes[self.manifest],self.prepared,self.root/'retry',request_key='attempt-2',decision='owner approved retry')

    def test_exact_retained_parent_replaces_stale_zip_without_editing_history(self):
        result=self.build();self.assertEqual(85,result['selected_parent']['revision'])
        with zipfile.ZipFile(self.root/'retry'/'inputs.zip') as z:
            self.assertEqual((self.prepared/'catalog.sqlite').read_bytes(),z.read('catalog.sqlite'))
            self.assertEqual((self.prepared/'inventory.sqlite').read_bytes(),z.read('inventory.sqlite'))
            for n in result['unchanged_members']:self.assertEqual(self.original[n],z.read(n))
            form=json.loads(z.read('form.json'));self.assertEqual({'request_key':'attempt-2','visual':'card'},form)
            plan=json.loads(z.read('operator-plan.json'));self.assertEqual('retained-source',plan['source_context'])
        self.assertEqual(self.hashes,{p:sha(p) for p in self.hashes})
        self.assertEqual(0,result['physical_requests']);self.assertEqual(0,result['model_calls'])

    def test_selected_parent_rejects_even_history_difference(self):
        wrong={**self.model,'events':[]}
        with self.assertRaisesRegex(ValueError,'SELECTED_MODEL_DIFFERS'):
            selected_parent(self.prepared/'catalog.sqlite','fixture',wrong)
        self.assertEqual(self.hashes[self.prepared/'catalog.sqlite'],sha(self.prepared/'catalog.sqlite'))

    def test_dependency_tamper_refuses_before_output(self):
        (self.prepared/'inventory.sqlite').write_bytes(b'tampered')
        with self.assertRaisesRegex(ValueError,'DEPENDENCY_HASH_DIFFERS'):self.build()
        self.assertFalse((self.root/'retry').exists())

    def test_original_zip_tamper_refuses(self):
        with self.source.open('ab') as stream:stream.write(b'changed')
        with self.assertRaisesRegex(ValueError,'SOURCE_INPUT_ZIP_HASH_DIFFERS'):self.build()
        self.assertFalse((self.root/'retry').exists())

    def test_source_context_must_survive_exact_parent(self):
        with zipfile.ZipFile(self.source,'w') as z:
            for n,v in self.original.items():
                z.writestr(n,json.dumps({'source_context':'missing','source_context_hash':'a'*64}).encode() if n=='operator-plan.json' else v)
        self.hashes[self.source]=sha(self.source)
        with self.assertRaisesRegex(ValueError,'RETAINED_SOURCE_CONTEXT_MISSING'):self.build()
        self.assertFalse((self.root/'retry').exists())


if __name__=='__main__':unittest.main()

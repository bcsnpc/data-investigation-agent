import contextlib,hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
from investigator.normal_audit import AuditContext,normal_context,mode
from investigator.ticket_catalog import materialize
from investigator.onboarding import ModelStore,digest,encoded

class NormalAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.sent=[]
        self.parent=SimpleNamespace(root=self.root,record=lambda kind,value:self.sent.append((kind,value))or {'key':'outer:'+str(len(self.sent))})
    def test_default_and_test_modes_are_distinct_and_unknown_refuses(self):
        self.assertEqual(mode(),'NORMAL');self.assertEqual(mode('TEST'),'TEST')
        with self.assertRaises(ValueError):mode('maybe')
    def test_records_batch_without_losing_original_values_and_progress_is_immediate(self):
        with normal_context(self.parent,'case-one')as audit:
            value={'query':'SELECT quantity FROM declared_object','value':16}
            first=audit.record('query',value);value['value']=99
            for i in range(10):audit.record('evidence-summary',{'id':str(i),'state':'observed'})
            self.assertEqual(self.sent,[])
            audit.progress({'stage':'ACKNOWLEDGED'});self.assertEqual(self.sent[-1][0],'progress')
        batches=[v for k,v in self.sent if k=='normal-audit-batch']
        self.assertEqual(len(batches),1);self.assertFalse(batches[0]['byte_exact_replay'])
        self.assertEqual(batches[0]['records'][0]['value']['value'],16)
        self.assertEqual(batches[0]['records'][0]['id'],first['key'])
        for row in batches[0]['records']:
            raw=json.dumps(row['value'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
        self.assertFalse(list(self.root.glob('*tape*')))
    def test_exception_publishes_partial_audit_instead_of_losing_failed_run(self):
        with self.assertRaisesRegex(ValueError,'original'):
            with normal_context(self.parent,'failed')as audit:
                audit.record('error',{'type':'query error'});raise ValueError('original')
        self.assertTrue(next(v for k,v in self.sent if k=='normal-audit-batch')['partial'])
    def test_failed_partial_publication_cannot_replace_original_error(self):
        self.parent.record=Mock(side_effect=OSError('storage unavailable'))
        with self.assertRaisesRegex(ValueError,'original'):
            with normal_context(self.parent,'failed')as audit:
                audit.record('error',{'class':'QUERY_ERROR'});raise ValueError('original')
    def test_ticket_catalog_contains_only_selected_current_rows_not_history(self):
        from cloud_stage_worker import offline
        source=self.root/'source.sqlite';inventory=self.root/'inventory.json';inventory.write_text('{}')
        model_id='11111111-1111-4111-8111-111111111111';context_id='22222222-2222-4222-8222-222222222222'
        model={'id':model_id,'context_id':context_id,'context':{'model_assets':[]}}
        with offline():original=ModelStore(source,inventory,'development')
        with original.connect()as db:
            db.execute('INSERT INTO models VALUES(?,?,?,?,?,?,?,?,?,?)',(model_id,'development','workspace','native','fixture','[]',1,1,context_id,'{}'))
            db.execute('INSERT INTO model_contexts VALUES(?,?,?,?,?,?)',(context_id,model_id,'scan',encoded(model['context']),digest(model['context']),'2026-10-22T00:00:00Z'))
            db.execute('CREATE TABLE unrelated_history(body)')
            db.executemany('INSERT INTO unrelated_history VALUES(?)',[('old private evidence'*1000,)]*100)
        current={'version':'scan','assets':[],'graph':{'edges':[]}}
        store,summary=materialize(source,self.root/'session.sqlite',model=model,context=current,inventory=inventory,environment='development')
        self.assertEqual(summary['historical_scans'],0);self.assertEqual(summary['model_contexts'],1)
        with store.connect()as db:
            self.assertEqual(db.execute('SELECT count(*) FROM models').fetchone()[0],1)
            self.assertFalse(db.execute("SELECT 1 FROM sqlite_master WHERE name='unrelated_history'").fetchone())
        from investigator.context_search import latest
        self.assertEqual(latest(store),current)
        self.assertLess(store.database.stat().st_size,source.stat().st_size/4)

if __name__=='__main__':unittest.main()

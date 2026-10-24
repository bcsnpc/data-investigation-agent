import contextlib,hashlib,json,sqlite3,tempfile,unittest,os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
from investigator.normal_audit import AuditContext,normal_context,mode
from investigator.ticket_catalog import materialize
from investigator.onboarding import ModelStore,digest,encoded

class NormalAuditTests(unittest.TestCase):
    def test_normal_mode_disables_legacy_exact_recording_and_restores_switches(self):
        from investigator.run_recording import operation
        agent=SimpleNamespace(config={},planner_profile={'adapter':'azure'})
        original=Mock(return_value={'status':'DELIVERED'})
        decorated=operation('intake')(original)
        with patch.dict(os.environ,{'INVESTIGATOR_RECORD_RUNS':'1','INVESTIGATOR_RECORD_PLANNER':'1'}):
            with normal_context(self.parent,'legacy'):
                self.assertEqual(os.environ['INVESTIGATOR_RECORD_RUNS'],'0')
                self.assertEqual(os.environ['INVESTIGATOR_RECORD_PLANNER'],'0')
                self.assertEqual(decorated(agent,{'text':'Describe the named calculation.'}),{'status':'DELIVERED'})
            self.assertEqual(os.environ['INVESTIGATOR_RECORD_RUNS'],'1')
            self.assertEqual(os.environ['INVESTIGATOR_RECORD_PLANNER'],'1')
        original.assert_called_once()
        self.assertFalse(hasattr(agent,'_run_tapes'))

    def test_failed_normal_run_restores_recording_switches(self):
        with patch.dict(os.environ,{'INVESTIGATOR_RECORD_RUNS':'1'}):
            with self.assertRaisesRegex(ValueError,'failed'):
                with normal_context(self.parent,'legacy-failed'):
                    raise ValueError('failed')
            self.assertEqual(os.environ['INVESTIGATOR_RECORD_RUNS'],'1')

    def test_legacy_comparison_handler_uses_normal_mode_without_changing_intake(self):
        from investigator.unified_runner import handlers
        ticket={'id':'baseline-case','text':'Describe the named calculation.'}
        path=self.root/'ticket.json';path.write_text(json.dumps(ticket))
        workspace=SimpleNamespace(close=Mock())
        manifest={'model':{'credential':{},'endpoint':'configured','deployment':'configured'}}
        def submit(actual_workspace,actual_ticket):
            self.assertIs(actual_workspace,workspace);self.assertEqual(actual_ticket,ticket)
            self.assertEqual(os.environ['INVESTIGATOR_RECORD_RUNS'],'0')
            return {'status':'CLARIFYING','question':'Original intake question.'}
        with patch('investigator.estate_installation.build',return_value=(manifest,workspace)), \
             patch('run_adaptive_investigation.local_azure_key',return_value=contextlib.nullcontext()), \
             patch('cloud_form_worker.run_form',side_effect=submit)as intake:
            result=handlers()['legacy-baseline']({'manifest':'unused','run_id':'legacy-one',
                'options':{'ticket':str(path)}},self.parent)
        self.assertEqual(result['question'],'Original intake question.')
        intake.assert_called_once();workspace.close.assert_called_once()
        self.assertTrue(any(k=='normal-audit-batch'for k,v in self.sent))

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
            db.execute('CREATE TABLE discovery_models(model_id,denied,policy_hash)')
            db.execute('INSERT INTO discovery_models VALUES(?,?,?)',(model_id,1,'approved-policy-hash'))
            db.executemany('INSERT INTO unrelated_history VALUES(?)',[('old private evidence'*1000,)]*100)
        current={'version':'scan','assets':[],'graph':{'edges':[]}}
        store,summary=materialize(source,self.root/'session.sqlite',model=model,context=current,inventory=inventory,environment='development')
        self.assertEqual(summary['historical_scans'],0);self.assertEqual(summary['model_contexts'],1)
        with store.connect()as db:
            self.assertEqual(db.execute('SELECT count(*) FROM models').fetchone()[0],1)
            self.assertFalse(db.execute("SELECT 1 FROM sqlite_master WHERE name='unrelated_history'").fetchone())
        from investigator.context_search import latest
        self.assertEqual(latest(store),current)
        self.assertEqual(store.get(model_id)['discovery'],{'denied':1,'policy_hash':'approved-policy-hash'})
        self.assertLess(store.database.stat().st_size,source.stat().st_size/4)

if __name__=='__main__':unittest.main()

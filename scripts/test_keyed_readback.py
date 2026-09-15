import copy
from decimal import Decimal
import hashlib
from io import BytesIO
import json
import sqlite3
import unittest
from unittest.mock import MagicMock, patch

import test_adaptive_investigation as fixture
from investigator import record_readback as records, record_comparison as comparison
from investigator.adaptive_candidates import catalog
from investigator.admin_api import create_app
from investigator.onboarding import Conflict
from investigator.runtime import Runtime
from run_source_diagnostic import read_once
from test_native_diagnostics import response, database


class ReadbackTests(unittest.TestCase):
    def setUp(self):
        h=fixture.AdaptiveTests();h.setUp();self.addCleanup(h.doCleanups);self.helper=h
        for key in ('store','config','model','envelope','agent','planner','native','source'):setattr(self,key,getattr(h,key))
        source=h.envelope['source_tests'][0]['plan'];obj=source['object_id']
        with database(self.store.inventory) as db:
            db.row_factory=sqlite3.Row
            row=dict(db.execute('SELECT * FROM assets WHERE id=?',(obj+'/currency',)).fetchone())
            meta=json.loads(row['metadata']);meta['name']='entity_id'
            row.update(id=obj+'/entity_id',name='entity_id',metadata=json.dumps(meta,sort_keys=True,ensure_ascii=False))
            row['content_hash']=hashlib.sha256(row['metadata'].encode()).hexdigest()
            db.execute('INSERT INTO assets('+','.join(row)+') VALUES('+','.join('?' for _ in row)+')',list(row.values()))
        self.model['context']['reports'][0]['model_assets'] += [
            {'id':'key','kind':'SemanticColumn','name':'entity_id','parent_id':'t','metadata':{'dataType':'string'}},
            {'id':'amount','kind':'SemanticColumn','name':'amount','parent_id':'t','metadata':{'dataType':'decimal'}}]
        self.nplan={k:source[k] for k in ('model_id','revision','context_id')}
        self.nplan.update(object_id='t',column_ids=['key','amount'],key_column_ids=['key'],filters=self.envelope['filters'],limit=3)
        self.splan=dict(self.nplan,object_id=obj,column_ids=[obj+'/entity_id',obj+'/amount'],key_column_ids=[obj+'/entity_id'],filters=source['filters'])
        self.mapping=[{'native_column_id':a,'source_column_id':b} for a,b in zip(self.nplan['column_ids'],self.splan['column_ids'])]
        self.filters=[{'native_column_id':'c','source_column_id':obj+'/currency'}]
        self.ntransport=MagicMock(return_value=self.native_rows([('A','10',1),('B','20',1)]))
        self.stransport=MagicMock(return_value=self.sql_rows([('A','10',1),('B','20',1)]))
        self.runtime=Runtime(self.store,self.config,self.ntransport,self.stransport)

    def native_rows(self,rows):return response([{'[c0]':k,'[c1]':Decimal(v) if v is not None else None,'[multiplicity]':m} for k,v,m in rows])
    def sql_rows(self,rows):return {'rows':[{'c0':k,'c1':v,'multiplicity':str(m)} for k,v,m in rows]}
    def build(self,backend='native_records',plan=None):return records.build(self.store,plan or (self.nplan if backend=='native_records' else self.splan),self.config,backend)
    def receipts(self):
        n=records.run(self.store,self.nplan,self.config,'native_records',self.ntransport)
        s=records.run(self.store,self.splan,self.config,'source_records',self.stransport)
        return records.read(self.store,'model',n['id']),records.read(self.store,'model',s['id'])
    def compare(self):return comparison.compare(*self.receipts(),self.mapping,self.filters)
    def request(self):return {'model_id':'model','call_budget':2,'actions':[
        {'tool':'native_records','input':self.nplan},{'tool':'source_records','input':self.splan},
        {'tool':'compare_records','input':{'native_step':0,'source_step':1,'column_bindings':self.mapping,'filter_bindings':self.filters}}]}

    def test_native_groups_and_orders_all_projection_columns_with_count(self):
        query=self.build()['query']
        self.assertIn('TOPN(4,SUMMARIZECOLUMNS',query)
        self.assertIn("'O''Brien'[entity_id],ASC,'O''Brien'[amount],ASC",query)
        self.assertIn("COUNTROWS('O''Brien')",query)

    def test_source_query_preserves_scope_and_group_multiplicity(self):
        request=self.build('source_records')
        self.assertIn('TOP (4)',request['query']);self.assertIn('GROUP BY [entity_id],[amount]',request['query'])
        self.assertIn('COUNT_BIG(*)',request['query']);self.assertNotIn('USD',request['query'])
        self.assertEqual(request['parameters'],[{'name':'@p0','value':'USD'}])

    def test_invalid_limits_projection_keys_and_cross_table_rejected(self):
        for change in [{'limit':0},{'limit':251},{'limit':True},{'column_ids':['key','key']},
                       {'key_column_ids':['unknown']},{'object_id':'missing'},{'filters':[]}]:
            with self.subTest(change=change),self.assertRaises(ValueError):self.build(plan=dict(self.nplan,**change))
        with self.assertRaises(ValueError):self.build('source_records',dict(self.splan,column_ids=['key']))

    def test_unknown_native_type_and_cross_workspace_rejected(self):
        self.model['context']['reports'][0]['model_assets'][-1]['metadata']['dataType']='double'
        with self.assertRaises(ValueError):self.build()
        self.model['context']['reports'][0]['model_assets'][-1]['metadata']['dataType']='decimal'
        self.config['fabric']['workspace_id']='other'
        with self.assertRaises(Conflict):self.build()

    def test_exact_decimal_and_submicrosecond_dates_are_not_rounded(self):
        raw='12345678901234567890123456789.1234'
        self.assertEqual(records.value(raw,'decimal','source_records')['value'],raw)
        self.assertEqual(records.value('2026-01-01T00:00:00.0000001','dateTime','source_records')['value'],'2026-01-01T00:00:00.0000001')
        self.assertEqual(records.value('2026-01-01','dateTime','source_records')['value'],'2026-01-01T00:00:00')
        self.assertEqual(records.value('-0.000','decimal','source_records')['value'],'0')
        self.assertEqual(records.value(Decimal('1E+3'),'decimal','native_records')['value'],'1000')

    def test_lossy_or_malformed_record_values_rejected(self):
        for raw,kind in [(1.1,'decimal'),(True,'int64'),('NaN','decimal'),('1e2','decimal'),('1.1','int64'),
                         ('2026-01-01T00:00:00Z','dateTime'),('2026-02-30','dateTime'),('x'*1001,'string')]:
            with self.subTest(raw=raw,kind=kind),self.assertRaises(ValueError):records.value(raw,kind,'native_records')

    def test_complete_empty_response_is_not_missing_response(self):
        result=records.extract(self.native_rows([]),self.build())
        self.assertEqual(result['completeness'],'COMPLETE_RESPONSE');self.assertEqual(result['observed_row_count'],'0')
        with self.assertRaises(ValueError):records.extract({'results':[{'tables':[{}]}]},self.build())

    def test_extra_group_marks_partial_and_preserves_sentinel_count(self):
        result=records.extract(self.native_rows([(str(i),'1',1) for i in range(4)]),self.build())
        self.assertEqual(result['completeness'],'PARTIAL');self.assertEqual(result['returned_groups'],4)
        self.assertEqual(result['retained_groups'],3)

    def test_unbounded_response_errors_and_duplicate_group_fail(self):
        for output in [self.native_rows([(str(i),'1',1) for i in range(5)]),
                       self.native_rows([('A','1',1),('A','1',1)]),self.native_rows([('A','1',0)]),
                       {'results':[{'error':{'message':'private'}}]}]:
            with self.subTest(output=output),self.assertRaises(ValueError):records.extract(output,self.build())

    def test_null_and_boolean_types_preserved(self):
        self.assertEqual(records.value(None,'decimal','source_records'),{'type':'blank','value':None})
        self.assertEqual(records.value('1','boolean','source_records'),{'type':'boolean','value':True})
        with self.assertRaises(ValueError):records.value('true','boolean','source_records')

    def test_same_totals_can_have_two_changed_keys(self):
        self.ntransport.return_value=self.native_rows([('A','15',1),('B','15',1)])
        result=self.compare()
        self.assertEqual(result['status'],'OBSERVED_DIFFERENCE');self.assertEqual(result['difference_count'],2)
        self.assertTrue(all(d['kind']=='VALUES_DIFFER' for d in result['differences']))
        self.assertFalse(result['root_cause_verified']);self.assertFalse(result['comparable'])

    def test_missing_and_extra_keys_are_directional(self):
        self.ntransport.return_value=self.native_rows([('A','10',1),('C','20',1)])
        result=self.compare()
        self.assertEqual({d['kind'] for d in result['differences']},{'ONLY_NATIVE','ONLY_SOURCE'})

    def test_equal_capture_is_not_expected_behavior_or_cause(self):
        result=self.compare();self.assertEqual(result['status'],'OBSERVED_EQUAL')
        self.assertEqual(result['difference_count'],0);self.assertFalse(result['delivery_eligible'])
        self.assertIn('SHARED_GENERATION_UNVERIFIED',result['proof_gaps'])

    def test_partial_read_never_reports_missing_keys(self):
        self.ntransport.return_value=self.native_rows([(str(i),'1',1) for i in range(4)])
        result=self.compare();self.assertEqual(result['status'],'NOT_ASSESSED')
        self.assertIsNone(result['difference_count']);self.assertEqual(result['differences'],[])
        self.assertIn('PARTIAL_READBACK',result['gaps'])

    def test_duplicate_key_multiplicity_and_distinct_values_are_gaps(self):
        for rows in [[('A','10',2)],[('A','10',1),('A','20',1)]]:
            self.ntransport.return_value=self.native_rows(rows)
            result=self.compare();self.assertIn('DUPLICATE_KEY',result['gaps']);self.assertEqual(result['differences'],[])

    def test_null_keys_do_not_pair_as_an_entity(self):
        self.ntransport.return_value=self.native_rows([(None,'10',1)])
        self.assertIn('NULL_KEY',self.compare()['gaps'])

    def test_filter_difference_disables_record_diff(self):
        self.splan['filters']=[dict(self.splan['filters'][0],values=['EUR'])]
        self.assertIn('FILTER_SCOPE_DIFFERS',self.compare()['gaps'])

    def test_full_bijection_and_key_mapping_required(self):
        receipts=self.receipts()
        for mapping in [self.mapping[:1],[self.mapping[0],self.mapping[0]]]:
            with self.assertRaises(ValueError):comparison.compare(*receipts,mapping,self.filters)

    def test_canonical_decimal_text_and_row_order_do_not_create_changes(self):
        self.stransport.return_value=self.sql_rows([('B','20.0000',1),('A','10.00',1)])
        self.assertEqual(self.compare()['status'],'OBSERVED_EQUAL')

    def test_receipt_reserved_before_dispatch_and_history_survives_disable(self):
        def execute(request):
            with self.store.connect() as db:self.assertEqual(db.execute('SELECT status FROM record_readbacks').fetchone()[0],'RUNNING')
            return self.native_rows([('A','10',1)])
        receipt=records.run(self.store,self.nplan,self.config,'native_records',execute)
        self.model['enabled']=False
        self.assertFalse(records.read(self.store,'model',receipt['id'])['local_context_current'])
        with self.assertRaises(KeyError):records.read(self.store,'other',receipt['id'])

    def test_midflight_change_and_timeout_are_not_success(self):
        def changed(request):
            self.model['revision']+=1
            return self.native_rows([('A','10',1)])
        self.assertEqual(records.run(self.store,self.nplan,self.config,'native_records',changed)['status'],'HELD')
        self.model['revision']=3
        result=records.run(self.store,self.splan,self.config,'source_records',MagicMock(side_effect=TimeoutError('private')))
        self.assertEqual(result['status'],'INTERRUPTED');self.assertNotIn('private',str(result))

    def test_durable_two_reads_and_comparison_replay(self):
        result=self.runtime.execute(self.runtime.create(self.request(),'records')['id'])
        self.assertEqual(result['status'],'COMPLETED');self.assertEqual(result['outcome']['status'],'OBSERVED_EQUAL')
        self.runtime.execute(result['id']);self.ntransport.assert_called_once();self.stransport.assert_called_once()
        self.assertEqual(result['calls_reserved'],2)

    def test_recovery_adopts_saved_read_without_requery(self):
        identity=self.runtime.create(self.request(),'crash')['id']
        original=self.runtime.commit
        self.runtime.commit=MagicMock(side_effect=RuntimeError('crash'))
        self.assertEqual(self.runtime.execute(identity)['status'],'HELD')
        self.runtime.commit=original
        self.runtime.reconcile(identity)
        self.assertEqual(self.runtime.execute(identity)['status'],'COMPLETED')
        self.ntransport.assert_called_once();self.stransport.assert_called_once()

    def test_recovery_adopts_local_comparison_without_failed_status(self):
        identity=self.runtime.create(self.request(),'local-crash')['id'];original=self.runtime.commit
        def commit(run,ordinal,token,result):
            if ordinal==2:raise RuntimeError('crash')
            return original(run,ordinal,token,result)
        self.runtime.commit=commit;self.assertEqual(self.runtime.execute(identity)['status'],'HELD')
        self.runtime.commit=original
        result=self.runtime.reconcile(identity)
        self.assertEqual(result['status'],'COMPLETED');self.assertEqual(result['outcome']['status'],'OBSERVED_EQUAL')
        self.ntransport.assert_called_once();self.stransport.assert_called_once()

    def test_remote_timeout_cannot_be_retried_by_reconciliation(self):
        self.ntransport.side_effect=TimeoutError()
        identity=self.runtime.create(self.request(),'timeout')['id'];self.runtime.execute(identity)
        with self.assertRaises(Conflict):self.runtime.reconcile(identity)
        self.ntransport.assert_called_once();self.stransport.assert_not_called()

    def test_comparison_api_roles_and_saved_hash(self):
        left,right=self.receipts();body={'native_receipt_id':left['id'],'source_receipt_id':right['id'],'column_bindings':self.mapping,'filter_bindings':self.filters}
        app=create_app(self.store,'a'*32,'r'*32)
        for token,status in [('r'*32,'403 Forbidden'),('a'*32,'200 OK')]:
            statuses=[];raw=json.dumps(body).encode()
            out=b''.join(app({'PATH_INFO':'/api/v2/admin/models/model/record-comparisons','REQUEST_METHOD':'POST',
                             'HTTP_AUTHORIZATION':'Bearer '+token,'CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(raw)),
                             'wsgi.input':BytesIO(raw)},lambda s,h:statuses.append(s)))
            self.assertEqual(statuses,[status])
            if status=='200 OK':
                result=json.loads(out);self.assertEqual(comparison.read(self.store,'model',result['id'])['hash'],result['hash'])

    def test_source_worker_receives_record_limits_and_shape(self):
        self.config['sql']['auth']['credential_file']='unused'
        request=self.build('source_records')
        with patch('run_source_diagnostic.subprocess.run',return_value=MagicMock(returncode=0,stdout='{"rows":[]}')) as call:
            self.assertEqual(read_once(self.config,request),{'rows':[]})
        payload=json.loads(call.call_args.kwargs['input'])
        self.assertEqual(payload['max_rows'],4);self.assertEqual(payload['result_columns'],['c0','c1','multiplicity'])

    def test_adaptive_record_test_unlocks_after_scalar_and_preserves_evidence(self):
        self.envelope['record_tests']=[{'tool':'native_records','measure_id':'Unseen ratio','plan':self.nplan}]
        self.envelope['limits']['planner_calls']=3
        def planner(payload):
            if not payload['observations']:
                self.assertFalse(any(c['tool']=='native_records' for c in payload['candidates']))
                return fixture.decision(self.helper.choose(payload)),{}
            if len(payload['observations'])==1:
                self.native.return_value=self.native_rows([('A','10',1)])
                return fixture.decision(next(c['id'] for c in payload['candidates'] if c['tool']=='native_records')),{}
            return fixture.decision(),{}
        self.planner.side_effect=planner
        result=self.agent.run(self.agent.create(self.envelope,'adaptive-record')['id'])
        self.assertEqual(result['status'],'COMPLETED')
        self.assertEqual(result['observations'][1]['record_readback']['column_ids'],['key','amount'])
        self.assertFalse(result['outcome']['cause_verified'])

    def test_adaptive_readback_cannot_drop_native_filter(self):
        self.envelope['record_tests']=[{'tool':'native_records','measure_id':'Unseen ratio','plan':dict(self.nplan,filters=[])}]
        with self.assertRaises(ValueError):catalog(self.store,self.config,self.envelope)

    def test_invalid_comparison_mapping_is_rejected_before_any_cloud_read(self):
        request=self.request();request['actions'][2]['input']['column_bindings']=self.mapping[:1]
        with self.assertRaises(ValueError):self.runtime.create(request,'invalid-map')
        self.ntransport.assert_not_called();self.stransport.assert_not_called()

    def test_readback_tamper_prevents_comparison_and_recovery(self):
        left,right=self.receipts()
        with self.store.connect() as db:db.execute("UPDATE record_readbacks SET result='{}' WHERE id=?",(left['id'],))
        with self.assertRaises(ValueError):records.read(self.store,'model',left['id'])
        with self.assertRaises(ValueError):comparison.assess(self.store,'model',{'native_receipt_id':left['id'],'source_receipt_id':right['id'],
                                                                              'column_bindings':self.mapping,'filter_bindings':self.filters})

    def test_more_than_fifty_differences_have_exact_count_and_bounded_examples(self):
        self.nplan['limit']=60;self.splan['limit']=60
        self.ntransport.return_value=self.native_rows([(str(i),'1',1) for i in range(60)])
        self.stransport.return_value=self.sql_rows([(str(i),'2',1) for i in range(60)])
        result=self.compare()
        self.assertEqual(result['difference_count'],60);self.assertEqual(len(result['differences']),50)
        self.assertTrue(result['examples_truncated'])

    def test_cancelled_record_run_does_not_restart_during_recovery(self):
        identity=self.runtime.create(self.request(),'cancel')['id'];original=self.runtime.commit
        self.runtime.commit=MagicMock(side_effect=RuntimeError('crash'))
        self.runtime.execute(identity);self.runtime.cancel(identity);self.runtime.commit=original
        result=self.runtime.reconcile(identity)
        self.assertEqual(result['status'],'CANCELLED');self.ntransport.assert_called_once();self.stransport.assert_not_called()

    def test_adaptive_pair_is_saved_and_informs_next_decision_without_extra_query(self):
        self.envelope['record_tests']=[{'tool':'native_records','measure_id':'Unseen ratio','plan':self.nplan},
                                       {'tool':'source_records','measure_id':'Unseen ratio','plan':self.splan}]
        self.envelope['record_pairs']=[{'native_test':0,'source_test':1,'column_bindings':self.mapping,'filter_bindings':self.filters}]
        self.source.return_value=self.sql_rows([('A','10',1)])
        def planner(payload):
            count=len(payload['observations'])
            if count==0:return fixture.decision(self.helper.choose(payload)),{}
            if count==1:
                self.native.return_value=self.native_rows([('A','11',1)])
                tool='native_records'
            elif count==2:tool='source_records'
            else:
                self.assertEqual(payload['record_comparisons'][0]['difference_count'],1)
                self.assertFalse(payload['record_comparisons'][0]['root_cause_verified'])
                return fixture.decision(),{}
            return fixture.decision(next(c['id'] for c in payload['candidates'] if c['tool']==tool)),{}
        self.planner.side_effect=planner
        result=self.agent.run(self.agent.create(self.envelope,'paired-records')['id'])
        self.assertEqual(result['status'],'COMPLETED')
        self.assertEqual(result['outcome']['record_comparisons'][0]['status'],'OBSERVED_DIFFERENCE')
        self.assertEqual(result['cloud_calls'],3);self.assertEqual(self.native.call_count,2);self.source.assert_called_once()
        self.agent.run(result['id']);self.source.assert_called_once()

    def test_bad_adaptive_pair_references_are_rejected_before_planning(self):
        self.envelope['record_tests']=[{'tool':'native_records','measure_id':'Unseen ratio','plan':self.nplan}]
        self.envelope['record_pairs']=[{'native_test':0,'source_test':0,'column_bindings':self.mapping,'filter_bindings':self.filters}]
        with self.assertRaises(ValueError):self.agent.create(self.envelope,'bad-pair')
        self.planner.assert_not_called()


if __name__=='__main__':unittest.main()

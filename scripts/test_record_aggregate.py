import copy
from decimal import Decimal
from io import BytesIO
import json
import unittest
from unittest.mock import MagicMock

import test_record_discovery as fixture
from test_native_diagnostics import response
from test_adaptive_investigation import decision
from investigator import record_aggregate as reconcile, record_bindings, diagnostic_evidence, source_diagnostics
from investigator.runtime import Runtime
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.admin_api import create_app


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        h=fixture.DiscoveryTests();h.setUp();self.addCleanup(h.doCleanups);self.h=h
        self.store=h.store;self.model=h.model;self.config=h.config
        self.measure=h.envelope['measure_id']
        for asset in self.model['context']['reports'][0]['model_assets']:
            if asset['id']==self.measure:asset['metadata']={'expression':"SUM('O''Brien'[amount])"}
        self.model['context']['semantic_graph']['measures'][self.measure].update(operations=['AGGREGATE'],dependencies=[])
        self.review=h.register()
        candidates=h.selected();self.nr=next(c['plan'] for c in candidates if c['tool']=='native_records')
        self.sr=next(c['plan'] for c in candidates if c['tool']=='source_records')
        self.np={k:h.envelope[k] for k in ('model_id','revision','context_id','filters')}
        self.np.update(measure_ids=[self.measure],dimension_id=None,include_dependencies=False)
        self.sp={k:self.sr[k] for k in ('model_id','revision','context_id','object_id','filters')}
        self.sp.update(operation='sum',column_id=self.sr['column_ids'][1])
        self.nrows=[('A','10',1),('B','20',1)];self.srows=[('A','10',1),('B','18',1)]
        self.nvalue=Decimal('30');self.svalue='28';self.scount='2';self.snonblank='2'
        self.native=MagicMock(side_effect=lambda r:h.h.native_rows(self.nrows) if r.get('version')=='record-readback-v1' else response([{'[m0]':self.nvalue}]))
        self.source=MagicMock(side_effect=lambda r:h.h.sql_rows(self.srows) if r.get('version')=='record-readback-v1' else {'value':self.svalue,'row_count':self.scount,'nonblank_count':self.snonblank})
        self.runtime=Runtime(self.store,self.config,self.native,self.source)

    def request(self):
        return {'model_id':'model','call_budget':4,'actions':[
            {'tool':'native','input':self.np},{'tool':'source','input':self.sp},
            {'tool':'native_records','input':self.nr},{'tool':'source_records','input':self.sr},
            {'tool':'reconcile_records','input':{'native_step':0,'source_step':1,'native_records_step':2,'source_records_step':3,
                                               'measure_id':self.measure,'record_mapping_id':self.review['id']}}]}

    def run_case(self,key='case'):
        return self.runtime.execute(self.runtime.create(self.request(),key)['id'])

    def test_records_explain_delta_but_never_certify_cause(self):
        run=self.run_case();r=run['outcome']
        self.assertEqual(run['status'],'COMPLETED');self.assertEqual(r['status'],'CAPTURES_RECONCILE')
        self.assertEqual(r['record_explained_native_minus_source'],'2')
        self.assertFalse(r['root_cause_verified']);self.assertFalse(r['delivery_eligible']);self.assertEqual(len(r['proof_gaps']),3)
        self.assertEqual(self.native.call_count,2);self.assertEqual(self.source.call_count,2)
        self.runtime.execute(run['id']);self.assertEqual(self.native.call_count,2)
        self.assertEqual(reconcile.read(self.store,'model',r['id'])['hash'],r['hash'])

    def test_wrong_native_total_is_capture_inconsistency(self):
        self.nvalue=Decimal('31');r=self.run_case()['outcome']
        self.assertEqual(r['status'],'CAPTURE_INCONSISTENCY');self.assertFalse(r['observations']['native']['matches'])
        self.assertIsNone(r['record_explained_native_minus_source'])

    def test_wrong_source_total_or_counts_are_not_reconciled(self):
        self.svalue='27';self.scount='3';r=self.run_case()['outcome']
        self.assertEqual(r['status'],'CAPTURE_INCONSISTENCY')
        self.assertFalse(r['observations']['source']['matches']);self.assertFalse(r['observations']['source']['counts_match'])

    def test_multiplicity_contributes_to_sum_and_row_count(self):
        self.nrows=[('A','10',2)];self.srows=[('A','10',2)];self.nvalue=Decimal(20);self.svalue='20'
        r=self.run_case()['outcome'];self.assertEqual(r['status'],'CAPTURES_RECONCILE')
        self.assertEqual(r['observations']['native']['reconstructed']['row_count'],'2')

    def test_decimal_cancellation_is_exact(self):
        self.nrows=[('A','12345678901234567890123456789.12',1),('B','-12345678901234567890123456789.11',1)]
        self.srows=self.nrows;self.nvalue=Decimal('.01');self.svalue='.01'
        # SQL transport requires a leading integer digit.
        self.svalue='0.01';r=self.run_case()['outcome']
        self.assertEqual(r['status'],'CAPTURES_RECONCILE');self.assertEqual(r['record_explained_native_minus_source'],'0.00')

    def test_all_blank_sum_remains_blank(self):
        self.nrows=[('A',None,1)];self.srows=self.nrows;self.nvalue=None;self.svalue=None;self.scount='1';self.snonblank='0'
        r=self.run_case()['outcome'];self.assertEqual(r['status'],'CAPTURES_RECONCILE')
        self.assertEqual(r['observations']['native']['reconstructed']['value']['type'],'blank')
        self.assertIsNone(r['record_explained_native_minus_source'])

    def test_zero_sum_is_not_blank(self):
        self.nrows=[('A','0',1)];self.srows=self.nrows;self.nvalue=Decimal(0);self.svalue='0';self.scount='1';self.snonblank='1'
        self.assertEqual(self.run_case()['outcome']['status'],'CAPTURES_RECONCILE')

    def test_empty_count_preserves_native_blank_and_sql_zero(self):
        for asset in self.model['context']['reports'][0]['model_assets']:
            if asset['id']==self.measure:asset['metadata']['expression']="COUNTROWS('O''Brien')"
        self.sp.update(operation='count_rows',column_id=None)
        self.nrows=[];self.srows=[];self.nvalue=None;self.svalue='0';self.scount='0';self.snonblank='0'
        r=self.run_case()['outcome'];self.assertEqual(r['status'],'CAPTURES_RECONCILE')
        self.assertEqual(r['observations']['source']['reconstructed']['value']['value'],'0')
        self.assertIsNone(r['record_explained_native_minus_source'])

    def test_partial_capture_blocks_arithmetic(self):
        self.nrows=[(str(i),'1',1) for i in range(4)]
        r=self.run_case()['outcome'];self.assertEqual(r['status'],'NOT_ASSESSED');self.assertIn('NATIVE_RECORDS_INCOMPLETE',r['gaps'])

    def test_unsupported_expression_retains_precise_gap(self):
        for a in self.model['context']['reports'][0]['model_assets']:
            if a['id']==self.measure:a['metadata']['expression']='DIVIDE([Child],2)'
        r=self.run_case()['outcome'];self.assertEqual(r['status'],'NOT_ASSESSED');self.assertIn('AGGREGATE_RECONSTRUCTION_UNSUPPORTED',r['gaps'])

    def test_changed_filter_scope_cannot_reconcile(self):
        self.np=copy.deepcopy(self.np);self.np['filters'][0]['values']=['EUR']
        r=self.run_case()['outcome'];self.assertIn('AGGREGATE_RECORD_SCOPE_DIFFERS',r['gaps'])

    def test_different_source_operation_cannot_reconcile(self):
        self.sp.update(operation='count_rows',column_id=None);self.svalue='2'
        r=self.run_case()['outcome'];self.assertIn('AGGREGATE_OPERATIONS_DIFFER',r['gaps'])

    def test_legacy_unsealed_receipt_is_readable_but_ineligible(self):
        run=self.run_case();request=run['outcome']['request']
        with self.store.connect() as db:db.execute('DELETE FROM aggregate_receipt_seals WHERE id=?',(request['native_receipt_id'],))
        receipt=diagnostic_evidence.read(self.store,'model',request['native_receipt_id'])
        self.assertEqual(receipt['integrity']['state'],'LEGACY_UNSEALED')
        result=reconcile.assess(self.store,'model',request)
        self.assertIn('NATIVE_RECEIPT_UNSEALED',result['gaps']);self.assertEqual(result['status'],'NOT_ASSESSED')

    def test_native_and_source_result_tampering_is_rejected(self):
        run=self.run_case();request=run['outcome']['request']
        for table,key,reader in [('native_diagnostics','native_receipt_id',diagnostic_evidence.read),('source_diagnostics','source_receipt_id',source_diagnostics.evidence)]:
            with self.subTest(table=table):
                with self.store.connect() as db:db.execute('UPDATE '+table+" SET result='{}' WHERE id=?",(request[key],))
                with self.assertRaises(ValueError):reader(self.store,'model',request[key])

    def test_local_result_tampering_is_rejected(self):
        r=self.run_case()['outcome']
        with self.store.connect() as db:db.execute("UPDATE record_aggregate_assessments SET body='{}' WHERE id=?",(r['id'],))
        with self.assertRaises(ValueError):reconcile.read(self.store,'model',r['id'])

    def test_revoked_mapping_blocks_new_assessment_not_saved_history(self):
        result=self.run_case()['outcome']
        record_bindings.revoke(self.store,'model',self.review['id'],'Retired','reviewer')
        current=reconcile.assess(self.store,'model',result['request'])
        self.assertIn('RECORD_MAPPING_REVOKED',current['gaps']);self.assertEqual(current['status'],'NOT_ASSESSED')
        self.assertEqual(reconcile.read(self.store,'model',result['id'])['status'],'CAPTURES_RECONCILE')

    def test_disabled_model_blocks_new_assessment_not_history(self):
        result=self.run_case()['outcome'];self.model['enabled']=False
        current=reconcile.assess(self.store,'model',result['request'])
        self.assertIn('MODEL_DISABLED',current['gaps'])
        self.assertEqual(reconcile.read(self.store,'model',result['id'])['hash'],result['hash'])

    def test_cross_model_evidence_is_not_readable(self):
        result=self.run_case()['outcome']
        with self.assertRaises(KeyError):reconcile.assess(self.store,'other',result['request'])
        with self.assertRaises(KeyError):reconcile.read(self.store,'other',result['id'])

    def test_changed_context_cannot_reconcile_historical_captures(self):
        result=self.run_case()['outcome'];self.model['context']['new_metadata']='changed'
        current=reconcile.assess(self.store,'model',result['request'])
        self.assertIn('NATIVE_CONTEXT_DIFFERS',current['gaps']);self.assertIn('SOURCE_RECORDS_CONTEXT_DIFFERS',current['gaps'])

    def test_partial_blank_sum_checks_nonblank_count(self):
        self.nrows=[('A',None,1),('B','20',1)];self.srows=self.nrows
        self.nvalue=Decimal(20);self.svalue='20';self.snonblank='1'
        result=self.run_case()['outcome'];self.assertEqual(result['status'],'CAPTURES_RECONCILE')
        self.assertEqual(result['observations']['source']['reconstructed']['nonblank_count'],'1')

    def test_failed_native_read_seals_terminal_failure(self):
        self.native.side_effect=TimeoutError()
        result=self.run_case();self.assertEqual(result['status'],'HELD')
        receipt=diagnostic_evidence.read(self.store,'model',result['steps'][0]['receipt_id'])
        self.assertEqual(receipt['status'],'INTERRUPTED');self.assertEqual(receipt['integrity']['state'],'SEALED')

    def test_recovery_rejects_tampered_native_result_before_adoption(self):
        original=self.runtime.commit;self.runtime.commit=MagicMock(side_effect=RuntimeError('crash'))
        run=self.run_case();self.runtime.commit=original
        with self.store.connect() as db:db.execute("UPDATE native_diagnostics SET result='{}' WHERE id=?",(run['steps'][0]['receipt_id'],))
        with self.assertRaises(ValueError):self.runtime.reconcile(run['id'])
        self.native.assert_called_once();self.source.assert_not_called()

    def test_wrong_reference_rejected_before_any_read(self):
        request=self.request();request['actions'][-1]['input']['native_records_step']=0
        with self.assertRaises(ValueError):self.runtime.create(request,'wrong')
        self.native.assert_not_called();self.source.assert_not_called()

    def test_unpinned_review_rejected_before_any_read(self):
        request=copy.deepcopy(self.request());request['actions'][2]['input'].pop('record_mapping_id')
        with self.assertRaises(ValueError):self.runtime.create(request,'wrong')
        self.native.assert_not_called()

    def test_crash_after_local_assessment_recovers_without_queries(self):
        original=self.runtime.commit
        def commit(identity,ordinal,token,result):
            if ordinal==4:raise RuntimeError('simulated crash')
            return original(identity,ordinal,token,result)
        self.runtime.commit=commit;run=self.run_case();self.assertEqual(run['status'],'HELD')
        self.runtime.commit=original;r=self.runtime.reconcile(run['id'])
        self.assertEqual(r['status'],'COMPLETED');self.assertEqual(r['outcome']['status'],'CAPTURES_RECONCILE')
        self.assertEqual(self.native.call_count,2);self.assertEqual(self.source.call_count,2)

    def test_adaptive_arithmetic_informs_next_decision_without_extra_query(self):
        envelope=copy.deepcopy(self.h.envelope);envelope['source_tests']=[{'measure_id':self.measure,'plan':self.sp}]
        envelope['limits']['cloud_calls']=5
        planner=MagicMock()
        def choose(payload):
            count=len(payload['observations'])
            if count==4:
                self.assertEqual(payload['aggregate_reconciliations'][0]['record_explained_native_minus_source'],'2')
                return decision(),{}
            tool=['native','source','native_records','source_records'][count]
            return decision(next(c['id'] for c in payload['candidates'] if c['tool']==tool and c['dimension_id'] is None)),{}
        planner.side_effect=choose;agent=AdaptiveRuntime(self.runtime,planner,clock=lambda:1000)
        r=agent.run(agent.create(envelope,'adaptive')['id'])
        self.assertEqual(r['status'],'COMPLETED');self.assertEqual(r['cloud_calls'],4)
        self.assertEqual(r['outcome']['aggregate_reconciliations'][0]['status'],'CAPTURES_RECONCILE')

    def test_api_reader_cannot_create_assessment(self):
        body=self.run_case()['outcome']['request'];app=create_app(self.store,'a'*32,'r'*32)
        for token,status in [('r'*32,'403 Forbidden'),('a'*32,'200 OK')]:
            statuses=[];raw=json.dumps(body).encode()
            output=b''.join(app({'PATH_INFO':'/api/v2/admin/models/model/record-aggregate-assessments','REQUEST_METHOD':'POST',
                                'HTTP_AUTHORIZATION':'Bearer '+token,'CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(raw)),
                                'wsgi.input':BytesIO(raw)},lambda s,h:statuses.append(s)))
            self.assertEqual(statuses,[status])
            if status=='200 OK':self.assertEqual(json.loads(output)['status'],'CAPTURES_RECONCILE')


if __name__=='__main__':unittest.main()

from contextlib import closing
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from uuid import uuid4
import duckdb
from defect_lab import initialize,validate
from serve_lab_review import components


class ReportExecutionTests(unittest.TestCase):
    def test_approved_ticket_executes_and_persists_report_scope_finding(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);lab=root/'lab.duckdb';initialize(lab)
            app,worker,store=components(root/'review',lab,'x'*32,report_scope=True)
            def call(path,body=None,key=''):
                raw=json.dumps(body).encode();status=[]
                data=b''.join(app({'REQUEST_METHOD':'GET' if body is None else 'POST','PATH_INFO':path,'QUERY_STRING':'',
                    'HTTP_AUTHORIZATION':'Bearer '+'x'*32,'HTTP_IDEMPOTENCY_KEY':key,'CONTENT_TYPE':'application/json',
                    'CONTENT_LENGTH':str(len(raw)),'wsgi.input':BytesIO(raw)},lambda s,h:status.append(s)))
                self.assertTrue(status[0].startswith(('200','201')),data);return json.loads(data)
            self.assertEqual(call('/api/context')['workspace_mode'],'local_report_scope_lab')
            parent=call('/api/tickets',{'title':'Investigate cash discrepancy','report':'Lab All Orders vs Excluded Partial Returns','description':'Compare local layers'},str(uuid4()))['ticket_id']
            self.assertEqual(worker.process(store,worker.config,worker.estate_loader(),approved_only=True)['status'],'IDLE')
            self.assertEqual(store.get(parent)['status'],'QUEUED')
            draft=call('/api/tickets/'+parent+'/plan',{'confirm':True},str(uuid4()))['plan_id']
            detail=call('/api/plans/'+draft)
            child=call('/api/plans/'+draft+'/approve',{'confirm':True,'plan_hash':detail['plan_hash']})['ticket_id']
            worker.start();worker.thread.join(20);self.assertFalse(worker.thread.is_alive())
            ticket=call('/api/tickets/'+child)['ticket'];self.assertEqual(ticket['status'],'COMPLETED')
            evidence=call('/api/investigations/'+ticket['investigation_run_id'])
            result=evidence['investigation']['result']
            self.assertEqual(result['comparison_status'],'MISMATCH')
            self.assertEqual(result['impact_by_currency']['USD']['downstream_minus_upstream'],'-99.0000')
            self.assertEqual(result['classification'],'UNRESOLVED')
            self.assertFalse(result['root_cause_verified'])
            self.assertEqual(evidence['investigation']['request']['report_scope_evidence']['requested_scope'],'all_orders')
            self.assertEqual(store.get(parent)['status'],'QUEUED')
            self.assertEqual(validate(lab)['status'],'READY')

    def test_mode_cannot_change_for_existing_review_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);lab=root/'lab.duckdb';initialize(lab)
            components(root/'review',lab,'x'*32)
            with self.assertRaises(ValueError):components(root/'review',lab,'x'*32,report_scope=True)

    def test_source_cannot_change_for_existing_review_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);lab=root/'lab.duckdb';initialize(lab)
            components(root/'review',lab,'x'*32,report_scope=True)
            with self.assertRaises(ValueError):components(root/'review',root/'other.duckdb','x'*32,report_scope=True)

    def test_currency_outside_reviewed_scope_is_rejected_before_persistence(self):
        from report_scope_lab import investigate
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);lab=root/'lab.duckdb';initialize(lab)
            with closing(duckdb.connect(str(lab))) as db:
                db.execute("UPDATE g_order_line_summary SET currency='EUR' WHERE order_id='ORD-000001'")
            with self.assertRaises(ValueError):
                investigate(lab,root/'evidence.sqlite','all_orders','exclude_partial_returns',expected_currency='USD')
            self.assertFalse((root/'evidence.sqlite').exists())
            with self.assertRaises(ValueError):components(root/'review',lab,'x'*32,multilayer=True,report_scope=True)


if __name__=='__main__':unittest.main()

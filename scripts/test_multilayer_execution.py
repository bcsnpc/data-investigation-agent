from contextlib import closing
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from uuid import uuid4
import duckdb
from multilayer_lab import initialize_multilayer,reset_multilayer
from defect_lab import query
from serve_lab_review import components


class MultiExecutionTests(unittest.TestCase):
    def test_approved_ticket_executes_and_persists_current_three_layer_finding(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);lab=root/'lab.duckdb';initialize_multilayer(lab)
            with closing(duckdb.connect(str(lab))) as db:
                db.execute("UPDATE s_fact_order SET captured_amount=captured_amount+10 WHERE order_id='ORD-000002'")
                db.execute("UPDATE s_fact_order_line SET line_total=line_total+10,unit_price=unit_price+10 WHERE order_id='ORD-000002'")
                db.execute('DELETE FROM g_order_line_summary');db.execute('INSERT INTO g_order_line_summary '+query())
            app,worker,store=components(root/'review',lab,'x'*32,multilayer=True)
            def call(path,body=None,key=''):
                raw=json.dumps(body).encode();status=[]
                data=b''.join(app({'REQUEST_METHOD':'GET' if body is None else 'POST','PATH_INFO':path,'QUERY_STRING':'',
                    'HTTP_AUTHORIZATION':'Bearer '+'x'*32,'HTTP_IDEMPOTENCY_KEY':key,'CONTENT_TYPE':'application/json',
                    'CONTENT_LENGTH':str(len(raw)),'wsgi.input':BytesIO(raw)},lambda s,h:status.append(s)))
                self.assertTrue(status[0].startswith(('200','201')),data);return json.loads(data)
            self.assertEqual(call('/api/context')['workspace_mode'],'local_multilayer_lab')
            parent=call('/api/tickets',{'title':'Investigate cash discrepancy','report':'Lab Three-layer Net Cash','description':'Compare local layers'},str(uuid4()))['ticket_id']
            draft=call('/api/tickets/'+parent+'/plan',{'confirm':True},str(uuid4()))['plan_id']
            detail=call('/api/plans/'+draft)
            child=call('/api/plans/'+draft+'/approve',{'confirm':True,'plan_hash':detail['plan_hash']})['ticket_id']
            worker.start();worker.thread.join(20);self.assertFalse(worker.thread.is_alive())
            ticket=call('/api/tickets/'+child)['ticket'];self.assertEqual(ticket['status'],'COMPLETED')
            evidence=call('/api/investigations/'+ticket['investigation_run_id'])
            result=evidence['investigation']['result']
            self.assertEqual(result['first_observed_local_boundary'],{'upstream':'bronze','downstream':'silver'})
            self.assertEqual(result['boundaries'][1]['comparison_status'],'MATCH')
            self.assertEqual(result['classification'],'UNRESOLVED');self.assertEqual(len(evidence['summary']['observations']),9)
            self.assertEqual(store.get(parent)['status'],'QUEUED')
            self.assertEqual(reset_multilayer(lab)['status'],'READY')

    def test_mode_cannot_change_for_existing_review_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);lab=root/'lab.duckdb';initialize_multilayer(lab)
            components(root/'review',lab,'x'*32)
            with self.assertRaises(ValueError):components(root/'review',lab,'x'*32,multilayer=True)

    def test_source_cannot_change_for_existing_review_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);lab=root/'lab.duckdb';initialize_multilayer(lab)
            components(root/'review',lab,'x'*32,multilayer=True)
            with self.assertRaises(ValueError):components(root/'review',root/'other.duckdb','x'*32,multilayer=True)


if __name__=='__main__':unittest.main()

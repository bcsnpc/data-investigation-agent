from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from uuid import uuid4
from defect_lab import initialize,mutate
from serve_lab_review import components


class LabReviewTests(unittest.TestCase):
    def test_reviewed_cases_flow_to_saved_evidence(self):
        for injected,expected in [(None,'EXPECTED_BEHAVIOR'),('inject-filter','TECHNICAL_DEFECT'),('inject-stale','REFRESH_FRESHNESS'),('inject-double-refund','TECHNICAL_DEFECT')]:
            with self.subTest(injected=injected),tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/'lab.duckdb';initialize(path)
                if injected:mutate(path,injected)
                app,worker,store=components(Path(folder)/'review',path,'x'*32)
                def call(path,body=None,key=None):
                    raw=json.dumps(body).encode() if body is not None else b'';status=[]
                    result=b''.join(app({'REQUEST_METHOD':'POST' if body is not None else 'GET','PATH_INFO':path,'QUERY_STRING':'',
                        'HTTP_AUTHORIZATION':'Bearer '+'x'*32,'HTTP_IDEMPOTENCY_KEY':key or '',
                        'CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(raw)),'wsgi.input':BytesIO(raw)},lambda s,h:status.append(s)))
                    self.assertTrue(status[0].startswith(('200','201')),result)
                    return json.loads(result)
                self.assertEqual(call('/api/context')['workspace_mode'],'local_lab')
                parent=call('/api/tickets',{'title':'Check lab','report':'Lab Net Cash','description':'Review local USD cash'},str(uuid4()))['ticket_id']
                draft=call('/api/tickets/'+parent+'/plan',{'confirm':True},str(uuid4()))['plan_id']
                detail=call('/api/plans/'+draft)
                child=call('/api/plans/'+draft+'/approve',{'confirm':True,'plan_hash':detail['plan_hash']})['ticket_id']
                worker.start();worker.thread.join(5);self.assertFalse(worker.thread.is_alive())
                ticket=call('/api/tickets/'+child)['ticket'];self.assertEqual(ticket['status'],'COMPLETED')
                finding=call('/api/investigations/'+ticket['investigation_run_id'])['investigation']['result']
                self.assertEqual(finding['classification'],expected)
                self.assertFalse(finding['automatic_defect_routing'])
                self.assertEqual(store.get(parent)['status'],'QUEUED')


if __name__=='__main__':unittest.main()

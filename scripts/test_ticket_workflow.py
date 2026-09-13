from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from uuid import uuid4
from investigation_evidence_api import create_app
from lineage_graph import Graph
from ticket_worker import process_one
from ticket_workflow import TicketStore,Conflict


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.store=TicketStore(Path(self.folder.name)/'workflow.sqlite')
        self.lineage=str(uuid4())
        self.body={'title':'Check cash','report':'Sales','description':'Verify the baseline','metric':'Net Cash','currency':'USD'}
    def tearDown(self):self.folder.cleanup()

    def test_idempotency_survives_reopen_and_conflict(self):
        key=str(uuid4());identity,created=self.store.submit(self.body,key,self.lineage)
        self.assertTrue(created)
        reopened=TicketStore(self.store.database)
        self.assertEqual(reopened.submit(self.body,key,self.lineage),(identity,False))
        with self.assertRaises(Conflict):reopened.submit(dict(self.body,title='Different'),key,self.lineage)
        self.assertEqual(len(reopened.get(identity)['timeline']),1)

    def test_concurrent_claim_and_stale_fencing(self):
        identity,_=self.store.submit(self.body,str(uuid4()),self.lineage)
        with ThreadPoolExecutor(2) as pool:claims=list(pool.map(lambda _:self.store.claim(),range(2)))
        claimed=[c for c in claims if c];self.assertEqual(len(claimed),1)
        replacement=self.store.claim(now=time.time()+1801)
        with self.assertRaises(Conflict):self.store.finish(claimed[0],'COMPLETED',{})
        self.store.finish(replacement,'COMPLETED',{'classification':'UNRESOLVED'},str(uuid4()))
        self.assertEqual(self.store.get(identity)['status'],'COMPLETED')

    def test_missing_scope_needs_input_without_query(self):
        body=dict(self.body);body.pop('currency')
        identity,_=self.store.submit(body,str(uuid4()),self.lineage)
        with patch('ticket_worker.acquire') as execute:
            result=process_one(self.store,{}, {'investigation':{'lineage_run':self.lineage}},execute)
            execute.assert_not_called()
        self.assertEqual(result['status'],'NEEDS_INPUT')
        self.assertIsNone(self.store.get(identity)['investigation_run_id'])

    def graph(self):
        graph=Graph([dict(id=x,parent=None,name=n,kind=k,hash='h',meta={}) for x,n,k in
                     [('report','Sales','Report'),('metric','Net Cash','Measure')]])
        graph.edge('metric','report','binding','metric',{})
        return graph

    def test_execution_links_evidence_without_resolving_ticket(self):
        identity,_=self.store.submit(self.body,str(uuid4()),self.lineage);run=str(uuid4())
        execute=lambda *args:{'id':run,'classification':'UNRESOLVED','metrics':{'cash':{'boundaries':[{'status':'NOT_COMPARABLE'}]}}}
        with patch('ticket_worker.load_graph',return_value=self.graph()):
            process_one(self.store,{'storage':{'database':'unused'}},{'investigation':{'lineage_run':self.lineage}},execute)
        ticket=self.store.get(identity)
        self.assertEqual(ticket['investigation_run_id'],run)
        self.assertEqual([e['status'] for e in ticket['timeline']],['QUEUED','RUNNING','COMPLETED'])
        self.assertEqual(ticket['outcome']['classification'],'UNRESOLVED')
        self.assertEqual(ticket['outcome']['boundary_statuses'],['NOT_COMPARABLE'])

    def test_failure_is_sanitized(self):
        identity,_=self.store.submit(self.body,str(uuid4()),self.lineage)
        def execute(*args):raise RuntimeError('private credential or diagnostic')
        with patch('ticket_worker.load_graph',return_value=self.graph()):
            process_one(self.store,{'storage':{'database':'unused'}},{'investigation':{'lineage_run':self.lineage}},execute)
        self.assertEqual(self.store.get(identity)['status'],'FAILED')
        self.assertNotIn('private',json.dumps(self.store.get(identity)))

    def test_authenticated_intake_status_and_duplicate_submission(self):
        token='test-only-'+'x'*40
        app=create_app(Path(self.folder.name)/'unused.sqlite',token,self.store,self.lineage)
        key=str(uuid4())
        def request(body,authorization='Bearer '+token):
            encoded=json.dumps(body).encode();captured=[]
            result=app({'PATH_INFO':'/api/tickets','REQUEST_METHOD':'POST','HTTP_AUTHORIZATION':authorization,
                        'CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(encoded)),
                        'HTTP_IDEMPOTENCY_KEY':key,'wsgi.input':BytesIO(encoded)},lambda status,headers:captured.append(status))
            return captured[0],json.loads(b''.join(result))
        self.assertTrue(request(self.body,'wrong')[0].startswith('401'))
        self.assertTrue(request(dict(self.body,description=''))[0].startswith('400'))
        status,body=request(self.body);self.assertTrue(status.startswith('201'))
        self.assertTrue(request(self.body)[0].startswith('200'))
        self.assertTrue(request(dict(self.body,title='Changed'))[0].startswith('409'))
        self.assertEqual(self.store.get(body['ticket_id'])['status'],'QUEUED')


if __name__=='__main__':unittest.main()

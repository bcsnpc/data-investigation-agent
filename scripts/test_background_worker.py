from contextlib import closing
from io import BytesIO
import json
from pathlib import Path
import tempfile
from threading import Event
import time
import unittest
from unittest.mock import patch
from uuid import uuid4
from background_worker import BackgroundWorker
from investigation_evidence_api import create_app
from lineage_graph import Graph
from review_ticket_plan import approve
from ticket_planner import plan_ticket
from ticket_worker import process_one
from ticket_workflow import TicketStore


class BackgroundTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=TicketStore(Path(self.temp.name)/'workflow.sqlite');self.lineage=str(uuid4())
        self.estate={'investigation':{'lineage_run':self.lineage}}
        self.config={'storage':{'database':'unused'}}
        self.graph=Graph([{'id':'r','kind':'Report','name':'Sales'},{'id':'m','kind':'Measure','name':'Net Cash'}])
        self.graph.edge('m','r','binding','r','test')

    def approved(self):
        parent,_=self.store.submit({'title':'Check','report':'Sales','description':'Check USD cash'},str(uuid4()),self.lineage)
        plan=plan_ticket(self.store,parent,self.graph,lambda _:({'report_id':'r','metric':'Net Cash','currency':'USD','order_id':None,'questions':[]},{}))
        with patch('review_ticket_plan.load_graph',return_value=self.graph):
            child=approve(self.store,plan['id'],self.config,self.estate,'test')['ticket_id']
        return parent,child

    def test_approved_handoff_runs_once_and_preserves_parent_and_job_limit(self):
        parent,child=self.approved();_,second=self.approved();calls=[]
        def execute(*args):
            calls.append(args)
            return {'id':str(uuid4()),'classification':'UNRESOLVED','metrics':{}}
        def process(*args,**kwargs):return process_one(*args,execute=execute,**kwargs)
        worker=BackgroundWorker(self.store,self.config,lambda:self.estate,process=process)
        with patch('ticket_worker.load_graph',return_value=self.graph):
            worker.start();worker.thread.join(3)
        self.assertFalse(worker.thread.is_alive());self.assertEqual(len(calls),1)
        self.assertEqual(worker.status()['status'],'JOB_LIMIT')
        self.assertEqual(self.store.get(child)['status'],'COMPLETED')
        self.assertEqual(self.store.get(parent)['status'],'QUEUED')
        self.assertEqual(self.store.get(second)['status'],'QUEUED')

    def test_idle_stop_does_not_execute_or_claim_unapproved(self):
        self.store.submit({'title':'Check','report':'Sales','description':'Check'},str(uuid4()),self.lineage)
        worker=BackgroundWorker(self.store,self.config,lambda:self.estate,poll_seconds=.01)
        worker.start();worker.stop()
        self.assertEqual(worker.status()['processed'],0)
        self.assertEqual(worker.status()['status'],'STOPPED')
        self.assertIsNone(self.store.claim(approved_only=True))

    def test_expired_approved_run_is_not_automatically_replayed(self):
        self.approved();job=self.store.claim(approved_only=True)
        self.assertIsNotNone(job)
        self.assertIsNone(self.store.claim(now=time.time()+2000,approved_only=True))

    def test_stop_finishes_active_work_without_second_claim(self):
        entered=Event();release=Event();calls=[]
        def process(*args,**kwargs):
            calls.append(kwargs);entered.set();release.wait(2);return {'status':'COMPLETED'}
        worker=BackgroundWorker(self.store,self.config,lambda:self.estate,max_jobs=2,process=process)
        worker.start();self.assertTrue(entered.wait(2));worker.stop_event.set();release.set();worker.stop()
        self.assertEqual(len(calls),1);self.assertTrue(calls[0]['approved_only'])
        self.assertEqual(worker.status()['status'],'STOPPED')

    def test_time_limit_and_failure_are_finite_and_sanitized(self):
        worker=BackgroundWorker(self.store,self.config,lambda:self.estate,max_seconds=1,poll_seconds=.01,process=lambda *a,**k:{'status':'IDLE'})
        worker.start();worker.thread.join(2);self.assertEqual(worker.status()['status'],'TIME_LIMIT')
        def fail():raise RuntimeError('secret connection detail')
        worker=BackgroundWorker(self.store,self.config,fail)
        worker.start();worker.thread.join(2)
        self.assertEqual(worker.status()['status'],'FAILED');self.assertNotIn('secret',json.dumps(worker.status()))

    def test_worker_status_requires_authentication_and_is_read_only(self):
        app=create_app(self.store.database,'x'*32,worker_status=lambda:{'status':'JOB_LIMIT','processed':1})
        def call(method,auth):
            response=[];body=b''.join(app({'REQUEST_METHOD':method,'PATH_INFO':'/api/worker','QUERY_STRING':'','HTTP_AUTHORIZATION':auth,'wsgi.input':BytesIO()},lambda status,headers:response.append(status)))
            return response[0],json.loads(body)
        self.assertTrue(call('GET','')[0].startswith('401'))
        self.assertTrue(call('POST','Bearer '+'x'*32)[0].startswith('405'))
        self.assertEqual(call('GET','Bearer '+'x'*32)[1]['processed'],1)


if __name__=='__main__':unittest.main()

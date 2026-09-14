from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
import tempfile
from threading import Event
from types import SimpleNamespace
import unittest
from uuid import uuid4
from explanation_request import request_explanation
from investigation_explanation import explain
from ticket_workflow import TicketStore


class RequestTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=TicketStore(Path(self.temp.name)/'workflow.sqlite');self.run=str(uuid4())
        self.item={'id':self.run,'classification':'UNRESOLVED','request':{},'result':{}}
        self.evidence=SimpleNamespace(get=lambda identity:self.item if identity==self.run else None)

    def generate(self,identity):
        return explain(self.store,self.item,lambda facts:({'finding_ids':['classification'],'next_step_ids':['review-scope']},{}))['id']

    def request(self,generate):return request_explanation(self.store,self.evidence,self.run,generate)

    def test_concurrent_requests_only_generate_once(self):
        entered=Event();release=Event();calls=[]
        def generate(identity):
            calls.append(identity);entered.set();release.wait(2);return self.generate(identity)
        with ThreadPoolExecutor(2) as pool:
            first=pool.submit(self.request,generate);self.assertTrue(entered.wait(2))
            replay=self.request(generate);self.assertEqual(replay['status'],'RUNNING')
            release.set();self.assertEqual(first.result()['status'],'COMPLETED')
        self.assertEqual(len(calls),1);self.assertTrue(self.request(generate)['replayed'])

    def test_existing_explanation_reused_without_paid_call(self):
        identity=self.generate(self.run)
        result=self.request(lambda _:self.fail('Unexpected model call'))
        self.assertEqual(result['explanation_id'],identity)

    def test_failure_is_durable_and_not_retried(self):
        def fail(_):raise RuntimeError('private provider detail')
        self.assertEqual(self.request(fail)['status'],'FAILED')
        result=self.request(lambda _:self.fail('Unexpected retry'))
        self.assertEqual(result['status'],'FAILED');self.assertTrue(result['replayed'])

    def test_returned_id_without_persisted_evidence_is_rejected(self):
        self.assertEqual(self.request(lambda _:str(uuid4()))['status'],'FAILED')

    def test_interrupted_running_request_is_not_repeated(self):
        def crash(_):raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):self.request(crash)
        self.assertEqual(self.request(lambda _:self.fail('Unexpected retry'))['status'],'RUNNING')


if __name__=='__main__':unittest.main()

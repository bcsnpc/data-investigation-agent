from io import BytesIO
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import unittest
from types import SimpleNamespace
import test_routing_drafts as fixtures
from routing_review import RoutingReview
from routing_drafts import save
from ticket_workflow import TicketStore,Conflict
from investigation_evidence_api import create_app


class ReviewTests(unittest.TestCase):
    def setUp(self):
        fixtures.RoutingTests.setUp(self)
        self.store=TicketStore(Path(self.temp.name)/'review.sqlite')
        self.review=RoutingReview(self.store,SimpleNamespace(get=lambda identity:self.item),lambda:self.policy)
        self.record=save(self.store,self.item,self.policy)

    def test_concurrent_approval_is_idempotent_and_disabled_for_delivery(self):
        detail=self.review.detail(self.record['id'])
        with ThreadPoolExecutor(2) as pool:results=list(pool.map(lambda _:self.review.approve(self.record['id'],detail['draft_hash']),range(2)))
        self.assertEqual(results[0]['approval'],results[1]['approval'])
        self.assertFalse(results[0]['delivery_enabled'])

    def test_changed_policy_evidence_or_displayed_hash_rejected(self):
        detail=self.review.detail(self.record['id'])
        with self.assertRaises(Conflict):self.review.approve(self.record['id'],'bad-hash')
        self.policy['owners'][0]['team']='Changed team'
        with self.assertRaises(Conflict):self.review.approve(self.record['id'],detail['draft_hash'])
        self.policy['owners'][0]['team']='Fixture Data Team';self.item['result']['root_cause']='Changed cause'
        with self.assertRaises(Conflict):self.review.approve(self.record['id'],detail['draft_hash'])

    def test_missing_owner_not_approvable(self):
        self.policy['owners']=[];record=save(self.store,self.item,self.policy)
        with self.assertRaises(Conflict):self.review.approve(record['id'],self.review.detail(record['id'])['draft_hash'])

    def test_api_auth_confirmation_and_body_limits(self):
        app=create_app(Path(self.temp.name)/'evidence.sqlite','x'*32,routing=self.review)
        def call(body,auth=True):
            raw=json.dumps(body).encode();status=[]
            response=b''.join(app({'PATH_INFO':'/api/routing/'+self.record['id']+'/approve','REQUEST_METHOD':'POST','QUERY_STRING':'',
                'HTTP_AUTHORIZATION':'Bearer '+'x'*32 if auth else '', 'CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(raw)),
                'wsgi.input':BytesIO(raw)},lambda s,h:status.append(s)))
            return status[0],json.loads(response)
        body={'confirm':True,'draft_hash':self.review.detail(self.record['id'])['draft_hash']}
        self.assertTrue(call(body,False)[0].startswith('401'))
        self.assertTrue(call({'confirm':False})[0].startswith('400'))
        self.assertTrue(call({'confirm':True,'draft_hash':'x'*2000})[0].startswith('413'))
        self.assertTrue(call(body)[0].startswith('200'))


if __name__=='__main__':unittest.main()

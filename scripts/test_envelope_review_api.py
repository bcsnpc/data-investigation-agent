from io import BytesIO
import json
from pathlib import Path
import unittest
import test_envelope_workflow as fixtures
from envelope_review_api import EnvelopeReviewApi
from investigation_evidence_api import create_app
from envelope_workflow import EnvelopeWorkflow


class EnvelopeApiTests(unittest.TestCase):
    def setUp(self):
        fixtures.EnvelopeTests.setUp(self)
        self.app = create_app(Path(self.temp.name)/'evidence.sqlite', 'x'*32,
                              envelopes=EnvelopeReviewApi(self.flow))

    def call(self, path, body=None, *, authenticated=True, method=None):
        raw = json.dumps(body).encode(); status=[]
        result=b''.join(self.app({'PATH_INFO':path, 'REQUEST_METHOD':method or ('GET' if body is None else 'POST'),
            'QUERY_STRING':'','HTTP_AUTHORIZATION':'Bearer '+'x'*32 if authenticated else '',
            'CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(raw)), 'wsgi.input':BytesIO(raw)},lambda s,h:status.append(s)))
        return status[0],json.loads(result)

    def test_prepare_approve_and_status_never_send(self):
        status,detail=self.call('/api/routing/'+self.identity+'/envelope', {'confirm':True,'draft_hash':self.hash,'sender':self.sender})
        self.assertTrue(status.startswith('200'))
        self.assertEqual(detail['preview']['envelope']['sender'],self.sender)
        status,detail=self.call('/api/envelopes/'+self.key+'/approve',{'confirm':True})
        self.assertTrue(status.startswith('200'));self.assertIsNotNone(detail['approval'])
        self.assertFalse(detail['delivery_enabled']);self.assertEqual(self.sent,[])
        self.assertEqual(self.call('/api/envelopes/'+self.key)[1],detail)

    def test_auth_body_and_no_send_route(self):
        path='/api/envelopes/'+self.key+'/approve'
        self.assertTrue(self.call(path,{'confirm':True},authenticated=False)[0].startswith('401'))
        self.assertTrue(self.call(path,{'confirm':False})[0].startswith('400'))
        self.assertTrue(self.call(path,{'confirm':True,'extra':'x'*2000})[0].startswith('413'))
        self.assertTrue(self.call('/api/envelopes/'+self.key+'/send',{'confirm':True})[0].startswith('405'))
        self.assertEqual(self.sent,[])

    def test_changed_policy_is_conflict(self):
        self.policy['owners'][0]['team']='Changed'
        self.assertTrue(self.call('/api/envelopes/'+self.key+'/approve',{'confirm':True})[0].startswith('409'))

    def test_live_coordinator_cannot_back_review_api(self):
        with self.assertRaises(ValueError): EnvelopeReviewApi(EnvelopeWorkflow(self.email,delivery_enabled=True))


if __name__=='__main__':unittest.main()

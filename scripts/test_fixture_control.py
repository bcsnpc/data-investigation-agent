import tempfile,unittest
from unittest.mock import Mock
from fixture.control import FixtureControl,ControlError

W='d028fa2b-0d1b-4dd8-b423-37dd161cd5d0'
class Governor:
    def __init__(self):self.count=0;self.hold=False
    def snapshot(self):return {'reserved_today':{'cloud_calls':self.count}}
    def metered_read(self,session,key,send):
        if self.hold:raise RuntimeError('approved cap reached')
        self.count+=1;return send()

class FixtureControlTest(unittest.TestCase):
    def make(self,transport):
        path=self.enterContext(tempfile.TemporaryDirectory())
        self.g=Governor();c=FixtureControl(W,self.g,path,'test',transport,sleep=lambda _:None)
        return self.enterContext(c)
    def test_existing_workspace_cannot_be_escaped(self):
        send=Mock();c=self.make(send)
        for endpoint,method in [('workspaces/00000000-0000-0000-0000-000000000000/items','GET'),('connections/id','POST'),('operations/id','POST'),('https://evil.test','GET')]:
            with self.assertRaises(ValueError):c.call(endpoint,method,key='mutation')
        send.assert_not_called();self.assertEqual(self.g.count,0)
    def test_cap_refusal_precedes_physical_dispatch(self):
        send=Mock();c=self.make(send);self.g.hold=True
        with self.assertRaisesRegex(RuntimeError,'approved cap'):c.call('workspaces/'+W+'/items')
        send.assert_not_called();self.assertEqual(c.record['requests'][0]['error'],'approved cap reached')
    def test_uncertain_mutation_cannot_be_retried(self):
        send=Mock(side_effect=TimeoutError('connection lost'));c=self.make(send)
        with self.assertRaises(TimeoutError):c.call('workspaces/'+W+'/lakehouses','POST',{},key='create-once')
        with self.assertRaisesRegex(RuntimeError,'Uncertain publication'):c.call('workspaces/'+W+'/lakehouses','POST',{},key='create-once')
        self.assertEqual(send.call_count,1);self.assertEqual(self.g.count,1)
    def test_received_mutation_reuse_records_response_without_charge(self):
        send=Mock(return_value={'status_code':201,'text':{'id':W}});c=self.make(send)
        first=c.call('workspaces/'+W+'/lakehouses','POST',{},key='once')
        self.assertEqual(first,c.call('workspaces/'+W+'/lakehouses','POST',{},key='once'))
        self.assertEqual(send.call_count,1);self.assertEqual(c.finish('DONE')['physical_requests'],1)
    def test_failure_retains_exact_service_response(self):
        body={'errorCode':'ScopeRefused','message':'Precisely refused'};c=self.make(Mock(return_value={'status_code':403,'text':body}))
        with self.assertRaisesRegex(ControlError,'Precisely refused'):c.call('workspaces/'+W+'/items')
        self.assertEqual(c.record['requests'][0]['response']['text'],body)
    def test_other_sessions_are_not_counted_as_this_control(self):
        c=self.make(Mock(return_value={'status_code':200,'text':{}}))
        c.call('workspaces/'+W+'/items')
        self.g.count+=7
        self.assertEqual(c.finish('DONE')['physical_requests'],1)
    def test_completed_definition_update_does_not_request_nonexistent_result(self):
        send=Mock(return_value={'status_code':200,'text':{'status':'Succeeded'}})
        c=self.make(send)
        response={'status_code':202,'headers':{'x-ms-operation-id':W}}
        self.assertEqual(c.resolve(response,expect_result=False),{'status':'Succeeded'})
        self.assertEqual(send.call_count,1)
        self.assertFalse(send.call_args.kwargs['endpoint'].endswith('/result'))

if __name__=='__main__':unittest.main()

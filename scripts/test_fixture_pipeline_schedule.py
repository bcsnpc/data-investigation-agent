import copy,unittest
from fixture.pipeline_schedule import PipelineScheduleScenario,same_configuration

W='149f8d99-1c66-4a0a-9624-759be002bb60';P='b4871498-bd35-45be-916c-9a642568012c';S='659ea59a-256f-4673-a661-0d6f3359d9be'

class ScheduleControlTests(unittest.TestCase):
    def control(self):
        class Control:
            workspace=W
            def __init__(self):self.native=[];self.calls=[]
            def call(self,endpoint,method='GET',body=None,**kwargs):
                self.calls.append((endpoint,method,body))
                if method=='POST':
                    native={'id':S,**copy.deepcopy(body)};self.native=[native];return {'status_code':201,'text':native}
                if method=='DELETE':self.native=[];return {'status_code':204,'text':{}}
                return {'status_code':200,'text':{'value':copy.deepcopy(self.native)}if endpoint.endswith('/schedules')else copy.deepcopy(self.native[0])}
        return Control()
    def test_future_only_one_execution_window_and_no_existing_schedule_replacement(self):
        for start in ('2026-10-24T00:00:00Z','2026-10-24T00:59:59Z','2026-10-27T00:00:00Z','2026-10-25T00:00:00'):
            with self.subTest(start=start),self.assertRaises(ValueError):PipelineScheduleScenario.plan(start=start,now='2026-10-24T00:00:00Z')
        body=PipelineScheduleScenario.plan(start='2026-10-25T00:00:00Z',now='2026-10-24T00:00:00Z')
        self.assertEqual(body['configuration']['endDateTime'],'2026-10-25T00:01:00Z')
        native=copy.deepcopy(body['configuration'])
        for key in ('startDateTime','endDateTime'):native[key]=native[key].removesuffix('Z')
        self.assertTrue(same_configuration(native,body['configuration']))
        c=self.control();c.native=[{'id':S}];scenario=PipelineScheduleScenario(c,P)
        with self.assertRaisesRegex(ValueError,'EXISTING_STATE'):scenario.create(start='2026-10-25T00:00:00Z',now='2026-10-24T00:00:00Z',key='create')
        self.assertEqual([x[1]for x in c.calls],['GET'])
    def test_create_and_cleanup_preserve_every_unowned_schedule(self):
        c=self.control();s=PipelineScheduleScenario(c,P)
        owned=s.create(start='2026-10-25T00:00:00Z',now='2026-10-24T00:00:00Z',key='create')
        other={'id':P,'enabled':False,'configuration':{}}
        original_call=c.call
        def call(endpoint,method='GET',body=None,**kwargs):
            if method=='DELETE':
                c.calls.append((endpoint,method,body));c.native=[other];return {'status_code':204,'text':{}}
            return original_call(endpoint,method,body,**kwargs)
        c.native.append(other);c.call=call
        result=s.remove(owned,key='cleanup')
        self.assertEqual(result['other_schedules'],[other])
        self.assertTrue(next(x[0]for x in c.calls if x[1]=='DELETE').endswith('/'+S))
    def test_changed_owned_schedule_or_incomplete_listing_refuses_without_deletion(self):
        c=self.control();s=PipelineScheduleScenario(c,P)
        owned=s.create(start='2026-10-25T00:00:00Z',now='2026-10-24T00:00:00Z',key='create')
        c.native[0]['enabled']=False
        with self.assertRaisesRegex(ValueError,'CONCURRENT_CHANGE'):s.remove(owned,key='cleanup')
        self.assertNotIn('DELETE',[x[1]for x in c.calls])
        c.call=lambda *args,**kwargs:{'text':{'value':[],'continuationToken':'more'}}
        with self.assertRaisesRegex(ValueError,'COMPLETE_NATIVE'):s.list()

if __name__=='__main__':unittest.main()

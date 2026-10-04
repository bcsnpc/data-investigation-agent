import unittest
from test_process_debugging import Adapter
from investigator.process_debugging import vertical


class FreshnessRoutingTests(unittest.TestCase):
    def test_shared_job_history_retains_original_receipt_once_per_adapter_run(self):
        from unittest.mock import Mock
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        adapter=MicrosoftProcessAdapter(None,{},None,None,None)
        receipt={'status':'CURRENT','evidence':{'id':'sealed-original'}}
        adapter._read_job_history=Mock(return_value=receipt)
        for upper in ('a','b'):
            self.assertIs(adapter.job_history({'upper':{'id':upper},'lower':{'id':'c','transformation_asset_id':'job'}}),receipt)
        adapter._read_job_history.assert_called_once()
    def test_transformation_stop_does_not_skip_declared_loads(self):
        class Loads(Adapter):
            def __init__(self):
                super().__init__(['report','prepared','landing','source'],
                                 dict(report=10,prepared=11,landing=11,source=11),explain=True)
                self.layers[1]['transformation_asset_id']='job-a'
                self.layers[3]['transformation_asset_id']='job-b'
                self.jobs=[];self.deliveries=[]
            def capabilities(self):return super().capabilities()|{'source_delivery'}
            def job_history(self,boundary):
                self.jobs.append(boundary['lower']['id'])
                return {'status':'UNAVAILABLE','reason':'No current accounting for this declared load.'}
            def source_delivery(self,boundary,scope):
                self.deliveries.append(boundary['lower']['id'])
                return {'status':'UNAVAILABLE','reason':'No source capture cut.','observations':[]}
        a=Loads();result=vertical(a,'measure',{'question_kind':{'kind':'FRESHNESS','source':{'start':0,'end':9,'quote':'freshness'}}})
        self.assertEqual(result['classification'],'TRANSFORMATION_LOGIC')
        self.assertEqual(a.jobs,['prepared','source'])
        self.assertEqual(a.deliveries,['prepared','source'])
        self.assertEqual(a.evaluated,['report','prepared'])
        attempts=[o['freshness_attempt'] for o in result['_observations'] if 'freshness_attempt' in o]
        self.assertEqual([x['lower_layer'] for x in attempts],['prepared','source'])
        self.assertTrue(all(x['checks']['job_history']['status']=='UNAVAILABLE' for x in attempts))

    def test_reuse_and_unreachable_source_never_read_application(self):
        class Loads(Adapter):
            def __init__(self):
                super().__init__(['top','landing','source'],dict(top=10,landing=10,source=10))
                self.layers[-1]['transformation_asset_id']='load'
                self.jobs=0;self.deliveries=0
            def capabilities(self):return super().capabilities()|{'source_delivery'}
            def resolve_path(self,measure):
                return {**super().resolve_path(measure),'system_of_record':{'asset_id':'source','reachable':False}}
            def job_history(self,boundary):
                self.jobs+=1
                return {'status':'UNAVAILABLE','reason':'Load accounting unavailable.'}
            def source_delivery(self,*args):self.deliveries+=1;raise AssertionError('Unreachable source must not be read')
        a=Loads();r=vertical(a,'measure',{'question_kind':{'kind':'FRESHNESS','source':{'start':0,'end':9,'quote':'freshness'}}})
        self.assertEqual(r['classification'],'CONSISTENT_TO_BOUNDARY')
        self.assertEqual(a.jobs,1);self.assertEqual(a.deliveries,0)
        self.assertNotIn('source',a.evaluated)
        self.assertIn('configured unreachable',next(o['freshness_attempt'] for o in r['_observations'] if 'freshness_attempt' in o)['checks']['source_delivery']['reason'])


if __name__=='__main__':unittest.main()

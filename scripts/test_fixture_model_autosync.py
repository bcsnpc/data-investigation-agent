import copy,unittest
from fixture.model_autosync import ModelAutoSyncScenario

W='149f8d99-1c66-4a0a-9624-759be002bb60'
M='3484a2bc-98c5-4cef-be5c-a6215484075e'
OTHER='0c89889c-6fe6-49ab-91e9-4b00a51070e6'

class AutoSyncPlans(unittest.TestCase):
    def builder(self):
        return ModelAutoSyncScenario(W,[M],{'status_code':200,'text':{'@odata.context':'https://wabi-us-east2-primary-redirect.analysis.windows.net/v1.0/myorg/$metadata#capacities'}})
    def test_only_native_microsoft_api_roots_and_three_known_models(self):
        for uri in ('http://api.powerbi.com/v1.0/myorg/$metadata#capacities','https://analysis.windows.net.evil.test/v1.0/myorg/$metadata#capacities','https://user:secret@api.powerbi.com/v1.0/myorg/$metadata#capacities','https://api.powerbi.com:443/v1.0/myorg/$metadata#capacities','https://api.powerbi.com/other#capacities','https://api.powerbi.com/v1.0/myorg/$metadata?key=x#capacities'):
            with self.subTest(uri=uri),self.assertRaisesRegex(ValueError,'ROOT_REFUSED'):
                ModelAutoSyncScenario(W,[M],{'status_code':200,'text':{'@odata.context':uri}})
        with self.assertRaisesRegex(ValueError,'OUTSIDE_APPROVED'):self.builder().model_read(OTHER)
        with self.assertRaises(ValueError):ModelAutoSyncScenario(W,[M]*4,{})
    def test_native_numeric_id_bound_to_exact_requested_model(self):
        b=self.builder();metadata={'request':b.model_read(M),'status_code':200,'text':{'model':{'id':123}}}
        request=b.settings_read(M,metadata)
        self.assertTrue(request['url'].endswith('/metadata/models/123/settings'))
        changed=copy.deepcopy(metadata);changed['request']['url']+='/other'
        with self.assertRaisesRegex(ValueError,'BINDING_REQUIRED'):b.settings_read(M,changed)
        for identity in (True,'123',0,-1,'123/permissions'):
            changed=copy.deepcopy(metadata);changed['text']['model']['id']=identity
            with self.assertRaisesRegex(ValueError,'MODEL_ID_REQUIRED'):b.settings_read(M,changed)
    def test_toggle_and_restore_touch_only_autosync_and_refuse_changed_preimage(self):
        b=self.builder();metadata={'request':b.model_read(M),'status_code':200,'text':{'model':{'id':123}}}
        settings={'request':b.settings_read(M,metadata),'status_code':200,'text':{'directLakeAutoSync':True,'unrelated':'preserved'}}
        change=b.change(M,metadata,settings,expected=True,enabled=False)
        self.assertEqual(change,{'method':'POST','url':settings['request']['url'],'body':{'directLakeAutoSync':False},'expected_status_code':204})
        with self.assertRaisesRegex(ValueError,'PREIMAGE_CHANGED'):b.change(M,metadata,settings,expected=False,enabled=True)
        unavailable=copy.deepcopy(settings);unavailable['status_code']=405
        unavailable['text']={'Message':"The requested resource does not support http method 'GET'."}
        with self.assertRaisesRegex(ValueError,'PREIMAGE_CHANGED'):b.change(M,metadata,unavailable,expected=True,enabled=False)
        settings['text']['directLakeAutoSync']=False
        self.assertEqual(b.change(M,metadata,settings,expected=False,enabled=True)['body'],{'directLakeAutoSync':True})
        self.assertEqual(b.change(M,metadata,settings,expected=False,enabled=False)['mutations'],0)
        with self.assertRaisesRegex(ValueError,'BOOLEAN_REQUIRED'):b.change(M,metadata,settings,expected=False,enabled=1)

if __name__=='__main__':unittest.main()

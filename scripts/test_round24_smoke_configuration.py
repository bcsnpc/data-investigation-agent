import unittest,json,copy
from investigator.adapters.guided_smoke_configuration import guided_environment
class ConfigTests(unittest.TestCase):
 def test_full_existing_reader_environment_replaces_partial_legacy_policy(self):
  smoke={'environment':{'DIA_PLATFORM_GATEWAY_POLICY':json.dumps({'identities':{'old':{'http':[]}}})},'checks':{'daily':{'kind':'smoke'}},'input':{'url':'new'}}
  policy={'identities':{'worker:state':{'graph':{'fixture':['known']},'http':[{'method':'GET','url':'old-bundle'}]},'reader':{'role':'reader','http':[{'method':'GET','url':'native-endpoint'}]}}}
  guided={'environment':{'DIA_PLATFORM_GATEWAY_POLICY':json.dumps(policy),'DIA_GATEWAY_HTTP_IDENTITY':'reader'},'input':{'url':'old-bundle'},'checks':{'ticket':{'kind':'guided-investigation'}}};before=copy.deepcopy(guided)
  result=guided_environment(smoke,guided,input_url='new-bundle');observed=json.loads(result['environment']['DIA_PLATFORM_GATEWAY_POLICY'])
  self.assertEqual(observed['identities']['reader'],policy['identities']['reader']);self.assertNotIn('old',observed['identities']);self.assertEqual(observed['identities']['worker:state']['http'][0]['url'],'new-bundle');self.assertEqual(guided,before);self.assertEqual(result['checks'],smoke['checks'])
if __name__=='__main__':unittest.main()

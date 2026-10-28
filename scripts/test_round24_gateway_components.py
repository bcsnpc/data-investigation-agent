import unittest,json,copy
from unittest.mock import patch
from investigator.live_gateway import Gateway,GatewayDenied
from investigator.adapters.anthropic_runtime_policy import audit,migrate
from investigator.adapters.enrichment_anthropic import BatchClient,SESSION,request_for,ENDPOINT
from investigator.adapters.evaluation_anthropic import request_for as evaluation
from test_enrichment import source,secret_reference
class GatewayComponents(unittest.TestCase):
 @patch.dict('os.environ',{'DIA_LIVE_ACCESS_DISABLED':'0'})
 def test_every_anthropic_component_uses_only_its_exact_gateway_contract(self):
  policy={'version':1,'live_enabled':True,'identities':{'reasoning':{'role':'model','reasoning_models':['claude-opus-5-5'],'http':[{'method':'POST','url':'https://api.anthropic.com/v1/'+p,'purpose':'reasoning_model'}for p in ('messages','messages/count_tokens')]},'enrichment':{'role':'enrichment','enrichment_batches':{'provider':'anthropic','purpose':'ENRICHMENT_ONLY','model':'claude-sonnet-4-6'}},'model':{'http':[{'method':'POST','url':'https://unused.openai.azure.com/openai/v1/responses','purpose':'model'}]}}}
  before=copy.deepcopy(policy);policy=migrate(policy);self.assertTrue(all(r['admitted']for r in audit(policy)));self.assertEqual(before['identities']['reasoning'],policy['identities']['reasoning'])
  routes={(r['component'],r['identity'])for r in audit(policy)}
  for component in ('writer','grader'):
   self.assertIn((component,'reasoning'),routes);self.assertIn((component,'enrichment'),routes)
  gateway=Gateway(policy)
  for component in ('investigator','smoke','screenshot','writer','grader'):
   body={'model':'claude-opus-5-5','max_tokens':1000,'system':[{'type':'text','text':'instructions','cache_control':{'type':'ephemeral'}}],'messages':[{'role':'user','content':'input'}],'tools':[{'name':'resolve_intake'if component in ('screenshot','writer','grader')else'run_sql','description':'read','input_schema':{'type':'object'}}]}
   gateway.http('reasoning','POST','https://api.anthropic.com/v1/messages',json.dumps(body).encode())
   with self.assertRaises(GatewayDenied):gateway.http('reasoning','POST','https://api.anthropic.com/v1/messages/batches',b'{}')
  client=BatchClient(secret_reference=secret_reference(),identity='enrichment',record=lambda *a:None,purpose='ENRICHMENT');token=SESSION.set(client)
  try:
   tasks=[request_for(source(),'a'*64),evaluation({'protocol':'scored-evaluation-v1','purpose':'WRITE_TICKETS','case_id':'writer','description':'A figure differs.','labels':['Report'],'variations':['short']},'b'*64),evaluation({'protocol':'scored-evaluation-v1','purpose':'GRADE_GUIDED_ANSWER','case_id':'grader','expected':{},'delivered':{}},'c'*64)]
   for component,task in zip(('enrichment','writer','grader'),tasks):
    with self.subTest(component=component):gateway.http('enrichment','POST',ENDPOINT,json.dumps({'requests':[task]}).encode())
   with self.assertRaises(GatewayDenied):gateway.http('enrichment','POST','https://api.anthropic.com/v1/messages',b'{}')
   with self.assertRaises(GatewayDenied):gateway.http('enrichment','GET',ENDPOINT+'/unadmitted',None)
  finally:SESSION.reset(token)
if __name__=='__main__':unittest.main()

import copy,unittest
from types import SimpleNamespace
from unittest.mock import patch
from investigator.claim_provider import extract
class FakeDecision:
 calls=[];values=[]
 def __init__(self,runtime,session_id,**kw):self.runtime=runtime
 def _call(self,payload,**kwargs):
  self.calls.append((copy.deepcopy(self.runtime.config),copy.deepcopy(self.runtime.generation_options),payload,kwargs));return self.values.pop(0)
class ClaimProviderTests(unittest.TestCase):
 def setUp(self):
  FakeDecision.calls=[]
  self.agent=SimpleNamespace(config={'_estate':{'investigation':{'mode':'HYBRID','input_characters_per_request':150000,'agent_deployment':'strong'}}},generation_options={'max_payload_characters':32000})
  self.workspace=SimpleNamespace(agent=self.agent)
 def test_agent_override_not_inherited_and_tokens_not_copied_quotes(self):
  FakeDecision.values=[{'facts':[{'field':'metric','reference':[1,1],'symbol':None,'metric_reference':None}]}]
  with patch('investigator.claim_provider.GovernedDecision',FakeDecision):result,audit=extract(self.workspace,'Quantity','doc','session')
  config,options,payload,_=FakeDecision.calls[0]
  self.assertEqual(options['max_payload_characters'],32000);self.assertEqual(config['_estate']['investigation'],{'mode':'PIPELINE'})
  self.assertEqual(result[0]['value'],{'phrase':'Quantity'});self.assertEqual(payload['ticket_tokens'],[[1,'Quantity']]);self.assertEqual(self.agent.config['_estate']['investigation']['input_characters_per_request'],150000)
 def test_one_invalid_reference_retry_then_valid(self):
  FakeDecision.values=[{'facts':[{'field':'metric','reference':[99,99],'symbol':None,'metric_reference':None}]},{'facts':[]}]
  with patch('investigator.claim_provider.GovernedDecision',FakeDecision):_,audit=extract(self.workspace,'Quantity','doc','session')
  self.assertEqual(audit['calls'],2);self.assertEqual(len(audit['rejections']),1)
 def test_two_invalid_references_refuse_without_third_call(self):
  bad={'facts':[{'field':'metric','reference':[99,99],'symbol':None,'metric_reference':None}]};FakeDecision.values=[bad,bad]
  with patch('investigator.claim_provider.GovernedDecision',FakeDecision),self.assertRaisesRegex(ValueError,'REJECTED_TWICE'):extract(self.workspace,'Quantity','doc','session')
  self.assertEqual(len(FakeDecision.calls),2)
if __name__=='__main__':unittest.main()

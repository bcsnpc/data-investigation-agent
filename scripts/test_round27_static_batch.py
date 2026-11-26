from types import SimpleNamespace
from unittest.mock import Mock
import unittest
from investigator.adapters.reasoning_anthropic_batch import StaticBatch,BatchPending,permits,ENDPOINT,SESSION,batch_rate
from investigator.adapters.reasoning_anthropic import BASE
from investigator.reasoning_budget import RateCard
from investigator.adapters.free_dev_defaults import pin,MODELS
class BatchTests(unittest.TestCase):
 def client(self):
  return SimpleNamespace(model='claude-opus-5-5',identity='reasoner',budget=Mock(),record=Mock(),send=Mock(),sleep=Mock())
 def body(self):
  return {'model':'claude-opus-5-5','max_tokens':40,'system':[{'type':'text','text':'stable','cache_control':{'type':'ephemeral'}}],'messages':[{'role':'user','content':'synthetic'}],'tools':[{'name':'get_evidence','description':'read','input_schema':{'type':'object'}}]}
 def test_pre_reserved_generation_is_not_reserved_twice_and_is_durable(self):
  client=self.client();client.send.return_value={'id':'msgbatch_existing','processing_status':'ended'}
  batch=StaticBatch(client,static_ticket=True);receipt=batch.submit([self.body()],reserved=['reservation-one'])
  client.budget.reserve.assert_not_called();self.assertEqual(list(receipt['reservations'].values()),['reservation-one'])
  self.assertTrue(any(x.args[0]['event']=='STATIC_BATCH_SUBMITTED'for x in client.record.call_args_list))
 def test_client_static_generation_uses_batch_only_and_keeps_usage(self):
  from unittest.mock import patch
  from investigator.adapters.reasoning_anthropic import Client
  budget=Mock();budget.rate.model='claude-opus-5-5'
  with patch('investigator.adapters.managed_identity.validate_secret_reference'):
   client=Client(model='claude-opus-5-5',budget=budget,identity='reader',secret_reference={},record=Mock(),send=Mock(),batch_static=True)
  message={'content':[],'usage':{'input_tokens':20,'output_tokens':5}}
  with patch('investigator.adapters.reasoning_anthropic_batch.StaticBatch')as cls:
   cls.return_value.submit.return_value={'id':'msgbatch_owned'};cls.return_value.collect.return_value={'one':{'type':'succeeded','message':message}}
   self.assertEqual(client.generate(self.body(),'existing-reservation'),message)
   cls.return_value.submit.assert_called_once_with([self.body()],reserved=['existing-reservation'])
  client.send.assert_not_called()
 def test_unknown_batch_generation_never_retries_submit(self):
  from unittest.mock import patch
  from investigator.adapters.reasoning_anthropic import Client
  budget=Mock();budget.rate.model='claude-opus-5-5'
  with patch('investigator.adapters.managed_identity.validate_secret_reference'):
   client=Client(model='claude-opus-5-5',budget=budget,identity='reader',secret_reference={},record=Mock(),send=Mock(),batch_static=True)
  with patch('investigator.adapters.reasoning_anthropic_batch.StaticBatch')as cls:
   cls.return_value.submit.side_effect=TimeoutError()
   with self.assertRaisesRegex(BatchPending,'SUBMIT_UNCERTAIN'):client.generate(self.body(),'r')
   self.assertEqual(cls.return_value.submit.call_count,1)
 def test_authentication_or_credit_failure_stays_visible_to_hard_stop(self):
  from unittest.mock import patch
  from investigator.adapters.reasoning_anthropic import Client,ProviderHTTPError
  budget=Mock();budget.rate.model='claude-opus-5-5'
  with patch('investigator.adapters.managed_identity.validate_secret_reference'):
   client=Client(model='claude-opus-5-5',budget=budget,identity='reader',secret_reference={},record=Mock(),send=Mock(),batch_static=True)
  with patch('investigator.adapters.reasoning_anthropic_batch.StaticBatch')as cls:
   cls.return_value.submit.side_effect=ProviderHTTPError(401,'authentication_error')
   with self.assertRaises(ProviderHTTPError):client.generate(self.body(),'r')
   self.assertEqual(cls.return_value.submit.call_count,1)
 def test_static_batch_is_installed_anthropic_only_and_not_ticket_selected(self):
  from investigator.adapters.provider_runtime import validate
  configuration={'provider':'anthropic','model':'claude-opus-5-5','rate_card':{},'secret_reference':{},'gateway_identity':'reader','worker_identity':'round27-confirmation','batch_static':True}
  self.assertEqual(validate(configuration),'anthropic')
  for change in ({'provider':'openai'},{'batch_static':False},{'batch_static':'true'}):
   with self.assertRaisesRegex(ValueError,'STATIC_ANTHROPIC'):validate({**configuration,**change})
 def test_unknown_submission_not_retried_and_reserved(self):
  client=self.client();client.send.side_effect=TimeoutError()
  with self.assertRaises(TimeoutError):StaticBatch(client,static_ticket=True).submit([self.body()])
  self.assertEqual(client.send.call_count,1);client.budget.reserve.assert_called_once();client.budget.settle.assert_called_once()
 def test_owned_results_settle_exact_usage_and_duplicate_ids_refuse(self):
  client=self.client();client.send.return_value={'id':'msgbatch_test','processing_status':'ended'}
  batch=StaticBatch(client,static_ticket=True);receipt=batch.submit([self.body()]);key=next(iter(receipt['reservations']));usage={'input_tokens':20,'output_tokens':5}
  client.send.return_value=[{'custom_id':key,'result':{'type':'succeeded','message':{'usage':usage}}}]
  batch.collect(receipt);client.budget.settle.assert_called_once_with(receipt['reservations'][key],usage)
  with self.assertRaises(ValueError):batch.collect({'id':'msgbatch_other','reservations':{}})
 def test_pending_submission_has_durable_id_and_no_second_post(self):
  client=self.client();client.send.return_value={'id':'msgbatch_test','processing_status':'in_progress'};batch=StaticBatch(client,static_ticket=True);receipt=batch.submit([self.body()])
  with self.assertRaises(BatchPending):batch.collect(receipt)
  self.assertEqual([c.args[0]for c in client.send.call_args_list],['POST','GET'])
 def test_policy_no_arbitrary_model_tool_write_url_or_foreign_batch(self):
  client=self.client();batch=StaticBatch(client,static_ticket=True);body={'requests':[{'custom_id':'ticket','params':self.body()}]};batch.submitting=body
  policy={'role':'model','reasoning_models':[client.model],'http':[{'method':'POST','url':BASE+'/messages','purpose':'reasoning_model'}]}
  self.assertFalse(permits(policy,'reasoner','POST',ENDPOINT,body));marker=SESSION.set(batch)
  try:
   self.assertTrue(permits(policy,'reasoner','POST',ENDPOINT,body))
   for method,url in [('DELETE',ENDPOINT),('POST',ENDPOINT+'/msgbatch_other/cancel'),('GET',ENDPOINT+'/msgbatch_other')]:self.assertFalse(permits(policy,'reasoner',method,url,None))
   bad=self.body();bad['tools'][0]['name']='write_data';self.assertFalse(permits(policy,'reasoner','POST',ENDPOINT,{'requests':[{'custom_id':'x','params':bad}]}))
  finally:SESSION.reset(marker)
  with self.assertRaises(ValueError):StaticBatch(client,static_ticket=False)
 def test_batch_half_price_including_cache_and_active_two_models_only(self):
  rate=RateCard(model='claude-opus-5-5',input_rate=5,output_rate=20,base_input_rate=4,cache_read_rate=.2,cache_write_rate=5,source='https://platform.claude.com/docs/en/about-claude/pricing',observed_at='2026-11-25')
  self.assertEqual(batch_rate(rate).usage_price({'input_tokens':100,'cache_read_input_tokens':100,'output_tokens':10}),310)
  self.assertEqual(len(MODELS),2);self.assertTrue(pin({})['model'].endswith(':free'));self.assertEqual(pin({},role='backup')['provider'],'nvidia')
if __name__=='__main__':unittest.main()

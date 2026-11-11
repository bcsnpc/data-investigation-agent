"""Offline Nova transport, secret boundaries, normalized usage and round cap."""
import json, os, unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
from investigator.adapters.reasoning_bedrock import BedrockProvider, model_guard, request_for, response_for, authorize_body, BedrockError
from investigator.live_gateway import configured, GatewayDenied
from investigator.provider_budget import ensure_account, account_for
from investigator.shared_state import SharedState
from investigator.reasoning_budget import TicketBudget, RateCard
MODEL='amazon.nova-micro-v1:0'
URL='https://bedrock-runtime.us-east-1.amazonaws.com/model/amazon.nova-micro-v1%3A0/converse'
TOOLS=[{'name':'resolve_intake','description':'Synthetic only','input_schema':{'type':'object'}}]
NATIVE={'output':{'message':{'role':'assistant','content':[{'toolUse':{'toolUseId':'t1','name':'resolve_intake','input':{'ok':True}}}]}},'usage':{'inputTokens':12,'outputTokens':5,'cacheReadInputTokens':1024,'cacheWriteInputTokens':16},'stopReason':'tool_use','ResponseMetadata':{'RequestId':'synthetic-request'}}
def policy():
 return {'version':1,'live_enabled':True,'identities':{'nova':{'role':'model','http':[{'method':'POST','url':URL,'purpose':'configured_ai'}],'ai_providers':{'bedrock':{'region':'us-east-1','models':[MODEL],'tools':['resolve_intake']}}}}}
class BedrockTests(unittest.TestCase):
 def provider(self,**kw):
  budget=Mock();budget.rate.model=MODEL;budget.reserve.return_value='r1';sdk=Mock();sdk.converse.return_value=NATIVE
  values={'access_key_id':'synthetic-access-id','secret_access_key':'synthetic-secret','region':'us-east-1'};factory=Mock(return_value=sdk);record=Mock()
  with patch('investigator.adapters.managed_identity.validate_secret_reference'):
   model=BedrockProvider(model=MODEL,budget=budget,identity='nova',secret_reference={k:{'name':k}for k in values},record=record,sdk_factory=factory,key_reader=lambda r,**_:values[r['name']],sleep=Mock(),**kw)
  return model,budget,sdk,factory,record
 def test_claude_and_profile_bypasses_refused_by_default(self):
  with patch.dict(os.environ,{'BEDROCK_ALLOW_CLAUDE':'false'}):
   for model in ('anthropic.claude-opus-5-5','us.anthropic.claude-opus-5-5','arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude'):
    with self.assertRaisesRegex(ValueError,'CLAUDE_DISABLED'):model_guard(model)
  for model in ('meta.llama','openai.gpt','us.amazon.nova-pro-v1:0','amazon.nova-micro-v1:0/other'):
   with self.assertRaisesRegex(ValueError,'AMAZON_NOVA_ONLY'):model_guard(model)
 def test_single_haiku_credit_exception_is_exact_and_guarded(self):
  model='anthropic.claude-3-haiku-20240307-v1:0';url='https://bedrock-runtime.us-east-1.amazonaws.com/model/anthropic.claude-3-haiku-20240307-v1%3A0/converse'
  permissions={'ai_providers':{'bedrock':{'region':'us-east-1','models':[model],'single_haiku_credit_test':True}}}
  body={'messages':[{'role':'user','content':[{'text':'Reply OK.'}]}],'inferenceConfig':{'maxTokens':20}}
  with patch.dict(os.environ,{'BEDROCK_ALLOW_CLAUDE':'true'}):
   authorize_body(permissions,'POST',url,body)
   for changed in ({**body,'inferenceConfig':{'maxTokens':21}},{**body,'messages':[{'role':'user','content':[{'text':'Different'}]}]}):
    with self.assertRaisesRegex(ValueError,'CREDIT_TEST_BOUND'):authorize_body(permissions,'POST',url,changed)
  with patch.dict(os.environ,{'BEDROCK_ALLOW_CLAUDE':'false'}):
   with self.assertRaisesRegex(ValueError,'CLAUDE_DISABLED'):authorize_body(permissions,'POST',url,body)
 def test_tools_results_and_cache_roundtrip(self):
  messages=[{'role':'user','content':'synthetic'},{'role':'assistant','content':[{'type':'tool_use','id':'t1','name':'resolve_intake','input':{'a':1}}]},{'role':'user','content':[{'type':'tool_result','tool_use_id':'t1','content':'ok'}]}]
  body=request_for(model=MODEL,system='fixed',messages=messages,tools=TOOLS,max_tokens=100,explicit_cache=True)
  self.assertEqual(body['system'],[{'text':'fixed'},{'cachePoint':{'type':'default'}}]);self.assertNotIn('cachePoint',body['toolConfig']['tools'][0])
  self.assertEqual(body['messages'][2]['content'][0]['toolResult']['content'],[{'text':'ok'}])
  reply=response_for(NATIVE,MODEL);self.assertEqual(reply.usage.input_tokens,1052);self.assertEqual(reply.usage.budget_usage(),{'input_tokens':12,'output_tokens':5,'cache_read_input_tokens':1024,'cache_creation_input_tokens':16});self.assertEqual(reply.content[0]['id'],'t1')
 def test_gateway_denies_other_models_tools_and_extra_fields(self):
  body=request_for(model=MODEL,system='fixed',messages=[{'role':'user','content':'hi'}],tools=TOOLS,max_tokens=100);body.pop('modelId');permissions=policy()['identities']['nova'];authorize_body(permissions,'POST',URL,body)
  for url,payload in ((URL.replace('nova-micro','nova-pro'),body),(URL,{**body,'guardrailConfig':{}}),(URL,{**body,'toolConfig':{'tools':[{'toolSpec':{'name':'unapproved','description':'','inputSchema':{'json':{}}}}]}})):
   with self.assertRaises(ValueError):authorize_body(permissions,'POST',url,payload)
 def test_mock_boto3_explicit_vault_credentials_no_retries_no_secret_record(self):
  model,budget,sdk,factory,record=self.provider(explicit_cache=True)
  with patch.dict(os.environ,{'DIA_LIVE_ACCESS_DISABLED':'0'}),configured(policy()),patch('investigator.round23_calendar.require_live_window'):
   result=model.complete(system='fixed',messages=[{'role':'user','content':'synthetic'}],tools=TOOLS,max_tokens=100)
  self.assertEqual(factory.call_args.kwargs['aws_access_key_id'],'synthetic-access-id');self.assertEqual(factory.call_args.kwargs['config'].retries['total_max_attempts'],1)
  sdk.converse.assert_called_once();sdk.close.assert_called_once();budget.settle.assert_any_call('r1',response_for(NATIVE,MODEL).usage.budget_usage());self.assertEqual(result['stop_reason'],'tool_use')
  serialized=json.dumps(record.call_args_list,default=str);self.assertNotIn('synthetic-access-id',serialized);self.assertNotIn('synthetic-secret',serialized)
 def test_denied_gateway_makes_no_sdk_call(self):
  model,budget,sdk,_,_=self.provider()
  with patch.dict(os.environ,{'DIA_LIVE_ACCESS_DISABLED':'0'}),configured({'version':1,'live_enabled':True,'identities':{}}),patch('investigator.round23_calendar.require_live_window'):
   with self.assertRaises(GatewayDenied):model.complete(system='fixed',messages=[{'role':'user','content':'x'}],tools=TOOLS)
  sdk.converse.assert_not_called();budget.settle.assert_called_with('r1')
 def test_billing_error_not_retried_and_body_not_exposed(self):
  from botocore.exceptions import ClientError
  model,budget,sdk,_,_=self.provider();sdk.converse.side_effect=ClientError({'Error':{'Code':'AccessDeniedException','Message':'synthetic-secret'},'ResponseMetadata':{'HTTPStatusCode':403}},'Converse')
  with patch.dict(os.environ,{'DIA_LIVE_ACCESS_DISABLED':'0'}),configured(policy()),patch('investigator.round23_calendar.require_live_window'):
   with self.assertRaisesRegex(BedrockError,'AccessDeniedException')as got:model.complete(system='fixed',messages=[{'role':'user','content':'x'}],tools=TOOLS)
  self.assertNotIn('synthetic-secret',str(got.exception));sdk.converse.assert_called_once();model.sleep.assert_not_called()
 def test_nova_cannot_become_investigator(self):
  model,budget,sdk,_,_=self.provider()
  with self.assertRaisesRegex(ValueError,'INVESTIGATOR_NOT_APPROVED'):model.complete(system='x',messages=[],tools=[{'name':'submit_finding'}])
  budget.reserve.assert_not_called();sdk.converse.assert_not_called()
 def test_five_dollar_round_cap_does_not_reset_monthly(self):
  with TemporaryDirectory()as d:
   state=SharedState.offline(Path(d)/'s.db');state.migrate();at=lambda m:datetime(2026,m,1,tzinfo=timezone.utc).timestamp()
   account=ensure_account(state,'bedrock',at(11));state.reserve(account,'old','w',4999900);state.settle(account,'old','w',4999900)
   self.assertEqual(account,account_for('bedrock',at(12)));self.assertEqual(int(state.totals(account)['ceiling']),5000000)
   rate=RateCard(model=MODEL,input_rate=1,output_rate=1,source='https://aws.amazon.com/bedrock/pricing/',observed_at='2026-11-01');budget=TicketBudget(state,case_id='nova-test',owner='w',provider='bedrock',clock=lambda:at(12),rate=rate,actual_usage_limit=3000000)
   with self.assertRaisesRegex(Exception,'MONTHLY_MODEL_EXHAUSTED'):budget.reserve({'model':MODEL,'max_tokens':100},input_tokens_upper_bound=100)
   self.assertEqual(int(state.totals(account)['charged']),4999900)
 def test_zero_cost_cache_writes_use_documented_rate_not_reservation_rate(self):
  rate=RateCard(model=MODEL,input_rate='.035',output_rate='.14',cache_read_rate='.00875',cache_write_rate=0,source='https://aws.amazon.com/bedrock/pricing/',observed_at='2026-11-01')
  self.assertEqual(rate.usage_price({'input_tokens':1000,'output_tokens':1000,'cache_creation_input_tokens':2000,'cache_read_input_tokens':1000}),184)
 def test_native_sdk_capture_projects_and_replays_without_raw_value_on_disk(self):
  from types import SimpleNamespace
  from investigator.privacy_tape import PrivacyTape
  from investigator.privacy_projection import canonical
  from test_privacy_projection import projector,policy as privacy_policy
  model,_,sdk,_,_=self.provider();events=[];model.record=events.append;raw='PRIVATE SYNTHETIC PERSON'
  def response(**body):
   handler=sdk.meta.events.register.call_args.args[1]
   handler(SimpleNamespace(url=URL,body=json.dumps({k:v for k,v in body.items()if k!='modelId'}).encode(),headers={'Authorization':'NEVER_CAPTURE_THIS_HEADER'}))
   return NATIVE
  sdk.converse.side_effect=response
  with patch.dict(os.environ,{'DIA_LIVE_ACCESS_DISABLED':'0'}),configured(policy()),patch('investigator.round23_calendar.require_live_window'):
   model.complete(system='Check '+raw,messages=[{'role':'user','content':raw}],tools=TOOLS,max_tokens=100)
  self.assertTrue(any(e['event']=='BEDROCK_NATIVE_REQUEST'and'body'in e for e in events))
  self.assertNotIn('NEVER_CAPTURE_THIS_HEADER',json.dumps(events));self.assertNotIn('body_base64',json.dumps(events))
  typed={'columns':privacy_policy()['columns'],'rows':[[raw]]}
  with TemporaryDirectory()as d:
   path=Path(d)/'projected.json';tape=PrivacyTape(path,projector());tape.event('TYPED_RESULT',canonical(typed))
   for event in events:tape.event('PROVIDER',canonical(event))
   result=tape.finish({'passed':True});self.assertNotIn(raw,path.read_text())
   replay=PrivacyTape(path,projector(),replay=True);replay.event('TYPED_RESULT',canonical(typed))
   for event in events:replay.event('PROVIDER',canonical(event))
   self.assertEqual(replay.finish(result),result)
if __name__=='__main__':unittest.main()

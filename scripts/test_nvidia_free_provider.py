"""Zero-network synthetic dev tests; no credential or paid-provider calls."""
import json
import time
import io
import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
from investigator.shared_state import SharedState
from investigator.nvidia_free_budget import FreeRateCard, FreeBudget, provision, account_for
from investigator.adapters.reasoning_nvidia import BASE, Client, ProviderError, ProviderUnavailable, request_for, response_for, authorize_body, stream_response, HTTP_TIMEOUT_SECONDS
from investigator.adapters.provider_runtime import validate, validate_graders
from investigator.model_spend import SpendHold

MODEL='z-ai/glm-5.3-flash'
TOOLS=[{'name':'get_definition','description':'Read synthetic value','input_schema':{'type':'object','properties':{'id':{'type':'integer'}},'required':['id']}}]

def response():
    return {'id':'r1','model':MODEL,'choices':[{'finish_reason':'tool_calls','message':{'role':'assistant','content':None,
            'tool_calls':[{'id':'t1','type':'function','function':{'name':'get_definition','arguments':'{"id":7}'}}]}}],
            'usage':{'prompt_tokens':20,'completion_tokens':9,'prompt_tokens_details':{'cached_tokens':4}}}

class NvidiaFreeTests(unittest.TestCase):
    def test_real_gateway_transport_accepts_documented_model_stream_timeout(self):
        from types import SimpleNamespace
        from investigator.nvidia_dev_profile import configuration,gateway
        from investigator.live_gateway import configured,Gateway
        raw=io.BytesIO(json.dumps(response()).encode());raw.status=200;raw.headers={'Content-Type':'application/json'}
        opener=SimpleNamespace(open=Mock(return_value=raw))
        reference={'vault_url':'https://kv-test.vault.azure.net','secret_name':'nvidia-api-key','secret_version':'a'*32,'identity':{}}
        config=configuration({'gateway_identity':'reasoning'},model=MODEL,discovered_models=[MODEL],secret_reference=reference)
        prior={'version':1,'live_enabled':True,'identities':{'reasoning':{'role':'model','http':[]}}}
        with patch('investigator.adapters.managed_identity.validate_secret_reference'):
            c=Client(model=MODEL,budget=self.budget(),identity='reasoning',secret_reference={},record=Mock(),key_reader=lambda *a,**k:'synthetic-private-key')
        with configured(gateway(prior,config)),patch.object(Gateway,'check_live',return_value=None),patch('investigator.adapters.reasoning_nvidia.build_opener',return_value=opener):
            self.assertEqual(c._http('POST',BASE+'/chat/completions',request_for(model=MODEL,system='s',messages=[],tools=TOOLS,max_tokens=20)),response())
        self.assertEqual(opener.open.call_args.kwargs['timeout'],300)

    def test_streaming_wire_and_assistant_text_follow_native_api_shape(self):
        from investigator.regression_features import configured
        body=request_for(model=MODEL,system='s',messages=[{'role':'assistant','content':[{'type':'text','text':'Read it.'}]}],tools=TOOLS,max_tokens=50)
        self.assertEqual(body['messages'][1]['content'],'Read it.')
        self.assertTrue(body['stream']);self.assertEqual(body['stream_options'],{'include_usage':True})
    def stream_bytes(self,*,done=True,usage=True,finish=True,model=MODEL):
        chunks=[{'id':'r1','model':model,'choices':[{'index':0,'delta':{'role':'assistant','reasoning_content':'opaque',
          'tool_calls':[{'index':0,'id':'t1','type':'function','function':{'name':'get_definition','arguments':'{"id":'}}]},'finish_reason':None}]},
          {'id':'r1','model':model,'choices':[{'index':0,'delta':{'tool_calls':[{'index':0,'function':{'arguments':'7}'}}]},'finish_reason':'tool_calls' if finish else None}]}]
        if usage:chunks.append({'id':'r1','model':model,'choices':[],'usage':response()['usage']})
        return b''.join(('data: '+json.dumps(c)+'\n\n').encode()for c in chunks)+(b'data: [DONE]\n\n' if done else b'')
    def test_stream_retains_exact_native_lines_and_assembles_complete_tool_and_usage(self):
        import base64
        raw=self.stream_bytes();events=[]
        result=stream_response(io.BytesIO(raw),model=MODEL,record=events.append,clock=lambda:1,started=0,secret_value='never-echo-this-key')
        self.assertEqual(b''.join(base64.b64decode(e['raw_base64'])for e in events),raw)
        self.assertEqual(response_for(result,MODEL,TOOLS).content[-1]['input'],{'id':7})
        self.assertEqual(result['usage'],response()['usage'])
    def test_incomplete_stream_never_executes_a_complete_looking_tool(self):
        from http.client import IncompleteRead
        for option in ('done','usage','finish'):
            with self.subTest(missing=option),self.assertRaises(IncompleteRead):
                stream_response(io.BytesIO(self.stream_bytes(**{option:False})),model=MODEL,record=Mock(),clock=lambda:1,started=0,secret_value='key-not-in-body')
        with self.assertRaisesRegex(ValueError,'MODEL_DIFFERS'):
            stream_response(io.BytesIO(self.stream_bytes(model='other')),model=MODEL,record=Mock(),clock=lambda:1,started=0,secret_value='key-not-in-body')
    def test_stream_has_an_absolute_time_bound_and_secret_echo_refusal(self):
        with self.assertRaises(TimeoutError):
            stream_response(io.BytesIO(self.stream_bytes()),model=MODEL,record=Mock(),clock=lambda:HTTP_TIMEOUT_SECONDS,started=0,secret_value='key-not-in-body')
        with self.assertRaisesRegex(ValueError,'SECRET_ECHO'):
            stream_response(io.BytesIO(b'data: private-secret\n\n'),model=MODEL,record=Mock(),clock=lambda:1,started=0,secret_value='private-secret')
    def test_transport_exhaustion_is_environment_affected_and_all_attempts_stay_charged(self):
        events=[];send=Mock(side_effect=TimeoutError('synthetic timeout'))
        with patch('investigator.adapters.managed_identity.validate_secret_reference'):
            c=Client(model=MODEL,budget=self.budget(),identity='test',secret_reference={},record=events.append,send=send,sleep=self.sleep,clock=lambda:self.now[0],jitter=lambda:0)
        with self.assertRaises(ProviderUnavailable):c.complete(system='s',messages=[],tools=TOOLS,max_tokens=50)
        self.assertEqual(send.call_count,3);self.assertEqual(c.budget.status()['monthly_calls_used'],3)
        failed=next(e for e in events if e['event']=='REASONING_UNAVAILABLE')
        self.assertTrue(failed['environment_affected']);self.assertFalse(failed['is_quality_result'])
        self.assertEqual(failed['error_type'],'TimeoutError');self.assertEqual(failed['attempts'],3)
        self.assertTrue(all(r['status']=='UNCERTAIN'for r in self.state.snapshot(account_for(self.now[0]))['reservations']))
    def test_http_negotiates_streaming_with_longer_timeout_and_no_async_repost(self):
        from types import SimpleNamespace
        body=request_for(model=MODEL,system='s',messages=[],tools=TOOLS,max_tokens=50)
        def transport(raw,status=200,content_type='text/event-stream'):
            stream=io.BytesIO(raw);stream.status=status;stream.headers={'Content-Type':content_type};return stream
        with patch('investigator.adapters.managed_identity.validate_secret_reference'):
            c=Client(model=MODEL,budget=self.budget(),identity='test',secret_reference={},record=Mock(),key_reader=lambda *a,**k:'synthetic-private-key')
        with patch('investigator.live_gateway.current',return_value=SimpleNamespace(http=Mock())),patch('investigator.live_gateway.open_http',return_value=transport(self.stream_bytes()))as send:
            out=c._http('POST',BASE+'/chat/completions',body)
        self.assertEqual(out['choices'][0]['message']['tool_calls'][0]['id'],'t1')
        self.assertEqual(send.call_args.kwargs['timeout'],300)
        self.assertEqual(send.call_args.args[1].get_header('Accept'),'text/event-stream')
        with patch('investigator.live_gateway.current',return_value=SimpleNamespace(http=Mock())),patch('investigator.live_gateway.open_http',return_value=transport(b'{}',202,'application/json'))as send:
            with self.assertRaisesRegex(ProviderUnavailable,'ASYNC_RESULT_PENDING'):c._http('POST',BASE+'/chat/completions',body)
        self.assertEqual(send.call_count,1)
        with patch('investigator.live_gateway.current',return_value=SimpleNamespace(http=Mock())),patch('investigator.live_gateway.open_http',return_value=transport(json.dumps(response()).encode(),content_type='application/json')):
            self.assertEqual(c._http('POST',BASE+'/chat/completions',body),response())
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.state=SharedState.offline(Path(self.tmp.name)/'state.db');self.state.migrate()
        self.now=[1795392000.0]
        self.sleep=lambda n:self.now.__setitem__(0,self.now[0]+n)
        self.rate=FreeRateCard(model=MODEL,input_rate=0,output_rate=0,source='https://build.nvidia.com',observed_at='2026-11-22')
        provision(self.state,self.now[0])
    def budget(self):
        return FreeBudget(self.state,case_id='synthetic',owner='round27-free-test',rate=self.rate,clock=lambda:self.now[0],sleep=self.sleep)
    def test_calls_tokens_and_zero_dollars_do_not_spend_paid_credit(self):
        b=self.budget();k=b.reserve({'model':MODEL,'max_tokens':20});b.settle(k,{'input_tokens':20,'output_tokens':9});b.settle(k)
        s=self.state.snapshot(account_for(self.now[0]));self.assertEqual(s['charged'],'1');self.assertEqual(s['unit'],'CALLS')
        self.assertEqual(s['reservations'][0]['status'],'SETTLED');self.assertEqual(b.status()['charged_microdollars'],0)
        self.assertEqual(s['reservations'][0]['detail']['settlement']['usage']['input_tokens'],20)
    def test_unknown_calls_stay_charged_and_model_cannot_change(self):
        b=self.budget();k=b.reserve({'model':MODEL,'max_tokens':20});b.settle(k)
        self.assertEqual(self.state.snapshot(account_for(self.now[0]))['reservations'][0]['status'],'UNCERTAIN')
        with self.assertRaises(SpendHold):b.reserve({'model':'another','max_tokens':20})
    def test_free_policy_drift_and_paid_account_path_refuse_before_reserving(self):
        from investigator.provider_budget import policy,account_for as paid_account
        approved=policy('nvidia')
        with patch('investigator.provider_budget.policy',return_value={**approved,'monthly_call_allowance':1001}):
            with self.assertRaisesRegex(SpendHold,'CONFIGURATION_POLICY_DIFFERS'):
                self.budget().reserve({'model':MODEL,'max_tokens':20})
        self.assertEqual(self.budget().status()['monthly_calls_used'],0)
        with self.assertRaisesRegex(ValueError,'CALLS_ACCOUNT'):
            paid_account('nvidia',self.now[0])
    def test_lost_commit_acknowledgement_does_not_charge_or_dispatch_twice(self):
        b=self.budget(); operation=self.state._retry_connection_operation
        def replay_commit(name, callback):
            self.assertEqual(name,'IDEMPOTENT_NVIDIA_FREE_CALL')
            self.assertIsNone(callback())
            return callback()
        with patch.object(self.state,'_retry_connection_operation',side_effect=replay_commit):
            key=b.reserve({'model':MODEL,'max_tokens':20})
        self.assertEqual(b.status()['monthly_calls_used'],1)
        b.settle(key,{'input_tokens':1,'output_tokens':1})
        self.assertEqual(len(self.state.snapshot(account_for(self.now[0]))['reservations']),1)
    def test_paid_accounts_unchanged_and_new_month_requires_own_account(self):
        with self.state.transaction() as db:
            self.state.sql(db,'INSERT INTO state_accounts VALUES(?,?,?,?,?,?)',('paid','MICRODOLLARS',100,0,70,0))
        before=self.state.snapshot('paid');b=self.budget()
        key=b.reserve({'model':MODEL,'max_tokens':20});b.settle(key)
        self.assertEqual(before,self.state.snapshot('paid'))
        self.now[0]=1796083200.0
        with self.assertRaisesRegex(SpendHold,'NOT_PROVISIONED'):
            b.reserve({'model':MODEL,'max_tokens':20})
        provision(self.state,self.now[0]);self.assertEqual(b.status()['monthly_calls_used'],0)
    def test_rate_queue_spaces_dispatches_and_monthly_limit_is_atomic(self):
        b=self.budget();a=b.reserve({'model':MODEL,'max_tokens':20});before=self.now[0]
        c=b.reserve({'model':MODEL,'max_tokens':20});self.assertGreaterEqual(self.now[0]-before,1.5)
        b.settle(a);b.settle(c)
        with self.state.transaction() as db:self.state.sql(db,'UPDATE state_accounts SET opening=? WHERE identity=?',(998,account_for(self.now[0])))
        with self.assertRaisesRegex(SpendHold,'ALLOWANCE_EXHAUSTED'):b.reserve({'model':MODEL,'max_tokens':20})
    def test_third_concurrent_dispatch_waits_without_holding_connection(self):
        b=self.budget();a=b.reserve({'model':MODEL,'max_tokens':20});c=b.reserve({'model':MODEL,'max_tokens':20})
        def release(n):
            self.sleep(n);b.settle(a)
        b.sleep=release;third=b.reserve({'model':MODEL,'max_tokens':20})
        b.settle(c);b.settle(third)
        self.assertEqual(b.status()['monthly_calls_used'],3)
    def test_protocol_roundtrip_keeps_call_ids_arguments_usage_and_reasoning_state(self):
        raw=response();raw['choices'][0]['message']['reasoning_content']='synthetic opaque state'
        reply=response_for(raw,MODEL,TOOLS);self.assertEqual(reply.usage.budget_usage()['input_tokens'],16)
        request=request_for(model=MODEL,system='s',messages=[{'role':'assistant','content':reply.content},{'role':'user','content':[{'type':'tool_result','tool_use_id':'t1','content':'7'}]}],tools=TOOLS,max_tokens=50)
        self.assertEqual(request['messages'][1]['tool_calls'][0]['id'],'t1')
        self.assertEqual(request['messages'][1]['reasoning_content'],'synthetic opaque state')
        self.assertEqual(request['messages'][2]['tool_call_id'],'t1')
    def test_gateway_rejects_writes_server_tools_endpoint_and_model_substitution(self):
        spec={'endpoint':BASE,'models':[MODEL],'tools':['get_definition'],'synthetic_only':True,'quality_scope':'DEV_ONLY'};p={'ai_providers':{'nvidia':spec}}
        body=request_for(model=MODEL,system='s',messages=[],tools=TOOLS,max_tokens=50)
        authorize_body(p,'POST',BASE+'/chat/completions',body);authorize_body(p,'GET',BASE+'/models',None)
        for method,url,v in [('DELETE',BASE+'/models',None),('POST',BASE+'/batches',body),('POST',BASE+'/chat/completions',{**body,'model':'other'}),('POST',BASE+'/chat/completions',{**body,'tools':[{'type':'web_search'}]}),('POST',BASE+'/chat/completions',{**body,'stream':False})]:
            with self.subTest(url=url,method=method),self.assertRaises(ValueError):authorize_body(p,method,url,v)
        with self.assertRaises(ValueError):authorize_body({'ai_providers':{'nvidia':{**spec,'synthetic_only':False}}},'POST',BASE+'/chat/completions',body)
    def test_client_retries_429_same_model_accounts_each_attempt_and_never_auth_retries(self):
        send=Mock(side_effect=[ProviderError(429,2),response()]);events=[]
        with patch('investigator.adapters.managed_identity.validate_secret_reference'):
            c=Client(model=MODEL,budget=self.budget(),identity='test',secret_reference={},record=events.append,send=send,sleep=self.sleep,clock=lambda:self.now[0],jitter=lambda:0)
        out=c.complete(system='s',messages=[],tools=TOOLS,max_tokens=50)
        self.assertEqual(out['content'][0]['input'],{'id':7});self.assertEqual(c.budget.status()['monthly_calls_used'],2)
        self.assertEqual({x.args[2]['model'] for x in send.call_args_list},{MODEL})
        send.side_effect=ProviderError(401)
        with self.assertRaises(ProviderError):c.complete(system='s',messages=[],tools=TOOLS,max_tokens=50)
        self.assertEqual(send.call_count,3)
    def test_bad_native_tool_does_not_erase_known_usage(self):
        raw=response();raw['choices'][0]['message']['tool_calls'][0]['function']['name']='write_data'
        with patch('investigator.adapters.managed_identity.validate_secret_reference'):
            c=Client(model=MODEL,budget=self.budget(),identity='test',secret_reference={},record=Mock(),send=Mock(return_value=raw))
        with self.assertRaisesRegex(ValueError,'INVALID_TOOL'):c.complete(system='s',messages=[],tools=TOOLS,max_tokens=50)
        self.assertEqual(self.state.snapshot(account_for(self.now[0]))['reservations'][0]['status'],'SETTLED')
    def test_token_truncated_tool_json_is_incomplete_not_a_crash_or_executable_call(self):
        raw=response();raw['choices'][0]['finish_reason']='length'
        call=raw['choices'][0]['message']['tool_calls'][0]
        call['function'].update(name='evaluate_delivery',arguments='{"question":')
        from investigator.delivery_evaluator import evaluate
        from investigator.regression_features import configured
        events=[]
        with patch('investigator.adapters.managed_identity.validate_secret_reference'):
            model=Client(model=MODEL,budget=self.budget(),identity='test',secret_reference={},record=events.append,send=Mock(return_value=raw))
        with configured({'r27_slim_evaluator':True,'r27_evaluator_advisory':False}):
            result=evaluate(model,{'ticket':{},'draft':{},'cited_evidence':[]})
        self.assertEqual(result['format_error']['stop_reason'],'max_tokens')
        self.assertEqual(result['blocking_failures'],[])
        self.assertEqual(next(e['body']for e in events if e['event']=='REASONING_RESPONSE'),raw)
        self.assertEqual(self.state.snapshot(account_for(self.now[0]))['reservations'][0]['status'],'SETTLED')
        raw['choices'][0]['finish_reason']='tool_calls'
        with self.assertRaisesRegex(ValueError,'TOOL_JSON_REQUIRED'):
            response_for(raw,MODEL,[{'name':'evaluate_delivery'}])
    def test_development_configuration_is_mandatory_and_cannot_enter_quality_gate(self):
        config={'provider':'nvidia','endpoint':BASE,'model':MODEL,'rate_card':{},'secret_reference':{},'gateway_identity':'g','worker_identity':'round27-free-test','synthetic_only':True,'quality_scope':'DEV_ONLY'}
        self.assertEqual(validate(config),'nvidia')
        for changed in ({'synthetic_only':False},{'quality_scope':'GATE'},{'endpoint':'https://evil.test/v1'}):
            with self.assertRaises(ValueError):validate({**config,**changed})
        with self.assertRaisesRegex(ValueError,'NOT_A_QUALITY_GATE'):validate_graders(config,config,config,config)
        with self.assertRaises(ValueError):FreeRateCard(model=MODEL,input_rate=1,output_rate=0,source='https://build.nvidia.com',observed_at='2026-11-22')
    def test_prepared_gateway_covers_all_read_tools_and_preserves_estate_scopes(self):
        from investigator.nvidia_dev_profile import configuration, gateway
        from investigator.adapters.reasoning_nvidia import READ_TOOLS
        from investigator.live_gateway import Gateway
        reference={'vault_url':'https://kv-test.vault.azure.net','secret_name':'nvidia-api-key','secret_version':'a'*32,'identity':{}}
        prior={'version':1,'live_enabled':True,'identities':{'reasoning':{'role':'model','http':[]}}}
        config=configuration({'gateway_identity':'reasoning'},model=MODEL,discovered_models=[MODEL],secret_reference=reference)
        prepared=gateway(prior,config);self.assertEqual(prior['identities']['reasoning'],{'role':'model','http':[]})
        g=Gateway(prepared)
        # Exercise pure authorization only. No transport is installed here;
        # the suite-wide live kill switch has its own refusal assertion below.
        with patch.object(Gateway,'check_live',return_value=None):
            for name in READ_TOOLS:
                body=request_for(model=MODEL,system='Synthetic evidence',messages=[],tools=[{'name':name,'description':'Read only','input_schema':{'type':'object'}}],max_tokens=20)
                g.http('reasoning','POST',BASE+'/chat/completions',json.dumps(body).encode())
            bad=deepcopy(body);bad['tools'][0]['function']['name']='execute_write'
            prepared['identities']['reasoning']['ai_providers']['nvidia']['tools'].append('execute_write')
            rejected=Gateway(prepared)
            with self.assertRaisesRegex(Exception,'CONFIGURED_AI_REQUEST_REFUSED'):
                rejected.http('reasoning','POST',BASE+'/chat/completions',json.dumps(bad).encode())
        import os
        with patch.dict(os.environ,{'DIA_LIVE_ACCESS_DISABLED':'1'}),self.assertRaisesRegex(Exception,'LIVE_ACCESS_DISABLED'):
            Gateway(prepared).http('reasoning','POST',BASE+'/chat/completions',json.dumps(body).encode())
        with self.assertRaisesRegex(ValueError,'NOT_DISCOVERED'):
            configuration({'gateway_identity':'reasoning'},model='unlisted',discovered_models=[MODEL],secret_reference=reference)

if __name__=='__main__':unittest.main()

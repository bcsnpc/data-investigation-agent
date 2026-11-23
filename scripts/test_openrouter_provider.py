"""Synthetic offline quota, codec and gateway regressions. No generation."""
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from copy import deepcopy
from unittest.mock import patch, Mock
from investigator.shared_state import SharedState, encoded, sha
from investigator.nvidia_free_budget import FreeRateCard
from investigator.openrouter_budget import FreeBudget, PaidBudget, provision, account_for, PAID_ACCOUNT
from investigator.reasoning_budget import RateCard
from investigator.model_spend import SpendHold
from investigator.adapters.reasoning_openrouter import BASE, Client, request_for, response_for, authorize_body, READ_TOOLS
from investigator.openrouter_dev_profile import configuration, gateway
from investigator.adapters.provider_runtime import validate, validate_graders, client

MODEL='nvidia/nemotron-3.5-lightning:free'
TOOLS=[{'name':'get_definition','description':'Read synthetic definition','input_schema':{'type':'object'}}]


class OpenRouterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.state=SharedState.offline(Path(self.tmp.name)/'state.db');self.state.migrate()
        self.now=[1795392000.0];self.sleep=lambda n:self.now.__setitem__(0,self.now[0]+n)
        self.key={'limit':10,'limit_remaining':10,'limit_reset':'weekly','usage':0,'free_model_daily_requests':{'limit':1000,'used':0,'remaining':1000}}
        provision(self.state,self.now[0],self.key)
        self.rate=FreeRateCard(model=MODEL,input_rate=0,output_rate=0,source='https://openrouter.ai/api/v1/models',observed_at='2026-11-22')
        self.ref={'vault_url':'https://kv-test.vault.azure.net','secret_name':'openrouter-api-key','secret_version':'a'*32,'identity':{}}
        self.config=configuration({'gateway_identity':'reasoning'},model=MODEL,discovered_models=[{'id':MODEL,'pricing':{'prompt':'0','completion':'0'},'supported_parameters':['tools']}],secret_reference=self.ref)
        self.prior={'version':1,'live_enabled':True,'identities':{'reasoning':{'role':'model','http':[]},'reader':{'sql':[]}}}

    def budget(self):
        return FreeBudget(self.state,case_id='synthetic',owner='round27-free-test',rate=self.rate,clock=lambda:self.now[0],sleep=self.sleep)

    def body(self):return request_for(model=MODEL,system='Synthetic',messages=[],tools=TOOLS,max_tokens=100)

    def test_free_call_zero_dollars_unknown_attempt_charged_and_global_twenty_rpm(self):
        b=self.budget();k=b.reserve(self.body());b.settle(k,{'input_tokens':20,'output_tokens':3})
        at=self.now[0];q=b.reserve(self.body());self.assertGreaterEqual(self.now[0]-at,3);b.settle(q)
        totals=self.state.snapshot(account_for(self.now[0]))
        self.assertEqual(totals['charged'],'2');self.assertEqual(totals['unit'],'CALLS')
        self.assertCountEqual([r['status']for r in totals['reservations']],['SETTLED','UNCERTAIN'])
        self.assertEqual(b.status()['daily_call_allowance'],1000)
        self.assertEqual(self.state.totals(PAID_ACCOUNT)['charged'],'0')

    def test_key_daily_cap_used_and_day_rollover_require_new_verification(self):
        b=self.budget();account=account_for(self.now[0])
        with self.state.transaction() as db:self.state.sql(db,'UPDATE state_accounts SET opening=? WHERE identity=?',(1000,account))
        with self.assertRaises(SpendHold):b.reserve(self.body())
        self.now[0]+=86400
        with self.assertRaisesRegex(SpendHold,'FRESH_KEY_QUOTA'):b.reserve(self.body())
        provision(self.state,self.now[0],self.key)
        b.reserve(self.body())
        self.assertEqual(self.state.totals(account)['charged'],'1000')
        self.assertEqual(self.state.totals(account_for(self.now[0]))['charged'],'1')

    def test_pinned_model_and_zero_rates_required(self):
        b=self.budget()
        with self.assertRaises(SpendHold):b.reserve({**self.body(),'model':'paid/model'})
        with self.assertRaises(ValueError):FreeRateCard(model=MODEL,input_rate=1,output_rate=0,source='https://openrouter.ai',observed_at='now')

    def test_gateway_exact_endpoint_all_read_tools_and_no_write_no_fallback(self):
        prepared=gateway(self.prior,self.config)
        self.assertEqual(prepared['identities']['reader'],self.prior['identities']['reader'])
        spec=prepared['identities']['reasoning']
        for name in READ_TOOLS:
            body=request_for(model=MODEL,system='s',messages=[],tools=[{**TOOLS[0],'name':name}],max_tokens=20)
            authorize_body(spec,'POST',BASE+'/chat/completions',body)
        for changed in ({'models':['paid/model']},{'model':'paid/model'},{'provider':{'allow_fallbacks':True}}, {'tools':[{'type':'function','function':{'name':'execute_write','description':'write','parameters':{}}}]}):
            with self.subTest(change=changed),self.assertRaises(ValueError):authorize_body(spec,'POST',BASE+'/chat/completions',{**self.body(),**changed})
        for path in ('key','models'):authorize_body(spec,'GET',BASE+'/'+path,None)
        with self.assertRaises(ValueError):authorize_body(spec,'POST',BASE+'/keys',{})
        from investigator.live_gateway import Gateway
        with patch.object(Gateway,'check_live',return_value=None):Gateway(prepared).http('reasoning','POST',BASE+'/chat/completions',json.dumps(self.body()).encode())

    def test_synthetic_only_no_router_alias_no_gate(self):
        self.assertEqual(validate(self.config),'openrouter')
        for change in ({'synthetic_only':False},{'quality_scope':'GATE'},{'model':'openrouter/free'},{'endpoint':'https://other.test'}):
            with self.assertRaises(ValueError):validate({**self.config,**change})
        with self.assertRaisesRegex(ValueError,'NOT_A_QUALITY_GATE'):validate_graders(self.config,self.config,self.config,self.config)

    def test_normalized_reply_retains_native_and_opaque_state(self):
        native={'id':'r','model':MODEL,'choices':[{'finish_reason':'tool_calls','message':{'content':None,'reasoning_content':'opaque',
          'tool_calls':[{'id':'t','type':'function','function':{'name':'get_definition','arguments':'{"id":7}'}}]}}], 'usage':{'prompt_tokens':20,'completion_tokens':9}}
        events=[]
        with patch('investigator.adapters.managed_identity.validate_secret_reference'):
            c=client(self.config,budget=self.budget(),record=events.append,send=Mock(return_value=native),sleep=self.sleep)
        reply=c.complete(system='s',messages=[],tools=TOOLS,max_tokens=100)
        self.assertEqual(reply['provider'],'openrouter');self.assertEqual(reply['label'],'openrouter-free')
        self.assertEqual(next(e['body']for e in events if e['event']=='REASONING_RESPONSE'),native)
        body=request_for(model=MODEL,system='s',messages=[{'role':'assistant','content':reply['content']}],tools=TOOLS,max_tokens=100)
        self.assertEqual(body['messages'][1]['reasoning_content'],'opaque')
        self.assertEqual(reply['cost_microdollars'],0)

    def failed_free_receipt(self):
        receipt={'discovered_free_tool_models':[MODEL],'results':[{'model':MODEL,'status':'FAILED','capture_sha256':'a'*64}]}
        with self.state.transaction() as db:self.state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',('openrouter-qualification','all-free-tool-tests',0,encoded(receipt),sha(receipt)))

    def test_paid_blocked_before_free_failures_and_lifetime_cap_never_resets(self):
        rate=RateCard(model='test/paid',input_rate=1,output_rate=1,source='https://openrouter.ai/api/v1/models',observed_at='now')
        b=PaidBudget(self.state,case_id='synthetic',owner='round27-free-test',rate=rate,actual_usage_limit=3000000,clock=lambda:self.now[0],sleep=self.sleep)
        body={**self.body(),'model':'test/paid'}
        with self.assertRaisesRegex(SpendHold,'ALL_FREE_TOOL_TESTS_FAILED'):b.reserve(body)
        self.failed_free_receipt()
        k=b.reserve(body);b.settle(k,{'input_tokens':20,'output_tokens':9})
        self.assertEqual(self.state.totals(PAID_ACCOUNT)['charged'],'29')
        with self.state.transaction() as db:self.state.sql(db,'UPDATE state_accounts SET opening=? WHERE identity=?',(10000000,PAID_ACCOUNT))
        for days in (0,7,30):
            self.now[0]+=days*86400
            with self.assertRaises(SpendHold):b.reserve(body)

    def test_remote_weekly_reset_cannot_erase_lifetime_spend(self):
        self.failed_free_receipt()
        provision(self.state,self.now[0],{**self.key,'usage':10,'limit_remaining':10})
        rate=RateCard(model='test/paid',input_rate=1,output_rate=1,source='https://openrouter.ai/api/v1/models',observed_at='now')
        b=PaidBudget(self.state,case_id='s',owner='round27-free-test',rate=rate,clock=lambda:self.now[0],sleep=self.sleep)
        with self.assertRaisesRegex(SpendHold,'LIFETIME_CREDIT_EXHAUSTED'):b.reserve({**self.body(),'model':'test/paid'})

    def test_free_response_cannot_charge_and_silently_execute_a_tool(self):
        native={'id':'r','model':MODEL,'choices':[{'finish_reason':'stop','message':{'content':'OK'}}],
                'usage':{'prompt_tokens':20,'completion_tokens':9,'cost':.01}}
        with patch('investigator.adapters.managed_identity.validate_secret_reference'):
            c=client(self.config,budget=self.budget(),record=Mock(),send=Mock(return_value=native),sleep=self.sleep)
        with self.assertRaisesRegex(SpendHold,'NONZERO_COST'):c.complete(system='s',messages=[],tools=TOOLS,max_tokens=100)
        self.assertEqual(self.state.snapshot(account_for(self.now[0]))['reservations'][0]['status'],'UNCERTAIN')


if __name__=='__main__':unittest.main()

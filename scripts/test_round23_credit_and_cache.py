import copy,json,tempfile,unittest,time
from pathlib import Path
from datetime import datetime,timezone
from investigator.shared_state import SharedState,StateConflict
from investigator.enrichment_job import EnrichmentSpendBudget
from investigator.anthropic_credit import status
from investigator.adapters.anthropic_prompt_cache import StablePrefix,assert_cache_reads
from investigator.adapters.reasoning_anthropic import authorize_body
from investigator.build_phase import model_ceiling


class CreditTests(unittest.TestCase):
 def test_both_account_limits_protect_grading_and_bound_combined_spend(self):
  with tempfile.TemporaryDirectory()as folder:
   state=SharedState.offline(Path(folder)/'state.sqlite');state.migrate()
   with state.transaction()as db:
    db.execute('INSERT INTO state_accounts VALUES(?,?,?,?,?,?)',('model','MICRODOLLARS',96000000,13000000,70000000,0))
    db.execute('INSERT INTO state_accounts VALUES(?,?,?,?,?,?)',('enrichment:round-twenty-one','MICRODOLLARS',25000000,12000000,10000000,0))
   month=datetime.now(timezone.utc).strftime('%Y-%m')
   policy={'approval':'owner-approved 2026-10-27','model_account':'model','grading_account':'enrichment:round-twenty-one','grading_account_protected':12000000,'baseline_model_charged':70000000,'baseline_grading_charged':10000000,'baseline_higher_microdollars':80000000,'normalized_ceiling_microdollars':96000000,'protected_grading_microdollars':3000000}
   state.put('anthropic_credit',month,policy)
   budget=EnrichmentSpendBudget(state,owner='grader',price=lambda i,o:1)
   self.assertEqual(status(state)['remaining_microdollars'],16000000)
   state.reserve('model','m','worker',13000000)
   with self.assertRaises(StateConflict):state.reserve('model','too-much','worker',1)
   state.reserve(budget.account,'g','grader',3000000)
   with self.assertRaises(StateConflict):state.reserve(budget.account,'too-much','grader',1)
   self.assertEqual(status(state)['charged_microdollars'],96000000)
   self.assertEqual(status(state)['remaining_microdollars'],0)
 def test_october_ceiling_does_not_lower_november(self):
  at=lambda x:datetime.fromisoformat(x).replace(tzinfo=timezone.utc).timestamp()
  self.assertEqual(model_ceiling(at('2026-10-28')),96000000)
  self.assertEqual(model_ceiling(at('2026-11-01')),150000000)


class CacheTests(unittest.TestCase):
 def body(self):
  return {'model':'claude-opus-5-5','max_tokens':4000,'system':[{'type':'text','text':'instructions; retained path, schemas, DAX, definitions and triage','cache_control':{'type':'ephemeral'}}],
    'tools':[{'name':'get_lineage','description':'Read path','input_schema':{'type':'object','properties':{'node':{'type':'string'}}}}],
    'messages':[{'role':'user','content':'current counter 1, evidence IDs and results'}]}
 def test_prefix_byte_identical_while_timestamp_ids_tools_and_results_change(self):
  cache=StablePrefix();first=self.body();a=cache.prepare(first);second=self.body();second['messages'][0]['content']='counter 2; fresh timestamp; evidence X';second['tools'][0]['input_schema']['properties']['node']['enum']=['new-id'];second['system'][0]['text']+=' new observed timestamp'
  b=cache.prepare(second)
  self.assertEqual(json.dumps([a['tools'],a['system']],sort_keys=True),json.dumps([b['tools'],b['system']],sort_keys=True))
  self.assertNotEqual(a['messages'],b['messages']);self.assertIn('new observed timestamp',b['messages'][-1]['content']);self.assertIn('new-id',b['messages'][-1]['content'])
  self.assertEqual(a['tools'][-1]['cache_control'],{'type':'ephemeral'})
  self.assertNotIn('current_admitted_tools',a['messages'][-1]['content'])
 def test_second_call_zero_cache_reads_fails_the_cache_assertion(self):
  cache=StablePrefix();cache.prepare(self.body());records=[cache.observe({'cache_creation_input_tokens':2048}),cache.observe({'input_tokens':2048,'cache_read_input_tokens':0})]
  with self.assertRaisesRegex(AssertionError,'ZERO_CACHE_READS'):assert_cache_reads(records)
 def test_subsequent_cache_reads_and_ratio_use_native_counts(self):
  cache=StablePrefix();cache.prepare(self.body());a=cache.observe({'input_tokens':100,'cache_creation_input_tokens':2048});b=cache.observe({'input_tokens':200,'cache_read_input_tokens':2048});assert_cache_reads([a,b])
  self.assertEqual(b['total_input_tokens'],2248);self.assertEqual(b['cache_read_input_tokens'],2048)
 def test_cached_diagnostic_preserves_changing_screenshot_helper_requests(self):
  from unittest.mock import Mock,patch
  from investigator.adapters.reasoning_anthropic import Client
  budget=Mock();budget.rate.model='claude-opus-5-5';budget.reserve.return_value='r'
  send=Mock(return_value={'content':[],'usage':{'input_tokens':100,'output_tokens':1}});record=Mock()
  with patch('investigator.adapters.managed_identity.validate_secret_reference'):
   client=Client(model='claude-opus-5-5',budget=budget,identity='reader',secret_reference={},record=record,send=send,diagnostic_prompt_cache=True)
  for name in ('describe_screenshot','plan_screenshot_lookup'):
   tools=[{'name':name,'description':'Use this named helper','input_schema':{'type':'object','properties':{}}}]
   client.complete(system='helper instructions',messages=[],tools=tools)
   body=send.call_args.args[2]
   self.assertEqual(body['tools'],tools);self.assertEqual(body['system'][0]['text'],'helper instructions')
  events=[x.args[0]for x in record.call_args_list if x.args[0].get('event')=='REASONING_CACHE_USAGE']
  self.assertEqual(len(events),2);self.assertTrue(all(x['phase']=='INTAKE_HELPER_UNCHANGED'for x in events));assert_cache_reads(events)
 def test_investigation_cache_check_still_rejects_later_misses(self):
  with self.assertRaisesRegex(AssertionError,'ZERO_CACHE_READS'):
   assert_cache_reads([{'successful_call':2,'cache_read_input_tokens':0,'cache_assertion_applies':True}])
 def test_gateway_tool_breakpoint_requires_explicit_diagnostic_permission(self):
  cache=StablePrefix();body=cache.prepare(self.body());permissions={'reasoning_models':['claude-opus-5-5']}
  with self.assertRaises(ValueError):authorize_body(permissions,'POST','https://api.anthropic.com/v1/messages',body)
  permissions['diagnostic_prompt_cache']=True;self.assertEqual(authorize_body(permissions,'POST','https://api.anthropic.com/v1/messages',body),body)
  broken=copy.deepcopy(body);broken['tools'][0]['cache_control']={'type':'ephemeral'}
  with self.assertRaises(ValueError):authorize_body(permissions,'POST','https://api.anthropic.com/v1/messages',broken)

if __name__=='__main__':unittest.main()

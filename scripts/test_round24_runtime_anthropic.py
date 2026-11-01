"""Structured calls use only the configured provider and Key Vault reference."""
import ast,json,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from investigator.adapters import runtime_anthropic as runtime
class RuntimeTests(unittest.TestCase):
 def test_ticket_identity_survives_nested_calls_with_sidecar_recording_disabled(self):
  from investigator.planner_recording import recording,SESSION,ACTIVE
  with patch.dict('os.environ',{'INVESTIGATOR_RECORD_PLANNER':'0'}):
   with recording({'session_id':'intake:one'}):
    self.assertIsNone(ACTIVE.get());self.assertEqual(SESSION.get(),'intake:one')
    with recording({'session_id':'standalone:inner'}):self.assertEqual(SESSION.get(),'intake:one')
   self.assertIsNone(SESSION.get())
 def test_legacy_named_entry_point_uses_anthropic_and_never_azure_sdk(self):
  from ticket_planner import _azure_generate
  client=Mock();client.model='claude-opus-5-5';client.complete.return_value={'id':'response','content':[{'type':'tool_use','name':'resolve_intake','input':{'answer':'value'}}],'usage':{'input_tokens':1,'output_tokens':1}}
  token=runtime.CLIENT.set(client)
  try:
   with patch.dict('os.environ',{},clear=True):
    value,meta=_azure_generate({'input':'test'},schema={'type':'object'})
   self.assertEqual(value,{'answer':'value'});self.assertEqual(meta['model'],'claude-opus-5-5')
   self.assertEqual(client.complete.call_args.kwargs['tools'][0]['name'],'resolve_intake')
  finally:runtime.CLIENT.reset(token)
 def test_structured_entry_uses_only_the_explicitly_configured_provider(self):
  configuration={'provider':'openai','model':'synthetic','rate_card':{'input_rate':'1','output_rate':'2','source':'https://example.test/pricing','observed_at':'2026-11-01'},'secret_reference':{},'gateway_identity':'model','worker_identity':'worker'}
  expected=Mock()
  with patch.dict('os.environ',{'DIA_RUNTIME_AI_JSON':json.dumps(configuration),'DIA_RUN_ID':'synthetic-case'},clear=True),patch.object(runtime,'configured_state',return_value=Mock()),patch.object(runtime,'TicketBudget')as budget,patch('investigator.adapters.provider_runtime.client',return_value=expected)as factory:
   self.assertIs(runtime.installed_client(),expected)
   self.assertEqual(budget.call_args.kwargs['provider'],'openai')
   self.assertEqual(factory.call_args.args[0],configuration)
 def test_key_vault_configuration_required_no_environment_azure_key_fallback(self):
  with patch.dict('os.environ',{'AZURE_OPENAI_API_KEY':'synthetic-unused'},clear=True),self.assertRaises(KeyError):runtime.installed_client()
if __name__=='__main__':unittest.main()


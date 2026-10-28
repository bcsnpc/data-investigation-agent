"""Current structured entry points have no Azure transport or secret fallback."""
import ast,json,unittest
from pathlib import Path
from unittest.mock import Mock,patch
from investigator.adapters import runtime_anthropic as runtime
class RuntimeTests(unittest.TestCase):
 def test_legacy_named_entry_point_uses_anthropic_and_never_azure_sdk(self):
  from ticket_planner import _azure_generate
  client=Mock();client.model='claude-opus-5-5';client.complete.return_value={'id':'response','content':[{'type':'tool_use','name':'resolve_intake','input':{'answer':'value'}}],'usage':{'input_tokens':1,'output_tokens':1}}
  token=runtime.CLIENT.set(client)
  try:
   with patch('ticket_planner.provider_body',return_value={'model':'old-id'}),patch.dict('os.environ',{},clear=True):
    value,meta=_azure_generate({'input':'test'},schema={'type':'object'})
   self.assertEqual(value,{'answer':'value'});self.assertEqual(meta['model'],'claude-opus-5-5')
   self.assertEqual(client.complete.call_args.kwargs['tools'][0]['name'],'resolve_intake')
  finally:runtime.CLIENT.reset(token)
 def test_production_source_has_no_azure_openai_constructor(self):
  for path in Path('scripts').rglob('*.py'):
   if path.name.startswith('test_')or 'fixtures'in path.parts:continue
   tree=ast.parse(path.read_text(encoding='utf-8-sig'))
   for node in ast.walk(tree):
    if isinstance(node,ast.Call):
     name=node.func.id if isinstance(node.func,ast.Name)else node.func.attr if isinstance(node.func,ast.Attribute)else ''
     self.assertNotIn(name,('OpenAI','AzureOpenAI'),str(path))
 def test_key_vault_configuration_required_no_environment_azure_key_fallback(self):
  with patch.dict('os.environ',{'AZURE_OPENAI_API_KEY':'synthetic-unused'},clear=True),self.assertRaises(KeyError):runtime.installed_client()
if __name__=='__main__':unittest.main()


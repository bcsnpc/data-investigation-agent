"""Offline config ablations; no provider/estate calls, identity or budget changes."""
from copy import deepcopy
from unittest.mock import Mock,patch
from types import SimpleNamespace
from pathlib import Path
import ast,json,unittest
from investigator.regression_features import DEFAULTS,enabled,configured,snapshot,validate,baseline_prompt

class FeatureTests(unittest.TestCase):
 def test_each_flag_is_independent_scoped_and_defaults_to_current(self):
  self.assertEqual(len(DEFAULTS),55)
  self.assertFalse(DEFAULTS['r27_evaluator_advisory'])
  for name in DEFAULTS:
   with self.subTest(feature=name),configured({name:not DEFAULTS[name]}):
    self.assertEqual(enabled(name),not DEFAULTS[name])
    self.assertEqual({k:v for k,v in snapshot().items()if k!=name},{k:v for k,v in DEFAULTS.items()if k!=name})
   self.assertEqual(enabled(name),DEFAULTS[name])
 def test_nested_and_exception_scopes_restore_without_leaking(self):
  with configured({'r27_delivery_evaluator':False}):
   try:
    with configured({'r26_terminal_report':False}):
     self.assertTrue(enabled('r27_delivery_evaluator'));raise RuntimeError('test')
   except RuntimeError:pass
   self.assertFalse(enabled('r27_delivery_evaluator'));self.assertTrue(enabled('r26_terminal_report'))
  self.assertEqual(snapshot(),DEFAULTS)
 def test_unknown_safety_and_nonboolean_options_are_refused(self):
  for value in ({'read_only':False},{'budget':False},{'r27_delivery_evaluator':0},{'r27_delivery_evaluator':'false'},[]):
   with self.assertRaises(ValueError):validate(value)
 def test_every_registered_feature_has_a_real_code_hook(self):
  used=set()
  for path in Path(__file__).parent.rglob('*.py'):
   if path.name.startswith('test_'):continue
   for call in ast.walk(ast.parse(path.read_text(encoding='utf-8-sig'))):
    if isinstance(call,ast.Call)and isinstance(call.func,ast.Name)and call.func.id=='enabled'and call.args and isinstance(call.args[0],ast.Constant):used.add(call.args[0].value)
  self.assertEqual(set(DEFAULTS)-used,set())
 def test_root_runner_uses_trusted_spec_and_resets_after_call(self):
  import cloud_guided_investigator as runner
  with patch.object(runner,'specification',return_value={'regression_flags':{'r27_delivery_evaluator':False}}),patch.object(runner,'_run',side_effect=lambda *a:snapshot()):
   result=runner.run({'options':{}},None)
  self.assertFalse(result['r27_delivery_evaluator']);self.assertTrue(enabled('r27_delivery_evaluator'))
 def test_intake_model_route_flag_does_not_change_identity_or_input(self):
  from investigator.adapters.provider_runtime import intake_selection
  from test_intake_model_routing import config
  routing={'steps':{'INTAKE':config('configured'),'INVESTIGATOR':config('reasoning')}};before=deepcopy(routing)
  with configured({'r27_reasoning_model_intake':False}):self.assertEqual(intake_selection(routing,tenant='x')['model'],'configured')
  self.assertEqual(intake_selection(routing,tenant='x')['model'],'reasoning');self.assertEqual(routing,before)
 def test_auxiliary_model_roles_switch_independently(self):
  from investigator.adapters.provider_runtime import auxiliary_selection
  from test_intake_model_routing import config
  routing={'steps':{'INVESTIGATOR':config('reasoning'),**{name:config(name.lower())for name in ('SCREENSHOT','SUMMARY','EVALUATOR')}}};before=deepcopy(routing)
  for role in ('SCREENSHOT','SUMMARY','EVALUATOR'):
   self.assertEqual(auxiliary_selection(routing,tenant='x',step=role)['model'],'reasoning')
   with configured({'r27_reasoning_model_'+role.lower():False}):
    self.assertEqual(auxiliary_selection(routing,tenant='x',step=role)['model'],role.lower())
    for other in ('SCREENSHOT','SUMMARY','EVALUATOR'):
     if other!=role:self.assertEqual(auxiliary_selection(routing,tenant='x',step=other)['model'],'reasoning')
  self.assertEqual(routing,before)
 def test_evaluator_disabled_still_requires_code_validation(self):
  from investigator.ai_investigation import Investigator
  loop=object.__new__(Investigator);loop.refresh_tools=lambda:None;loop.schemas={'submit_finding':Mock()};loop.context={'conclusion_contract':'question-first-v1'};loop.state={'evidence':{},'outcome':None};loop.queries=SimpleNamespace(records=[]);loop.case_view=Mock(return_value={});loop.validate_finding=Mock(return_value={'business':'grounded','technical':{}});loop.evaluate_draft=Mock(side_effect=AssertionError('must not call a model'))
  conclusion={'direct_answer':'Grounded','context_gap':{'type':'other','note':'none'}}
  with configured({'r27_delivery_evaluator':False}),patch('investigator.conclusion_contract.validate',return_value=conclusion),patch('investigator.conclusion_contract.render',return_value='Grounded'):
   loop.dispatch('submit_finding',{'evidence_ids':[]})
  loop.validate_finding.assert_called_once();loop.evaluate_draft.assert_not_called();self.assertEqual(loop.state['outcome']['status'],'ANSWERED')
 def test_evaluator_repair_has_its_own_output_limit(self):
  from investigator.delivery_evaluator import evaluate
  model=Mock();model.complete.return_value={'content':[],'stop_reason':'max_tokens'}
  with configured({'r27_evaluator_format_repair':False}):result=evaluate(model,{})
  self.assertEqual(model.complete.call_args.kwargs['max_tokens'],1600);self.assertIsNone(result['format_error']);self.assertFalse(result['approved'])
  evaluate(model,{});self.assertEqual(model.complete.call_args.kwargs['max_tokens'],3200)
 def test_identifier_hint_switch_removes_hints_but_preserves_enums(self):
  from investigator.ai_investigation import toolbox
  layers={'native':{'dialect':'T-SQL'}}
  original=toolbox(layers,{})
  with configured({'r27_identifier_role_descriptions':False}):changed=toolbox(layers,{})
  old=next(t for t in original if t['name']=='run_sql')['input_schema']['properties']['layer']
  new=next(t for t in changed if t['name']=='run_sql')['input_schema']['properties']['layer']
  self.assertIn('description',old);self.assertNotIn('description',new);self.assertEqual(old['enum'],new['enum'])
 def test_optional_analysis_tools_disable_separately(self):
  from investigator.investigation_read_tools import ReadTools
  tools=object.__new__(ReadTools);tools.visible={'node'};tools.nodes={'node':{'kind':'TABLE'}};tools.queries=SimpleNamespace(layers={'native':{}});tools.target_inventory=None
  with configured({'r27_contribution_tool':False}):self.assertNotIn('contribution_analysis',tools.registry());self.assertIn('row_layer_diff',tools.registry())
  with configured({'r27_row_diff_tool':False}):self.assertNotIn('row_layer_diff',tools.registry());self.assertIn('contribution_analysis',tools.registry())
 def test_metadata_off_never_disables_read_only_or_object_checks(self):
  from investigator.investigative_queries import validate as query
  from test_round23_intake_queries import sql_objects
  layer={'dialect':'T-SQL','objects':sql_objects()}
  for on in (False,True):
   with configured({'r26_metadata_reads':on,'r27_metadata_gateway_revalidation':on}):
    for text in ('DELETE FROM dbo.Items','EXEC dangerous','SELECT * FROM dbo.NotAdmitted'):
     with self.assertRaises(Exception):query(text,layer)
  with configured({'r26_metadata_reads':False}):
   with self.assertRaises(Exception):query('SELECT name FROM sys.tables',layer)
 def test_temporal_extensions_switch_preserves_original_asof(self):
  from sqlglot import parse_one,exp
  from investigator.query_sql import temporal_read
  between=next(parse_one("SELECT * FROM dbo.Items FOR SYSTEM_TIME BETWEEN '2026-01-01' AND '2026-01-02'",read='tsql').find_all(exp.Version))
  asof=next(parse_one("SELECT * FROM dbo.Items FOR SYSTEM_TIME AS OF '2026-01-01'",read='tsql').find_all(exp.Version))
  with configured({'r26_temporal_extensions':False}):self.assertFalse(temporal_read(between));self.assertTrue(temporal_read(asof))
  self.assertTrue(temporal_read(between))
 def test_terminal_report_off_preserves_original_result_without_inventing_status(self):
  from investigator.terminal_findings import attach
  original={'status':'BLOCKED','business':'Unavailable','stop':'read failed'}
  with configured({'r26_terminal_report':False}):self.assertEqual(attach(original),original)
 def test_source_deferral_off_is_strict_admission(self):
  from investigator.guided_intake import admit_investigation_candidate,Catalog
  from test_round23_intake_queries import graph,request
  value=request();value['compared_with']={'kind':'SOURCE_SYSTEM','source':'the application rows'}
  with configured({'r27_source_label_deferral':False}):
   with self.assertRaisesRegex(ValueError,'SOURCE_NAME_UNRESOLVED'):admit_investigation_candidate(value,Catalog(graph()))
 def test_terminal_report_off_finishes_an_unresolved_case(self):
  from investigator.ai_investigation import Investigator
  loop=object.__new__(Investigator);loop.context={'conclusion_contract':'question-first-v1'};loop.state={'outcome':{'status':'UNRESOLVED','business':'Not established'},'model_calls':0,'tools_used':0};loop.queries=SimpleNamespace(records=[],layers={});loop.model_seconds=0;loop.save=Mock();loop.case_view=Mock(return_value={});loop.evaluate_draft=Mock(side_effect=AssertionError('no report to evaluate'))
  with configured({'r26_terminal_report':False}):result=loop.finish()
  self.assertEqual(result['status'],'UNRESOLVED');self.assertEqual(result['handoff']['investigation_report'],{});loop.evaluate_draft.assert_not_called()
 def test_legacy_contract_still_requires_unresolved_when_no_candidate_wins(self):
  from investigator.ai_investigation import Investigator
  loop=object.__new__(Investigator);loop.refresh_tools=lambda:None;loop.schemas={'submit_finding':Mock()};loop.context={'candidate_inventory':{'candidates':[]}};loop.state={'evidence':{'check':{'tool':'check_target_candidates','result':{'selected':None}}},'outcome':None};loop.queries=SimpleNamespace(records=[]);loop.case_view=Mock(return_value={});loop.validate_finding=Mock(return_value={'business':'All candidates checked; cannot distinguish them.'})
  loop.dispatch('submit_finding',{'evidence_ids':['check'],'selected_target':None,'verdict':'not found'})
  self.assertEqual(loop.state['outcome']['target_resolution']['selected'],None)
  with self.assertRaisesRegex(ValueError,'UNSELECTED_TARGET'):
   loop.dispatch('submit_finding',{'evidence_ids':['check'],'selected_target':None,'verdict':'as designed'})
 def test_baseline_prompt_is_retained_text_only(self):
  for key in ('intake','investigator'):
   text=baseline_prompt(key);self.assertIsInstance(text,str);self.assertGreater(len(text),100)

if __name__=='__main__':unittest.main()

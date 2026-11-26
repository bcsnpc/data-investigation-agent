"""Only evaluator experiments remain configurable; retired fixes are unconditional."""
from pathlib import Path
from unittest.mock import patch
import ast,unittest
from investigator.regression_features import DEFAULTS,RETIRED,enabled,configured,snapshot,validate
class FeatureTests(unittest.TestCase):
 def test_only_measured_evaluator_modes_are_flags(self):
  self.assertEqual(set(DEFAULTS),{'r27_evaluator_advisory','r27_slim_evaluator','r27_delivery_evaluator'})
  self.assertEqual(len(RETIRED),61)
  for name in DEFAULTS:
   with configured({name:not DEFAULTS[name]}):self.assertEqual(enabled(name),not DEFAULTS[name])
   self.assertEqual(snapshot(),DEFAULTS)
 def test_historical_default_specs_are_noops_and_off_ablations_are_refused(self):
  self.assertEqual(validate(RETIRED),DEFAULTS)
  for name in RETIRED:
   with self.assertRaisesRegex(ValueError,'RETIRED_REGRESSION_ABLATION'):validate({name:False})
 def test_nested_scope_and_exceptions_reset(self):
  with configured({'r27_delivery_evaluator':False}):
   with self.assertRaises(RuntimeError):
    with configured({'r27_slim_evaluator':True}):raise RuntimeError('test')
   self.assertFalse(enabled('r27_delivery_evaluator'))
  self.assertEqual(snapshot(),DEFAULTS)
 def test_no_safety_budget_identity_or_unknown_switch(self):
  for value in ({'read_only':False},{'budget':False},{'identity':False},{'r27_delivery_evaluator':0},[]):
   with self.assertRaises(ValueError):validate(value)
 def test_retired_switches_have_no_runtime_hooks(self):
  for path in (Path(__file__).parent/'investigator').rglob('*.py'):
   for call in ast.walk(ast.parse(path.read_text(encoding='utf-8-sig'))):
    if isinstance(call,ast.Call)and isinstance(call.func,ast.Name)and call.func.id=='enabled'and call.args and isinstance(call.args[0],ast.Constant):self.assertIn(call.args[0].value,DEFAULTS,str(path))
 def test_root_runner_resets_flag_context(self):
  import cloud_guided_investigator as runner
  with patch.object(runner,'specification',return_value={'regression_flags':{'r27_delivery_evaluator':False}}),patch.object(runner,'_run',side_effect=lambda *a:snapshot()):result=runner.run({'options':{}},None)
  self.assertFalse(result['r27_delivery_evaluator']);self.assertEqual(snapshot(),DEFAULTS)
if __name__=='__main__':unittest.main()

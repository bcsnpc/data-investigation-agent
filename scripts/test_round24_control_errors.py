import unittest,subprocess,json
from unittest.mock import Mock,patch
from types import SimpleNamespace
from pathlib import Path
from investigator.adapters.runner_deployment import launch
from investigator.adapters.investigator_harness_user import AzureCLIUser
import test_runner_prepare as prepare_fixtures
from investigator.runner_prepare import probe_plan
class ControlTests(unittest.TestCase):
 def test_unconfirmed_start_keeps_native_error_and_bound_run_without_retry(self):
  inputs=prepare_fixtures.PrepareTests().inputs();config=probe_plan(*inputs,image='registry/worker@sha256:'+'a'*64,run_id='run',cli=['az'],budget_environment='budget')
  for message,safe in [('ERROR: (BadGateway) native refusal','BadGateway'),('password=synthetic-secret-value','REDACTED_UNSAFE_PROVIDER_ERROR')]:
   execute=Mock(side_effect=[SimpleNamespace(stdout=json.dumps(inputs[0])),subprocess.CalledProcessError(1,['az'],stderr=message)])
   with patch('investigator.build_phase.admit_platform'),self.assertRaisesRegex(RuntimeError,'AZURE_JOB_START_UNESTABLISHED.*run_id=run.*'+safe):launch(config,'bronze',execute=execute)
   self.assertEqual(execute.call_count,2)
 def test_guided_ticket_does_not_repeat_whole_estate_audit_but_smoke_does(self):
  import tempfile
  import test_unified_runner as fixtures
  from investigator.unified_runner import run
  with tempfile.TemporaryDirectory()as folder:
   config=fixtures.RunnerTests().config(Path(folder));config['checks']={'answer':{'kind':'guided-investigation','options':{}}}
   def guarded_read(plan,ctx):
    self.assertEqual(ctx.access_result['status'],'NOT_RUN')
    from investigator.live_gateway import GatewayDenied
    raise GatewayDenied('READ_ONLY_GATEWAY_STILL_ENFORCED')
   with patch('investigator.access_check.configured')as audit:
    with self.assertRaisesRegex(Exception,'READ_ONLY_GATEWAY_STILL_ENFORCED'):
     run(config,'answer',registry={'guided-investigation':guarded_read},put=lambda *_:None)
    audit.assert_not_called()
  with tempfile.TemporaryDirectory()as folder:
   config=fixtures.RunnerTests().config(Path(folder));config['checks']={'health':{'kind':'smoke','options':{}}}
   with patch('investigator.access_check.configured',return_value={'status':'PASS','rows':[]})as audit:
    run(config,'health',registry={'smoke':lambda *_:{'status':'PASS'}},put=lambda *_:None)
    audit.assert_called_once()
 def test_bad_gateway_read_is_retried_but_a_start_is_not(self):
  user=AzureCLIUser.__new__(AzureCLIUser);user.cli=['az'];user.control=Mock()
  error=subprocess.CalledProcessError(1,['az'],stderr='BadGateway')
  user.execute=Mock(side_effect=[error,SimpleNamespace(stdout='{"status":"Running"}')])
  with patch('time.sleep')as wait:self.assertEqual(user._json(['az','containerapp','job','execution','show'])['status'],'Running')
  self.assertEqual(user.execute.call_count,2);wait.assert_called_once_with(5)
  user.execute=Mock(side_effect=error)
  with self.assertRaises(subprocess.CalledProcessError):user._json(['az','containerapp','job','start'])
  self.assertEqual(user.execute.call_count,1)
if __name__=='__main__':unittest.main()

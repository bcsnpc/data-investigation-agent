import subprocess,unittest
from unittest.mock import Mock
from investigator.adapters.runner_deployment import read_job
class Tests(unittest.TestCase):
 def test_connection_reset_retries_only_the_same_prestart_get(self):
  args=['az','containerapp','job','show','--ids','existing'];error=subprocess.CalledProcessError(1,args,stderr='Connection broken: ConnectionResetError(10054)');execute=Mock(side_effect=[error,subprocess.CompletedProcess(args,0,'{}','')]);sleep=Mock();result=read_job(execute,args,sleep=sleep);self.assertEqual(result.stdout,'{}');self.assertEqual(execute.call_count,2);self.assertTrue(all(call.args[0]==args for call in execute.call_args_list));sleep.assert_called_once_with(5)
 def test_authorization_is_not_treated_as_transient(self):
  args=['az','containerapp','job','show'];execute=Mock(side_effect=subprocess.CalledProcessError(1,args,stderr='AuthorizationFailed HTTP403'))
  with self.assertRaisesRegex(RuntimeError,'BEFORE_START'):read_job(execute,args,sleep=Mock())
  self.assertEqual(execute.call_count,1)

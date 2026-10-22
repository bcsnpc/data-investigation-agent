import subprocess
import unittest
from investigator.adapters.control_failure import execute_checked,ControlCommandFailure

class ControlFailureTests(unittest.TestCase):
    def test_secret_stderr_is_redacted_while_safe_stdout_survives(self):
        secret='sk-'+'a'*60
        def execute(argv,**kwargs):raise subprocess.CalledProcessError(1,argv,output='safe stdout\n',stderr='Authorization: Bearer '+secret)
        with self.assertRaises(ControlCommandFailure)as caught:execute_checked(execute,['az','rest'],operation='test',check=True)
        receipt=caught.exception.receipt
        self.assertEqual(receipt['stdout'],'safe stdout\n')
        self.assertTrue(receipt['stderr_redacted'])
        self.assertNotIn(secret,str(receipt))
    def test_show_failure_is_preserved_without_attempting_patch(self):
        calls=[]
        def execute(argv,**kwargs):calls.append(argv);raise subprocess.CalledProcessError(2,argv,stderr='ERROR: please sign in\n')
        with self.assertRaises(ControlCommandFailure)as caught:execute_checked(execute,['az','show'],operation='schedule-show')
        self.assertEqual(caught.exception.receipt['returncode'],2)
        self.assertEqual(caught.exception.receipt['stderr'],'ERROR: please sign in\n')
        self.assertEqual(len(calls),1)

if __name__=='__main__':unittest.main()

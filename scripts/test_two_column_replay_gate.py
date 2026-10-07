import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('two_columns',Path(__file__).resolve().parents[1]/'acceptance/known_domain/two_columns.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)


class TwoColumnReplayGateTests(unittest.TestCase):
    def test_both_columns_run_all_fifteen_and_a_missing_inferred_case_fails(self):
        for missing in (False,True):
            calls=[]
            def replay(case,root,output,*,mechanism_root=None):
                self.assertEqual(mechanism_root,Path('supersessions'))
                calls.append((str(root),case['ticket']))
                return {'ticket':case['ticket'],'status':'BLOCKED' if missing and str(root)=='inferred' and len(calls)==30 else 'PASSED','physical_requests':0,'network_calls':0}
            with tempfile.TemporaryDirectory() as d,patch.object(gate,'run_case',side_effect=replay),contextlib.redirect_stdout(io.StringIO()):
                code=gate.run('archived','inferred',Path(d)/'out',mechanism_root=Path('supersessions'))
                self.assertEqual(code,1 if missing else 0)
                self.assertEqual(len(calls),30)
                self.assertEqual(len({c for root,c in calls if root=='archived'}),15)
                self.assertEqual(len({c for root,c in calls if root=='inferred'}),15)

    def test_answer_change_requires_a_changed_reason_in_the_same_change(self):
        before={'expected':{'outcome':'X'},'acceptance_change_reason':'old reason'}
        with self.assertRaisesRegex(ValueError,'REQUIRES_NEW_REASON'):
            gate.require_change_reason(before,dict(before,expected={'outcome':'Y'}))
        gate.require_change_reason(before,dict(before,expected={'outcome':'Y'},acceptance_change_reason='new evidence and reason'))
        gate.require_change_reason(before,dict(before))


if __name__=='__main__':unittest.main()

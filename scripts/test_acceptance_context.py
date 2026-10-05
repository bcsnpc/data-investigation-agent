import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from investigator.acceptance_context import require_context,select_store
from investigator.onboarding import Conflict

class AcceptanceContextTests(unittest.TestCase):
    def test_invoked_successor_refuses_before_store_or_transport_with_both_ids(self):
        x='00000000-0000-4000-8000-000000000001';y='00000000-0000-4000-8000-000000000002'
        case={'context_pin':{'context_id':x,'hash':'a'*64}}
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'case.json';path.write_text(json.dumps(case))
            with patch('investigator.acceptance_context.ModelStore',side_effect=AssertionError('no transport/store on mismatch')):
                with self.assertRaises(Conflict) as exc:select_store(path,None,'model',invoked_context={'context_id':y,'hash':'b'*64})
        self.assertIn(x,str(exc.exception));self.assertIn(y,str(exc.exception))

    def test_runner_reads_pin_from_file_not_manual_selection(self):
        # Tested ModelStore pin selection is exercised directly with its retained
        # contexts in test_model_onboarding; this test checks runner ownership.
        pin={'context_id':'00000000-0000-4000-8000-000000000001','hash':'a'*64}
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'case.json';path.write_text(json.dumps({'context_pin':pin}))
            with patch('investigator.acceptance_context.ModelStore') as ctor,patch('investigator.onboarding.digest',return_value=pin['hash']):
                store=type('Store',(),{'database':'db','inventory':'inventory','environment':'env'})()
                ctor.return_value.get.return_value={'context_id':pin['context_id'],'context':{}}
                self.assertIs(select_store(path,store,'model'),ctor.return_value)
                self.assertEqual(ctor.call_args.kwargs,{'context_pins':{'model':pin}})

if __name__=='__main__':unittest.main()

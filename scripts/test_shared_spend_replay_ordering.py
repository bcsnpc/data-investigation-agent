import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from investigator.model_spend import admission,SpendBudget
from investigator.shared_state import SharedState
from investigator.process_tape import Tape,active,clock
from investigator.shared_application import VERSION
from test_process_tape import bootstrap

class SharedSpendReplayOrderingTests(unittest.TestCase):
 def test_shared_reservation_identity_replays_before_provider_clock_without_ledger_access(self):
  with tempfile.TemporaryDirectory()as folder:
   root=Path(folder);state=SharedState.offline(root/'state.sqlite');state.migrate()
   state.import_accounts('test',{'accounts':[{'identity':'model-microdollars','unit':'MICRODOLLARS','ceiling':1000000,'protected':0,'opening':0,'violated':False}]})
   header=bootstrap();header['state'].update(shared_application=VERSION,shared_usage_replay={'owner':'recorded'})
   tape=Tape(root/'tape.json',header);body={'input':'fixture','max_output_tokens':10,'model':'synthetic'}
   with patch.dict(os.environ,{'INVESTIGATOR_WORKER_ID':'test-owner','INVESTIGATOR_MODEL_SPEND_MICRODOLLARS':'1000000','INVESTIGATOR_MODEL_SPEND_MARGIN_MICRODOLLARS':'0','INVESTIGATOR_OPERATING_MODE':''}),patch('investigator.shared_state.configured_state',return_value=state),patch.object(SpendBudget,'price',return_value=100),active(tape):
    with admission(body)as settle:
     self.assertEqual(clock('provider_timeout',lambda:10),10)
     settle({'input_tokens':1,'output_tokens':1})
    tape.finish({'result':'unchanged'})
   raw=(root/'tape.json').read_bytes();before=state.snapshot('model-microdollars')
   replay=Tape(root/'tape.json')
   with patch('investigator.shared_state.configured_state',side_effect=AssertionError('Replay must not touch a ledger')),active(replay):
    with admission(body)as settle:
     self.assertEqual(clock('provider_timeout',lambda:self.fail('No real clock')),10)
     settle({'input_tokens':1,'output_tokens':1})
    replay.finish({'result':'unchanged'})
   self.assertEqual((root/'tape.json').read_bytes(),raw)
   self.assertEqual(state.snapshot('model-microdollars'),before)
 def test_local_capture_without_shared_markers_keeps_original_clock_order(self):
  with tempfile.TemporaryDirectory()as folder:
   path=Path(folder)/'tape.json';tape=Tape(path,bootstrap())
   with active(tape):clock('provider_timeout',lambda:12);tape.finish({})
   replay=Tape(path)
   with active(replay),admission({'input':'fixture'})as settle:
    self.assertEqual(clock('provider_timeout',lambda:self.fail()),12);settle(None)
   replay.finish({})
if __name__=='__main__':unittest.main()

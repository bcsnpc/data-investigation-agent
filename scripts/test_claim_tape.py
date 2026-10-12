import unittest,tempfile,json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from investigator.process_tape import Tape,active,event,bytes_of,CLAIM_OPERATIONS,CLAIM_VERSIONS,VERSION
from investigator.claim_intake import ClaimIntake
from test_claim_intake import Store,CAT
from test_process_tape import bootstrap
class ClaimTapeTests(unittest.TestCase):
 def test_claim_submit_and_confirm_replay_exact_without_network_or_provider(self):
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);path=root/'tape.json';tape=Tape(path,bootstrap())
   def exercise(filename,t):
    workspace=SimpleNamespace(store=Store(root/filename),agent=SimpleNamespace(config={},planner_profile={'adapter':'injected'}))
    controller=ClaimIntake(workspace)
    request={'request_key':'freshness','claim':{'direction':'STALE','scope':{'kind':'PAGE','report_id':'report','page_id':'page'}}}
    with active(t),patch.object(controller,'_catalog',return_value=CAT),patch('socket.socket.connect',side_effect=AssertionError('NETWORK_FORBIDDEN')),patch('investigator.claim_provider.extract',side_effect=AssertionError('MODEL_FORBIDDEN')):
     event('OPERATION_START',{'name':'claim_submit','args':[request],'kwargs':{}});result=controller.submit(request);event('OPERATION_END',{'name':'claim_submit','error':None})
     confirm={'id':result['id'],'revision':0,'accepted':True}
     event('OPERATION_START',{'name':'claim_confirm','args':[confirm],'kwargs':{}});result=controller.confirm(confirm);event('OPERATION_END',{'name':'claim_confirm','error':None});t.finish(result)
    return result
   expected=exercise('record.sqlite',tape);actual=exercise('replay.sqlite',Tape(path))
   self.assertEqual(bytes_of(expected),bytes_of(actual));self.assertEqual(actual['engine_admission']['executed'],False)
 def test_claim_contract_is_new_version_and_legacy_v12_remains_supported(self):
  from investigator.process_tape import SUPPORTED_VERSIONS,AGENT_RESUME_VERSIONS
  self.assertEqual(VERSION,'bounded-worker-tape-v13');self.assertIn('bounded-worker-tape-v12',SUPPORTED_VERSIONS);self.assertIn('bounded-worker-tape-v12',AGENT_RESUME_VERSIONS)
  self.assertNotIn('bounded-worker-tape-v12',CLAIM_VERSIONS);self.assertIn('claim_screenshot_identify',CLAIM_OPERATIONS)
 def test_current_recorder_supports_all_inherited_budget_and_agent_features(self):
  from investigator.process_tape import SMART_VERSIONS,AGENT_VERSIONS,AGENT_RESUME_VERSIONS,DOLLAR_GUARDED_VERSIONS,CODE_VERSIONS,BUDGET_V2_VERSIONS,AGENT_CLOCK_VERSIONS
  from investigator.budget_checkpoint import implementation
  from investigator import budget_delta_v2
  for versions in(SMART_VERSIONS,AGENT_VERSIONS,AGENT_RESUME_VERSIONS,DOLLAR_GUARDED_VERSIONS,CODE_VERSIONS,BUDGET_V2_VERSIONS,AGENT_CLOCK_VERSIONS):self.assertIn(VERSION,versions)
  tape=SimpleNamespace(version=VERSION,bootstrap={'state':{'budget_checkpoint':'DELTA_V2'}})
  self.assertIs(implementation(tape),budget_delta_v2)
  self.assertNotIn('bounded-worker-tape-v7',BUDGET_V2_VERSIONS);self.assertNotIn('bounded-worker-tape-v11',AGENT_CLOCK_VERSIONS)
if __name__=='__main__':unittest.main()

"""Recorder and replay must conserve direct claim execution prose."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'acceptance/unknown_domain'))
from process_replay import final_envelope
from investigator.process_tape import bytes_of

class Tests(unittest.TestCase):
 def test_direct_claim_execution_outputs_are_in_exact_final_envelope(self):
  outputs={'business_explanation':'Two observed cells agreed.','technical_narrative':'Both sealed receipts retain the same scalar.'}
  result={'status':'COMPLETED','outputs':outputs,'checks':{'status':'OBSERVED'}}
  expected={'operation':'claim_run','error':None,'outputs':outputs,'status':'COMPLETED','result':result}
  self.assertEqual(bytes_of(final_envelope('claim_run',result,None)),bytes_of(expected))
 def test_legacy_synthesis_and_refusal_outputs_remain_exact(self):
  for result in ({'status':'COMPLETED','synthesis':{'outputs':{'business':'observed'}}},
                 {'status':'HELD','refusal_outputs':{'business':'unavailable'}}):
   outputs=(result.get('synthesis')or{}).get('outputs')or result.get('refusal_outputs')
   self.assertEqual(final_envelope('run',result,None)['outputs'],outputs)
 def test_other_operation_cannot_borrow_direct_outputs(self):
  self.assertIsNone(final_envelope('claim_submit',{'outputs':{'unexpected':'value'}},None)['outputs'])
 def test_failure_and_empty_result_are_preserved(self):
  self.assertEqual(final_envelope('claim_run',None,'ValueError'),{'operation':'claim_run','error':'ValueError','outputs':None,'status':None,'result':None})

if __name__=='__main__':unittest.main()

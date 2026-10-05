import json,unittest,tempfile
from pathlib import Path
from investigator.budget_tape_contract import equal,install,ACCOUNTING_HISTORY
from investigator.process_tape import Tape,TapeError,bytes_of
from test_process_tape import bootstrap

class BudgetContractTests(unittest.TestCase):
 def test_serialized_count_maps_compare_as_counts(self):
  a={'phase':'AFTER','error':None,'state':{'reservation':['SETTLED','{"cloud_calls":1,"input_characters":0}','{"cloud_calls":1}'],'usage_rows':1}}
  b={'state':{'usage_rows':1,'reservation':['SETTLED','{ "input_characters": 0, "cloud_calls": 1 }','{ "cloud_calls": 1 }']},'error':None,'phase':'AFTER'}
  self.assertTrue(equal(bytes_of(a),json.dumps(b).encode()))
  for change in ('count','decision','field'):
   changed=json.loads(json.dumps(b))
   if change=='count':changed['state']['reservation'][2]='{"cloud_calls":2}'
   elif change=='decision':changed['state']['reservation'][0]='REFUSED'
   else:changed['extra']=1
   self.assertFalse(equal(bytes_of(a),bytes_of(changed)))
 def test_only_budget_representation_is_relaxed(self):
  for kind in ('BOUNDED_REQUEST','PROVIDER_REQUEST','WORKER_SEND'):
   tape=object.__new__(Tape);tape.replaying=True;tape.take=lambda requested:b'{"count":1}'
   with self.subTest(kind=kind),self.assertRaisesRegex(TapeError,'REQUEST_BYTES_DIFFER'):
    tape.event(kind,b'{ "count": 1 }')
 def test_archived_producer_uses_same_budget_consumer(self):
  class Historical:
   class Tape:
    def event(self,kind,body):
     if self.take(kind)!=body:raise TapeError('OLD_BYTES')
   TapeError=TapeError
  install(Historical)
  tape=Historical.Tape();tape.replaying=True;tape.take=lambda kind:b'{"decision":"ADMITTED","count":1}'
  tape.event('BUDGET',b'{ "count":1, "decision":"ADMITTED" }')
  with self.assertRaisesRegex(TapeError,'DECISION_DIFFERS'):tape.event('BUDGET',b'{"decision":"REFUSED","count":1}')
  with self.assertRaisesRegex(TapeError,'OLD_BYTES'):tape.event('PROVIDER_REQUEST',b'{ "decision":"ADMITTED","count":1 }')
 def test_accounting_version_records_retroactive_reason(self):
  self.assertIn('#393',ACCOUNTING_HISTORY[2])
if __name__=='__main__':unittest.main()

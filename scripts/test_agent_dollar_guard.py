import copy,json,runpy,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'scripts'))
from investigator import agent_dollar_guard
P=vars(agent_dollar_guard)
class Tape:
 version='bounded-worker-tape-v10';bootstrap={}
 def __init__(self,replaying,event=None):self.replaying=replaying;self.event=event;self.calls=0
 def take(self,kind):self.calls+=1;assert kind=='CONFIGURATION';return json.dumps(self.event).encode()
class GuardTests(unittest.TestCase):
 def test_live_policy_verified_then_recorded_no_route(self):
  from investigator.model_spend import SpendBudget
  with tempfile.TemporaryDirectory() as d:
   path=str(Path(d)/'actual.sqlite');events=[]
   v=P['declare'](tape=Tape(False),environment={'INVESTIGATOR_MODEL_SPEND_DB':path,'INVESTIGATOR_MODEL_SPEND_MICRODOLLARS':'100000000'},emit=lambda k,v:events.append((k,v)))
   self.assertEqual(SpendBudget(path,100000000).snapshot()['calls'],0);self.assertEqual(events,[('CONFIGURATION',v)]);self.assertNotIn(path,json.dumps(v))
   with self.assertRaisesRegex(RuntimeError,'differs'):P['declare'](environment={'INVESTIGATOR_MODEL_SPEND_DB':path,'INVESTIGATOR_MODEL_SPEND_MICRODOLLARS':'1'})
 def test_replay_consumes_guard_without_environment_or_db(self):
  v={'control':P['CONTROL'],'version':P['VERSION'],'configured':True,'ceiling_microdollars':100000000,'admission':'MODEL_SPEND_V1'};t=Tape(True,v)
  def forbidden(*a):raise AssertionError('External DB write attempted')
  self.assertEqual(P['declare'](tape=t,environment={},policy_factory=forbidden),v);self.assertEqual(t.calls,1)
 def test_old_v9_refuses_without_retroactive_claim(self):
  t=Tape(True);t.version='bounded-worker-tape-v9'
  with self.assertRaisesRegex(ValueError,'NOT_RECORDED'):P['declare'](tape=t,environment={'INVESTIGATOR_MODEL_SPEND_DB':'dummy'})
  self.assertEqual(t.calls,0)
 def test_invalid_declaration_cannot_authorize_replay(self):
  for ceiling in (True,0,'100000000'):
   with self.assertRaisesRegex(ValueError,'SCHEMA'):P['declare'](tape=Tape(True,{'control':P['CONTROL'],'version':P['VERSION'],'configured':True,'ceiling_microdollars':ceiling,'admission':'MODEL_SPEND_V1'}))
if __name__=='__main__':unittest.main()

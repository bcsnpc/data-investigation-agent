import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from investigator.code_proposal_budget import Proposer
from investigator.usage_governance import UsageHold

class BudgetTests(unittest.TestCase):
    def proposer(self,provider):
        self.reserved=[];self.settled=[];self.events=[]
        db=SimpleNamespace(execute=lambda *args:None)
        @contextmanager
        def connect():yield db
        gov=SimpleNamespace(runtime=SimpleNamespace(db=connect),
            reserve=lambda *a,**kw:self.reserved.append((a,kw)),
            settle=lambda *a,**kw:self.settled.append((a,kw)))
        return Proposer(provider,governor=gov,session_id='code-session',
            options={'reasoning_effort':'none','max_payload_characters':8000,'timeout_seconds':10,'max_output_tokens':1500},
            deadline=100,max_calls=1,max_input=1000,event=lambda *a:self.events.append(a),
            context_version='retained-context',clock=lambda:1)

    def test_code_only_handoff_reserves_and_settles_once(self):
        p=self.proposer(lambda *args:([],{'usage':{'output_tokens':4}}))
        self.assertEqual(p({'code':{},'layers':[]},{}),[])
        self.assertEqual(len(self.reserved),1);self.assertEqual(len(self.settled),1)
        self.assertFalse(self.settled[0][1]['uncertain'])
        with self.assertRaises(UsageHold):p({'code':{},'layers':[]},{})
        self.assertEqual(len(self.reserved),1)

    def test_invalid_payload_and_deadline_refuse_before_provider_or_reservation(self):
        p=self.proposer(lambda *a:self.fail('No provider call'))
        with self.assertRaises(ValueError):p({'code':{},'layers':[],'ticket':{}},{})
        p.deadline=5
        with self.assertRaisesRegex(UsageHold,'deadline'):p({'code':{},'layers':[]},{})
        self.assertEqual(self.reserved,[])

    def test_provider_failure_is_charged_and_recorded_without_retry(self):
        def fail(*a):raise RuntimeError('Provider unavailable')
        p=self.proposer(fail)
        with self.assertRaisesRegex(RuntimeError,'Provider unavailable'):p({'code':{},'layers':[]},{})
        self.assertEqual(len(self.reserved),1);self.assertTrue(self.settled[0][1]['uncertain'])
        self.assertEqual(self.events[-1][0],'CODE_BINDING_PROPOSAL_FAILED')

if __name__=='__main__':unittest.main()

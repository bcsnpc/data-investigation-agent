import unittest
import test_read_budget as fixtures
from investigator.usage_governance import UsageHold,charged

class ModelReconciliationTests(unittest.TestCase):
    setUp=fixtures.ReadBudgetTests.setUp
    def test_completed_usage_releases_bound_without_editing_reservation(self):
        with self.runtime.db() as db:
            self.g.reserve(db,'s','a','planner',10,output_tokens=8000)
            self.g.settle(db,'s','a',{'output_tokens':123})
        s=self.g.snapshot()
        self.assertEqual(s['reserved_today']['output_tokens'],8000)
        self.assertEqual(s['charged_today']['output_tokens'],123)
        self.assertEqual(s['active_reservations']['output_tokens'],0)
        with self.runtime.db() as db:
            self.g.settle(db,'s','a',{'output_tokens':0})
        self.assertEqual(self.g.snapshot()['charged_today']['output_tokens'],123)

    def test_error_or_timeout_releases_inflight_but_never_invents_zero_usage(self):
        for uncertain in (False,True):
            with self.subTest(uncertain=uncertain),self.runtime.db() as db:
                key=str(uncertain)
                self.g.reserve(db,'s',key,'planner',10,output_tokens=8000)
                self.g.settle(db,'s',key,uncertain=uncertain)
        s=self.g.snapshot()
        self.assertEqual(s['active_reservations']['output_tokens'],0)
        self.assertEqual(s['charged_today']['output_tokens'],16000)
        self.assertEqual(s['unknown_output_charged'],16000)

    def test_real_overrun_remains_charged_and_latched(self):
        with self.runtime.db() as db:
            self.g.reserve(db,'s','a','planner',10,output_tokens=1500)
            self.g.settle(db,'s','a',{'output_tokens':2504})
        self.assertEqual(self.g.snapshot()['charged_today']['output_tokens'],2504)
        with self.runtime.db() as db,self.assertRaises(UsageHold):
            self.g.reserve(db,'s','b','planner',10)

    def test_admission_uses_actual_output_plus_active_bounds(self):
        self.g.policy['daily_limits']['output_tokens']=8000
        with self.runtime.db() as db:
            self.g.reserve(db,'s','a','planner',10,output_tokens=8000)
            self.g.settle(db,'s','a',{'output_tokens':100})
            self.g.reserve(db,'s','b','planner',10,output_tokens=7000)
        self.assertEqual(self.g.snapshot()['charged_today']['output_tokens'],7100)
        with self.runtime.db() as db,self.assertRaises(UsageHold):
            self.g.reserve(db,'s','c','planner',10,output_tokens=1500)

    def test_archived_accounting_preserves_full_bound(self):
        from investigator.process_tape import ACTIVE
        from types import SimpleNamespace
        token=ACTIVE.set(SimpleNamespace(replaying=True,accounting_version=2))
        try:self.assertEqual(charged({'reserved':'{"output_tokens":8000}', 'actual':'{"output_tokens":123}','status':'SETTLED'})['output_tokens'],8000)
        finally:ACTIVE.reset(token)

if __name__=='__main__':unittest.main()

import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from investigator import build_phase as b
from investigator.usage_governance import UsageHold


def instant(value):
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc).timestamp()


class MonthlyTests(unittest.TestCase):
    def rows(self, number, category='INVESTIGATION', at='2026-10-20'):
        row={'environment':'synthetic','session_id':'session','reservation_key':'slot',
             'reserved':json.dumps({'cloud_calls':number}), 'created':instant(at)}
        allocation={k:row[k]for k in('environment','session_id','reservation_key')}
        return [row],[dict(allocation,purpose=category)]

    def test_october_starts_at_adoption_then_calendar_months(self):
        self.assertEqual(b.month_window(instant('2026-10-21')),
                         ('2026-10',instant('2026-10-19'),instant('2026-11-01')))
        self.assertEqual(b.month_window(instant('2026-11-21')),
                         ('2026-11',instant('2026-11-01'),instant('2026-12-01')))

    def test_eighty_percent_warns_without_stopping(self):
        rows,alloc=self.rows(3924)
        status=b.admit_physical(rows,alloc,instant('2026-10-21'),'INVESTIGATION')
        self.assertIn('INVESTIGATION_MONTHLY_80_PERCENT',status['warnings'])
        self.assertTrue(b.model_status(32_000_000,'2026-10')['warning'])
        self.assertFalse(b.model_status(32_000_000,'2026-10')['exhausted'])
        self.assertTrue(b.admit_platform(16_000_000,instant('2026-10-21'))['warning'])

    def test_platform_exhaustion_does_not_block_local_or_estate_budget(self):
        with self.assertRaisesRegex(UsageHold,'MONTHLY_PLATFORM_EXHAUSTED'):
            b.admit_platform(20_000_000,instant('2026-10-21'))
        b.admit_physical([],[],instant('2026-10-21'),'INVESTIGATION')
        self.assertFalse(b.model_status(0,'2026-10')['exhausted'])
        self.assertIsNone(b.admit_platform(None,instant('2026-10-21'))['charged_microdollars'])

    def test_hundred_percent_stops_only_exhausted_category(self):
        rows,alloc=self.rows(4905)
        with self.assertRaisesRegex(UsageHold,'INVESTIGATION_EXHAUSTED'):
            b.admit_physical(rows,alloc,instant('2026-10-21'),'INVESTIGATION')
        b.admit_physical(rows,alloc,instant('2026-10-21'),'SCAN')
        b.admit_physical(rows,alloc,instant('2026-10-21'),'RESTORATION')
        self.assertTrue(b.model_status(40_000_000,'2026-10')['exhausted'])

    def test_restoration_95_automatically_reserved_without_credit_grant(self):
        rows,alloc=self.rows(4905)
        status=b.admit_physical(rows,alloc,instant('2026-10-21'),'RESTORATION')
        self.assertEqual(status['restoration_remaining'],95)
        self.assertEqual(sum(status['limits'].values()),6000)

    def test_collectors_never_consume_investigation_line(self):
        rows,alloc=self.rows(1000,'SCAN')
        with self.assertRaisesRegex(UsageHold,'SCAN_EXHAUSTED'):
            b.admit_physical(rows,alloc,instant('2026-10-21'),'SCAN')
        status=b.admit_physical(rows,alloc,instant('2026-10-21'),'INVESTIGATION')
        self.assertEqual(status['used']['INVESTIGATION'],0)

    def test_prior_history_and_prior_month_are_informational(self):
        old,alloc=self.rows(8000,at='2026-10-13')
        self.assertEqual(b.physical_status(old,alloc,instant('2026-10-21'))['total'],0)
        old,alloc=self.rows(6000,at='2026-10-31')
        self.assertEqual(b.physical_status(old,alloc,instant('2026-11-01'))['total'],0)

    def test_local_model_historical_107_dollars_does_not_block_new_call(self):
        from investigator.model_spend import SpendBudget
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'model.sqlite'
            with patch.dict(os.environ,{},clear=True):
                SpendBudget(path,150_000_000)
            db=sqlite3.connect(path)
            db.execute('INSERT INTO model_spend VALUES(?,?,?,?,?,?,?)',
                       ('historical',instant('2026-10-13'),107_957_725,107_957_725,'SETTLED',1,1))
            db.commit();db.close()
            with b.operating_mode(), patch('time.time',return_value=instant('2026-10-21')):
                budget=SpendBudget(path,150_000_000)
                with patch.object(SpendBudget,'price',return_value=1000):
                    identity=budget.reserve({'input':'synthetic','max_output_tokens':1000})
                status=budget.snapshot()
                self.assertEqual(status['charged_usd'],.001)
                self.assertEqual(status['historical_cumulative_usd_informational'],107.958725)
                self.assertEqual(status['monthly']['ceiling_microdollars'],40_000_000)
                self.assertTrue(identity)
            db=sqlite3.connect(path)
            self.assertEqual(db.execute('SELECT charged FROM model_spend WHERE id=?',('historical',)).fetchone()[0],107_957_725)
            self.assertEqual(db.execute('SELECT ceiling FROM spend_policy').fetchone()[0],150_000_000)
            db.close()

    def test_shared_model_account_keeps_old_total_without_limiting_new_period(self):
        from investigator.shared_state import SharedState
        from investigator.shared_spend import SharedSpendBudget
        from investigator.model_spend import SpendBudget
        with tempfile.TemporaryDirectory() as folder:
            state=SharedState.offline(Path(folder)/'state.sqlite');state.migrate()
            state.import_accounts('historical',{'accounts':[{'identity':'model-microdollars','unit':'MICRODOLLARS',
                'ceiling':'133046558','protected':'10000000','opening':'107957725','violated':False}]})
            with b.operating_mode(),patch.dict(os.environ,{'INVESTIGATOR_WORKER_ID':'synthetic'}),patch('time.time',return_value=instant('2026-10-21')):
                budget=SharedSpendBudget(state,133046558)
                with patch.object(SpendBudget,'price',return_value=1000):
                    budget.reserve({'input':'synthetic','max_output_tokens':1000})
                self.assertEqual(budget.snapshot()['charged'],'1000')
            self.assertEqual(state.snapshot('model-microdollars')['charged'],'107957725')
            opening=state.get('build_phase_account_opening','model-microdollars:2026-10')['body']
            self.assertEqual(opening['historical_total_microdollars_informational'],'107957725')

    def test_shared_model_40_dollars_stops_not_other_work(self):
        from investigator.shared_state import SharedState
        from investigator.shared_spend import SharedSpendBudget
        from investigator.model_spend import SpendBudget,SpendHold
        with tempfile.TemporaryDirectory() as folder:
            state=SharedState.offline(Path(folder)/'state.sqlite');state.migrate()
            with b.operating_mode(),patch.dict(os.environ,{'INVESTIGATOR_WORKER_ID':'synthetic'}),patch('time.time',return_value=instant('2026-10-21')):
                budget=SharedSpendBudget(state,133046558)
                with patch.object(SpendBudget,'price',return_value=40_000_000):
                    budget.reserve({'input':'synthetic','max_output_tokens':1000})
                with patch.object(SpendBudget,'price',return_value=1),self.assertRaisesRegex(SpendHold,'MONTHLY_MODEL_EXHAUSTED'):
                    budget.reserve({'input':'synthetic','max_output_tokens':1000})
                b.admit_physical([],[],instant('2026-10-21'),'INVESTIGATION')

    def test_shared_account_rolls_on_first_and_settles_original_month(self):
        from investigator.shared_state import SharedState
        from investigator.shared_spend import SharedSpendBudget
        from investigator.model_spend import SpendBudget
        with tempfile.TemporaryDirectory() as folder:
            state=SharedState.offline(Path(folder)/'state.sqlite');state.migrate()
            with b.operating_mode(),patch.dict(os.environ,{'INVESTIGATOR_WORKER_ID':'synthetic'}),patch.object(SpendBudget,'price',return_value=1000):
                with patch('time.time',return_value=instant('2026-10-31')):
                    budget=SharedSpendBudget(state,133046558)
                    october=budget.reserve({'input':'synthetic','max_output_tokens':1000})
                with patch('time.time',return_value=instant('2026-11-01')):
                    self.assertEqual(budget.snapshot()['charged'],'0')
                    budget.reserve({'input':'synthetic','max_output_tokens':1000})
                    budget.settle(october,{'input_tokens':1,'output_tokens':1})
                self.assertEqual(state.snapshot('model-microdollars:2026-10')['charged'],'1000')
                self.assertEqual(state.snapshot('model-microdollars:2026-11')['charged'],'1000')

    def test_build_mode_is_scoped_and_legacy_replay_not_reinterpreted(self):
        from types import SimpleNamespace
        from investigator.process_tape import ACTIVE
        with patch.dict(os.environ,{},clear=True):
            self.assertFalse(b.active())
            with b.operating_mode(category='SCAN'):
                self.assertTrue(b.active());self.assertEqual(b.purpose(), 'SCAN')
                token=ACTIVE.set(SimpleNamespace(replaying=True,bootstrap={'config':{}}))
                try:self.assertFalse(b.active())
                finally:ACTIVE.reset(token)
            self.assertFalse(b.active())


if __name__=='__main__':unittest.main()

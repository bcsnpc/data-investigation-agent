from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from investigator.reasoning_budget import TicketBudget, RateCard
from investigator.shared_state import SharedState
from investigator.provider_budget import ensure_account


class ReservationRetryTests(unittest.TestCase):
    def test_existing_postgres_accounts_need_no_writer_transaction(self):
        from investigator.model_spend import SpendHold
        for provider in ('anthropic', 'openai'):
            state=Mock();state.backend='postgresql'
            state.transaction.side_effect=AssertionError('worker must not acquire writer lock')
            state._read_transaction.side_effect=lambda read:read(object())
            state.sql.return_value.fetchone.return_value=(1,)
            account=ensure_account(state,provider,1793491200)
            self.assertIn('2026-11',account)
            state.transaction.assert_not_called()
            state.sql.return_value.fetchone.return_value=None
            with self.assertRaisesRegex(SpendHold,'ACCOUNT_NOT_PROVISIONED'):
                ensure_account(state,provider,1793491200)
            state.transaction.assert_not_called()

    def test_one_reservation_after_disconnect_before_or_after_commit(self):
        for phase in ('before_commit','after_commit'):
            with self.subTest(phase=phase), TemporaryDirectory()as folder:
                state=SharedState.offline(Path(folder)/'state.sqlite');state.migrate()
                rate=RateCard(model='synthetic',input_rate=1,output_rate=1,
                    source='https://example.test',observed_at='2026-11-01')
                budget=TicketBudget(state,case_id='one',owner='owner',rate=rate,
                                    provider='openai',actual_usage_limit=3000000)
                account=ensure_account(state,'openai',budget.clock())
                transaction=state.transaction;failed=[]
                @contextmanager
                def flaky(**kwargs):
                    inserted=False
                    with transaction(**kwargs)as db:
                        yield db
                        inserted=bool(db.execute("SELECT 1 FROM state_reservations WHERE identity='reasoning:fixed'").fetchone())
                        if inserted and not failed and phase=='before_commit':
                            failed.append(True);raise ConnectionError('synthetic lost connection')
                    if inserted and not failed and phase=='after_commit':
                        failed.append(True);raise ConnectionError('synthetic lost acknowledgment')
                attempts=[]
                def retry(name,operation):
                    self.assertEqual(name,'IDEMPOTENT_MODEL_RESERVATION')
                    for attempt in range(2):
                        attempts.append(attempt)
                        try:return operation()
                        except ConnectionError:
                            if attempt:raise
                with patch.object(state,'transaction',side_effect=flaky), \
                     patch.object(state,'_retry_connection_operation',side_effect=retry), \
                     patch('investigator.reasoning_budget.uuid4',return_value='fixed'):
                    identity=budget.reserve({'model':'synthetic','max_tokens':100},input_tokens_upper_bound=100)
                self.assertEqual(identity,'reasoning:fixed')
                snapshot=state.snapshot(account)
                self.assertEqual(len(snapshot['reservations']),1)
                self.assertEqual(snapshot['charged'],'200')
                self.assertEqual(attempts,[0,1])
                from investigator.model_spend import SpendHold
                with self.assertRaisesRegex(SpendHold,'MODEL_RESERVATION_REPLAY_DIFFERS'):
                    budget._reserve_identity(account,identity,201,201,snapshot['reservations'][0]['detail'])
                with state.transaction()as db:
                    db.execute('UPDATE state_accounts SET violated=1 WHERE identity=?',(account,))
                with self.assertRaisesRegex(SpendHold,'MODEL_ACCOUNT_VIOLATION'):
                    budget._reserve_identity(account,identity,200,200,snapshot['reservations'][0]['detail'])

    def test_postgres_credit_checks_return_totals_without_transferring_detail(self):
        from investigator.anthropic_credit import grading_charge, model_grading_charge
        state=Mock();state.backend='postgresql';state.sql.return_value.fetchone.return_value=(17,)
        self.assertEqual(grading_charge(state,object(),{'grading_account':'g','grading_month_tag':'2026-11'},{}),17)
        self.assertEqual(model_grading_charge(state,object(),'m'),17)
        for call in state.sql.call_args_list:
            self.assertIn('SUM(TRUNC(charged))',call.args[1])
            self.assertNotIn('SELECT charged,detail',call.args[1])


if __name__=='__main__':unittest.main()

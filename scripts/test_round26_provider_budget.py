from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from investigator.shared_state import SharedState
from investigator.provider_budget import account_for, ensure_account, report

NOW = datetime(2026, 11, 1, tzinfo=timezone.utc).timestamp()


class ProviderBudgetTests(unittest.TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.state = SharedState.offline(Path(folder.name) / 'state.sqlite')
        self.state.migrate()

    def test_separate_accounts_preserve_existing_usage(self):
        anthropic = ensure_account(self.state, 'anthropic', NOW)
        self.state.reserve(anthropic, 'old', 'worker', 12345)
        self.state.settle(anthropic, 'old', 'worker', 12345)
        openai = ensure_account(self.state, 'openai', NOW)
        self.assertNotEqual(anthropic, openai)
        self.assertEqual(int(self.state.totals(openai)['ceiling']), 180000000)
        self.assertEqual(int(self.state.totals(anthropic)['charged']), 12345)
        observed = report(self.state, NOW)
        self.assertEqual(observed['combined_charged_microdollars'], 12345)
        self.assertEqual(observed['providers']['openai']['charged_microdollars'], 0)

    def test_existing_owner_ceiling_is_never_raised_by_worker(self):
        account = ensure_account(self.state, 'openai', NOW)
        with self.state.transaction() as db:
            db.execute('UPDATE state_accounts SET ceiling=100 WHERE identity=?', (account,))
        ensure_account(self.state, 'openai', NOW)
        self.assertEqual(int(self.state.totals(account)['ceiling']), 100)

    def test_unknown_provider_refused(self):
        with self.assertRaises(KeyError):
            account_for('unconfigured', NOW)

    def test_month_rollover_keeps_history(self):
        first = ensure_account(self.state, 'openai', NOW)
        later = ensure_account(self.state, 'openai', datetime(2026, 12, 1, tzinfo=timezone.utc).timestamp())
        self.assertNotEqual(first, later)
        self.assertEqual(int(self.state.totals(first)['charged']), 0)

    def test_switching_provider_does_not_reset_ticket_actual_cap(self):
        from investigator.reasoning_budget import TicketBudget, RateCard
        from investigator.model_spend import SpendHold
        rate = RateCard(model='synthetic', input_rate=1, output_rate=1,
                        source='https://example.test/pricing', observed_at='2026-11-01')
        def budget(provider):
            return TicketBudget(self.state, case_id='same', owner='worker', rate=rate,
                                clock=lambda: NOW, actual_usage_limit=3000000, provider=provider)
        body = {'model': 'synthetic', 'max_tokens': 10}
        first = budget('anthropic')
        reservation = first.reserve(body, input_tokens_upper_bound=3000000)
        first.settle(reservation, {'input_tokens': 3000000, 'output_tokens': 0})
        second = budget('openai')
        with self.assertRaisesRegex(SpendHold, 'TICKET_MODEL_EXHAUSTED'):
            second.reserve(body, input_tokens_upper_bound=10)
        self.assertEqual(second.status()['charged_microdollars'], 3000000)


if __name__ == '__main__':
    unittest.main()

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


if __name__ == '__main__':
    unittest.main()

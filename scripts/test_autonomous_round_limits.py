"""The approved operator limits preserve reservations and remain binding."""
import json
from pathlib import Path
import tempfile
import unittest

from read_budget import Catalog
from investigator.usage_governance import UsageGovernor, UsageHold


class AutonomousRoundLimitsTests(unittest.TestCase):
    def test_approved_profile_keeps_history_and_stops_at_new_boundary(self):
        limits = json.loads((Path(__file__).resolve().parents[1] /
                             'infra/runtime/autonomous-round-limits.json').read_text())
        self.assertEqual(limits['rolling_physical_allowance'], 1000)
        self.assertEqual(limits['diagnostic_read_cap'], 12)
        with tempfile.TemporaryDirectory() as folder:
            runtime = Catalog(Path(folder) / 'catalog.sqlite', 'estate')
            policy = {'environment': 'estate', 'daily_limits': {
                'planner_calls': 20, 'cloud_calls': 60,
                'input_characters': 100000, 'output_tokens': 30000},
                'max_inflight_planners': 1, 'no_progress_limit': 2}
            old = UsageGovernor(runtime, policy, lambda: 100000.0)
            with runtime.db() as db:
                for index in range(60):
                    old.reserve(db, 'old', str(index), 'cloud')
                before = [tuple(r) for r in db.execute('SELECT * FROM adaptive_usage ORDER BY reservation_key')]
            policy['daily_limits']['cloud_calls'] = limits['rolling_physical_allowance']
            new = UsageGovernor(runtime, policy, lambda: 100000.0)
            self.assertEqual(new.snapshot()['read_allowance']['ordinary_charged'], 60)
            self.assertEqual(new.snapshot()['read_allowance']['ordinary_available'], limits['rolling_physical_allowance'] - 60)
            with runtime.db() as db:
                self.assertEqual(before, [tuple(r) for r in db.execute('SELECT * FROM adaptive_usage ORDER BY reservation_key')])
                for index in range(limits['rolling_physical_allowance'] - 60):
                    new.reserve(db, 'new', str(index), 'cloud')
                with self.assertRaises(UsageHold):
                    new.reserve(db, 'new', 'over', 'cloud')
            self.assertEqual(new.snapshot()['read_allowance']['ordinary_charged'], limits['rolling_physical_allowance'])


if __name__ == '__main__':
    unittest.main()

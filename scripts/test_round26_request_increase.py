import unittest
from datetime import datetime

from investigator.build_phase import round24_limits


class NovemberRequestIncrease(unittest.TestCase):
    def test_owner_approved_month_only_and_model_unchanged(self):
        for month, total, investigation in [('2026-11', 14500, 11905), ('2026-12', 9000, 6405)]:
            with self.subTest(month=month):
                limits = round24_limits(datetime.fromisoformat(month + '-15T00:00:00+00:00').timestamp())
                self.assertEqual(limits['total_limit'], total)
                self.assertEqual(limits['limits'], {'SCAN': 2500, 'INVESTIGATION': investigation, 'RESTORATION': 95})
                self.assertEqual(limits['model_microdollars'], 150000000)
                self.assertEqual(sum(limits['limits'].values()), total)


if __name__ == '__main__':
    unittest.main()

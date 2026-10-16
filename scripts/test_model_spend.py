import concurrent.futures
import tempfile
import unittest
from pathlib import Path
from investigator.model_spend import SpendBudget, SpendHold


class ModelSpendTests(unittest.TestCase):
    def test_parallel_reservations_never_cross_shared_ceiling(self):
        with tempfile.TemporaryDirectory() as directory:
            budget = SpendBudget(Path(directory)/'spend.sqlite', 400000)
            body = {'input': 'test', 'max_output_tokens': 8000}
            def call(_):
                try:
                    identity = budget.reserve(body)
                except SpendHold:
                    return False
                budget.settle(identity, {'input_tokens': 1000, 'output_tokens': 1000})
                return True
            with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
                accepted = sum(pool.map(call, range(80)))
            snapshot = budget.snapshot()
            self.assertEqual(snapshot['calls'], accepted)
            self.assertAlmostEqual(snapshot['charged_usd'], accepted*0.0175)
            self.assertLessEqual(snapshot['charged_usd'], 0.4)
            self.assertEqual(snapshot['unsettled_calls'], 0)

    def test_unknown_usage_keeps_full_bound_and_settlement_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            budget = SpendBudget(Path(directory)/'spend.sqlite', 200000)
            identity = budget.reserve({'input':'test','max_output_tokens':8000})
            before = budget.snapshot()['charged_usd']
            budget.settle(identity)
            budget.settle(identity, {'input_tokens':1,'output_tokens':1})
            self.assertEqual(budget.snapshot()['charged_usd'], before)
            self.assertEqual(budget.snapshot()['unsettled_calls'], 1)

    def test_later_process_cannot_silently_raise_ceiling(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'spend.sqlite'
            SpendBudget(path, 100000000)
            with self.assertRaises(SpendHold):
                SpendBudget(path, 200000000)


if __name__ == '__main__':
    unittest.main()

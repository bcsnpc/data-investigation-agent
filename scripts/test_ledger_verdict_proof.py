import unittest
from prove_ledger_verdicts import prove
from investigator.evidence_verdicts import VERDICTS


class NineContracts(unittest.TestCase):
    def test_all_nine_are_exercised_through_actual_investigator_with_no_live_ports(self):
        result=prove()
        self.assertEqual(result['passed'],9);self.assertEqual(result['total'],9)
        self.assertEqual({row['expected'] for row in result['cases']},set(VERDICTS))
        for row in result['cases']:
            with self.subTest(row['expected']):
                self.assertTrue(row['matched']);self.assertTrue(row['support_ids'])
                self.assertGreater(row['event_count'],2)
                self.assertEqual(row['model_calls'],0);self.assertEqual(row['estate_reads'],0)


if __name__=='__main__':unittest.main()

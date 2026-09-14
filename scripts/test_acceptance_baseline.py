import unittest
from evaluate_acceptance import evaluate


class AcceptanceTests(unittest.TestCase):
    def test_workflow_gates_and_product_gaps(self):
        result=evaluate()
        self.assertTrue(result['workflow_passed'])
        self.assertFalse(result['product_acceptance_complete'])
        self.assertEqual(len(result['cases']),3)
        self.assertTrue(result['pending'])


if __name__=='__main__':unittest.main()

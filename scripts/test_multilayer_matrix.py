from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from evaluate_multilayer_matrix import evaluate,assess
from investigation_evidence_api import EvidenceStore


class MultiMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.output=Path(cls.temp.name)/'run';cls.report=evaluate(cls.output)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_matrix_persists_observations_and_resets(self):
        self.assertTrue(self.report['passed']);self.assertEqual(self.report['passed_count'],5)
        self.assertFalse(self.report['product_acceptance'])
        for row in self.report['cases']:
            self.assertEqual(row['reset_status'],'READY')
            item=EvidenceStore(self.output/row['evidence_database']).get(row['investigation_id'])
            self.assertNotIn('expected_boundaries',item['request']);self.assertNotIn('case',item['request'])

    def test_offsetting_changes_are_not_hidden_by_equal_totals(self):
        row=next(r for r in self.report['cases'] if r['case']=='offsetting_records')
        impact=row['observed']['boundaries'][0]['impact_by_currency']['USD']
        self.assertEqual(impact['upstream_total'],impact['downstream_total'])
        self.assertEqual(impact['affected_records'],2)
        self.assertEqual(row['observed']['boundaries'][0]['comparison_status'],'MISMATCH')

    def test_wrong_boundary_or_aggregate_only_result_fails_evaluation(self):
        result=next(r['observed'] for r in self.report['cases'] if r['case']=='offsetting_records')
        changed=deepcopy(result);changed['boundaries'][0]['comparison_status']='MATCH'
        self.assertFalse(assess('offsetting_records',changed)['passed'])
        changed=deepcopy(result);changed['first_observed_local_boundary']={'upstream':'silver','downstream':'gold'}
        self.assertFalse(assess('offsetting_records',changed)['passed'])
        changed=deepcopy(result);changed['classification']='TECHNICAL_DEFECT';changed['root_cause_verified']=True
        self.assertFalse(assess('offsetting_records',changed)['passed'])


if __name__=='__main__':unittest.main()

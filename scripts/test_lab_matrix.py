from copy import deepcopy
from pathlib import Path
import json
import tempfile
import unittest
from evaluate_lab_matrix import evaluate,assess
from investigation_evidence_api import EvidenceStore


class MatrixTests(unittest.TestCase):
    def test_matrix_persists_evidence_and_resets_all_cases(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'run';report=evaluate(output)
            self.assertTrue(report['passed']);self.assertEqual(report['passed_count'],10)
            self.assertFalse(report['product_acceptance'])
            self.assertEqual(report,json.loads((output/'report.json').read_text()))
            for case in report['cases']:
                self.assertEqual(case['reset_status'],'READY')
                item=EvidenceStore(output/case['evidence_database']).get(case['investigation_id'])
                self.assertIsNotNone(item)
                self.assertNotIn('expected',item['request']);self.assertNotIn('case',item['request'])

    def test_false_promotion_wrong_impact_and_routing_fail(self):
        result={'classification':'UNRESOLVED','impact_by_currency':{'USD':{'downstream_minus_upstream':'10.0000'}},
                'root_cause_verified':False,'affected_records':[{}],'automatic_defect_routing':False}
        self.assertTrue(assess(result,'UNRESOLVED','10.0000',False,1)['passed'])
        for field,value in [('classification','TECHNICAL_DEFECT'),('root_cause_verified',True),('automatic_defect_routing',True),('affected_records',[])]:
            bad=deepcopy(result);bad[field]=value
            self.assertFalse(assess(bad,'UNRESOLVED','10.0000',False,1)['passed'])
        self.assertFalse(assess(result,'UNRESOLVED','11.0000',False,1)['passed'])

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            marker=Path(folder)/'keep';marker.write_text('unchanged')
            with self.assertRaises(FileExistsError):evaluate(folder)
            self.assertEqual(marker.read_text(),'unchanged')


if __name__=='__main__':unittest.main()

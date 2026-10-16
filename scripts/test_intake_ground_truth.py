import copy
import json
import unittest
from pathlib import Path
from audit_intake_ground_truth import audit


class GroundTruthTests(unittest.TestCase):
    def test_definition_enumeration_does_not_trust_expected_candidates(self):
        path=Path(__file__).resolve().parents[1]/'acceptance/model_steps/intake-round-ten-e-original-nine.json'
        golden=json.loads(path.read_text(encoding='utf8'))
        rows=audit(golden)
        self.assertEqual([r['count'] for r in rows],[1,1,1,2,2,2,2,2,2])
        hostile=copy.deepcopy(golden)
        for case in hostile['cases']:
            if case.get('group')=='nine':case['candidate_target_ids']=[]
        other=audit(hostile)
        self.assertEqual([r['matching_primary'] for r in other],[r['matching_primary'] for r in rows])
        self.assertTrue(all(r['definition_parts'] for r in rows))

    def test_amended_nine_have_explicit_unique_visuals_and_fifty_is_unchanged(self):
        root=Path(__file__).resolve().parents[1]/'acceptance/model_steps'
        current=json.loads((root/'intake-round-ten-current-59.json').read_text(encoding='utf8'))
        self.assertEqual([r['count'] for r in audit(current)],[1]*9)
        self.assertEqual(sum(c.get('group')=='fifty' for c in current['cases']),50)


if __name__=='__main__':unittest.main()

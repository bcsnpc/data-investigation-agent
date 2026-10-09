"""Human-review draft preserves the old seals and cannot pretend approval."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class OracleDraftTests(unittest.TestCase):
    def test_draft_conserves_every_original_partition_and_sealed_record_hash(self):
        split_path=ROOT/'acceptance/model_steps/intake-round-ten-f-split.json'
        split=json.loads(split_path.read_text())
        draft=json.loads((ROOT/'acceptance/oracle/oracle-draft.json').read_text())
        self.assertEqual(draft['status'],'DRAFT_NOT_APPROVED_NOT_SCORED')
        self.assertEqual(draft['source_split_sha256'],hashlib.sha256(split_path.read_bytes()).hexdigest())
        expected={r['id']:(part,r['record_hash']) for part in ('dev','held_out') for r in split[part]}
        self.assertEqual(len(draft['records']),68)
        self.assertEqual({r['id']:(r['partition'],r['golden_record_hash']) for r in draft['records']},expected)
        for row in draft['records']:
            self.assertEqual(row['approvals'],{'owner':None,'reviewer':None})
            self.assertEqual(row['review_status'],'PENDING_OWNER_AND_INDEPENDENT_REVIEWER')
            for field in ('true_target_and_cell','true_reported_figure','true_comparison_route','true_report_and_page'):
                value=row[field]
                if value['state']=='UNDETERMINED':
                    self.assertNotIn('value',value);self.assertTrue(value['reason'])

    def test_pure_business_meaning_cannot_ask_into_an_investigation(self):
        draft=json.loads((ROOT/'acceptance/oracle/oracle-draft.json').read_text())
        rows=[r for r in draft['records'] if r['authored_question_kind']=='BUSINESS_MEANING']
        self.assertTrue(rows)
        for row in rows:
            self.assertEqual(row['legitimate_questions'],[])
            self.assertEqual(row['required_disposition']['value'],'BUSINESS_VALIDATION')


if __name__=='__main__':unittest.main()

"""Human-review draft preserves the old seals and cannot pretend approval."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class OracleDraftTests(unittest.TestCase):
    def test_owner_amendment_diff_accounts_for_every_changed_field(self):
        root=ROOT/'acceptance/oracle'
        before=json.loads((root/'oracle-draft-before-owner-review.json').read_text())
        # This diff documents the earlier owner review. A1 is a separate,
        # later approved amendment, with its own exhaustive diff test.
        sealed_review=root/'oracle-before-a1.json'
        self.assertEqual(hashlib.sha256(sealed_review.read_bytes()).hexdigest(),
                         'be029b56a6de27195dac507bfb5010f0ce7abc2732702d9a230e5f4a8d38406c')
        after=json.loads(sealed_review.read_text())
        diff=json.loads((root/'oracle-approval-diff.json').read_text())
        changes={r['id']:r['fields'] for r in diff['changes']}
        for old,new in zip(before['records'],after['records']):
            self.assertEqual(old['id'],new['id'])
            self.assertEqual(old['golden_record_hash'],new['golden_record_hash'])
            expected={k:{'before':old.get(k),'after':new.get(k)} for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}
            self.assertEqual(changes.get(old['id'],{}),expected)
        self.assertEqual(hashlib.sha256((root/'oracle-draft-before-owner-review.json').read_bytes()).hexdigest(),
                         '0bce64af7690c4fc86b7e9bfd2e796d80dfc5a3aadf1154f605cac21254e11dd')

    def test_r1_is_not_inferred_from_measure_identity_or_missing_definitions(self):
        rows=json.loads((ROOT/'acceptance/oracle/oracle-draft.json').read_text())['records']
        for row in rows:
            value=row['true_target_and_cell'].get('value',{})
            if value.get('kind')!='MEASURE_AT_SCOPE':continue
            proof=row['scope_equivalence_review']
            self.assertEqual(proof['status'],'VERIFIED_EQUIVALENT_DECLARED_SCOPE')
            self.assertTrue(proof['retained_context_id']);self.assertTrue(proof['retained_context_hash'])
            scopes=proof['candidate_scopes'];self.assertTrue(scopes)
            self.assertTrue(all(s['restrictions']==scopes[0]['restrictions'] for s in scopes))
            self.assertFalse(any(q['field']=='NUMBER' for q in row['legitimate_questions']))

    def test_reviewer_rules_preserve_cant_tell_and_never_invent_a_primary_number(self):
        rows={r['id']:r for r in json.loads((ROOT/'acceptance/oracle/oracle-draft.json').read_text())['records']}
        for name in ('refusal-two-figures','refusal-two-figures-total'):
            row=rows['original:'+name]
            self.assertEqual(row['true_reported_figure']['value']['state'],'AMBIGUOUS')
            self.assertIsNone(row['true_reported_figure']['value']['selected_value'])
            self.assertEqual([q['field'] for q in row['legitimate_questions']],['FIGURE'])
            self.assertEqual(row['required_disposition']['value'],'HOLD_TWO_REPORTED_FIGURES')
        for name in ('question-change-days','question-change-week'):
            row=rows['original:'+name];self.assertEqual(row['legitimate_questions'],[])
            self.assertEqual(row['required_disposition']['value'],'UNSUPPORTED_ROUTE')
        for row in rows.values():
            if 'family-I' in row['id']:
                self.assertEqual(row['true_comparison_route']['value'],'APPLICATION')
                self.assertEqual(row['business_disposition']['value'],'BUSINESS_VALIDATION')

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

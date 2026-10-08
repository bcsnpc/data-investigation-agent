"""An earned roster cannot turn a wrong answer or missing output into a pass."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from check import grade, corrected_case


def refusal():
    output = {'explanation': {'text': 'You asked: synthetic question.\nAnswer to your question: Not answered.\n\nThe request needs clarification.'}}
    return {'intake': {'status': 'NEEDS_INPUT', 'refusal_outputs': {
        'business_output': copy.deepcopy(output), 'technical_output': copy.deepcopy(output)}}}


class SealedExpectationTest(unittest.TestCase):
    def test_human_corrections_keep_sealed_files_and_unapproved_columns_unchanged(self):
        root=Path(__file__).resolve().parents[2]
        revisions=json.loads((root/'acceptance/tickets/round-ten/expectation-corrections.json').read_text())['corrections']
        self.assertEqual({r['id'] for r in revisions},{'family-F-terse','family-F-typo','question-hiding-rows'})
        for r in revisions:
            raw=(root/('acceptance/tickets/round-ten/'+r['id']+'.json')).read_bytes()
            original=json.loads(raw);updated=corrected_case(original,raw,[r])
            self.assertEqual(original['expectation_columns'][r['column']],r['before'])
            self.assertEqual(updated['expectation_columns'][r['column']],r['after'])
            if r['id'].startswith('family-F-'):
                self.assertEqual(r['reason'],'boundary consistency does not answer a mechanism question')
                self.assertEqual(r['after']['answer_category'],'NOT_ANSWERED')
            else:
                self.assertEqual(r['after']['outcome'],'DECLARED_FILTER_EFFECTS')
                self.assertIn('authorized placeholder',r['reason'])
            for column in original['expectation_columns']:
                if column != r['column']:
                    self.assertEqual(original['expectation_columns'][column],updated['expectation_columns'][column])
            with self.assertRaisesRegex(ValueError,'SOURCE_HASH'):
                corrected_case(original,raw+b' ',[r])
    def test_all_fifty_authored_files_preserve_the_pre_run_byte_seal(self):
        root = Path(__file__).resolve().parents[2]
        index = json.loads((root / 'acceptance/tickets/round-ten/index.json').read_text())
        self.assertEqual(len(index['entries']), 50)
        for entry in index['entries']:
            with self.subTest(ticket=entry['id']):
                self.assertEqual(hashlib.sha256((root / entry['path']).read_bytes()).hexdigest(), entry['sha256'])

    def test_honest_refusal_passes_and_missing_output_does_not(self):
        case = {'expectation_columns': {'stripped': {'accepted_dispositions': ['NEEDS_INPUT']}}}
        run = refusal()
        self.assertTrue(grade(case, 'stripped', run)['passed'])
        del run['intake']['refusal_outputs']['technical_output']
        self.assertIn('technical_output:MISSING_OUTPUT', grade(case, 'stripped', run)['errors'])

    def test_technical_finding_cannot_earn_a_required_refusal(self):
        case = {'expectation_columns': {'stripped': {'accepted_dispositions': ['CAPABILITY_REFUSAL']}}}
        run = {'session': {'status': 'COMPLETED', 'assessment': {'classification': 'DEFECT'},
                           'synthesis': {'status': 'COMPLETED', 'outputs': refusal()['intake']['refusal_outputs']}}}
        with patch('check.answer_category', return_value='NOT_ANSWERED'):
            self.assertIn('REQUEST_NOT_REFUSED', grade(case, 'stripped', run)['errors'])

    def test_earned_artifact_does_not_replace_authored_outcome(self):
        expected = {'status': 'COMPLETED', 'outcome': 'TRANSFORMATION_LOGIC', 'answer_category': 'NOT_ANSWERED'}
        case = {'expectation_columns': {'stripped': expected}}
        run = {'session': {'status': 'COMPLETED', 'assessment': {'classification': 'DEFECT'},
                           'synthesis': {'status': 'COMPLETED', 'outputs': refusal()['intake']['refusal_outputs']}}}
        before = copy.deepcopy(case)
        with patch('check.answer_category', return_value='NOT_ANSWERED'):
            self.assertIn('OUTCOME_CHANGED', grade(case, 'stripped', run)['errors'])
        self.assertEqual(case, before)

    def test_failed_synthesis_is_not_an_end_to_end_pass(self):
        case = {'expectation_columns': {'stripped': {'status': 'COMPLETED', 'outcome': 'TRANSFORMATION_LOGIC', 'answer_category': 'NOT_ANSWERED'}}}
        run = {'session': {'status': 'COMPLETED', 'assessment': {'classification': 'TRANSFORMATION_LOGIC'},
                           'synthesis': {'status': 'FAILED'}}}
        with patch('check.answer_category', return_value='NOT_ANSWERED'):
            self.assertIn('SYNTHESIS_NOT_COMPLETED', grade(case, 'stripped', run)['errors'])


if __name__ == '__main__':
    unittest.main()

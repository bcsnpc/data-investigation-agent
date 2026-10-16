"""Historical policy is exact and cohort-bound; current defects stay visible."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check
import historical_policy


def sample():
    text = 'You asked: Why?\nAnswer to your question: Not answered.\n\nThe engine stops before compiling a quantity.'
    mechanism = 'The engine stops before compiling a quantity.'
    outputs = {k: {'explanation': {'text': text}} for k in ('business_output', 'technical_output')}
    outputs['technical_output'].update(question_account={'status': 'NOT_ANSWERED'},
                                      model_mechanism={'text': mechanism})
    run = {'session': {'status': 'COMPLETED', 'assessment': {'classification': 'NO_KNOWN_PATTERN'},
                       'synthesis': {'status': 'COMPLETED', 'outputs': outputs}}}
    case = {'expectation_columns': {'stripped': {'status': 'COMPLETED',
              'outcome': 'NO_KNOWN_PATTERN', 'answer_category': 'NOT_ANSWERED'}}}
    return case, run


class HistoricalPolicyTests(unittest.TestCase):
    def test_real_archived_policy_accepts_phrase_current_policy_rejects(self):
        case, run = sample()
        policy = json.loads(historical_policy.POLICY.read_text())
        self.assertTrue(historical_policy.grade(policy, case, 'stripped', run)['passed'])
        current = check.grade(case, 'stripped', run)
        self.assertIn('technical_output:FORM:Mechanism contains an engine-owned limitation', current['errors'])

    def test_changed_structured_field_fails_both_policies(self):
        case, run = sample()
        run['session']['assessment']['classification'] = 'TRANSFORMATION_LOGIC'
        old = historical_policy.grade(json.loads(historical_policy.POLICY.read_text()), case, 'stripped', run)
        current = check.grade(case, 'stripped', run)
        self.assertIn('OUTCOME_CHANGED', old['errors'])
        self.assertIn('OUTCOME_CHANGED', current['errors'])

    def test_roster_and_exact_entry_are_required(self):
        roster = HERE / 'earned-1.json'
        selected = json.loads(roster.read_text())['entries'][0]
        self.assertIsNotNone(historical_policy.select(roster, selected))
        changed = copy.deepcopy(selected)
        changed['tape_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'HISTORICAL_COHORT_ENTRY_DIFFERS'):
            historical_policy.select(roster, changed)
        with tempfile.TemporaryDirectory() as folder:
            new = Path(folder) / 'new.json'
            new.write_text(json.dumps({'entries': [selected]}))
            self.assertIsNone(historical_policy.select(new, selected))

    def test_archived_checker_hash_cannot_be_substituted(self):
        case, run = sample()
        policy = json.loads(historical_policy.POLICY.read_text())
        policy['checker_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'HISTORICAL_POLICY_CHECKER_DIFFERS'):
            historical_policy.grade(policy, case, 'stripped', run)


if __name__ == '__main__':
    unittest.main()

import unittest
from copy import deepcopy
from investigator.conclusion_contract import fields, validate, render


class ConclusionTests(unittest.TestCase):
    def value(self):
        return dict(direct_answer='The total is higher because the implemented measure sums units, not records.',
                    verdict_class='AS DESIGNED', verdict='as designed',
                    calculation_explanation='The retained measure adds the units column without a record-count operation.',
                    undecided=[], routing='BUSINESS_OWNER',
                    context_gap={'type': 'metric definition', 'note': 'Whether the label is intended to mean units or records.'})

    def test_direct_answer_and_rule_survive_delivery(self):
        value = self.value()
        rendered = render(validate(value, {'intake': {}}))
        self.assertTrue(rendered.startswith(value['direct_answer']))
        self.assertIn(value['calculation_explanation'], rendered)
        self.assertEqual(len(fields()), 6)

    def test_incidental_join_cannot_be_labelled_as_designed_with_old_verdict(self):
        value = self.value(); value['verdict'] = 'transformation logic'
        with self.assertRaisesRegex(ValueError, 'IMPLEMENTED_RULE_VERDICT'):
            validate(value, {})

    def test_unresolved_names_what_is_missing(self):
        value = self.value(); value.update(verdict_class='UNRESOLVED', verdict='not found')
        with self.assertRaisesRegex(ValueError, 'MISSING_EVIDENCE'):
            validate(value, {})
        value['undecided'] = ['The earlier native snapshot is outside the observed retention period.']
        self.assertEqual(validate(value, {})['verdict_class'], 'UNRESOLVED')

    def test_explicit_target_not_overridden_by_same_number_elsewhere(self):
        case = {'intake': {'visual': 'other'}, 'context': {'explicit_target': {'visual': 'chosen'}}}
        with self.assertRaisesRegex(ValueError, 'EXPLICIT_TARGET_CHANGED:visual'):
            validate(self.value(), case)

    def test_input_not_mutated_and_context_gap_record_only(self):
        value = self.value(); before = deepcopy(value)
        checked = validate(value, {})
        checked['context_gap']['note'] = 'changed copy'
        self.assertEqual(value, before)


if __name__ == '__main__':
    unittest.main()

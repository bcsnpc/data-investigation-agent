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

    def test_implemented_access_rule_is_compatible_with_question_class(self):
        from investigator.regression_features import configured
        value = self.value()
        value.update(verdict='access difference', direct_answer='The view uses the caller mapping.',
                     calculation_explanation='The retained mapping yields 10/1 and 25/2.')
        self.assertEqual(validate(value, {})['verdict_class'], 'AS DESIGNED')
        with configured({'r27_conclusion_detail_compatibility': False}):
            with self.assertRaisesRegex(ValueError, 'IMPLEMENTED_RULE_VERDICT'):
                validate(value, {})
            self.assertNotIn('description', fields()['verdict_class'])

    def test_current_record_absence_does_not_require_an_unresolved_label(self):
        value = self.value()
        value.update(verdict='not found', direct_answer='The current record is absent at every checked layer.')
        self.assertEqual(validate(value, {})['verdict_class'], 'AS DESIGNED')
        value['verdict_class'] = 'DEVIATION'
        with self.assertRaisesRegex(ValueError, 'DEVIATION_REQUIRES'):
            validate(value, {})

    def test_explicit_target_not_overridden_by_same_number_elsewhere(self):
        case = {'intake': {'visual': 'other'}, 'context': {'explicit_target': {'visual': 'chosen'}}}
        with self.assertRaisesRegex(ValueError, 'EXPLICIT_TARGET_CHANGED:visual'):
            validate(self.value(), case)

    def test_input_not_mutated_and_context_gap_record_only(self):
        value = self.value(); before = deepcopy(value)
        checked = validate(value, {})
        checked['context_gap']['note'] = 'changed copy'
        self.assertEqual(value, before)

    def test_invalid_or_missing_record_only_tag_never_suppresses_valid_answer(self):
        for tag in [None, 'malformed provider field', 3, [], {'type':'invented','note':'x'}, {'type':'other','note':' '}]:
            with self.subTest(tag=tag):
                value=self.value();value['context_gap']=tag;before=deepcopy(value)
                checked=validate(value,{})
                self.assertEqual(value,before)
                self.assertEqual(checked['direct_answer'],value['direct_answer'])
                self.assertEqual(checked['verdict_class'],'AS DESIGNED')
                self.assertIn('UNRECORDED_CONTEXT_GAP',checked['context_gap']['note'])
                self.assertNotIn('UNRECORDED_CONTEXT_GAP',render(checked))
        value=self.value();del value['context_gap']
        self.assertIn('UNRECORDED_CONTEXT_GAP',validate(value,{})['context_gap']['note'])

    def test_record_only_tag_flag_restores_old_strict_contract_independently(self):
        from investigator.regression_features import configured
        from jsonschema import ValidationError
        value=self.value();value['context_gap']='invalid'
        with configured({'r27_context_gap_nonblocking':False}):
            with self.assertRaises(ValidationError):validate(value,{})

    def test_bad_metadata_does_not_disable_target_or_verdict_checks(self):
        value=self.value();value['context_gap']='invalid';value['verdict_class']='DEVIATION'
        with self.assertRaisesRegex(ValueError,'DEVIATION_REQUIRES'):validate(value,{})
        value=self.value();value['context_gap']='invalid'
        with self.assertRaisesRegex(ValueError,'EXPLICIT_TARGET_CHANGED'):
            validate(value,{'intake':{'visual':'other'},'context':{'explicit_target':{'visual':'chosen'}}})

    def test_limit_keeps_observations_and_names_missing_layer_without_success_upgrade(self):
        from investigator.terminal_findings import attach
        query={'id':'q1','layer':'serving','purpose':'recreate','status':'SUCCEEDED',
               'row_count':1,'text':'SELECT SUM(units) FROM dbo.Items','result':{'rows':[{'value':7}]}}
        result=attach({'status':'UNRESOLVED','business':'Limit reached.','stop':'TOOL_OR_TIME_LIMIT'},
                      queries=[query],context={'conclusion_contract':'question-first-v1',
                      'layers':{'serving':{'label':'Serving'},'source':{'label':'Application'}}})
        self.assertEqual(result['status'],'UNRESOLVED')
        self.assertEqual(result['conclusion']['verdict_class'],'UNRESOLVED')
        self.assertIn('Application has not been measured.',result['conclusion']['undecided'])
        self.assertIn('"value": 7',result['business'])
        self.assertIn('q1',result['business'])

    def test_hard_stop_keeps_its_status_and_partial_conclusion(self):
        from investigator.terminal_findings import attach
        result=attach({'status':'BLOCKED','business':'Monthly cap reached.','stop':'MONTHLY_MODEL_EXHAUSTED'},
                      context={'conclusion_contract':'question-first-v1'})
        self.assertEqual(result['status'],'BLOCKED')
        self.assertEqual(result['conclusion']['verdict_class'],'UNRESOLVED')
        self.assertIn('MONTHLY_MODEL_EXHAUSTED',result['conclusion']['undecided'])


if __name__ == '__main__':
    unittest.main()

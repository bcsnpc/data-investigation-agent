import copy,importlib.util,unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('known_acceptance',Path(__file__).resolve().parents[1]/'acceptance/known_domain/check.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)


class AcceptanceGateTests(unittest.TestCase):
    def case(self):
        return {'expected_status':'COMPLETED','expected_outcome':'NO_KNOWN_PATTERN',
            'expected_answer_line':'Answer to your question: Not answered.',
            'required_output_terms':[],'invariants':sorted(gate.INVARIANTS),'acceptance_change_reason':'Initial reviewed scope.'}

    def test_missing_outputs_cannot_be_a_pass_even_with_matching_outcome(self):
        errors=gate.output_checks(self.case(),{'status':'COMPLETED','assessment':{'classification':'NO_KNOWN_PATTERN'}})
        self.assertIn('business_output:MISSING_OUTPUT',errors);self.assertIn('technical_output:MISSING_OUTPUT',errors)

    def test_unknown_invariant_and_unexplained_change_fail_closed(self):
        for change in ('unknown','reason','duplicate'):
            case=self.case()
            if change=='unknown':case['invariants'].append('future_unknown_check')
            elif change=='duplicate':case['invariants'].append(case['invariants'][0])
            else:case['acceptance_change_reason']=''
            with self.assertRaises(ValueError):gate.validate_case(case)

    def test_changed_outcome_and_duplicate_timing_are_detected(self):
        case=self.case();text=case['expected_answer_line']+'\n\nThe checks may describe the same moment. Different update times remain possible.'
        state={'status':'COMPLETED','assessment':{'classification':'CONSISTENT_TO_BOUNDARY'},
            'synthesis':{'outputs':{k:{'explanation':{'text':text}} for k in ('business_output','technical_output')}}}
        errors=gate.output_checks(case,state)
        self.assertIn('OUTCOME_CHANGED',errors);self.assertIn('business_output:REPEATED_TIMING_LIMIT',errors)

    def test_missing_replay_inputs_are_blocked_without_network_or_substitute(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            case={**self.case(),'ticket':'test','source_session_id':'source'}
            result=gate.run_case(case,Path(d),Path(d)/'output')
        self.assertEqual(result['status'],'BLOCKED');self.assertEqual(result['reason'],'MISSING_PRIVATE_REPLAY_INPUTS')
        self.assertEqual(result['network_calls'],0)


if __name__=='__main__':unittest.main()

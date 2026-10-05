import copy,importlib.util,unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('known_acceptance',Path(__file__).resolve().parents[1]/'acceptance/known_domain/check.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)


class AcceptanceGateTests(unittest.TestCase):
    def test_mechanism_role_is_explicit_not_inferred_from_paragraph_position(self):
        case=self.case()
        text=case['expected_answer_line']+'\n\nMeasure: units; boundary facts.\n\nAn engine-rendered paragraph containing a role name.'
        state={'status':'COMPLETED','assessment':{'classification':'NO_KNOWN_PATTERN'},
            'synthesis':{'outputs':{kind:{'explanation':{'text':text}} for kind in ('business_output','technical_output')}}}
        errors=gate.output_checks(case,state,provider_mechanism={'text':'The measured quantity is unchanged.','provenance':'SEALED_PROVIDER_MECHANISM'})
        self.assertFalse(any('LAYER_REFERENCE' in error for error in errors))
        self.assertIn('technical_output:MISSING_MODEL_MECHANISM_PROVENANCE',gate.output_checks(case,state))

    def test_reproduction_grading_does_not_grade_walk_outcome(self):
        case={**self.case(),'grade_kind':'reproduction','expected_reproduction':{
            'cell_id':'cell','label':'REPRODUCED','reproduced_value':'16','reported_state':'NUMBER','reported_value':'16'}}
        state={'status':'COMPLETED','assessment':{'classification':'NO_COMPARABLE_PATH'},'observations':[
            {'check_kind':'DECLARED_CONTEXT_REPRODUCTION','cell':{'id':'cell'},'label':'REPRODUCED',
             'reproduced_value':'16','reported_figure':{'state':'NUMBER','value':'16'}}]}
        errors=gate.output_checks(case,state)
        self.assertNotIn('OUTCOME_CHANGED',errors);self.assertNotIn('REPRODUCTION_CHANGED',errors)
        state['observations'][0]['cell']['id']='other-cell'
        self.assertIn('REPRODUCTION_CHANGED',gate.output_checks(case,state))

    def test_wrong_context_cannot_grade_as_empty(self):
        case={**self.case(),'context_pin':{'context_id':'earned','hash':'a'*64}}
        state={'status':'COMPLETED','envelope':{'context_id':'different'}}
        errors=gate.output_checks(case,state,pinned_context={'context_id':'different','hash':'b'*64})
        self.assertIn('CONTEXT_ID_CHANGED',errors);self.assertIn('CONTEXT_HASH_NOT_ESTABLISHED',errors)

    def case(self):
        return {'context_pin':{'context_id':'00000000-0000-4000-8000-000000000000','hash':'a'*64},'expected_status':'COMPLETED','expected_outcome':'NO_KNOWN_PATTERN',
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

"""Claim-basis admission must not convert inferred intent into authority."""
import copy
import unittest
from investigator import assessment_support, dynamic_reasoning


class AssessmentSupportTests(unittest.TestCase):
    def setUp(self):
        self.observations={'q':{'tool':'bounded_sql','status':'COMPLETED','completeness':'COMPLETE_RESPONSE'},
                           'm':{'tool':'context','status':'COMPLETED','completeness':'COMPLETE_RESPONSE'}}
        self.assessment={'classification':'LIKELY_TECHNICAL_DEFECT','evidence_ids':['q','m'],
            'support':{'mechanism':'Observed matching rows multiply the input.',
                       'mechanism_evidence_ids':['q'],'intent_dependency':'NOT_REQUIRED',
                       'intent_basis':'The claim is limited to measured multiplication, not the correct business total.',
                       'intent_evidence_ids':[],'measure_connection':'NOT_ESTABLISHED_CAPABILITY',
                       'measure_connection_basis':'The available source read was not bound to the reported measure.',
                       'measure_connection_evidence_ids':[],'remaining_test':'Check whether version selection is intended.'}}

    def test_unknown_intent_cannot_support_defect_or_expected_behavior(self):
        self.assessment['support']['intent_dependency']='UNKNOWN'
        for label in ('LIKELY_TECHNICAL_DEFECT','EXPECTED_BEHAVIOR','SOURCE_OR_APPLICATION_ISSUE','REFRESH_OR_FRESHNESS_ISSUE'):
            self.assessment['classification']=label
            with self.assertRaisesRegex(ValueError,'unknown business intent'):
                assessment_support.validate(self.assessment,self.observations)
        self.assessment['classification']='BUSINESS_CONTEXT_REQUIRED'
        assessment_support.validate(self.assessment,self.observations)

    def test_failed_partial_and_metadata_only_mechanism_are_not_live_support(self):
        for change in ({'status':'FAILED'},{'completeness':'PARTIAL'},{'tool':'context'}):
            observations=copy.deepcopy(self.observations);observations['q'].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):
                assessment_support.validate(self.assessment,observations)

    def test_established_intent_requires_citation_but_does_not_certify_it(self):
        self.assessment['support']['intent_dependency']='ESTABLISHED'
        with self.assertRaisesRegex(ValueError,'cited evidence'):
            assessment_support.validate(self.assessment,self.observations)
        self.assessment['support']['intent_evidence_ids']=['m']
        assessment_support.validate(self.assessment,self.observations)
        self.assertNotIn('provenance',self.assessment['support'])

    def test_support_citations_must_be_declared_and_successful(self):
        for refs in (['missing'],['q',{}],['q']*9):
            self.assessment['support']['mechanism_evidence_ids']=refs
            with self.subTest(refs=refs),self.assertRaises(ValueError):
                assessment_support.validate(self.assessment,self.observations)

    def test_provider_decision_cannot_omit_support(self):
        with self.assertRaises(ValueError):
            dynamic_reasoning.from_wire({'next':{'kind':'STOP','assessment':{'classification':'BUSINESS_CONTEXT_REQUIRED','claim':'Unknown','evidence_ids':[],'alternatives':['Unknown'],'limits':['Unknown']}},'hypotheses':[]},{})

    def test_wire_requires_support_without_changing_historical_assessments(self):
        schema=dynamic_reasoning.wire_schema([],[],[])
        stop=next(x for x in schema['properties']['next']['anyOf'] if x['properties']['kind']['enum']==['STOP'])
        self.assertIn('support',stop['properties']['assessment']['required'])
        assessment_support.validate(self.assessment,self.observations)

    def test_established_measure_connection_needs_a_contribution_or_admitted_mapping(self):
        self.assessment['support']['measure_connection']='ESTABLISHED'
        self.assessment['support']['measure_connection_evidence_ids']=['q']
        with self.assertRaisesRegex(ValueError,'test contribution'):
            assessment_support.validate(self.assessment,self.observations)
        self.observations['q']['test_purpose']='TEST_CONTRIBUTION'
        assessment_support.validate(self.assessment,self.observations)

    def test_honest_uncertainty_needs_no_measure_connection_evidence(self):
        self.assessment['classification']='BUSINESS_CONTEXT_REQUIRED'
        self.assessment['support']['intent_dependency']='UNKNOWN'
        self.assessment['support']['measure_connection']='NOT_ASSERTED'
        self.assessment['support']['measure_connection_evidence_ids']=[]
        assessment_support.validate(self.assessment,self.observations)


if __name__=='__main__':unittest.main()

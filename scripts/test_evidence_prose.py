import copy
import unittest
from jsonschema import Draft202012Validator, ValidationError
from investigator import evidence_prose, evidence_synthesis, proposal_repairs
from investigator import synthesis_narrative, proposal_limits as limits
import test_synthesis_narrative as narrative_fixture
import test_substantive_business_output as business_fixture
from investigator.output_contract import business_text


class EvidenceProseTests(unittest.TestCase):
    def test_boundary_and_incomplete_endings_are_rejected_without_changes(self):
        for size in (limits.ASSESSMENT_DETAIL,limits.ASSESSMENT_CLAIM):
            good='A'*(size-1)+'.'
            evidence_prose.validate(good,size)
            Draft202012Validator(evidence_prose.schema(size)).validate(good)
            for bad in (good+'x','A'*(size-1)+',','A'*(size-1)+'x','The limitation is...',
                        'The limitation is …','The evidence is limited because.'):
                with self.subTest(bad=bad[-30:]),self.assertRaises(ValueError):
                    evidence_prose.validate(bad,size)

    def test_assembly_rejects_partial_technical_text_and_partial_limitations(self):
        helper=narrative_fixture.NarrativeContractTests();state,payload=helper.source('CONSISTENT_TO_BOUNDARY')
        for location in ('technical_output','limitation'):
            value=helper.response(payload)
            target=value['limitations'][0] if location=='limitation' else value[location]
            target['text']='Observed agreement does not establish source-record correctness, duplicate-row,'
            original=copy.deepcopy(value)
            with self.assertRaises((ValueError,ValidationError)):
                synthesis_narrative.assemble(synthesis_narrative.Response(value),payload,state)
            self.assertEqual(value,original)

    def test_immediate_divergence_also_shows_both_verified_numbers(self):
        p=business_fixture.BusinessFactsTests().payload()
        p['evidence'].append({'id':'input','provenance':{'receipt_seal':'sealed'},'verified_quantity':{'quantity':'8200'}})
        p['evidence'][3]['result']['values_equal']=False
        value=business_text('NO_KNOWN_PATTERN',p)
        self.assertIn('8,765',value);self.assertIn('8,200',value)
        self.assertIn('between the report and the information it reads',value)
        self.assertNotIn('7,661',value)

    def test_all_former_prose_cutters_preserve_and_reject(self):
        for field,size in (('claim',1000),('alternatives',500),('limits',500)):
            value={field:['x'*(size+1)] if field!='claim' else 'x'*(size+1)}
            original=copy.deepcopy(value)
            with self.assertRaises(ValueError):evidence_synthesis.normalize(value)
            self.assertEqual(value,original)
            repaired,_=proposal_repairs.repair({'assessment':value})
            self.assertEqual(repaired['assessment'],original)
        for field in ('mechanism','intent_basis','measure_connection_basis','remaining_test'):
            value={'support':{field:'x'*501}};original=copy.deepcopy(value)
            with self.assertRaises(ValueError):evidence_synthesis.normalize(value)
            self.assertEqual(value,original)

    def test_earlier_number_requires_seal_and_mechanism_requires_unambiguous_definition(self):
        helper=business_fixture.BusinessFactsTests()
        p=helper.payload();p['evidence'][1]['provenance']={}
        self.assertNotIn('7,661',business_text('TRANSFORMATION_LOGIC',p))
        for edit in ('judgment','operation','join_kind'):
            p=helper.payload();result=p['evidence'][2]['result']
            if edit=='judgment':result['judgment']['judgment']='INDETERMINATE'
            if edit=='operation':result['quantity_contract']['operations'].append({'operation':'FILTER'})
            if edit=='join_kind':result['quantity_contract']['operations'][0]['how']='anti'
            self.assertNotIn('counted more than once',business_text('TRANSFORMATION_LOGIC',p))

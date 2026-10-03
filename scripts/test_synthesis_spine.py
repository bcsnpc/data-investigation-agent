import copy
import unittest
from investigator.synthesis_spine import build
from investigator.onboarding import encoded


class RenderedSpineTests(unittest.TestCase):
    def fixture(self, candidates=1, restrictions=1):
        rows=[]
        for n in range(candidates):
            rows.append({'id': 'candidate-'+str(n), 'result': {
                'check_kind': 'DECLARED_CONTEXT_REPRODUCTION',
                'definition_evidence_id':'definition', 'upper_evidence_id':'baseline', 'lower_evidence_id':'read-'+str(n),
                'composed_restrictions':[{'field_id':'field-'+str(i), 'operator':'IN', 'values':['selected']} for i in range(restrictions)],
                'undeclared_context_value':'20', 'reproduced_value':'7', 'reported_figure':{'state':'NUMBER','value':'7','precision':{'state':'EXACT'}},
                'label':'REPRODUCED','comparison_status':'WITHIN_LAYER_CHECK', 'limitations':['Saved defaults were assumed.'],
                'upper_surface_attestation':{'status':'PARTIAL','attested_fields':['identity']},
                'lower_surface_attestation':{'status':'PARTIAL','attested_fields':['identity']},
                'declarations':[{'disposition':'ACTIVE','opaque_provenance':'DO_NOT_SEND_NATIVE_DECLARATION'}],
                'surface_report':{'DO_NOT_SEND_RAW_COLUMN':'x'}}})
        return {'question':'A reported value differs.','scope':{'measure_name':'Count'},'evidence':rows}, {'envelope':{}}

    def test_ten_candidates_ten_restrictions_fit_and_growth_is_linear(self):
        small,state=self.fixture();large,_=self.fixture(10,10)
        a=build(small,state,48000);b=build(large,state,48000)
        self.assertEqual(len(b['candidates']),10)
        self.assertFalse(b['elided'])
        self.assertLess(len(encoded(b)),24000)
        self.assertLess(len(encoded(b)),100*len(encoded(a)))

    def test_raw_evidence_never_crosses_provider_seam_and_originals_unchanged(self):
        payload,state=self.fixture();before=copy.deepcopy(payload)
        wire=build(payload,state,48000)
        self.assertNotIn('DO_NOT_SEND',encoded(wire))
        self.assertEqual(wire['evidence'],[{'id':'candidate-0'}])
        self.assertEqual(payload,before)
        self.assertEqual(wire['candidates'][0]['read_receipt_ids'],['baseline','read-0'])

    def test_oversize_view_names_whole_elisions_instead_of_truncating_or_blocking(self):
        payload,state=self.fixture(20,10)
        wire=build(payload,state,4000)
        self.assertLessEqual(len(encoded(wire)),4000)
        self.assertTrue(wire['elided'])
        self.assertEqual(len(payload['evidence']),20)


if __name__=='__main__':unittest.main()

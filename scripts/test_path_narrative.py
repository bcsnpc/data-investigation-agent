import copy,unittest
from jsonschema import Draft202012Validator
from investigator import path_narrative as path,synthesis_narrative as narrative
import test_substantive_business_output as fixture

class PathNarrativeTests(unittest.TestCase):
    def payload(self):
        p=fixture.BusinessFactsTests().payload()
        p['evidence'].append({'id':'input','provenance':{'receipt_seal':'sealed'},'verified_quantity':{'quantity':'8765'}})
        p['evidence'][3]['result'].update(upper_layer='report',lower_layer='prepared')
        p['evidence'][4]['result'].update(upper_layer='prepared',lower_layer='original')
        p['scope']={'measure_name':'Handled Quantity'}
        return p
    def test_fixed_terms_follow_procedure_direction_and_receipt_quantities(self):
        p=self.payload();facts=path.facts(p)
        self.assertEqual(facts[1]['input'],{'term':'L2','layer':'original','quantity':'7,661'})
        self.assertEqual(facts[1]['output'],{'term':'L1','layer':'prepared','quantity':'8,765'})
        self.assertIn('Measure: Handled Quantity.',path.render(p))
        self.assertIn('Boundary B2 diverges:',path.render(p))
        self.assertIn('Observed input 7,661; observed output 8,765.',path.render(p))
        self.assertIn('L2 (original, upstream input) -> L1 (prepared, downstream output)',path.render(p))
    def test_narrative_cannot_invert_direction_or_redeclare_values(self):
        p=self.payload();wire=narrative.schema(p)['properties']['technical_output']['properties']['text'];v=Draft202012Validator(wire)
        self.assertTrue(v.is_valid(path.summary(p)))
        for bad in ('The higher upstream total is 8765.','prepared feeds original.','L1 is upstream of L2.','Input is 8765 and output is 7661.','The fixed boundary account states input-to-output ordering and observed quantities.','The boundary account describes the comparison.'):
            with self.subTest(bad=bad):self.assertFalse(v.is_valid(bad));self.assertFalse(v.is_valid(path.summary(p)+' '+bad))
        self.assertNotIn('limitations',narrative.schema(p)['properties'])
    def test_no_payload_directory_loss(self):
        p=self.payload();p['context_entry_points']=[{'id':str(i),'kind':'SqlObject'} for i in range(28)];before=copy.deepcopy(p)
        narrative.schema(p);path.render(p);self.assertEqual(p,before)

import copy,unittest
from jsonschema import Draft202012Validator
from investigator import path_narrative as path,synthesis_narrative as narrative
import test_substantive_business_output as fixture

class PathNarrativeTests(unittest.TestCase):
    def test_possibility_is_stated_once_in_both_producer_and_consumer_rules(self):
        validator=Draft202012Validator(path.mechanism_schema(1000))
        for good in ('The join can repeat matching rows.','Matching rows are allowed to multiply at the join.'):
            path.validate_mechanism(good);self.assertTrue(validator.is_valid(good))
        for bad in ('The join can repeat rows and can therefore raise the total.',
                    'Matching rows are allowed to multiply and can duplicate quantities.',
                    'Matches may multiply, and the total can rise.'):
            with self.subTest(text=bad):
                self.assertFalse(validator.is_valid(bad))
                with self.assertRaises(path.RepeatedHedge):path.validate_mechanism(bad)

    def test_non_role_layer_words_refuse_even_when_no_roles_are_declared(self):
        for bad in ('The measure layer repeats matches.','The lower-layer read stops.',
                    'The layers preserve the quantity.'):
            with self.subTest(text=bad):
                self.assertFalse(Draft202012Validator(path.mechanism_schema(1000)).is_valid(bad))
                with self.assertRaises(path.LayerReferenceError):path.validate_declared_layer_tokens(bad,{})

    def test_held_or_reproduction_only_role_identity_does_not_claim_a_read(self):
        p={'evidence':[],'layer_labels':{'model':{'role':'SEMANTIC','business_name':'reported calculation'}}}
        self.assertEqual(path.layer_tokens(p),{'L0 (SEMANTIC)':'model'})
        self.assertIn('L0 (SEMANTIC)',path.render_roles(p))
        self.assertIn('do not establish successful reads',path.render_roles(p))

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

    def test_layers_must_use_the_exact_token_and_role_in_the_spine(self):
        p=self.payload();p['layer_labels']={k:{'role':v} for k,v in
            [('report','SEMANTIC'),('prepared','LANDING'),('original','APPLICATION')]}
        self.assertEqual(path.layer_tokens(p),{'L0 (SEMANTIC)':'report','L1 (LANDING)':'prepared','L2 (APPLICATION)':'original'})
        good='The declared join associates L1 (LANDING) with L2 (APPLICATION).'
        path.validate_layer_references(good,p);path.validate_mechanism(good)
        for bad in ('The application measure repeats matches.','L0 (APPLICATION) repeats matches.',
                    'L7 (LANDING) repeats matches.','L0 repeats matches.','The semantic layer repeats matches.'):
            with self.subTest(text=bad),self.assertRaises(path.LayerReferenceError):path.validate_layer_references(bad,p)

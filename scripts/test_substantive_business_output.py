import copy
import unittest
from investigator.output_contract import business_text, ACTIONS, action
from investigator.synthesis_narrative import schema
from jsonschema import Draft202012Validator, ValidationError


class BusinessFactsTests(unittest.TestCase):
    def payload(self):
        return {'deterministic_process_finding':{'classification':'TRANSFORMATION_LOGIC'},'evidence':[
            {'id':'report','test_purpose':'ESTABLISH_BASELINE','provenance':{'receipt_seal':'sealed'},
             'verified_quantity':{'quantity':'8765'},'result':{'returned_rows':406},
             'asset_name':'movement_values SQL Gold Delta commit'},
            {'id':'a','tool':'process','result':{'comparison_status':'CROSS_SURFACE_VERIFIED',
              'values_equal':True,'referenced_evidence_ids':['report','input']}},
            {'id':'b','tool':'process','result':{'comparison_status':'CROSS_SURFACE_VERIFIED',
              'values_equal':False,'referenced_evidence_ids':['input','earlier']}}]}

    def test_five_sentences_keep_quantity_comparison_limits_action_without_jargon(self):
        payload=self.payload();text=business_text('TRANSFORMATION_LOGIC',payload)
        self.assertIn('8,765',text);self.assertIn('further back found a different total',text)
        self.assertIn('rules out a report-to-input difference',text)
        self.assertIn('earlier information',text);self.assertIn(action('TRANSFORMATION_LOGIC')['text'],text)
        self.assertEqual(len(text.rstrip('.').split('. ')),5)
        for forbidden in ('406','movement_values','SQL','Gold','Silver','Bronze','Delta','aggregate','ingestion','report-id'):
            self.assertNotIn(forbidden,text)
        wire=schema(payload)['properties']['business_output']['properties']['text']
        Draft202012Validator(wire).validate(text)
        with self.assertRaises(ValidationError):Draft202012Validator(wire).validate(text+' SQL')

    def test_only_sealed_scalar_baseline_and_real_cross_surface_agreement_are_used(self):
        for edit in ('seal','quantity','comparison'):
            p=self.payload()
            if edit=='seal':p['evidence'][0]['provenance']={}
            if edit=='quantity':p['evidence'][0]['verified_quantity']={'quantity':'asset SQL 8765'}
            if edit=='comparison':p['evidence'][1]['result']['comparison_status']='WITHIN_LAYER_CHECK'
            text=business_text('NO_KNOWN_PATTERN',p)
            if edit!='comparison':self.assertNotIn('8,765',text)
            if edit!='quantity':self.assertNotIn('rules out',text)
        for outcome in ACTIONS:
            self.assertIn(action(outcome)['text'],business_text(outcome,{}))

    def test_business_enum_does_not_change_directory_coverage(self):
        p=self.payload();p['context_entry_points']=[{'id':str(i),'kind':'SqlObject'} for i in range(11)]
        original=copy.deepcopy(p)
        schema(p)
        self.assertEqual(p,original)

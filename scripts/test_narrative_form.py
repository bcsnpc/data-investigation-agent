import copy
import unittest
from investigator import narrative_form as form
from investigator.output_contract import business_text,action
import test_path_narrative as fixture


class NarrativeFormTests(unittest.TestCase):
    def fixture(self):
        payload=fixture.PathNarrativeTests().payload()
        names={'report':'fabric://workspace/model/table/Sales',
               'prepared':'fabric://workspace/prepared/table/order_totals',
               'original':'fabric://workspace/original/table/Orders'}
        for entry in payload['evidence']:
            result=entry.get('result',{})
            for key in ('upper_layer','lower_layer'):
                if key in result:result[key]=names[result[key]]
        fields=[{'layer':names[layer],'field':field,'evidence_id':receipt}
                for layer,receipt,columns in [('report','read-a',['engine','connection','object']),
                                              ('prepared','read-b',['engine','object']),
                                              ('original','read-c',['engine','object'])]
                for field in columns]
        source={'limits':['Unattested surface field '+x['field']+' on '+x['layer'] for x in fields]+
                ['Comparison 1: SNAPSHOT_UNVERIFIED; agreement does not establish currency.',
                 'Comparison 2: SNAPSHOT_UNVERIFIED; timing was not excluded.',
                 'Intended grain is not established.','Intended grain is not established.'],
                'technical_output':{'unattested_surface_fields':fields}}
        return payload,source,names

    def test_each_typed_limit_once_with_receipt_and_identifiers_only_in_legend(self):
        payload,source,names=self.fixture();original=copy.deepcopy((payload,source))
        text=form.technical('A left join can repeat matches.',payload,source,action('TRANSFORMATION_LOGIC'))
        self.assertLess(text.index('B2 diverges'),text.index('B1 agrees'))
        self.assertLess(text.index('A left join'),text.index('Layers:'))
        self.assertIn('L2 (Orders, upstream input) 7,661 -> L1 (order totals, downstream output) 8,765',text)
        for identity in names.values():self.assertEqual(text.count(identity),1)
        for term,fields,receipt in [('L0','engine, connection, object','read-a'),
                                    ('L1','engine, object','read-b'),('L2','engine, object','read-c')]:
            self.assertEqual(text.count('Unattested '+fields+' on '+term+' (receipt '+receipt+').'),1)
        self.assertEqual(text.count('SNAPSHOT_UNVERIFIED'),1)
        self.assertEqual(text.count('Intended grain is not established.'),1)
        self.assertNotIn('Comparison 1:',text)
        self.assertEqual((payload,source),original)

    def test_business_timing_is_integrated_not_appended_in_schema_language(self):
        payload,_,_=self.fixture()
        body=business_text('TRANSFORMATION_LOGIC',payload)
        self.assertEqual(form.business(body,payload),body)
        for term in ('Comparison 1','verified data version','check nearer the report','snapshot_attestation','SNAPSHOT_UNVERIFIED'):
            self.assertNotIn(term,body)
            with self.subTest(term=term),self.assertRaises(ValueError):form.validate(body+' '+term,True)

    def test_serialized_structures_and_duplicate_limit_lines_are_rejected(self):
        for text in ('{"status":"AVAILABLE"}','[1, 2]','["status"]',"{'status': 'AVAILABLE'}",'[null]',"['one', 'two']"):
            for business in (True,False):
                with self.subTest(text=text,business=business),self.assertRaisesRegex(ValueError,'serialized'):
                    form.validate('Evidence. '+text,business)
        with self.assertRaisesRegex(ValueError,'repeats'):
            form.validate('Limits:\n- Scope unknown.\n- Scope unknown.')

    def test_optional_metadata_is_prose_and_structured_record_is_not_mutated(self):
        payload,source,_=self.fixture()
        payload['evidence'].append({'id':'timing','result':{'refresh_timing':{
            'status':'AVAILABLE','identity_provenance':{'account':'metadata@example.com'},'arbitrary_detail':{'version':3}}}})
        before=copy.deepcopy(payload)
        text=form.technical('A left join can repeat matches.',payload,source,action('TRANSFORMATION_LOGIC'))
        self.assertIn('metadata@example.com (receipt timing)',text)
        self.assertNotIn('arbitrary_detail',text)
        self.assertNotIn('{',text)
        self.assertEqual(before,payload)


if __name__=='__main__':unittest.main()

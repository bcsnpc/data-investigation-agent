import copy
import unittest
from investigator import narrative_form as form
from investigator.output_contract import business_text,action
import test_path_narrative as fixture


class NarrativeFormTests(unittest.TestCase):
    def test_distinct_grades_are_attributed_to_their_own_boundaries(self):
        payload,_,_=self.fixture()
        comparisons=[e for e in payload['evidence'] if e.get('result',{}).get('comparison_status')=='CROSS_SURFACE_VERIFIED']
        for entry,grade in zip(comparisons,('ENGINE_INDEPENDENT','OBJECT_DISTINCT')):
            entry['result']['surface_difference']={'grade':grade}
        original=copy.deepcopy(payload)
        text=form.business(business_text('TRANSFORMATION_LOGIC',payload),payload)
        self.assertIn('For the report and the serving data, the two checks used different calculation engines.',text)
        self.assertIn('For the serving data and the refined data, the checks read different data sources;',text)
        self.assertEqual(payload,original)
        self.assertNotIn('earlier',text.lower())

    def test_source_consistency_has_one_timing_qualification(self):
        payload,_,_=self.fixture()
        text=form.business(business_text('CONSISTENT_TO_SOURCE',payload),payload)
        self.assertEqual(text.count('same moment'),1)
        self.assertNotIn('different update times',text)

    def test_kind_undeclared_reproduction_is_technical_only(self):
        payload,source,_=self.fixture()
        reason='Declared-context reproduction is undeclared for question kind BUSINESS_MEANING.'
        payload['evidence'].append({'id':'not-applicable','result':{
            'check_kind':'DECLARED_CONTEXT_REPRODUCTION_UNAVAILABLE','question_kind':'BUSINESS_MEANING',
            'capability_status':'UNDECLARED','reason':reason}})
        body=business_text('TRANSFORMATION_LOGIC',payload)
        self.assertEqual(form.business(body,payload),body)
        self.assertIn(reason,form.technical('A left join can repeat matches.',payload,source,action('TRANSFORMATION_LOGIC')))

    def fixture(self):
        payload=fixture.PathNarrativeTests().payload()
        names={'report':'fabric://workspace/model/table/Sales',
               'prepared':'fabric://workspace/prepared/table/order_totals',
               'original':'fabric://workspace/original/table/Orders'}
        for entry in payload['evidence']:
            result=entry.get('result',{})
            for key in ('upper_layer','lower_layer'):
                if key in result:result[key]=names[result[key]]
        payload['layer_labels']={names[k]:{'role':r,'business_name':n} for k,r,n in [('report','PRESENTATION','report'),('prepared','SERVING','serving data'),('original','REFINED','refined data')]}
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

    def test_discovered_containers_distinguish_same_named_layers(self):
        from investigator.layer_display import discovered_labels
        payload,source,names=self.fixture()
        assets=[{'id':names['prepared'],'name':'Sales','parent_id':'container-a'},
                {'id':names['original'],'name':'Sales','parent_id':'container-b'},
                {'id':'container-a','name':'Regional reporting'},
                {'id':'container-b','name':'Operational capture'}]
        labels=discovered_labels(assets,[{'id':i} for i in names.values()])
        source['technical_output']['layer_labels']=labels
        registry=form.layers(payload,source)
        self.assertEqual(registry[names['prepared']]['name'],'Sales in Regional reporting')
        self.assertEqual(registry[names['original']]['name'],'Sales in Operational capture')
        self.assertEqual(labels[names['original']]['container_id'],'container-b')
        self.assertEqual(labels[names['original']]['provenance'],'DISCOVERED_PARENT_ID')

    def test_mechanism_cannot_repeat_limits_even_when_model_paraphrases(self):
        from investigator import path_narrative
        from jsonschema import Draft202012Validator
        payload,source,_=self.fixture()
        wire=Draft202012Validator(path_narrative.mechanism_schema(1000))
        for caveat in ('Actual duplicate matches are unconfirmed.',
                       'This does not establish actual repeated matches.',
                       'Both reads might reflect a different snapshot.',
                       'Business intent is unknown.',
                       'We have not confirmed the repeated matches.'):
            text='A left join can multiply rows. '+caveat
            with self.subTest(caveat=caveat):
                self.assertFalse(wire.is_valid(text))
                with self.assertRaisesRegex(ValueError,'limitation'):
                    form.technical(text,payload,source,action('TRANSFORMATION_LOGIC'))
        with self.assertRaisesRegex(ValueError,'limitation'):
            form.technical('A left join can multiply rows. Intended grain is not established.',payload,source,action('TRANSFORMATION_LOGIC'))
        self.assertTrue(wire.is_valid('A left join can multiply rows when several entries match the same key.'))

    def test_retained_judge_clause_coalesces_without_losing_other_limits(self):
        payload,source,_=self.fixture()
        original='The definition does not establish whether duplicate matches occurred or whether both sides use the same snapshot.'
        source['limits'].append(original);before=copy.deepcopy(source)
        text=form.technical('A left join can multiply rows.',payload,source,action('TRANSFORMATION_LOGIC'))
        self.assertIn('The definition does not establish whether duplicate matches occurred.',text)
        self.assertNotIn('both sides use the same snapshot',text)
        self.assertEqual(text.count('SNAPSHOT_UNVERIFIED'),1)
        self.assertEqual(source,before)
        self.assertEqual(form.retained_limit(original,False),original)
        other='The definition does not establish whether duplicate matches occurred or whether a separate audit is complete.'
        self.assertEqual(form.retained_limit(other,True),other)
        assertion='The definition establishes that both sides use the same snapshot.'
        self.assertEqual(form.retained_limit(assertion,True),assertion)


if __name__=='__main__':unittest.main()

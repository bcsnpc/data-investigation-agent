import copy
import unittest
from investigator.adapters.notebook_quantities import DeclaredQuantities
from investigator.adapters.declared_chain import extend
from investigator.business_vocabulary import validate_terms,validate_text
from investigator.output_contract import business_text
from investigator.synthesis_digest import _context_evidence
from investigator.synthesis_narrative import schema
import test_declared_chain_depth as chain_fixture
import test_substantive_business_output as business_fixture
from jsonschema import Draft202012Validator,ValidationError


class VocabularyTests(unittest.TestCase):
    def fixture(self):
        context,layers=chain_fixture.QuantityTraceTests().context()
        code=chain_fixture.definition().replace('events=spark','deliveries=spark').replace('lookup=spark','tariffs=spark').replace('events.join(lookup,','deliveries.join(tariffs,')
        context['assets'][-1]['metadata']['content']=code
        planned,_,_=extend(context,layers)
        contract=planned[2]['quantity_contract'];terms=planned[2]['business_vocabulary']
        p=business_fixture.BusinessFactsTests().payload();p['evidence'][2]['result'].update(quantity_contract=contract,business_vocabulary=terms)
        return p,contract,terms,code

    def test_nouns_have_exact_definition_spans_and_are_not_guessed_from_table_names(self):
        p,contract,terms,code=self.fixture()
        self.assertEqual({v['text'] for v in terms.values()},{'deliveries','tariffs'})
        self.assertEqual(validate_terms(terms,contract),terms)
        text=business_text('TRANSFORMATION_LOGIC',p)
        self.assertIn('8,765 for deliveries',text);self.assertIn('7,661',text)
        self.assertIn('matches deliveries with tariffs',text)
        self.assertIn('Several matching tariffs',text)
        self.assertIn('how deliveries were first entered',text)
        validate_text(text,text)
        for word in ('events','lookup','amount','key','clean','served','information','records'):
            self.assertNotIn(word,text)

    def test_missing_or_ambiguous_labels_are_explicit_not_generic_placeholders(self):
        p,contract,terms,_=self.fixture();p['evidence'][2]['result'].pop('business_vocabulary')
        text=business_text('TRANSFORMATION_LOGIC',p)
        self.assertIn('no usable business names',text)
        self.assertNotIn('information',text)
        self.assertNotIn('deliveries',text)
        validate_text(text,text)

    def test_ungrounded_technical_and_abstract_substitutions_are_rejected(self):
        p,contract,terms,_=self.fixture();expected=business_text('TRANSFORMATION_LOGIC',p)
        for bad in ('other information','the information before the last check','silver','table_name','fabric://id','invented products'):
            with self.subTest(bad=bad),self.assertRaises(ValueError):validate_text(expected.replace('deliveries',bad),expected)
        for bad in ('other information','the information before the last check','silver','table_name','fabric://id'):
            with self.subTest(bad=bad),self.assertRaises(ValueError):validate_text(bad,bad)
        for field,value in (('text','invoices'),('source_start',1),('definition_hash','different')):
            changed=copy.deepcopy(terms);changed['subject'][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):validate_terms(changed,contract)
        wire=schema(p)['properties']['business_output']['properties']['text']
        with self.assertRaises(ValidationError):Draft202012Validator(wire).validate(expected.replace('deliveries','invoices'))

    def test_physical_names_and_multiple_operation_aliases_are_not_promoted(self):
        context,layers=chain_fixture.QuantityTraceTests().context()
        planned,_,_=extend(context,layers)
        self.assertEqual(planned[2]['business_vocabulary'],{}) # lookup is an unusable generic label
        _,_,_,code=self.fixture();frames=DeclaredQuantities(code).writes
        self.assertEqual(frames['served/output'].vocabulary['amount']['subject']['text'],'deliveries')
        self.assertEqual(frames['served/output'].vocabulary['rate']['subject']['text'],'tariffs')

    def test_plain_word_is_allowed_even_when_a_schema_shares_it(self):
        context,layers=chain_fixture.QuantityTraceTests().context()
        _,_,_,code=self.fixture();context['assets'][-1]['metadata']['content']=code
        next(a for a in context['assets'] if a['id']=='clean/events')['name']='deliveries.actual'
        planned,_,_=extend(context,layers)
        self.assertEqual(planned[2]['business_vocabulary']['subject']['text'],'deliveries')

    def test_unrelated_table_or_schema_homonym_cannot_erase_declared_vocabulary(self):
        context,layers=chain_fixture.QuantityTraceTests().context()
        _,_,_,code=self.fixture();context['assets'][-1]['metadata']['content']=code
        before,_,_=extend(context,layers)
        for name in ('Deliveries','tariffs.other'):
            context['assets'].append({'id':name,'kind':'SemanticTable','name':name,
                                      'availability':'CURRENT','metadata':{}})
        after,_,_=extend(context,layers)
        self.assertEqual(after[2]['business_vocabulary'],before[2]['business_vocabulary'])
        self.assertEqual(after[2]['business_vocabulary']['subject']['text'],'deliveries')

    def test_digest_preserves_validated_spans_without_evicting_directory(self):
        p,contract,terms,_=self.fixture()
        observation={'id':'definition','asset_id':contract['definition_asset_id'],'content_hash':contract['definition_hash'],
            'operations':contract['operations'],'quantity_contract':contract,'business_vocabulary':terms,
            'process_roles':['transformation_definition'],'judgment':{'judgment':'EXPLAINS'},'limitation':'Limited.'}
        result=_context_evidence(observation)
        self.assertEqual(result['result']['business_vocabulary'],terms)
        p['context_entry_points']=[{'id':str(i),'kind':'SqlObject'} for i in range(11)]
        before=copy.deepcopy(p);schema(p);self.assertEqual(p,before)

    def test_output_labels_do_not_change_judge_request(self):
        from types import SimpleNamespace
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        _,contract,terms,_=self.fixture();calls=[]
        a=MicrosoftProcessAdapter.__new__(MicrosoftProcessAdapter)
        def judge(payload):
            calls.append(copy.deepcopy(payload))
            return {'status':'COMPLETED','judgment':'EXPLAINS','explains':True,'explanation':'Possible multiplicity.','limitation':'Intent unknown.'}
        a.judge_definition=judge
        boundary={'lower':{'id':'lower','quantity_contract':contract,'business_vocabulary':terms},
                  'upper':{'id':'upper'},'upper_probe':SimpleNamespace(value=10),'lower_probe':SimpleNamespace(value=8)}
        receipt=a.transformation_definition(boundary)['evidence']
        self.assertNotIn('business_vocabulary',calls[0]['definition'])
        self.assertEqual(receipt['business_vocabulary'],terms)


    def test_sales_customers_table_names_remain_business_vocabulary(self):
        context,layers=chain_fixture.QuantityTraceTests().context()
        import json
        context=json.loads(json.dumps(context).replace('events','Sales').replace('lookup','Customers'))
        planned,_,_=extend(context,layers)
        terms=planned[2]['business_vocabulary'];contract=planned[2]['quantity_contract']
        self.assertEqual({v['text'] for v in terms.values()},{'Sales','Customers'})
        validate_terms(terms,contract)
        p=business_fixture.BusinessFactsTests().payload()
        p['evidence'][2]['result'].update(quantity_contract=contract,business_vocabulary=terms)
        text=business_text('TRANSFORMATION_LOGIC',p)
        self.assertIn('Sales',text);self.assertIn('Customers',text);validate_text(text,text)

    def test_identifier_forms_are_rejected_without_catalog_name_matching(self):
        for text in ('app.Sales','Sales_units','Sales_abcdef12','Sales-abcdef12',
                     '[Sales]','receipt-123','C:/data/file','data/file.json',
                     '163ce520-ec47-4824-975c-96f5c749205f'):
            with self.subTest(text=text),self.assertRaises(ValueError):validate_text(text,text)
        for text in ('Sales','Customers','Inventory','Orders','The total is 8,765.'):validate_text(text,text)

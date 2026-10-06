"""Retained PBIR native compilation independent of a model's proposed predicate."""
import copy
import unittest
import test_declared_predicate_adapter as fixture
from investigator.adapters.translation_filter_definition import compile_native
from investigator.adapters.report_predicates import Refusal
from investigator import query_dax


class NativeDefinitionTests(unittest.TestCase):
    setUp = fixture.DeclaredPredicateAdapterTests.setUp
    part = fixture.DeclaredPredicateAdapterTests.part

    def request(self, document):
        return {'definition':{'pbir_filter':document}, 'scope':{'restrictions':[]},
                'metadata':{'native_key_columns':[self.column['id']]},
                'relative':False, 'evaluation_timestamp':None}

    def top(self):
        key = fixture.field(); measure = fixture.field('Sales', 'Revenue', 'Measure')
        selected = copy.deepcopy(key); selected['Name'] = 'key'
        query = {'Version':2, 'From':[{'Name':'c','Entity':'Customers','Type':0},
                 {'Name':'s','Entity':'Sales','Type':0}], 'Select':[selected],
                 'OrderBy':[{'Direction':2,'Expression':measure},{'Direction':1,'Expression':key}], 'Top':3}
        return {'Version':2, 'From':[{'Name':'keys','Expression':{'Subquery':{'Query':query}},'Type':2},
                {'Name':'c','Entity':'Customers','Type':0}],
                'Where':[{'Condition':{'In':{'Expressions':[key],'Table':{'SourceRef':{'Source':'keys'}}}}}]}

    def date(self, *, span=True):
        self.date_column = {'id':'resolved/customers/date','parent_id':self.dimension['id'],
                            'kind':'SemanticColumn','name':'Date','metadata':{'dataType':'dateTime'}}
        self.model['context']['model_assets'].append(self.date_column)
        column = fixture.field('Customers','Date')
        if span: column = {'DateSpan':{'TimeUnit':0,'Expression':column}}
        def boundary(offset):
            return {'DateSpan':{'TimeUnit':0,'Expression':{'DateAdd':{
                'Amount':offset,'TimeUnit':0,'Expression':{'Now':{}}}}}}
        doc = {'Version':2,'From':[{'Name':'c','Entity':'Customers','Type':0}],
               'Where':[{'Condition':{'Between':{'Expression':column,
                        'LowerBound':boundary(-2),'UpperBound':boundary(0)}}}]}
        request = self.request(doc); request.update(relative=True,evaluation_timestamp='2026-10-07T02:30:00+03:00')
        return request

    def test_top_query_uses_retained_order_and_compiles(self):
        request = self.request(self.top()); query = compile_native(self.model,request,{})
        self.assertIn("TOPN(3,VALUES('Customers'[Region]),'Sales'[Revenue],DESC,'Customers'[Region],ASC)",query)
        compiled = query_dax.compile_query(query,self.model['context']['model_assets'])
        self.assertEqual(set(compiled['asset_ids']),{self.column['id'],self.measure['id']})

    def test_unspecified_tie_order_refuses_not_invented(self):
        doc = self.top(); doc['From'][0]['Expression']['Subquery']['Query']['OrderBy'].pop()
        with self.assertRaisesRegex(Refusal,'TIE_ORDER'): compile_native(self.model,self.request(doc),{})

    def test_date_pin_uses_utc_without_live_clock(self):
        request = self.date(); query = compile_native(self.model,request,{})
        self.assertIn('DATE(2026,10,4)',query); self.assertIn('DATE(2026,10,6)',query)
        self.assertIn("INT('Customers'[Date])",query); self.assertNotIn('NOW()',query)
        compiled = query_dax.compile_query(query,self.model['context']['model_assets'])
        self.assertIsNotNone(compiled['compiled_read'])

    def test_bare_column_does_not_gain_day_rounding(self):
        query = compile_native(self.model,self.date(span=False),{})
        self.assertNotIn('INT(',query)

    def test_unknown_date_unit_and_additional_scope_refuse(self):
        request = self.date()
        request['definition']['pbir_filter']['Where'][0]['Condition']['Between']['LowerBound']['DateSpan']['TimeUnit'] = 2
        with self.assertRaisesRegex(Refusal,'DAY_ONLY'): compile_native(self.model,request,{})
        request = self.request(self.top()); request['scope']['restrictions'] = [{'unsupported':True}]
        with self.assertRaisesRegex(Refusal,'ADDITIONAL_SCOPE'): compile_native(self.model,request,{})

    def test_malformed_collected_declaration_refuses_instead_of_crashing(self):
        for field, value in (('From', [None]), ('Where', None)):
            doc = self.top(); doc[field] = value
            with self.assertRaises(Refusal): compile_native(self.model,self.request(doc),{})
        doc = self.top()
        doc['Where'][0]['Condition']['In']['Table']['SourceRef']['Source'] = []
        with self.assertRaises(Refusal): compile_native(self.model,self.request(doc),{})


if __name__ == '__main__': unittest.main()

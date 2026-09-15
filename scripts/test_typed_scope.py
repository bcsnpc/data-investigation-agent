from io import BytesIO
import json
import unittest

from investigator.filter_scope import scalar, compile_filter, catalog
from investigator.native_diagnostics import build
from investigator.capabilities import assess
from investigator.admin_api import create_app
from test_native_diagnostics import fixture
from unittest.mock import MagicMock


class TypedScopeTests(unittest.TestCase):
    def setUp(self):
        self.model,self.plan=fixture()
        for kind in ['dateTime','decimal','int64','boolean','double']:
            self.model['context']['reports'][0]['model_assets'].append({
                'id':kind,'kind':'SemanticColumn','parent_id':'t','name':kind,'metadata':{'dataType':kind}})

    def compile(self,kind,operator,values):
        return compile_filter({'column_id':kind,'operator':operator,'values':values},{'dataType':kind},"'Sales'[value]")

    def test_date_range_half_open_and_blank_excluded(self):
        query=self.compile('dateTime','range',['2024-02-29','2024-03-01'])
        self.assertIn('>=',query);self.assertIn('<(DATE(2024,3,1))',query)
        self.assertIn('NOT(ISBLANK(',query)
        self.assertIn('DATE(2024,2,29)',query)

    def test_datetime_seconds_and_no_timezone_guess(self):
        self.assertIn('TIME(12,34,56)',scalar('2026-09-14T12:34:56','dateTime')[0])
        for value in ['2026-02-30','09/14/2026','2026-09-14T00:00:00Z',
                      '2026-09-14T00:00:00-05:00','2026-09-14T00:00:00.1','1899-12-31']:
            with self.subTest(value=value),self.assertRaises(ValueError):scalar(value,'dateTime')

    def test_decimal_exact_text_and_limits(self):
        self.assertEqual(scalar('-12.3400','decimal')[0],'CURRENCY(-12.3400)')
        for value in [1.2,'1.00001','NaN','Infinity','1e2','1,234','1000000000.0001']:
            with self.subTest(value=value),self.assertRaises(ValueError):scalar(value,'decimal')

    def test_int_boolean_are_not_interchangeable(self):
        self.assertEqual(scalar(False,'boolean')[0],'FALSE()')
        self.assertEqual(scalar(42,'int64')[0],'42')
        for kind,value in [('int64',True),('boolean',1),('int64','42'),('int64',2**53),('double',1.0)]:
            with self.subTest(kind=kind,value=value),self.assertRaises(ValueError):scalar(value,kind)

    def test_blank_distinct_from_zero_empty_and_false(self):
        self.assertIn('{BLANK(),0}',self.compile('int64','in',[None,0]))
        self.assertIn('{BLANK(),FALSE()}',self.compile('boolean','in',[None,False]))
        self.assertIn('{BLANK(),""}',self.compile('string','in',[None,'']))

    def test_duplicates_and_invalid_ranges(self):
        for kind,op,values in [('decimal','in',['1','1.0']),('dateTime','in',['2026-01-01','2026-01-01T00:00:00']),
                               ('int64','range',[1,1]),('int64','range',[2,1]),('int64','range',[None,1]),
                               ('string','range',['a','z']),('boolean','range',[False,True]),('int64','not_in',[1])]:
            with self.subTest(values=values),self.assertRaises(ValueError):self.compile(kind,op,values)

    def test_native_scalar_and_dimension_keep_same_filters(self):
        self.plan['filters'].append({'column_id':'dateTime','operator':'range','values':['2026-01-01','2027-01-01']})
        scalar_request=build(self.model,self.plan)
        self.plan['dimension_id']='c';dim_request=build(self.model,self.plan)
        predicate="FILTER(ALL('O''Brien'[dateTime])"
        self.assertIn(predicate,scalar_request['query']);self.assertIn(predicate,dim_request['query'])
        self.assertEqual(dim_request['filter_scope_version'],'typed-scope-v1')
        self.assertFalse(assess(self.model,self.plan)['verification_eligible'])

    def test_unknown_column_duplicate_column_and_injection(self):
        for spec in [{'column_id':'unknown','operator':'in','values':[1]},
                     {'column_id':'c','operator':'in','values':['USD']},
                     {'column_id':'int64','operator':'in','values':['1); EVALUATE ROW("x",1)']},
                     {'column_id':'int64','operator':'in','values':[1],'query':'arbitrary'}]:
            with self.subTest(spec=spec),self.assertRaises(ValueError):
                build(self.model,dict(self.plan,filters=self.plan['filters']+[spec]))

    def test_legacy_request_shape_preserved(self):
        request=build(self.model,self.plan)
        self.assertNotIn('filter_scope_version',request)
        self.assertIn('TREATAS({"USD"}',request['query'])
        self.plan['filters'][0]['values']=[None]
        with self.assertRaises(ValueError):build(self.model,self.plan)

    def test_scope_catalog_and_api_role(self):
        result=catalog(self.model)
        by_id={c['column_id']:c for c in result['columns']}
        self.assertEqual(by_id['dateTime']['operators'],['in','range'])
        self.assertEqual(by_id['double']['state'],'UNSUPPORTED')
        store=MagicMock();store.get.return_value=self.model;app=create_app(store,'a'*32,'r'*32)
        for token,expected in [('a'*32,'200 OK'),('r'*32,'403 Forbidden')]:
            status=[]
            raw=b''.join(app({'PATH_INFO':'/api/v2/admin/models/model/scope','REQUEST_METHOD':'GET',
                'HTTP_AUTHORIZATION':'Bearer '+token,'wsgi.input':BytesIO()},lambda s,h:status.append(s)))
            self.assertEqual(status[0],expected)
            if token.startswith('a'):self.assertEqual(json.loads(raw)['version'],'typed-scope-v1')


if __name__=='__main__':unittest.main()

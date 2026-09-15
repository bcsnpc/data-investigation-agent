from contextlib import contextmanager, closing
from decimal import Decimal
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from investigator.native_diagnostics import build, extract, run
from investigator.onboarding import Conflict
from run_native_diagnostic import execute


def fixture():
    assets=[{'id':'t','kind':'SemanticTable','name':"O'Brien"},
            {'id':'c','kind':'SemanticColumn','name':'currency','parent_id':'t','metadata':{'dataType':'string'}}]
    assets += [{'id':name,'name':name,'kind':'Measure','parent_id':'t'} for name in ['Unseen ratio','Child']]
    graph={name:{'dependency_state':'SUPPORTED','operations':ops,'dependencies':deps}
           for name,ops,deps in [('Unseen ratio',['RATIO'],['Child']),('Child',['FILTERED_MEASURE'],[])]}
    model={'id':'model','revision':3,'context_id':'ctx','enabled':True,'workspace':'workspace','native_id':'native',
           'context':{'id':'ctx','reports':[{'model_assets':assets}],'semantic_graph':{'measures':graph}}}
    plan={'model_id':'model','revision':3,'context_id':'ctx','measure_ids':['Unseen ratio'],
          'filters':[{'column_id':'c','values':['USD']}],'dimension_id':None,'include_dependencies':False}
    return model,plan


def response(rows):
    return {'results':[{'tables':[{'rows':rows}]}]}


@contextmanager
def database(path):
    with closing(sqlite3.connect(path)) as db:
        with db:yield db


class NativeTests(unittest.TestCase):
    def setUp(self):
        self.model,self.plan=fixture()

    def test_unseen_measure_and_escaped_filter(self):
        self.plan['filters'][0]['values']=['USD"}); EVALUATE ROW("attack",1)']
        query=build(self.model,self.plan)['query']
        self.assertIn("'O''Brien'[Unseen ratio]",query)
        self.assertIn('"USD""}); EVALUATE ROW(""attack"",1)"',query)

    def test_stale_disabled_and_raw_query_rejected(self):
        for change in [{'revision':2},{'context_id':'old'},{'query':'arbitrary DAX'}]:
            with self.subTest(change=change),self.assertRaises(ValueError):build(self.model,dict(self.plan,**change))
        self.model['enabled']=False
        with self.assertRaises(Conflict):build(self.model,self.plan)

    def test_unknown_measure_or_filter_cannot_dispatch(self):
        for change in [{'measure_ids':['fake']},{'filters':[]},{'filters':[{'column_id':'unknown','values':['USD']}]},
                       {'filters':[{'column_id':'c','values':[42]}]}]:
            with self.subTest(change=change),self.assertRaises(ValueError):build(self.model,dict(self.plan,**change))

    def test_dependencies_preserve_context_gap(self):
        self.plan['include_dependencies']=True
        req=build(self.model,self.plan)
        self.assertEqual(req['measure_ids'],['Unseen ratio','Child'])
        self.assertEqual(req['gaps'][0]['measure'],'Child')

    def test_blank_and_exact_decimal(self):
        req=build(self.model,self.plan)
        for value,kind in [(None,'blank'),(Decimal('123456789.0123456789'),'decimal'),(0,'decimal')]:
            result=extract(response([{'[m0]':value}]),req)
            self.assertEqual(result['rows'][0]['[m0]']['type'],kind)
            if value is not None:self.assertEqual(result['rows'][0]['[m0]']['value'],str(value))

    def test_missing_error_and_float_are_not_zero(self):
        req=build(self.model,self.plan)
        for raw in [response([]),response([{}]),{'error':'error'},response([{'[m0]':1.2}]),
                    {'results':[{'tables':[{'rows':[{'[m0]':1}]}],'error':'partial'}]}]:
            with self.subTest(raw=raw),self.assertRaises(ValueError):extract(raw,req)

    def test_dimension_cap_and_empty_are_explicit(self):
        self.plan['dimension_id']='c';req=build(self.model,self.plan)
        self.assertIn('TOPN(501,',req['query'])
        result=extract(response([{'[dimension]':str(i),'[m0]':i} for i in range(501)]),req)
        self.assertEqual(result['completeness'],'PARTIAL');self.assertEqual(len(result['rows']),500)
        self.assertEqual(extract(response([]),req)['rows'],[])

    def test_saved_receipt_and_midflight_disable(self):
        with tempfile.TemporaryDirectory() as directory:
            model=self.model
            class Store:
                def get(self,identity):return model
                def connect(self):return database(Path(directory)/'catalog.sqlite')
            store=Store();calls=[]
            def transport(req):
                calls.append(req)
                with store.connect() as db:self.assertEqual(db.execute('SELECT status FROM native_diagnostics').fetchone()[0],'RUNNING')
                return response([{'[m0]':42}])
            receipt=run(store,self.plan,transport)
            self.assertEqual(receipt['status'],'COMPLETED');self.assertFalse(receipt['result']['root_cause_verified'])
            def changed(req):
                model['enabled']=False
                return response([{'[m0]':42}])
            self.assertEqual(run(store,self.plan,changed)['status'],'HELD')
            self.assertEqual(len(calls),1)

    def test_failure_redacted_and_never_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            store=MagicMock();store.get.return_value=self.model
            store.connect.side_effect=lambda:database(Path(directory)/'catalog.sqlite')
            transport=MagicMock(side_effect=RuntimeError('secret token'))
            receipt=run(store,self.plan,transport)
            self.assertEqual(receipt['status'],'FAILED');transport.assert_called_once()
            self.assertNotIn('secret',json.dumps(receipt))
            transport=MagicMock(side_effect=TimeoutError('remote may still run'))
            self.assertEqual(run(store,self.plan,transport)['status'],'INTERRUPTED')
            transport.assert_called_once()

    @patch('run_native_diagnostic.build_opener')
    @patch('run_native_diagnostic.FabricCliTokens')
    def test_transport_preserves_decimal_json_and_requests_nulls(self,tokens,opener):
        tokens.return_value.get_token.return_value='test-token'
        raw=b'{"results":[{"tables":[{"rows":[{"[m0]":123.123456789012345}]}]}]}'
        opener.return_value.open.return_value.__enter__.return_value.read.return_value=raw
        req=build(self.model,self.plan)
        req.update(workspace='00000000-0000-0000-0000-000000000001',native_model_id='00000000-0000-0000-0000-000000000002')
        result=json.loads(execute(req,'tenant'),parse_float=Decimal)
        self.assertEqual(extract(result,req)['rows'][0]['[m0]']['value'],'123.123456789012345')
        http=opener.return_value.open.call_args.args[0]
        self.assertTrue(json.loads(http.data)['serializerSettings']['includeNulls'])


if __name__=='__main__':unittest.main()

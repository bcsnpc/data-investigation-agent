import io
import json
import unittest
from unittest.mock import patch
import pyarrow as pa

from investigator.adapters.graph_dax_http import arrow_rows, DaxMetadataHttp, SCOPE
from investigator.adapters.graph_dependencies import collect, query
from investigator.adapters import scanner_identity as auth
from test_scanner_guardrails import DECL


def ipc(rows,metadata=None):
    table=pa.Table.from_pylist(rows)
    if metadata:table=table.replace_schema_metadata(metadata)
    out=pa.BufferOutputStream()
    with pa.ipc.new_stream(out,table.schema) as writer:writer.write_table(table)
    return out.getvalue().to_pybytes()


class ArrowTests(unittest.TestCase):
    def test_exact_rows_and_http_200_error_stream(self):
        raw=ipc([{'OBJECT':'M','TABLE':'T'}])
        self.assertEqual(arrow_rows(raw,row_limit=10)['rows'],[{'OBJECT':'M','TABLE':'T'}])
        error=ipc([{'ErrorCode':'denied','ErrorMessage':'Write permission missing'}],{'IsError':'true'})
        result=arrow_rows(raw+error,row_limit=10)
        self.assertEqual(result['status'],'FAILED');self.assertEqual(result['rows'],[])
        self.assertEqual(result['error']['arrow_errors'][0]['rows'][0]['ErrorCode'],'denied')

    def test_trailing_corruption_extra_result_and_row_bound_refused(self):
        raw=ipc([{'x':1}])
        for payload,limit in ((raw+b'garbage',10),(raw+raw,10),(ipc([{'x':1},{'x':2}]),1)):
            with self.assertRaises(Exception):arrow_rows(payload,row_limit=limit)

    def test_new_route_one_meter_exact_request_private_raw_receipt(self):
        captures=[];sends=[];meters=[];scopes=[]
        class Tokens(auth.Tokens):
            def get_token(self,scope):scopes.append(scope);return 'SECRET_TEST_TOKEN'
        class Response(io.BytesIO):
            status=200
            headers={'Content-Type':'application/vnd.apache.arrow.stream'}
        raw=ipc([{'OBJECT':'M'}])
        def send(opener,request,**kw):
            sends.append((request,kw));return Response(raw)
        with auth.job(DECL,['00000000-0000-0000-0000-000000000001'],kind='SCAN'):
            transport=DaxMetadataHttp(Tokens(DECL),'scanner',lambda value:(captures.append(value),'receipt')[1])
        with auth.job(DECL,['00000000-0000-0000-0000-000000000001'],kind='SCAN'), patch('investigator.live_gateway.authorize_http') as authorize, patch('investigator.live_gateway.open_http',side_effect=send):
            got=collect(kind='CALCULATIONS',target={'workspace':'00000000-0000-0000-0000-000000000001',
                'model':'00000000-0000-0000-0000-000000000002'},identity='scanner',gateway=None,
                meter=lambda descriptor,fn:(meters.append(descriptor),fn())[1],transport=transport,
                route='EXECUTE_DAX_QUERIES',semantic_write_permission=True,row_cap=10)
        self.assertEqual(got['status'],'COLLECTED');self.assertEqual(len(meters),1);self.assertEqual(len(sends),1)
        self.assertEqual(scopes,[SCOPE]);self.assertNotIn('SECRET_TEST_TOKEN',json.dumps(captures))
        self.assertEqual(authorize.call_count,1)
        body=json.loads(sends[0][0].data)
        self.assertEqual(body,{'query':query('CALCULATIONS',10),'queryTimeout':60,'resultSetRowCountLimit':11})
        self.assertEqual(sends[0][1]['identity'],'scanner')
        self.assertIn('body_base64',captures[0])


if __name__=='__main__':unittest.main()

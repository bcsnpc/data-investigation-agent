from contextlib import closing
from io import BytesIO
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from urllib.request import Request,urlopen
from wsgiref.simple_server import make_server
from investigation_evidence_api import create_app,EvidenceStore
from serve_investigations import QuietHandler

TOKEN='test-only-'+('x'*40)
FIRST='11111111-1111-1111-1111-111111111111'
SECOND='22222222-2222-2222-2222-222222222222'


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.database=Path(self.folder.name)/'evidence.sqlite'
        with closing(sqlite3.connect(self.database)) as db:
            db.execute('CREATE TABLE investigation_runs(id TEXT PRIMARY KEY,lineage_run TEXT,created TEXT,request TEXT,result TEXT)')
            for identity,date,status in [(FIRST,'2026-09-13T12:00:00Z','NOT_COMPARABLE'),(SECOND,'2026-09-13T11:00:00Z','INSUFFICIENT_EVIDENCE')]:
                db.execute('INSERT INTO investigation_runs VALUES(?,?,?,?,?)',(identity,'graph',date,
                    json.dumps({'kind':'cross_layer_metrics','observations':[]}),
                    json.dumps({'classification':'UNRESOLVED','checks':[{'status':status}]})))
            db.commit()
        self.app=create_app(self.database,TOKEN)

    def tearDown(self):self.folder.cleanup()

    def request(self,path='/api/investigations',query='',method='GET',token=TOKEN):
        captured={}
        def start(status,headers):captured.update(status=status,headers=dict(headers))
        body=b''.join(self.app({'PATH_INFO':path,'QUERY_STRING':query,'REQUEST_METHOD':method,
                              'HTTP_AUTHORIZATION':'Bearer '+token,'wsgi.input':BytesIO()},start))
        return captured,json.loads(body)

    def test_authentication_and_read_only_methods(self):
        self.assertTrue(self.request(token='wrong')[0]['status'].startswith('401'))
        self.assertTrue(self.request(token='non-ascii-\u2603')[0]['status'].startswith('401'))
        self.assertTrue(self.request(method='POST')[0]['status'].startswith('405'))
        with closing(EvidenceStore(self.database).connect()) as db:
            with self.assertRaises(sqlite3.OperationalError):db.execute('DELETE FROM investigation_runs')

    def test_pagination_is_bounded_and_stable(self):
        headers,body=self.request(query='limit=1')
        self.assertEqual(body['items'][0]['id'],FIRST)
        self.assertEqual(body['next_offset'],1)
        self.assertEqual(headers['headers']['Cache-Control'],'no-store')
        body=self.request(query='limit=1&offset=1')[1]
        self.assertEqual(body['items'][0]['id'],SECOND)
        self.assertIsNone(body['next_offset'])
        for query in ('limit=0','limit=101','offset=-1','limit=1&limit=2','sql=SELECT','limit=1;DROP','offset=100001'):
            self.assertTrue(self.request(query=query)[0]['status'].startswith('400'),query)

    def test_detail_preserves_insufficient_and_noncomparable_statuses(self):
        for identity,status in [(FIRST,'NOT_COMPARABLE'),(SECOND,'INSUFFICIENT_EVIDENCE')]:
            headers,body=self.request('/api/investigations/'+identity)
            item=body['investigation']
            self.assertEqual(item['result']['checks'][0]['status'],status)
            self.assertEqual(item['classification'],'UNRESOLVED')
            self.assertFalse(body['capabilities']['execute_queries'])
            self.assertFalse(body['capabilities']['route_defects'])

    def test_missing_and_invalid_ids(self):
        self.assertTrue(self.request('/api/investigations/33333333-3333-3333-3333-333333333333')[0]['status'].startswith('404'))
        for identity in ('../secret','1 OR 1=1',FIRST+'/extra'):
            self.assertTrue(self.request('/api/investigations/'+identity)[0]['status'].startswith('400'))

    def test_missing_store_does_not_create_file_or_leak_path(self):
        missing=Path(self.folder.name)/'private-missing.sqlite'
        self.app=create_app(missing,TOKEN)
        response,body=self.request()
        self.assertTrue(response['status'].startswith('503'))
        self.assertNotIn('private',json.dumps(body))
        self.assertFalse(missing.exists())

    def test_real_http_roundtrip(self):
        with make_server('127.0.0.1',0,self.app,handler_class=QuietHandler) as server:
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                request=Request(f'http://127.0.0.1:{server.server_port}/api/investigations/'+FIRST,
                                headers={'Authorization':'Bearer '+TOKEN})
                with urlopen(request,timeout=5) as response:body=json.load(response)
                self.assertEqual(body['investigation']['id'],FIRST)
            finally:server.shutdown();thread.join(timeout=5)


if __name__=='__main__':unittest.main()

from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from serve_categorical_replay import create_app
from defect_lab import initialize
from test_categorical_filter_replay import definitions,choices,PAGE

class ReplayApiTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name);self.lab=root/'lab.duckdb';initialize(self.lab);self.database=root/'review.sqlite'
        self.app=create_app(self.database,self.lab,definitions(),PAGE,'x'*32)
    def call(self,path,body=None,token='x'*32):
        raw=json.dumps(body).encode();status=[]
        output=b''.join(self.app({'PATH_INFO':path,'REQUEST_METHOD':'GET' if body is None else 'POST','HTTP_AUTHORIZATION':'Bearer '+token,'CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(raw)),'wsgi.input':BytesIO(raw)},lambda s,h:status.append(s)))
        return int(status[0][:3]),json.loads(output)
    def prepare(self):
        status,result=self.call('/api/reviews',{'selections':choices(order_id=['ORD-000001'])});self.assertEqual(status,201);return result
    def test_auth_required_and_choices_listed(self):
        self.assertEqual(self.call('/api/context',token='wrong')[0],401)
        self.assertEqual(len(self.call('/api/context')[1]['fields']),3)
    def test_preview_approval_run_and_replay(self):
        draft=self.prepare();path='/api/reviews/'+draft['id'];body={'confirm':True,'scope_hash':draft['scope_hash']}
        self.assertEqual(self.call(path+'/run',body)[0],409)
        self.assertEqual(self.call(path+'/approve',body)[1]['status'],'APPROVED')
        status,first=self.call(path+'/run',body);self.assertEqual(status,200)
        self.assertEqual(first['result']['selected_records'],1)
        self.assertEqual(self.call(path+'/run',body)[1],first)
    def test_confirmation_and_hash_enforced(self):
        draft=self.prepare();path='/api/reviews/'+draft['id']+'/approve'
        self.assertEqual(self.call(path,{'confirm':False,'scope_hash':draft['scope_hash']})[0],400)
        self.assertEqual(self.call(path,{'confirm':True,'scope_hash':'wrong'})[0],409)
    def test_database_cannot_change_server_scope(self):
        with self.assertRaises(ValueError):create_app(self.database,self.lab.parent/'other.duckdb',definitions(),PAGE,'x'*32)

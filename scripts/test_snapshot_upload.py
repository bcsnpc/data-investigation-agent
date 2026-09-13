import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit, parse_qs
from uuid import uuid4
from upload_source_snapshot import upload


class Response:
    def __init__(self,status,content=b''):self.status_code=status;self.content=content
    def iter_content(self,size):yield self.content


class Session:
    def __init__(self):self.headers={};self.files={};self.calls=[]
    def request(self,method,url,**kwargs):
        self.calls.append((method,url,kwargs));path=urlsplit(url).path;q=parse_qs(urlsplit(url).query)
        if method=='PUT' and q.get('resource')==['directory']:return Response(201)
        if method=='PUT':
            assert kwargs['headers']['If-None-Match']=='*'
            if path in self.files:return Response(412)
            self.files[path]=b'';return Response(201)
        if method=='GET':return Response(200,self.files[path])
        if q['action']==['append']:
            assert int(q['position'][0])==len(self.files[path])
            self.files[path]+=kwargs['data'];return Response(202)
        assert int(q['position'][0])==len(self.files[path]);return Response(200)


class UploadTests(unittest.TestCase):
    def test_create_append_flush_and_safe_retry(self):
        self.exercise(False)

    def test_conflicting_staged_file_never_overwritten(self):
        self.exercise(True)

    def exercise(self,conflict):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);identity=str(uuid4());workspace=str(uuid4());lakehouse=str(uuid4())
            folder=root/'.local/source-snapshots'/identity;folder.mkdir(parents=True)
            (folder/'orders.jsonl').write_bytes(b'["order",null]\n')
            (folder/'manifest.json').write_text(json.dumps({'tables':[{'file':'orders.jsonl'}]}))
            config={'storage':{'database':'unused'},'fabric':{'workspace_id':workspace,'auth':{'tenant_id':str(uuid4())}}}
            estate={'workspace_id':workspace,'bronze_lakehouse_id':lakehouse}
            session=Session()
            if conflict:session.files[f'/{workspace}/{lakehouse}/Files/source_snapshots/{identity}/orders.jsonl']=b'conflict'
            with patch('upload_source_snapshot.ROOT',root),patch('upload_source_snapshot.verify_registered',return_value={'manifest_sha256':'expected'}),patch('upload_source_snapshot.verify'),patch('upload_source_snapshot.FabricCliTokens'),patch('upload_source_snapshot.requests.Session',return_value=session):
                if conflict:
                    with self.assertRaises(ValueError):upload(config,estate,identity)
                    self.assertFalse(any(c[0]=='PATCH' for c in session.calls))
                else:
                    upload(config,estate,identity)
                    before=dict(session.files)
                    session.calls.clear();upload(config,estate,identity)
                    self.assertEqual(before,session.files)
                    self.assertFalse(any(c[0]=='PATCH' for c in session.calls))


if __name__=='__main__':unittest.main()

import io
import json
import sys
import types
import unittest
from unittest.mock import patch

import read_onelake_commit


class Response(io.BytesIO):
    def __enter__(self):return self
    def __exit__(self,*_):self.close()


class Opener:
    def __init__(self):self.requests=[]
    def open(self,request,timeout):
        self.requests.append((request.full_url,dict(request.headers),timeout))
        if 'resource=filesystem' in request.full_url:
            body={'paths':[{'name':'lake/Tables/dbo.events/_delta_log/00000000000000000001.json'}]}
        else:
            body='{"commitInfo":{"timestamp":123,"operation":"WRITE","userName":"redact"}}\n'
        return Response((json.dumps(body) if isinstance(body,dict) else body).encode())


class DeltaCommitTests(unittest.TestCase):
    def test_reads_only_latest_commit_metadata_and_returns_allowlisted_fields(self):
        auth=types.ModuleType('fabric_cli.core.fab_auth')
        auth.FabAuth=lambda:types.SimpleNamespace(get_access_token=lambda scopes,interactive_renew=False:'secret-token')
        opener=Opener()
        modules={'fabric_cli':types.ModuleType('fabric_cli'),'fabric_cli.core':types.ModuleType('fabric_cli.core'),
                 'fabric_cli.core.fab_auth':auth}
        with patch.dict(sys.modules,modules),patch.object(read_onelake_commit,'build_opener',return_value=opener):
            result=read_onelake_commit.read({'workspace':'00000000-0000-0000-0000-000000000001',
                'lakehouse':'00000000-0000-0000-0000-000000000002','table':'dbo.events'})
        self.assertEqual(result['status'],'AVAILABLE')
        self.assertEqual(result['commit_info'],{'timestamp':123,'operation':'WRITE'})
        self.assertEqual(len(opener.requests),2)
        self.assertTrue(all(request[2]==60 for request in opener.requests))
        self.assertNotIn('secret-token',json.dumps(result))

    def test_invalid_table_identity_fails_before_authentication(self):
        with self.assertRaises(ValueError):
            read_onelake_commit.read({'workspace':'00000000-0000-0000-0000-000000000001',
                'lakehouse':'00000000-0000-0000-0000-000000000002','table':'../outside'})


if __name__=='__main__':unittest.main()

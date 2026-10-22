"""Smoke Blob control reuses the run-bound recorder; it gains no CAS scope."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from investigator.daily_smoke import capture_roundtrip
from investigator.run_capture import DurableCapture
from investigator.live_gateway import Gateway,GatewayDenied
from test_process_tape import bootstrap


class RunBoundHealthTests(unittest.TestCase):
    def test_health_roundtrip_works_with_only_run_bound_permission(self):
        account='https://synthetic.blob.core.windows.net';prefix=account+'/captures/round21/'
        gateway=Gateway({'version':1,'live_enabled':True,'identities':{'capture':{
            'role':'platform','runner_captures':[{'account_url':account,'prefix':'round21','run_id':'health-one','max_bytes':1024*1024}]}}})
        objects={};requests=[]
        class Store:
            def __call__(self,key,raw):
                gateway.http('capture','PUT',prefix+key,raw,{'If-None-Match':'*','x-ms-blob-type':'BlockBlob'})
                self_key=prefix+key
                if self_key in objects:raise AssertionError('must be immutable')
                requests.append(('PUT',key));objects[self_key]=raw
            def read(self,key):
                gateway.http('capture','GET',prefix+key)
                requests.append(('GET',key));return objects[prefix+key]
        with tempfile.TemporaryDirectory() as temporary,patch.dict(os.environ,{'DIA_LIVE_ACCESS_DISABLED':'0'}):
            capture=DurableCapture(Path(temporary)/'capture',Store(),run_id='health-one',bootstrap=bootstrap())
            body=b'{"challenge":"fixture-only","kind":"DAILY_SMOKE","run_id":"health-one"}'
            with patch('investigator.daily_smoke._blob_roundtrip',side_effect=AssertionError('CAS must not be used')):
                result=capture_roundtrip(capture,body)
            self.assertEqual(result['status'],'PASS')
            self.assertEqual(result['surface'],'RUN_BOUND_OUTER_CAPTURE')
            self.assertEqual(result['sha256'],hashlib.sha256(body).hexdigest())
            self.assertEqual(requests[-2:],[('PUT',result['record']['key']),('GET',result['record']['key'])])
            self.assertFalse(gateway.identity('capture').get('platform_cas'))
            with self.assertRaises(GatewayDenied):gateway.http('capture','GET',account+'/captures/files/'+'a'*64)
            with self.assertRaises(GatewayDenied):gateway.http('capture','GET',prefix+'health-two/00000003-blob-health.json')
            with self.assertRaisesRegex(ValueError,'UNKNOWN_RECORD'):
                capture.readback({**result['record'],'key':result['record']['key'].replace('health-one','health-two')})
            objects[prefix+result['record']['key']]=b'{}'
            with self.assertRaisesRegex(ValueError,'BYTES_CHANGED'):capture.readback(result['record'])

    def test_missing_readback_transport_is_explicit_not_a_false_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            capture=DurableCapture(Path(temporary)/'capture',lambda *_:None,run_id='no-reader',bootstrap=bootstrap())
            with self.assertRaisesRegex(ValueError,'TRANSPORT_UNAVAILABLE'):capture_roundtrip(capture,b'{}')

if __name__=='__main__':unittest.main()

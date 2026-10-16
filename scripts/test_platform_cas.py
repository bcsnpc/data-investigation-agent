import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from investigator.adapters.platform_cas import bind,payload
from investigator.adapters.blob_artifacts import BlobObjects
from investigator.adapters.guarded_transport import GuardedTransport
from investigator.artifact_store import ArtifactError,canonical,VERSION,CHUNK_SIZE
from investigator.live_gateway import Gateway,GatewayDenied
from test_guarded_blob_transport import Wire

ACCOUNT='https://synthetic.blob.core.windows.net'
POLICY={'version':1,'live_enabled':True,'identities':{'worker:state':{'role':'platform',
    'platform_cas':[{'account_url':ACCOUNT,'container':'tapes'}]}}}


class CasTests(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict(os.environ,{'DIA_LIVE_ACCESS_DISABLED':'0'})
        self.env.start();self.addCleanup(self.env.stop)
        self.raw=b'private synthetic evidence';self.data=gzip.compress(self.raw,mtime=0)
        self.key='chunks/'+hashlib.sha256(self.raw).hexdigest();self.url=ACCOUNT+'/tapes/'+self.key
        self.gate=Gateway(POLICY)
        self.headers={'If-None-Match':'*','x-ms-blob-type':'BlockBlob'}

    def test_unknown_hash_is_bound_only_for_scoped_exact_get_and_immutable_put(self):
        with self.assertRaises(GatewayDenied):self.gate.http('worker:state','GET',self.url)
        with bind(self.gate,'worker:state',ACCOUNT,'tapes',self.key,self.data):
            self.gate.http('worker:state','PUT',self.url,self.data,self.headers)
            self.gate.http('worker:state','GET',self.url)
            for method,url,body,headers in [
                ('DELETE',self.url,None,{}),('HEAD',self.url,None,{}),
                ('GET',self.url+'?comp=metadata',None,{}),
                ('GET',self.url.replace('/tapes/','/captures/'),None,{}),
                ('GET',self.url.replace('synthetic.','otheracct.'),None,{}),
                ('GET',ACCOUNT+'/tapes/chunks/'+'0'*64,None,{}),
                ('PUT',self.url,self.data+b'x',self.headers),('PUT',self.url,self.data,{})]:
                with self.assertRaises(GatewayDenied):self.gate.http('worker:state',method,url,body,headers)
            with patch.dict(os.environ,{'DIA_LIVE_ACCESS_DISABLED':'1'}),self.assertRaises(GatewayDenied):
                self.gate.http('worker:state','GET',self.url)
        with self.assertRaises(GatewayDenied):self.gate.http('worker:state','GET',self.url)

    def test_other_channel_container_account_and_invalid_payload_never_bind(self):
        for channel,account,container in [('reader',ACCOUNT,'tapes'),('worker:state',ACCOUNT,'captures'),
                                         ('worker:state','https://otheracct.blob.core.windows.net','tapes')]:
            with self.assertRaises((GatewayDenied,ArtifactError)):
                with bind(self.gate,channel,account,container,self.key,self.data):self.fail('must refuse')
        for key,data in [('chunks/'+('0'*64),self.data),(self.key+'?x=1',self.data),
                         (self.key,gzip.compress(b'x'*(CHUNK_SIZE+1)))]:
            with self.assertRaises(ArtifactError):payload(key,data)
        policy=copy.deepcopy(POLICY);policy['identities']['worker:state']['role']='reader'
        with self.assertRaises(GatewayDenied):Gateway(policy)

    def test_file_manifest_binding_checks_address_shape_and_chunk_totals(self):
        digest=hashlib.sha256(self.raw).hexdigest()
        value={'version':VERSION,'sha256':digest,'bytes':len(self.raw),'chunk_bytes':CHUNK_SIZE,
               'chunks':[{'sha256':digest,'bytes':len(self.raw)}]}
        payload('files/'+digest,canonical(value))
        value['bytes']+=1
        with self.assertRaises(ArtifactError):payload('files/'+digest,canonical(value))
        value['sha256']='0'*64
        with self.assertRaises(ArtifactError):payload('files/'+digest,canonical(value))

    def test_real_sdk_put_goes_through_bound_gateway_and_private_control_journal(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'receipts.jsonl';wire=Wire()
            original=GuardedTransport
            with patch('investigator.adapters.guarded_transport.GuardedTransport',
                    side_effect=lambda g,i:original(g,i,receipts=path,inner=wire)):
                objects=BlobObjects(ACCOUNT,'tapes',None,channel='worker:state',gateway=self.gate)
                objects.put(self.key,self.data)
            self.assertEqual(wire.sent,[('PUT',self.url)])
            rows=[json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual([r['phase'] for r in rows],['DISPATCHED','RESPONSE'])
            self.assertNotIn(self.raw.decode(),path.read_text())
            with self.assertRaises(GatewayDenied):self.gate.http('worker:state','GET',self.url)


if __name__=='__main__':unittest.main()

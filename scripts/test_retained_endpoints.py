import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from investigator.adapters.retained_endpoints import read, validate


class RetainedEndpointTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.request = {'workspace':'00000000-0000-0000-0000-000000000001',
                        'lakehouse':'00000000-0000-0000-0000-000000000002'}
        endpoint = '00000000-0000-0000-0000-000000000003'
        self.path = Path(self.tmp.name)/'receipt.json'
        self.path.write_text(json.dumps([{'request':self.request,'response':{
            'id':self.request['lakehouse'],'workspaceId':self.request['workspace'],
            'type':'Lakehouse','properties':{'sqlEndpointProperties':{
                'id':endpoint,'connectionString':'reader.test'}}}}]))
        pin = {'version':1,'receipt_path':str(self.path),
               'receipt_sha256':hashlib.sha256(self.path.read_bytes()).hexdigest(),
               'source_context_version':'original','bindings':[{'request':self.request,
               'container_asset_hash':'a'*64,'endpoint_asset_hash':'b'*64}]}
        self.config = {'fabric':{'workspace_id':self.request['workspace'],
            'sql_reader':{'server':'reader.test'},'retained_endpoints':pin}}
        prefix = 'fabric://'+self.request['workspace']+'/'
        self.context = {'version':'approved-cloud','assets':[
            {'id':prefix+self.request['lakehouse'],'kind':'Lakehouse','availability':'CURRENT',
             'content_hash':'a'*64,'provenance':'DISCOVERED'},
            {'id':prefix+endpoint,'kind':'SQLEndpoint','availability':'CURRENT',
             'content_hash':'b'*64,'provenance':'DISCOVERED'}]}

    def test_exact_retained_binding_is_explicit_not_fresh_attestation(self):
        result=read(self.config,self.context,self.request)
        self.assertEqual(result['endpoint_provenance']['kind'],'RETAINED_METADATA')
        self.assertEqual(result['endpoint_provenance']['source_context_version'],'original')
        self.assertNotIn('surface_report',result)

    def test_cloud_input_requires_receipt_at_declared_path_not_only_prepared_copy(self):
        from cloud_runner_context import validate_retained_endpoint_input
        raw=self.path.read_bytes()
        prepared=self.path.parent/'prepared';prepared.mkdir()
        (prepared/'endpoints.json').write_bytes(raw)
        self.path.unlink()
        with self.assertRaisesRegex(ValueError,'CLOUD_ENDPOINT_INPUT_MISSING'):
            validate_retained_endpoint_input(self.config)
        # Packaging installs exactly the retained bytes at the existing pin.
        self.path.write_bytes((prepared/'endpoints.json').read_bytes())
        self.assertEqual(validate_retained_endpoint_input(self.config)['status'],'PINNED_INPUT_PRESENT')
        self.assertEqual(read(self.config,self.context,self.request)['id'],self.request['lakehouse'])
        self.path.write_bytes(raw+b' ')
        with self.assertRaisesRegex(ValueError,'CLOUD_ENDPOINT_INPUT_HASH_DIFFERS'):
            validate_retained_endpoint_input(self.config)

    def test_changed_receipt_refuses(self):
        self.path.write_text(self.path.read_text()+' ')
        with self.assertRaisesRegex(ValueError,'receipt changed'):
            read(self.config,self.context,self.request)

    def test_changed_or_missing_discovery_refuses(self):
        for field,value in [('content_hash','c'*64),('availability','STALE'),('provenance','INFERRED')]:
            with self.subTest(field=field):
                ctx=copy.deepcopy(self.context);ctx['assets'][1][field]=value
                with self.assertRaisesRegex(ValueError,'stale or absent'):
                    read(self.config,ctx,self.request)
        with self.assertRaisesRegex(ValueError,'stale or absent'):
            read(self.config,{'assets':[]},self.request)

    def test_changed_server_refuses_without_fallback(self):
        self.config['fabric']['sql_reader']['server']='other.test'
        with self.assertRaisesRegex(ValueError,'route differs'):
            read(self.config,self.context,self.request)

    def test_unknown_request_never_re_discovers(self):
        with self.assertRaisesRegex(ValueError,'no retained binding'):
            read(self.config,self.context,dict(self.request,lakehouse='other'))

    def test_duplicate_bindings_refuse(self):
        pin=self.config['fabric']['retained_endpoints']
        pin['bindings'].append(copy.deepcopy(pin['bindings'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate'):validate(pin)

if __name__=='__main__':unittest.main()

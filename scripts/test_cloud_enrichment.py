import contextlib
import hashlib
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import cloud_enrichment as worker
from investigator.unified_runner import handlers,KINDS


class CloudEnrichment(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.config={'secret_reference':{'vault_url':'https://kv-fixture.vault.azure.net','secret_name':'anthropic-api-key','secret_version':'a'*32,
            'identity':{'mode':'managed_identity','tenant_id':'aeb4d0a9-e637-4a7e-8efc-63cf0c3827df',
                'client_id':'4a0140cc-f1b5-4b08-852d-8fcab6c130e8','principal_id':'21e3405b-57e9-4581-834e-971b465f80ec'}},
            'gateway_identity':'enrichment','worker_identity':'fixture-worker'}
    def ref(self,name,value):
        path=self.root/name;path.write_text(json.dumps(value));return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    def options(self,operation='submit'):
        result={'operation':operation,'config':self.ref('config.json',self.config),'batch_key':'fixture-batch-1'}
        if operation=='submit':result['tasks']=self.ref('tasks.json',[{'estate':'fixture','subject':'visual','kind':'VISUAL',
            'definition_hash':'b'*64,'definition':'{"value":"SUM(units)"}','neighbours':[],'evidence_ids':['retained-definition']}])
        return result
    def test_registered_typed_handler_and_strict_submit_resume(self):
        self.assertIn('enrichment-batch',KINDS);self.assertIn('enrichment-batch',handlers())
        self.assertEqual(worker.validate_options(self.options())[0],'submit')
        self.assertEqual(worker.validate_options(self.options('resume'))[2],None)
        for invalid in ({**self.options(),'shell':'arbitrary'},{**self.options('resume'),'tasks':{}},{**self.options(),'operation':'delete'}):
            with self.assertRaisesRegex(ValueError,'RUNNER_OPTIONS'):worker.validate_options(invalid)
        options=self.options();Path(options['tasks']['path']).write_text('changed')
        with self.assertRaisesRegex(ValueError,'HASH_DIFFERS'):worker.validate_options(options)
    def test_cloud_execute_records_bodies_and_independent_budget_without_key(self):
        events=[];context=SimpleNamespace(root=self.root,record=lambda kind,value:events.append((kind,value)) or {'key':str(len(events))})
        budget=SimpleNamespace(snapshot=lambda:{'identity':'enrichment:round-twenty-one','ceiling':'25000000','charged':'0'})
        def job(config,record):
            record('request',{'method':'POST','body':{'requests':[]}})
            return SimpleNamespace(budget=budget,submit=lambda sources,batch_key:{'status':'SUBMITTED','batch_key':batch_key,'submitted':len(sources)})
        files=SimpleNamespace(capture=lambda path:{'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        slim=self.root/'slim.json';slim.write_text('{}')
        with (patch('investigator.shared_state.configured_state',return_value=SimpleNamespace(backend='postgresql')),
            patch('enrich_estate.live_job',side_effect=job),patch('investigator.runtime.fingerprint',return_value='a'*64),
            patch('investigator.source_revision.committed_revision',return_value='b'*40),
            patch('investigator.slim_recording.validate',return_value={}),patch('investigator.slim_recording.stores',return_value=(None,files)),
            patch.dict(os.environ,{'DIA_SLIM_RECORDING_CONFIG':str(slim)})):
            result=worker.execute({'options':self.options()},context)
        self.assertEqual(result['account'],'enrichment:round-twenty-one');self.assertEqual(result['investigator_model_calls'],0)
        self.assertEqual(result['estate_reads'],0);self.assertTrue(events[-1][1]['complete'])
        text=json.dumps(events);self.assertNotIn('x-api-key',text);self.assertNotIn('Authorization',text)


if __name__=='__main__':unittest.main()

import subprocess
import unittest
from io import BytesIO
import json
import hashlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4
import test_model_onboarding as fixtures
from investigator.scans import ScanQueue
from investigator.onboarding import Conflict
from investigator.admin_api import create_app
from run_catalog_scan import collector


class ScanTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.OnboardingTests();self.fixture.setUp();self.addCleanup(self.fixture.temp.cleanup)
        self.store=self.fixture.store;self.model=self.fixture.registered()
        self.queue=ScanQueue(self.store,self.fixture.workspace,'profile-v1')

    def request(self):return self.queue.request(self.model['id'],self.model['revision'],str(uuid4()),'admin')

    def collect(self):return {'scan_id':self.fixture.scan(),'status':'COMPLETE','connections':{'fabric_collection':'AVAILABLE'}}

    def test_deduplication_success_receipt_and_no_repeat(self):
        key=str(uuid4());a=self.queue.request(self.model['id'],1,key,'admin')
        self.assertEqual(self.queue.request(self.model['id'],1,key,'admin')['id'],a['id'])
        with self.assertRaises(Conflict):self.request()
        r=self.queue.run_one(self.collect)
        self.assertEqual(r['status'],'COMPLETED')
        self.assertEqual(r['receipt']['connections']['fabric_collection'],'AVAILABLE')
        self.assertIsNone(self.queue.run_one(lambda:self.fail('Must not repeat')))
        self.assertIsNotNone(self.store.get(self.model['id'])['context_id'])

    def test_profile_change_is_held_without_connector_call(self):
        self.request();other=ScanQueue(self.store,self.fixture.workspace,'new-profile')
        self.assertEqual(other.run_one(lambda:self.fail('No call'))['status'],'HELD')

    def test_failed_collection_preserves_context_and_redacts_error(self):
        self.queue.request(self.model['id'],1,str(uuid4()),'admin');self.queue.run_one(self.collect)
        self.model=self.store.get(self.model['id']);prior=self.model['context_id'];self.request()
        def fail():raise RuntimeError('secret-provider-token')
        result=self.queue.run_one(fail)
        self.assertEqual(result['status'],'FAILED');self.assertNotIn('secret-provider-token',str(result))
        self.assertEqual(self.store.get(self.model['id'])['context_id'],prior)

    def test_timeout_or_interruption_blocks_new_dispatch(self):
        self.request()
        def timeout():raise subprocess.TimeoutExpired('collector',900)
        self.assertEqual(self.queue.run_one(timeout)['status'],'INTERRUPTED')
        restarted=ScanQueue(self.store,self.fixture.workspace,'profile-v1')
        with self.assertRaises(Conflict):restarted.run_one(self.collect)
        with self.assertRaises(Conflict):self.request()

    def test_revision_and_workspace_rechecked(self):
        wrong=ScanQueue(self.store,str(uuid4()),'profile-v1')
        with self.assertRaises(ValueError):wrong.request(self.model['id'],1,str(uuid4()),'admin')
        self.request();self.store.enable(self.model['id'],1,False,'admin')
        self.assertEqual(self.queue.run_one(lambda:self.fail('No call'))['status'],'HELD')

    def test_admin_can_queue_but_reader_cannot(self):
        app=create_app(self.store,'a'*32,'r'*32,self.queue)
        body=json.dumps({'revision':1,'request_key':str(uuid4())}).encode()
        for token,expected in [('r'*32,'403 Forbidden'),('a'*32,'200 OK')]:
            statuses=[]
            result=b''.join(app({'PATH_INFO':'/api/v2/admin/models/'+self.model['id']+'/scans',
                'REQUEST_METHOD':'POST','CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(body)),
                'HTTP_AUTHORIZATION':'Bearer '+token,'wsgi.input':BytesIO(body)},lambda s,h:statuses.append(s)))
            self.assertEqual(statuses,[expected])
            if expected=='200 OK':self.assertEqual(json.loads(result)['status'],'QUEUED')

    def test_collector_uses_frozen_config_and_own_receipt_not_latest_scan(self):
        config=self.fixture.root/'config.json';config.write_text('{}')
        profile=hashlib.sha256(config.read_bytes()).hexdigest()
        own_scan=self.fixture.scan()
        self.fixture.scan()  # Unrelated newer scan must not replace receipt.
        def execute(command,**kwargs):
            frozen=Path(command[command.index('--config')+1])
            self.assertNotEqual(frozen,config);self.assertEqual(frozen.read_text(),'{}')
            Path(command[command.index('--summary')+1]).write_text(json.dumps({'scan_id':own_scan,'status':'COMPLETE'}))
            return SimpleNamespace(returncode=0)
        with patch('run_catalog_scan.subprocess.run',side_effect=execute):
            result=collector(config,self.fixture.inventory,profile)()
        self.assertEqual(result['scan_id'],own_scan)

    def test_changed_config_does_not_start_collector(self):
        config=self.fixture.root/'config.json';config.write_text('{}')
        with patch('run_catalog_scan.subprocess.run') as run:
            with self.assertRaises(Conflict):collector(config,self.fixture.inventory,'different')()
            run.assert_not_called()


if __name__=='__main__':unittest.main()

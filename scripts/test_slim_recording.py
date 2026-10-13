import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch, Mock
from uuid import uuid4

from investigator import slim_recording as slim
from investigator.artifact_store import ArtifactError, Files, LocalObjects
from investigator.process_tape import Tape, bytes_of


CONFIG={'version':'slim-recording-v1','account_url':'https://synthetic.blob.core.windows.net',
        'identity':{'mode':'managed_identity','client_id':'11111111-1111-1111-1111-111111111111',
        'principal_id':'22222222-2222-2222-2222-222222222222','tenant_id':'33333333-3333-3333-3333-333333333333'},
        'snapshot_channel':'worker-snapshots','tape_channel':'worker-tapes','tape_class':'EXACT'}


class Tests(unittest.TestCase):
    def test_store_adapter_preserves_identity_audience_and_exact_channels(self):
        import base64
        import sys
        from investigator.adapters import blob_artifacts
        encoded=base64.urlsafe_b64encode(json.dumps({'exp':1234567890}).encode()).decode().rstrip('=')
        token='header.'+encoded+'.signature'
        provider=Mock();provider.get_token.return_value=token
        gateway=object()
        with patch('investigator.adapters.managed_identity.Tokens',return_value=provider) as tokens, \
             patch('investigator.live_gateway.current',return_value=gateway), \
             patch.object(blob_artifacts,'BlobObjects') as objects:
            snapshots,tapes=slim.stores(CONFIG)
        tokens.assert_called_once_with(CONFIG['identity'])
        self.assertEqual([call.args[1] for call in objects.call_args_list],['snapshots','tapes'])
        self.assertEqual([call.kwargs['channel'] for call in objects.call_args_list],['worker-snapshots','worker-tapes'])
        self.assertTrue(all(call.kwargs['gateway'] is gateway for call in objects.call_args_list))
        credential=objects.call_args_list[0].args[2]
        with self.assertRaisesRegex(ArtifactError,'SLIM_AUTH_SCOPE'):
            credential.get_token('https://other.example/.default')
        provider.get_token.assert_not_called()
        constructor=lambda value,expiry:SimpleNamespace(token=value,expires_on=expiry)
        with patch.dict(sys.modules,{'azure.core.credentials':SimpleNamespace(AccessToken=constructor)}):
            result=credential.get_token('https://storage.azure.com/.default')
        self.assertEqual((result.token,result.expires_on),(token,1234567890))
        provider.get_token.assert_called_once_with('https://storage.azure.com/.default')

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.storage=(Files(LocalObjects(self.root/'snapshots')),Files(LocalObjects(self.root/'tapes')))

    def synthetic(self):
        import sqlite3
        from contextlib import closing
        root=self.root/str(uuid4());root.mkdir()
        sources=self.root/'live';sources.mkdir()
        for name in ('catalog.sqlite','inventory.sqlite'):
            with closing(sqlite3.connect(sources/name)) as db:
                db.execute('CREATE TABLE synthetic(value INTEGER)');db.commit()
            (root/name).write_bytes((sources/name).read_bytes())
        tape=Tape(root/'tape.json',{'entry_point':'synthetic','context_identity':'test','config':{},'profile':{},
                  'usage_policy':{},'engine_hash':'test','state':{'artifacts':{
                      name:__import__('hashlib').sha256((root/name).read_bytes()).hexdigest()
                      for name in ('catalog.sqlite','inventory.sqlite')}}})
        tape.event('BOUNDED_REQUEST',bytes_of({'quantity':1}));tape.event('BOUNDED_RESPONSE',bytes_of({'value':7}))
        tape.finish({'value':7})
        tape._slim_configuration=CONFIG;tape._slim_owned_root=root.resolve()
        agent=SimpleNamespace(store=SimpleNamespace(database=sources/'catalog.sqlite',inventory=sources/'inventory.sqlite'))
        return root,tape,agent

    def test_retirement_only_after_remote_verification_shared_sources_untouched(self):
        root,tape,agent=self.synthetic()
        source_before=agent.store.database.read_bytes();tape_before=tape.path.read_bytes()
        with patch.object(slim,'stores',return_value=self.storage):
            receipt=slim.publish_sealed(agent,tape)
            self.assertEqual(len(receipt['retired_private_files']),4)
            self.assertFalse((root/'catalog.sqlite').exists())
            self.assertEqual(tape.path.read_bytes(),tape_before)
            self.assertEqual(agent.store.database.read_bytes(),source_before)
            with slim.materialize(tape.path) as restored:
                replay=Tape(restored)
                replay.event('BOUNDED_REQUEST',bytes_of({'quantity':1}))
                self.assertEqual(json.loads(replay.take('BOUNDED_RESPONSE')),{'value':7})
                replay.finish({'value':7})
                self.assertEqual(restored.read_bytes(),tape_before)
        self.assertEqual(receipt['engine_replay'],'NOT_RUN')
        bundle=json.loads((root/'snapshot-bundle.json').read_bytes())
        self.assertEqual(set(bundle['final_state']),{'catalog.sqlite','inventory.sqlite'})
        tape.path.write_bytes(tape_before+b' ')
        with self.assertRaisesRegex(ArtifactError,'LOCAL_TAPE_DIFFERS'):
            with slim.materialize(tape.path,storage=self.storage):pass

    def test_failed_remote_verification_keeps_all_private_databases(self):
        root,tape,agent=self.synthetic()
        with patch.object(slim,'stores',return_value=self.storage),patch.object(self.storage[1],'verify',side_effect=ArtifactError('bad remote')):
            with self.assertRaisesRegex(ArtifactError,'bad remote'):slim.publish_sealed(agent,tape)
        self.assertTrue((root/'catalog.sqlite').exists());self.assertTrue((root/'final-catalog.sqlite').exists())
        self.assertFalse((root/'slim-recording.json').exists())

    def test_historical_tape_cannot_be_retired_by_switching_environment(self):
        root,tape,agent=self.synthetic();del tape._slim_configuration
        with patch.object(slim,'stores',side_effect=AssertionError('No publication')):
            self.assertIsNone(slim.publish_sealed(agent,tape))
        self.assertTrue((root/'catalog.sqlite').exists())

    def test_closed_configuration_and_projected_refusal(self):
        self.assertEqual(slim.validate(CONFIG),CONFIG)
        for value in ({**CONFIG,'password':'forbidden'},{**CONFIG,'account_url':'http://bad'},
                      {**CONFIG,'tape_class':'PRIVACY_PROJECTED'}):
            with self.assertRaises(ValueError):slim.validate(value)
        path=self.root/'config.json';path.write_text(json.dumps(CONFIG))
        with patch.dict(os.environ,{slim.CONFIG_ENV:str(path)}):
            with self.assertRaisesRegex(ArtifactError,'PROJECTED'):
                slim.configuration(SimpleNamespace(config={'_estate':{'recording':{'tape_class':'PRIVACY_PROJECTED'}}}))

    def test_full_process_intake_procedure_and_both_outputs_replay_from_cas(self):
        # Existing engine harness executes intake, preview, create, run, synthesize,
        # then checks all decisions and both output bodies against their sealed bytes.
        from test_process_tape import TapeTests
        helper=TapeTests();helper.setUp();self.addCleanup(helper.doCleanups)
        with patch.object(slim,'configuration',return_value=CONFIG),patch.object(slim,'stores',return_value=self.storage):
            helper.exercise_process()
        self.assertTrue(list((self.root/'snapshots/files').iterdir()))


if __name__=='__main__':unittest.main()

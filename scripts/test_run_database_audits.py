"""Real audit/retention coverage for ephemeral sealed-file reuse."""
from contextlib import closing
import hashlib,json,shutil,sqlite3,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
from cloud_stage_worker import audit_database,_audit_database_values
from cloud_verification_capture import snapshot
from cloud_runner_context import retain_dependencies
from investigator.artifact_store import Files,LocalObjects
from investigator.planner_recording import RecordingError,_safe
from investigator.run_database_audits import ACTIVE,scope,checked,identity,STAGE


class RunDatabaseAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def db(self,name='source.sqlite',value='public fixture'):
        path=self.root/name
        with closing(sqlite3.connect(path)) as db:
            db.execute('CREATE TABLE fixture(value)');db.execute('INSERT INTO fixture VALUES(?)',(value,));db.commit()
        return path
    def test_actual_retention_deduplicates_identical_sealed_copies_and_cas_bytes_stay_exact(self):
        folder=self.root/'capture';folder.mkdir();source=self.db();baseline=folder/'catalog.sqlite';shutil.copyfile(source,baseline)
        (folder/'working').mkdir();shutil.copyfile(source,folder/'working/catalog.sqlite')
        files=Files(LocalObjects(self.root/'cas'));ctx=SimpleNamespace(record=Mock())
        with scope(),patch('cloud_stage_worker._audit_database_values',wraps=_audit_database_values) as full:
            a=retain_dependencies(folder,ctx,kind='verification',phase='BEFORE_READS',files=files)
            b=retain_dependencies(folder,ctx,kind='verification',phase='AFTER_EXECUTION',files=files)
        self.assertEqual(1,full.call_count);self.assertEqual(a['files'],b['files'])
        for i,row in enumerate(a['files']):
            target=self.root/('restored'+str(i));files.restore(row['sha256'],target);self.assertEqual(source.read_bytes(),target.read_bytes())
    def test_snapshot_certifies_only_written_destination_not_unchecked_source(self):
        source=self.db();dest=self.root/'snapshot.sqlite';before=identity(source)
        with scope(),patch('cloud_stage_worker._audit_database_values',wraps=_audit_database_values) as full:
            snapshot(source,dest);audit_database(dest)
            self.assertEqual(0,full.call_count)
        self.assertEqual(before,identity(source))
    def test_new_run_and_profile_and_detector_each_need_new_full_audit(self):
        source=self.db();calls=Mock()
        with scope():
            checked(source,'one',_safe,calls);checked(source,'one',_safe,calls)
            checked(source,'two',_safe,calls);checked(source,'one',lambda b:_safe(b),calls)
        with scope():checked(source,'one',_safe,calls)
        self.assertEqual(4,calls.call_count);self.assertIsNone(ACTIVE.get())
    def test_same_size_mutation_reaudits_and_new_secret_refuses(self):
        source=self.db(value='a'*40)
        with scope(),patch('cloud_stage_worker._audit_database_values',wraps=_audit_database_values) as full:
            audit_database(source);size=source.stat().st_size
            with closing(sqlite3.connect(source)) as db:
                db.execute('UPDATE fixture SET value=?',('password=synthetic_credential_123',));db.commit()
            self.assertEqual(size,source.stat().st_size)
            with self.assertRaises(RecordingError):audit_database(source)
            self.assertEqual(2,full.call_count)
    def test_new_environment_secret_reaudits_unchanged_bytes(self):
        secret='synthetic_environment_probe_123';source=self.db(value=secret);before=identity(source)
        with scope(),patch('cloud_stage_worker._audit_database_values',wraps=_audit_database_values) as full:
            audit_database(source)
            with patch.dict('os.environ',{'TEST_API_KEY':secret}):
                with self.assertRaises(RecordingError):audit_database(source)
            self.assertEqual(2,full.call_count)
        self.assertEqual(before,identity(source))
    def test_all_sidecars_forbid_trust_even_after_success(self):
        for suffix in ('-wal','-shm','-journal'):
            with self.subTest(suffix=suffix),scope():
                source=self.db(suffix[1:]+'.sqlite');audit_database(source)
                Path(str(source)+suffix).write_bytes(b'')
                with self.assertRaisesRegex(ValueError,'SIDECAR'):audit_database(source)
    def test_sidecar_or_mutation_appearing_during_audit_registers_nothing(self):
        for sidecar in (False,True):
            with self.subTest(sidecar=sidecar),scope():
                source=self.db('change'+str(sidecar)+'.sqlite')
                def change():
                    if sidecar:Path(str(source)+'-wal').write_bytes(b'')
                    else:
                        with source.open('ab') as f:f.write(b'changed')
                with self.assertRaisesRegex(ValueError,'SIDECAR|CHANGED_DURING'):
                    checked(source,STAGE,_safe,change)
                self.assertEqual(set(),ACTIVE.get())
    def test_failed_audit_never_registers_success(self):
        source=self.db();perform=Mock(side_effect=[RecordingError('synthetic refusal'),None])
        with scope():
            with self.assertRaises(RecordingError):checked(source,STAGE,_safe,perform)
            self.assertEqual(set(),ACTIVE.get());checked(source,STAGE,_safe,perform)
        self.assertEqual(2,perform.call_count)
    def test_snapshot_still_audits_schema_after_stage_success(self):
        source=self.db()
        with closing(sqlite3.connect(source)) as db:
            db.execute('CREATE TABLE "password=synthetic_schema_credential"(value)');db.commit()
        destination=self.root/'forbidden-schema.sqlite'
        with scope():
            audit_database(source)
            with self.assertRaises(RecordingError):snapshot(source,destination)
        self.assertFalse(destination.exists())

    def test_snapshot_rejects_raw_escaped_and_binary_secrets_before_destination(self):
        values=['password=synthetic_credential_123','{"pass\\u0077ord":"synthetic_credential_123"}',
                b'Bearer synthetic_token_12345',b'{"note":"synthetic_env_\\u0073ecret_123"}']
        with patch.dict('os.environ',{'TEST_API_KEY':'synthetic_env_secret_123'}):
            for index,value in enumerate(values):
                with self.subTest(index=index),scope():
                    source=self.db('unsafe'+str(index)+'.sqlite',value);before=identity(source)
                    target=self.root/('refused'+str(index)+'.sqlite')
                    with self.assertRaises(RecordingError):snapshot(source,target)
                    self.assertFalse(target.exists());self.assertEqual(before,identity(source))
                    self.assertEqual(set(),ACTIVE.get())

    def test_environment_changing_during_audit_never_registers_success(self):
        source=self.db()
        import os
        with patch.dict('os.environ',{}),scope():
            def change():os.environ['NEW_TEST_SECRET']='synthetic_new_secret_12345'
            with self.assertRaisesRegex(ValueError,'ENVIRONMENT_CHANGED'):
                checked(source,STAGE,_safe,change)
            self.assertEqual(set(),ACTIVE.get())

    def test_retry_clears_scope_and_run_failure_always_resets(self):
        from investigator.unified_runner import retry,run
        source=self.db();attempt=Mock(side_effect=[TimeoutError('temporary'),None])
        with scope():
            audit_database(source);self.assertTrue(ACTIVE.get())
            retry(attempt,record=Mock(),sleep=Mock());self.assertEqual(set(),ACTIVE.get())
        def fail(*a,**k):
            self.assertIsNotNone(ACTIVE.get());raise ValueError('recorded failure')
        with patch('investigator.unified_runner._run',side_effect=fail):
            with self.assertRaisesRegex(ValueError,'recorded failure'):run({},'test')
        self.assertIsNone(ACTIVE.get())


if __name__=='__main__':unittest.main()

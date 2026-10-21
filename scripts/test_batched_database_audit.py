"""Batching retains the original credential checks without changing source DBs."""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from cloud_stage_worker import audit_database
from investigator.planner_recording import _safe,RecordingError


def legacy(values):
    for value in values:
        if isinstance(value,str):
            try:parsed=json.loads(value)
            except json.JSONDecodeError:parsed=value
            _safe(json.dumps(parsed,ensure_ascii=False).encode())
        elif isinstance(value,bytes):_safe(value)


class BatchedDatabaseAuditTests(unittest.TestCase):
    def database(self,values):
        folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
        path=Path(folder.name)/'fixture.sqlite'
        with closing(sqlite3.connect(path)) as db:
            db.execute('CREATE TABLE fixture(value)')
            db.executemany('INSERT INTO fixture VALUES(?)',[(value,) for value in values]);db.commit()
        return path
    def test_raw_escaped_json_environment_and_binary_secrets_refuse_identically(self):
        cases=['password=synthetic_credential_123',
               '{"pass\\u0077ord":"synthetic_credential_123"}',
               json.dumps(json.dumps({'password':'synthetic_credential_123'})),
               '{"note":"synthetic_env_\\u0073ecret_123"}',
               b'Bearer synthetic_token_12345']
        with patch.dict('os.environ',{'TEST_API_KEY':'synthetic_env_secret_123'}):
            for value in cases:
                with self.subTest(kind=type(value).__name__):
                    with self.assertRaises(RecordingError):legacy([value])
                    with self.assertRaises(RecordingError):audit_database(self.database([value]))
    def test_complete_values_are_bounded_and_large_value_uses_original_path(self):
        small=[json.dumps({'field':'value'+str(i)}) for i in range(40)]
        large=json.dumps({'definition':'x'*500})
        path=self.database(small+[large,'tail']);before=hashlib.sha256(path.read_bytes()).hexdigest()
        calls=[]
        def observe(raw):
            _safe(raw);calls.append(raw)
        with patch('cloud_stage_worker.AUDIT_BATCH_BYTES',128),patch('cloud_stage_worker._safe',side_effect=observe):
            audit_database(path)
        self.assertLess(len(calls),len(small)+2)
        for raw in calls:
            parsed=json.loads(raw)
            if isinstance(parsed,list):self.assertLessEqual(len(raw),128)
            else:self.assertEqual(parsed,json.loads(large))
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),before)
    def test_binary_keeps_individual_audit_and_progress_never_contains_values(self):
        path=self.database(['fixture narrative',b'public binary',json.dumps({'value':'ordinary'})]);calls=[];progress=[]
        def observe(raw):_safe(raw);calls.append(raw)
        with patch('cloud_stage_worker._safe',side_effect=observe):audit_database(path,progress=progress.append)
        self.assertIn(b'public binary',calls)
        self.assertEqual(progress,[{'table':'fixture','rows':0,'status':'STARTED'},{'table':'fixture','rows':3,'status':'COMPLETED'}])
        self.assertNotIn('narrative',json.dumps(progress))

    def test_capture_snapshot_audits_memory_before_destination_exists(self):
        from cloud_verification_capture import snapshot
        cases=['password=synthetic_credential_123',
               '{"pass\\u0077ord":"synthetic_credential_123"}',
               json.dumps(json.dumps({'password':'synthetic_credential_123'})),
               '{"note":"synthetic_env_\\u0073ecret_123"}',
               b'Bearer synthetic_token_12345',b'Bearer synthetic_token_12345\xff']
        with patch.dict('os.environ',{'TEST_API_KEY':'synthetic_env_secret_123'}):
            for value in cases:
                with self.subTest(kind=type(value).__name__):
                    source=self.database([value]);destination=source.with_name('output.sqlite')
                    before=hashlib.sha256(source.read_bytes()).hexdigest()
                    with self.assertRaises(RecordingError):snapshot(source,destination)
                    self.assertFalse(destination.exists())
                    self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),before)
    def test_capture_snapshot_keeps_all_rows_and_binary_normalization(self):
        from cloud_verification_capture import snapshot
        source=self.database([json.dumps({'ok':'fixture'}),b'plain binary',b'\xffplain'])
        before=hashlib.sha256(source.read_bytes()).hexdigest();destination=source.with_name('output.sqlite')
        snapshot(source,destination)
        with closing(sqlite3.connect(source)) as a,closing(sqlite3.connect(destination)) as b:
            self.assertEqual(a.execute('SELECT * FROM fixture').fetchall(),b.execute('SELECT * FROM fixture').fetchall())
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),before)

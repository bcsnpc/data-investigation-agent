"""Durable, explicitly dispatched metadata scans. No automatic retry on restart."""
from datetime import datetime, timezone
import json
import subprocess
from uuid import uuid4, UUID
from .onboarding import Conflict, encoded, text


class ScanQueue:
    def __init__(self, store, workspace, profile_hash):
        self.store=store
        self.workspace=str(UUID(text(workspace,100)))
        self.profile_hash=text(profile_hash,100)
        with store.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS catalog_scans(
              id TEXT PRIMARY KEY, model_id TEXT NOT NULL REFERENCES models(id),
              request_key TEXT NOT NULL, profile_hash TEXT NOT NULL, revision INTEGER NOT NULL,
              status TEXT NOT NULL, created TEXT NOT NULL, finished TEXT, receipt TEXT,
              UNIQUE(model_id,request_key));
            CREATE UNIQUE INDEX IF NOT EXISTS one_pending_scan_per_model
              ON catalog_scans(model_id) WHERE status IN ('QUEUED','RUNNING','INTERRUPTED');
            ''')

    def request(self, model_id, revision, request_key, actor):
        key=str(UUID(text(request_key,100)))
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            model=self.store.row(db,model_id)
            if model['workspace']!=self.workspace:
                raise ValueError('Model workspace differs from configured scan connection')
            old=db.execute('SELECT * FROM catalog_scans WHERE model_id=? AND request_key=?',(model_id,key)).fetchone()
            if old:
                if old['revision']!=revision or old['profile_hash']!=self.profile_hash:
                    raise Conflict('Scan request key reused with different inputs')
                return dict(old)
            self.store.check_revision(model,revision)
            if db.execute("SELECT 1 FROM catalog_scans WHERE model_id=? AND status IN ('QUEUED','RUNNING','INTERRUPTED')",(model_id,)).fetchone():
                raise Conflict('Model already has a pending scan')
            identity=str(uuid4())
            db.execute('INSERT INTO catalog_scans VALUES(?,?,?,?,?,?,?,NULL,NULL)',
                       (identity,model_id,key,self.profile_hash,revision,'QUEUED',datetime.now(timezone.utc).isoformat()))
            self.store.event(db,model_id,revision,'SCAN_QUEUED',actor,{'job_id':identity})
            return dict(db.execute('SELECT * FROM catalog_scans WHERE id=?',(identity,)).fetchone())

    def list(self, model_id):
        with self.store.connect() as db:
            self.store.row(db,model_id)
            return [dict(x) for x in db.execute('SELECT * FROM catalog_scans WHERE model_id=? ORDER BY created DESC',(model_id,))]

    def run_one(self, collect):
        """Claim once and call a trusted bounded collector; no caller-supplied code.

        A process death leaves RUNNING and blocks subsequent dispatch. Operators
        must reconcile it; a restart never silently reruns a remote scan.
        """
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute("SELECT 1 FROM catalog_scans WHERE status IN ('RUNNING','INTERRUPTED')").fetchone():
                raise Conflict('A scan is running or requires interruption reconciliation')
            row=db.execute("SELECT s.* FROM catalog_scans s JOIN models m ON m.id=s.model_id WHERE s.status='QUEUED' AND m.environment=? ORDER BY s.created,s.id LIMIT 1",(self.store.environment,)).fetchone()
            if not row:return None
            job=dict(row)
            db.execute("UPDATE catalog_scans SET status='RUNNING' WHERE id=?",(job['id'],))
        receipt={};status='FAILED'
        try:
            model=self.store.get(job['model_id'])
            self.store.check_revision(model,job['revision'])
            if model['workspace']!=self.workspace or job['profile_hash']!=self.profile_hash:
                raise Conflict('Configured connection changed; submit a new scan')
            result=collect()
            # Collector supplies only bounded summary observations, not errors,
            # tokens, raw logs, or a replacement credential/database path.
            receipt={'scan_id':str(UUID(result['scan_id'])),'scan_status':result['status'],
                     'connections':result.get('connections',{}),'live_queryability':'UNKNOWN'}
            if result['status'] in ('COMPLETE','PARTIAL'):
                model=self.store.import_scan(job['model_id'],job['revision'],result['scan_id'],'scan-worker')
                receipt['context_id']=model['context_id'];status='COMPLETED'
            else:
                receipt['reason']='Collection failed; previous context retained'
        except subprocess.TimeoutExpired:
            status='INTERRUPTED';receipt['reason']='Collector timeout; reconcile possible child work before another scan'
        except Conflict:
            status='HELD';receipt['reason']='Model or connection changed; review before resubmitting'
        except Exception as exc:
            # Error type only: provider exceptions can contain credentials.
            receipt['reason']='Scan/import failed; previous context retained'
            receipt['error_type']=type(exc).__name__
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute("UPDATE catalog_scans SET status=?,finished=?,receipt=? WHERE id=? AND status='RUNNING'",
                       (status,datetime.now(timezone.utc).isoformat(),encoded(receipt),job['id']))
            model=self.store.row(db,job['model_id'])
            self.store.event(db,job['model_id'],model['revision'],'SCAN_'+status,'scan-worker',{'job_id':job['id'],**receipt})
        return {'id':job['id'],'status':status,'receipt':receipt}

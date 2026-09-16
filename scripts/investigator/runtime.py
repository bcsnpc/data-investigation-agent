"""Durable typed-action runs for native/source/comparison tools. Not an AI planner."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
from uuid import uuid4

from .onboarding import fields, text, digest, encoded, Conflict
from . import native_diagnostics, source_diagnostics, comparisons
from . import record_readback, record_comparison, record_aggregate
from .tool_registry import TOOLS, normalize, compile_actions


def fingerprint():
    root = Path(__file__).resolve().parents[2]
    files = sorted((root / 'scripts/investigator').glob('*.py'))
    files += [root / name for name in ('scripts/run_native_diagnostic.py', 'scripts/run_source_diagnostic.py','scripts/run_investigation_v2.py',
               'scripts/run_adaptive_investigation.py', 'scripts/serve_investigator_workspace.py', 'scripts/connect_fixture_reader.py', 'scripts/ticket_planner.py', 'scripts/metadata_auth.py', 'scripts/metadata_config.py', 'scripts/sql_connect_retry.py', 'infra/scripts/Read-CatalogAggregate.ps1')]
    return digest({'python': sys.version, 'files': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}})


def project(row, steps, events):
    return {'id':row['id'],'model_id':row['model_id'],'status':row['status'],'engine_hash':row['engine_hash'],
            'request_hash':row['request_hash'],'context_hash':row['context_hash'],
            'call_budget':row['call_budget'],'calls_reserved':row['calls_reserved'],
            'outcome':json.loads(row['outcome']) if row['outcome'] else None,
            'steps':[{**s,'result':json.loads(s['result']) if s['result'] else None} for s in steps],
            'events':[{**e,'detail':json.loads(e['detail'])} for e in events]}


def read_run(store, model_id, identity):
    store.get(model_id)
    with store.connect() as db:
        db.row_factory=sqlite3.Row
        exists=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='v2_runs'").fetchone()
        row=db.execute('SELECT * FROM v2_runs WHERE id=? AND model_id=?',(identity,model_id)).fetchone() if exists else None
        if row is None:raise KeyError('Run not found')
        steps=[dict(r) for r in db.execute('SELECT ordinal,tool,status,receipt_id,result FROM v2_steps WHERE run_id=? ORDER BY ordinal',(identity,))]
        events=[dict(r) for r in db.execute('SELECT event,detail,created FROM v2_run_events WHERE run_id=? ORDER BY id',(identity,))]
    return project(dict(row),steps,events)


class Runtime:
    def __init__(self, store, config, native_transport, source_transport):
        self.store = store; self.config = config
        from .native_identity import guarded
        self.native_transport = (lambda request: guarded(self.config, request, native_transport)) if native_transport is not None else None
        self.source_transport = source_transport
        with self.db() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS v2_cancellations(run_id TEXT PRIMARY KEY,created TEXT);
            CREATE TABLE IF NOT EXISTS v2_runs(
              id TEXT PRIMARY KEY,model_id TEXT,request_key TEXT,request TEXT,request_hash TEXT,
              engine_hash TEXT,connection_hash TEXT,context_hash TEXT,status TEXT,
              call_budget INTEGER,calls_reserved INTEGER,lease_token TEXT,outcome TEXT,
              created TEXT,UNIQUE(model_id,request_key));
            CREATE TABLE IF NOT EXISTS v2_steps(
              run_id TEXT,ordinal INTEGER,tool TEXT,status TEXT,receipt_id TEXT,request_hash TEXT,
              result TEXT,PRIMARY KEY(run_id,ordinal));
            CREATE TABLE IF NOT EXISTS v2_run_events(
              id INTEGER PRIMARY KEY,run_id TEXT,event TEXT,detail TEXT,created TEXT);
            ''')

    @contextmanager
    def db(self):
        with self.store.connect() as db:
            db.row_factory = sqlite3.Row
            yield db

    def event(self, db, identity, kind, detail):
        db.execute('INSERT INTO v2_run_events(run_id,event,detail,created) VALUES(?,?,?,?)',
                   (identity, kind, encoded(detail), datetime.now(timezone.utc).isoformat()))

    def load(self, db, identity):
        row = db.execute('SELECT * FROM v2_runs WHERE id=?', (identity,)).fetchone()
        if row is None:raise KeyError('Run not found')
        self.store.get(row['model_id'])
        return dict(row)

    def validate(self, row):
        request = json.loads(row['request'])
        if digest(request) != row['request_hash']:raise ValueError('Run request integrity differs')
        if row['engine_hash'] != fingerprint() or row['connection_hash'] != digest(self.config):
            raise Conflict('Engine or connection changed')
        model = self.store.get(row['model_id'])
        if digest(model['context']) != row['context_hash']:raise Conflict('Context changed')
        return request, compile_actions(self.store,self.config,request)

    def create(self, request, request_key):
        request=normalize(request)
        text(request_key, 100)
        model = self.store.get(request['model_id'])
        identity = str(uuid4())
        row = {'id': identity, 'model_id': model['id'], 'request': encoded(request), 'request_hash': digest(request),
               'engine_hash': fingerprint(), 'connection_hash': digest(self.config), 'context_hash': digest(model['context'])}
        _, compiled = self.validate(row)
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            previous = db.execute('SELECT id,request_hash FROM v2_runs WHERE model_id=? AND request_key=?', (model['id'], request_key)).fetchone()
            if previous:
                if previous['request_hash'] != row['request_hash']:raise Conflict('Idempotency key has another request')
                return self.get(previous['id'])
            db.execute('INSERT INTO v2_runs VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (identity,model['id'],request_key,row['request'],row['request_hash'],row['engine_hash'],row['connection_hash'],
                 row['context_hash'],'READY',request['call_budget'],0,None,None,datetime.now(timezone.utc).isoformat()))
            for ordinal, action in enumerate(request['actions']):
                db.execute('INSERT INTO v2_steps VALUES(?,?,?,?,?,?,NULL)',
                           (identity,ordinal,action['tool'],'PENDING',str(uuid4()),digest(compiled[ordinal])))
            self.event(db,identity,'CREATED',{'call_budget':request['call_budget']})
        return self.get(identity)

    def get(self, identity):
        with self.db() as db:
            row = self.load(db, identity)
            steps = [dict(r) for r in db.execute('SELECT ordinal,tool,status,receipt_id,result FROM v2_steps WHERE run_id=? ORDER BY ordinal', (identity,))]
            events = [dict(r) for r in db.execute('SELECT event,detail,created FROM v2_run_events WHERE run_id=? ORDER BY id', (identity,))]
        return project(row,steps,events)

    def claim(self, identity):
        token = str(uuid4())
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE'); row = self.load(db, identity)
            if row['status'] == 'COMPLETED':return None
            if row['status'] != 'READY':raise Conflict('Run needs explicit reconciliation or remains held')
            self.validate(row)
            if db.execute("SELECT 1 FROM v2_steps WHERE status='DISPATCHED' LIMIT 1").fetchone():
                raise Conflict('Another dispatched action must finish or be reconciled')
            db.execute("UPDATE v2_runs SET status='RUNNING',lease_token=? WHERE id=?", (token,identity))
            self.event(db,identity,'CLAIMED',{})
        return token

    def commit(self, identity, ordinal, token, result):
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE'); row = self.load(db,identity)
            if row['lease_token'] != token or row['status'] != 'RUNNING':raise Conflict('Worker is fenced')
            self.validate(row)
            step = db.execute('SELECT * FROM v2_steps WHERE run_id=? AND ordinal=?',(identity,ordinal)).fetchone()
            if not step or step['status'] != 'DISPATCHED' or result['id'] != step['receipt_id']:
                raise Conflict('Result is not for this dispatch')
            if TOOLS[step['tool']]['cloud'] and result.get('request_hash') != step['request_hash']:
                raise Conflict('Result request hash differs')
            status = 'COMPLETED' if not TOOLS[step['tool']]['cloud'] or result.get('status','COMPLETED') == 'COMPLETED' else 'FAILED'
            if result.get('status') == 'INTERRUPTED':status = 'DISPATCHED'
            db.execute('UPDATE v2_steps SET status=?,result=? WHERE run_id=? AND ordinal=? AND status=\'DISPATCHED\'',
                       (status,encoded(result),identity,ordinal))
            self.event(db,identity,'STEP_'+status,{'ordinal':ordinal,'receipt_id':result['id']})
            if status in ('FAILED','DISPATCHED'):
                db.execute("UPDATE v2_runs SET status='HELD',lease_token=NULL WHERE id=?",(identity,))
            elif not db.execute("SELECT 1 FROM v2_steps WHERE run_id=? AND status!='COMPLETED'",(identity,)).fetchone():
                db.execute("UPDATE v2_runs SET status='COMPLETED',lease_token=NULL,outcome=? WHERE id=?",(encoded(self.outcome(db,identity)),identity))

    def outcome(self,db,identity):
        row=db.execute("SELECT result FROM v2_steps WHERE run_id=? AND tool IN ('compare','compare_records','reconcile_records') AND status='COMPLETED' ORDER BY ordinal DESC LIMIT 1",(identity,)).fetchone()
        return json.loads(row[0]) if row else {'outcome':'INSUFFICIENT_EVIDENCE','reason':'Observations only; no comparison assessment',
                                              'root_cause_verified':False,'delivery_eligible':False}

    def execute(self, identity):
        token = self.claim(identity)
        if token is None:return self.get(identity)
        try:
            while True:
                with self.db() as db:
                    db.execute('BEGIN IMMEDIATE'); row = self.load(db,identity)
                    if row['lease_token'] != token:raise Conflict('Worker is fenced')
                    request,compiled = self.validate(row)
                    step = db.execute("SELECT * FROM v2_steps WHERE run_id=? AND status='PENDING' ORDER BY ordinal LIMIT 1",(identity,)).fetchone()
                    if step is None:raise Conflict('No resumable pending step')
                    step = dict(step); ordinal = step['ordinal']
                    action=request['actions'][ordinal];tool=action['tool'];payload=action['input']
                    if tool!=step['tool']:raise Conflict('Action registry binding changed')
                    if TOOLS[tool]['cloud']:
                        if row['calls_reserved'] >= row['call_budget']:raise Conflict('Call budget exhausted')
                        if db.execute("SELECT 1 FROM v2_steps WHERE status='DISPATCHED' LIMIT 1").fetchone():raise Conflict('Another query is uncertain')
                        expected = digest(compiled[ordinal])
                        if expected != step['request_hash']:raise Conflict('Compiled request changed')
                        db.execute('UPDATE v2_runs SET calls_reserved=calls_reserved+1 WHERE id=?',(identity,))
                    else:
                        ids = {s['ordinal']:s['receipt_id'] for s in db.execute('SELECT ordinal,receipt_id FROM v2_steps WHERE run_id=?',(identity,))}
                        comparison_request = {'native_receipt_id':ids[payload['native_step']], 'source_receipt_id':ids[payload['source_step']]}
                        if tool=='reconcile_records':
                            comparison_request.update(native_records_id=ids[payload['native_records_step']],source_records_id=ids[payload['source_records_step']],
                                                      measure_id=payload['measure_id'],record_mapping_id=payload['record_mapping_id'])
                        else:comparison_request.update({k:payload[k] for k in (('column_bindings','filter_bindings') if tool=='compare_records' else ('measure_id','mapping_id'))})
                        db.execute('UPDATE v2_steps SET request_hash=? WHERE run_id=? AND ordinal=?',
                                   (digest(comparison_request),identity,ordinal))
                    db.execute("UPDATE v2_steps SET status='DISPATCHED' WHERE run_id=? AND ordinal=?",(identity,ordinal))
                    self.event(db,identity,'DISPATCHED',{'ordinal':ordinal,'receipt_id':step['receipt_id']})
                if tool == 'native':
                    result = native_diagnostics.run(self.store,payload,self.native_transport,receipt_id=step['receipt_id'])
                elif tool == 'source':
                    result = source_diagnostics.run(self.store,payload,self.config,self.source_transport,receipt_id=step['receipt_id'])
                elif tool in ('native_records','source_records'):
                    result=record_readback.run(self.store,payload,self.config,tool,
                        self.native_transport if tool=='native_records' else self.source_transport,receipt_id=step['receipt_id'])
                elif tool=='reconcile_records':
                    result=record_aggregate.assess(self.store,row['model_id'],comparison_request,assessment_id=step['receipt_id'])
                elif tool=='compare_records':
                    result=record_comparison.assess(self.store,row['model_id'],comparison_request,assessment_id=step['receipt_id'])
                else:
                    result = comparisons.assess(self.store,row['model_id'],comparison_request,
                        assessment_id=step['receipt_id'])
                self.commit(identity,ordinal,token,result)
                if self.get(identity)['status']!='RUNNING':return self.get(identity)
        except Exception as exc:
            with self.db() as db:
                row = self.load(db,identity)
                if row['lease_token'] == token:
                    db.execute("UPDATE v2_runs SET status='HELD',lease_token=NULL WHERE id=?",(identity,))
                    self.event(db,identity,'HELD',{'error_type':type(exc).__name__})
            return self.get(identity)

    def cancel_in_transaction(self,db,identity):
        row=self.load(db,identity)
        if row['status'] in ('COMPLETED','CANCELLED'):return
        db.execute('INSERT OR IGNORE INTO v2_cancellations VALUES(?,?)',(identity,datetime.now(timezone.utc).isoformat()))
        db.execute("UPDATE v2_runs SET status='CANCELLED',lease_token=NULL WHERE id=?",(identity,))
        self.event(db,identity,'CANCELLED',{'remote_cancellation_confirmed':False})

    def cancel(self,identity):
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE');self.cancel_in_transaction(db,identity)
        return self.get(identity)

    def reconcile(self, identity):
        """Adopt only a terminal receipt at the reserved ID; never resend a read."""
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE'); row = self.load(db,identity)
            cancelled=bool(db.execute('SELECT 1 FROM v2_cancellations WHERE run_id=?',(identity,)).fetchone())
            admission_valid = True
            try:self.validate(row)
            except Conflict:admission_valid = False
            steps = [dict(s) for s in db.execute("SELECT * FROM v2_steps WHERE run_id=? AND status='DISPATCHED'",(identity,))]
            if not steps and cancelled:return self.get(identity)
            if not steps:
                states = [s[0] for s in db.execute('SELECT status FROM v2_steps WHERE run_id=?',(identity,))]
                if row['status'] not in ('RUNNING','HELD') or 'FAILED' in states:
                    raise Conflict('No safely resumable interrupted run')
                db.execute('UPDATE v2_runs SET status=?,lease_token=NULL WHERE id=?',('READY' if admission_valid else 'HELD',identity))
                self.event(db,identity,'RECONCILED_BEFORE_DISPATCH',{})
            if len(steps)>1:raise Conflict('Multiple orphaned dispatches require investigation')
            for step in steps:
                if step['tool'] in ('compare','compare_records','reconcile_records'):
                    table=TOOLS[step['tool']]['receipt_table']
                    exists = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone()
                    saved = db.execute('SELECT body,hash,model_id FROM '+table+' WHERE id=?', (step['receipt_id'],)).fetchone() if exists else None
                    if not saved:
                        # Pure local assessment can be replayed after fencing;
                        # it cannot dispatch a cloud query or consume a call.
                        db.execute("UPDATE v2_steps SET status='PENDING' WHERE run_id=? AND ordinal=?",(identity,step['ordinal']))
                        db.execute('UPDATE v2_runs SET status=?,lease_token=NULL WHERE id=?',('CANCELLED' if cancelled else 'READY' if admission_valid else 'HELD',identity))
                        self.event(db,identity,'RECONCILED_LOCAL_REPLAY',{'ordinal':step['ordinal']})
                        continue
                    result = json.loads(saved['body'])
                    if saved['model_id'] != row['model_id'] or digest(result) != saved['hash'] or digest(result['request']) != step['request_hash']:
                        raise Conflict('Assessment does not match reserved request')
                    result = dict(result,id=step['receipt_id'],hash=saved['hash'])
                else:
                    table = TOOLS[step['tool']]['receipt_table']
                    exists = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone()
                    receipt = db.execute('SELECT model_id,status,request,result FROM '+table+' WHERE id=?',(step['receipt_id'],)).fetchone() if exists else None
                    if not receipt or receipt['status'] in ('RUNNING','INTERRUPTED'):raise Conflict('Remote completion is still uncertain')
                    if step['tool'] in ('native_records','source_records'):
                        record_readback.read(self.store,row['model_id'],step['receipt_id'])
                    if step['tool'] in ('native','source'):
                        from .receipt_integrity import verify
                        verify(db,step['tool'],step['receipt_id'])
                    compiled = json.loads(receipt['request']); compiled.pop('plan')
                    if receipt['model_id'] != row['model_id'] or digest(compiled) != step['request_hash']:raise Conflict('Receipt does not match reserved request')
                    result = {'id':step['receipt_id'],'status':receipt['status'],'request_hash':step['request_hash'],'result':json.loads(receipt['result'])}
                success = not TOOLS[step['tool']]['cloud'] or result.get('status','COMPLETED') == 'COMPLETED'
                db.execute('UPDATE v2_steps SET status=?,result=? WHERE run_id=? AND ordinal=?',
                           ('COMPLETED' if success else 'FAILED',encoded(result),identity,step['ordinal']))
                remaining=db.execute("SELECT 1 FROM v2_steps WHERE run_id=? AND status!='COMPLETED'",(identity,)).fetchone()
                state = 'COMPLETED' if success and not remaining else 'READY' if success else 'HELD'
                if not admission_valid:state='HELD'
                if cancelled:state='CANCELLED'
                db.execute('UPDATE v2_runs SET status=?,lease_token=NULL,outcome=? WHERE id=?',
                           (state,encoded(self.outcome(db,identity)) if state=='COMPLETED' else row['outcome'],identity))
                self.event(db,identity,'RECONCILED',{'ordinal':step['ordinal'],'receipt_id':step['receipt_id']})
        return self.get(identity)

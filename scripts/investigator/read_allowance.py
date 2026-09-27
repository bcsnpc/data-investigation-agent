"""Atomic read admission. Operator credits never change ordinary policy or refund usage."""
import json
import math
from .onboarding import encoded, fields, text

WINDOW_SECONDS = 86400


def initialize(db):
    db.executescript('''
      CREATE INDEX IF NOT EXISTS adaptive_usage_read_window ON adaptive_usage(environment,kind,created);
      CREATE TABLE IF NOT EXISTS read_batches(
        environment TEXT, batch_id TEXT, approval TEXT, issued REAL, expires REAL,
        PRIMARY KEY(environment,batch_id));
      CREATE TABLE IF NOT EXISTS read_batch_runs(
        environment TEXT, session_id TEXT, batch_id TEXT, purpose TEXT, allowance INTEGER,
        PRIMARY KEY(environment,session_id));
      CREATE TABLE IF NOT EXISTS read_allocations(
        environment TEXT, session_id TEXT, reservation_key TEXT, batch_id TEXT, purpose TEXT,
        PRIMARY KEY(environment,session_id,reservation_key));
    ''')


def grant(db, environment, approval, now):
    """Explicit operator operation; caller holds BEGIN IMMEDIATE. Not a planner tool.

    Each run receives its own earmarked credits. RESTORATION run IDs cannot be
    used by an investigation, and unused credits cannot spill to another run.
    """
    fields(approval, ['batch_id','environment','approved_by','approval_reference','expires_at','runs'])
    if approval['environment'] != environment: raise ValueError('Batch environment differs')
    for key in ('batch_id','approved_by','approval_reference'): text(approval[key], 500)
    expiry=approval['expires_at']
    if type(expiry) not in (float,int) or not math.isfinite(expiry) or expiry<=now:
        raise ValueError('Batch must have a future finite expiry')
    runs=approval['runs']
    if not isinstance(runs,list) or not 1<=len(runs)<=100: raise ValueError('Invalid batch runs')
    seen=set()
    for run in runs:
        fields(run,['session_id','purpose','reads'])
        text(run['session_id'],200)
        if run['session_id'] in seen: raise ValueError('Duplicate batch run')
        seen.add(run['session_id'])
        if run['purpose'] not in ('INVESTIGATION','RESTORATION'): raise ValueError('Invalid read purpose')
        if type(run['reads']) is not int or not 1<=run['reads']<=10000: raise ValueError('Invalid run credits')
        if db.execute('SELECT 1 FROM adaptive_usage WHERE environment=? AND session_id=?',
                      (environment,run['session_id'])).fetchone():
            raise ValueError('Credits must be assigned before the run starts')
    previous=db.execute('SELECT approval FROM read_batches WHERE environment=? AND batch_id=?',
                        (environment,approval['batch_id'])).fetchone()
    if previous: raise ValueError('Batch approval is immutable; already recorded')
    db.execute('INSERT INTO read_batches VALUES(?,?,?,?,?)',
               (environment,approval['batch_id'],encoded(approval),now,expiry))
    for run in runs:
        db.execute('INSERT INTO read_batch_runs VALUES(?,?,?,?,?)',
                   (environment,run['session_id'],approval['batch_id'],run['purpose'],run['reads']))


def ordinary_used(db, environment, now):
    # Legacy records have no allocation. Count them conservatively, without
    # pretending their historical logical reads were physically metered.
    return sum(json.loads(r[0])['cloud_calls'] for r in db.execute('''
      SELECT u.reserved FROM adaptive_usage u LEFT JOIN read_allocations a
      ON a.environment=u.environment AND a.session_id=u.session_id AND a.reservation_key=u.reservation_key
      WHERE u.environment=? AND u.kind='cloud' AND u.created>? AND (a.batch_id IS NULL)
    ''',(environment,now-WINDOW_SECONDS)))


def allocate(db, environment, session_id, key, now, ordinary_limit, purpose, hold):
    if purpose not in ('INVESTIGATION','RESTORATION'): raise ValueError('Invalid read purpose')
    run=db.execute('''SELECT r.*,b.expires FROM read_batch_runs r JOIN read_batches b
      ON b.environment=r.environment AND b.batch_id=r.batch_id WHERE r.environment=? AND r.session_id=?''',
      (environment,session_id)).fetchone()
    if run:
        if run['purpose']!=purpose: raise hold('Batch run purpose differs')
        if now>=run['expires']: raise hold('Batch credits expired')
        used=db.execute('SELECT count(*) FROM read_allocations WHERE environment=? AND session_id=?',
                        (environment,session_id)).fetchone()[0]
        if used>=run['allowance']: raise hold('Batch per-run read allowance exhausted')
        batch_id=run['batch_id']
    else:
        if purpose=='RESTORATION': raise hold('Restoration needs earmarked batch credits')
        if ordinary_used(db,environment,now)>=ordinary_limit: raise hold('Rolling 24-hour read allowance exhausted')
        batch_id=None
    db.execute('INSERT INTO read_allocations VALUES(?,?,?,?,?)',(environment,session_id,key,batch_id,purpose))


def snapshot(db, environment, now, limit):
    batches=[]
    for row in db.execute('SELECT * FROM read_batches WHERE environment=? ORDER BY issued',(environment,)):
        runs=[]
        for r in db.execute('SELECT * FROM read_batch_runs WHERE environment=? AND batch_id=?',
                            (environment,row['batch_id'])):
            used=db.execute('SELECT count(*) FROM read_allocations WHERE environment=? AND session_id=?',
                            (environment,r['session_id'])).fetchone()[0]
            runs.append({'session_id':r['session_id'],'purpose':r['purpose'],'allowance':r['allowance'],
                         'charged':used,'available':max(0,r['allowance']-used) if now<row['expires'] else 0})
        batches.append({'batch_id':row['batch_id'],'expires_at':row['expires'],
                        'expired':now>=row['expires'],'runs':runs})
    used=ordinary_used(db,environment,now)
    return {'window_seconds':WINDOW_SECONDS,'ordinary_limit':limit,'ordinary_charged':used,
            'ordinary_available':max(0,limit-used),'batches':batches,
            'accounting':'Physical request reservations; pre-migration records retain historical logical counts.'}

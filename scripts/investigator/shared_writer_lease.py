"""Short-lived application writer isolation using the existing document table.

This is a cooperative process guard, not a new database privilege. Old images
and raw administrative SQL must be drained separately before an isolated run.
"""
from contextlib import contextmanager
import json,os,re,time,math

NAMESPACE='application_writer_lease'
IDENTITY='exclusive'
OWNER_ENV='INVESTIGATOR_WORKER_ID'
LEASE_ENV='INVESTIGATOR_EXCLUSIVE_LEASE_ID'

def _now(state,db):
    if state.backend=='postgresql':return float(db.execute('SELECT EXTRACT(EPOCH FROM clock_timestamp())').fetchone()[0])
    return time.time()

def _table_exists(state,db):
    if state.backend=='postgresql':return db.execute("SELECT to_regclass('state_documents')").fetchone()[0]is not None
    return db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='state_documents'").fetchone()is not None

def check(state,db,*,release_only=False):
    """Called before waiting for the lock, then again after obtaining it."""
    from .shared_state import StateConflict,sha
    deadline=os.environ.get('INVESTIGATOR_CLOUD_WORK_DEADLINE')
    if deadline is not None and state.backend=='postgresql' and not release_only:
        try:deadline=float(deadline)
        except ValueError:raise StateConflict('CLOUD_WORK_DEADLINE_INVALID')from None
        if not math.isfinite(deadline)or _now(state,db)>=deadline:raise StateConflict('CLOUD_WORK_DEADLINE_EXPIRED')
    if not _table_exists(state,db):
        if os.environ.get(LEASE_ENV):raise StateConflict('EXCLUSIVE_WRITER_LEASE_NOT_ESTABLISHED')
        return
    row=state.sql(db,'SELECT body,body_hash FROM state_documents WHERE namespace=? AND identity=?',(NAMESPACE,IDENTITY)).fetchone()
    if row is None:
        if os.environ.get(LEASE_ENV):raise StateConflict('EXCLUSIVE_WRITER_LEASE_NOT_ESTABLISHED')
        return
    value=json.loads(row[0])
    if sha(value)!=row[1]:raise StateConflict('EXCLUSIVE_WRITER_LEASE_HASH_DIFFERS')
    ours=value['owner']==os.environ.get(OWNER_ENV) and value['lease_id']==os.environ.get(LEASE_ENV)
    if release_only:
        if not ours:raise StateConflict('EXCLUSIVE_WRITER_RELEASE_OWNER_DIFFERS')
        return
    if value['status']=='ACTIVE' and _now(state,db)<value['expires_at']:
        if not ours:raise StateConflict('EXCLUSIVE_WRITER_LEASE_OWNED_BY_ANOTHER_JOB')
    elif os.environ.get(LEASE_ENV):
        raise StateConflict('EXCLUSIVE_WRITER_LEASE_EXPIRED_OR_RELEASED')

def acquire(state,*,owner,lease_id,expires_at,approval):
    from .shared_state import StateConflict,encoded,sha
    if not all(isinstance(v,str)and re.fullmatch(r'[A-Za-z0-9_.:-]{1,100}',v)for v in (owner,lease_id)):
        raise ValueError('EXCLUSIVE_WRITER_ID_REQUIRED')
    if not isinstance(approval,str)or not approval.strip():raise ValueError('EXCLUSIVE_WRITER_APPROVAL_REQUIRED')
    if os.environ.get(LEASE_ENV):raise StateConflict('EXCLUSIVE_WRITER_NESTING_FORBIDDEN')
    with state.transaction()as db:
        now=_now(state,db)
        if type(expires_at)not in (int,float)or not now<expires_at<=now+3600:raise ValueError('EXCLUSIVE_WRITER_EXPIRY_BOUND')
        try:prior=state._get(db,NAMESPACE,IDENTITY)
        except KeyError:prior=None
        if prior and prior['body']['status']=='ACTIVE'and prior['body']['expires_at']>now:
            raise StateConflict('EXCLUSIVE_WRITER_LEASE_ALREADY_ACTIVE')
        value={'owner':owner,'lease_id':lease_id,'issued_at':now,'expires_at':expires_at,'approval':approval,'status':'ACTIVE'}
        if prior:
            history=IDENTITY+':'+str(prior['revision'])
            state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',(NAMESPACE+'_history',history,0,encoded(prior['body']),sha(prior['body'])))
            state.sql(db,'UPDATE state_documents SET revision=?,body=?,body_hash=? WHERE namespace=? AND identity=?',
                      (prior['revision']+1,encoded(value),sha(value),NAMESPACE,IDENTITY))
        else:state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',(NAMESPACE,IDENTITY,0,encoded(value),sha(value)))
    return value

def release(state,lease):
    from .shared_state import StateConflict,encoded,sha
    # Expired owners must not perform normal writes. Release is an explicit
    # control transaction, so clear only this process's expired marker first.
    saved=os.environ.get(LEASE_ENV);previous=os.environ.get(OWNER_ENV)
    try:
        os.environ[LEASE_ENV]=lease['lease_id'];os.environ[OWNER_ENV]=lease['owner']
        with state.transaction(_lease_release=True)as db:
            prior=state._get(db,NAMESPACE,IDENTITY);body=prior['body']
            if body['lease_id']!=lease['lease_id']or body['owner']!=lease['owner']:
                raise StateConflict('EXCLUSIVE_WRITER_RELEASE_OWNER_DIFFERS')
            body=dict(body,status='RELEASED',released_at=_now(state,db))
            state.sql(db,'UPDATE state_documents SET revision=?,body=?,body_hash=? WHERE namespace=? AND identity=?',
                      (prior['revision']+1,encoded(body),sha(body),NAMESPACE,IDENTITY))
    finally:
        os.environ.pop(LEASE_ENV,None)
        if saved is not None:os.environ[LEASE_ENV]=saved
        if previous is None:os.environ.pop(OWNER_ENV,None)
        else:os.environ[OWNER_ENV]=previous

def require(state,declaration,*,deadline):
    """Worker preflight: exact admitted job owns a live lease covering its run."""
    from .shared_state import StateConflict
    if (not isinstance(declaration,dict)or set(declaration)!={'owner','lease_id','expires_at'}
            or declaration['owner']!=os.environ.get(OWNER_ENV)
            or declaration['lease_id']!=os.environ.get(LEASE_ENV)):
        raise StateConflict('EXCLUSIVE_WRITER_JOB_DECLARATION_DIFFERS')
    with state.transaction()as db:
        value=state._get(db,NAMESPACE,IDENTITY)['body']
        if any(value[k]!=v for k,v in declaration.items())or value['expires_at']<deadline:
            raise StateConflict('EXCLUSIVE_WRITER_DEADLINE_NOT_COVERED')
    return {'owner':value['owner'],'lease_id':value['lease_id'],'expires_at':value['expires_at'],'status':'ACTIVE'}

@contextmanager
def isolated(state,*,owner,lease_id,expires_at,approval):
    lease=acquire(state,owner=owner,lease_id=lease_id,expires_at=expires_at,approval=approval)
    previous=os.environ.get(OWNER_ENV);os.environ[OWNER_ENV]=owner;os.environ[LEASE_ENV]=lease_id
    failure=None
    try:yield lease
    except BaseException as exc:failure=exc;raise
    finally:
        try:release(state,lease)
        except BaseException as exc:
            if failure is None:raise
            failure.add_note('Exclusive writer lease release failed: '+type(exc).__name__+'; expiry remains authoritative.')
        finally:
            os.environ.pop(LEASE_ENV,None)
            if previous is None:os.environ.pop(OWNER_ENV,None)
            else:os.environ[OWNER_ENV]=previous

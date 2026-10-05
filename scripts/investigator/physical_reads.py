"""Meter physical requests inside an admitted diagnostic operation.

The first slot is conservatively reserved before transport preparation. Each
subsequent SQL command/HTTP request needs admission before the child may send it.
Authentication and connection handshakes are not data/metadata read requests.
"""
from contextlib import contextmanager
from contextvars import ContextVar
import json
from hashlib import sha256
from .process_tape import uuid4
from pathlib import Path
import subprocess
from threading import Timer

_scope=ContextVar('physical_read_scope',default=None)
_guards=ContextVar('run_guard_cache',default=None)


def decode_completion(raw,kind,*,guard=False):
    done=json.loads(raw)
    if not isinstance(done,dict):raise RuntimeError('Physical request completion unavailable')
    if done.get('physical_read')!='DONE' or done.get('kind')!=kind:
        if done.get('error') or done.get('status')=='UNAVAILABLE':return None
        raise RuntimeError('Physical request completion unavailable')
    if done.get('status')!='AVAILABLE':raise RuntimeError('Physical request failed')
    if guard and done.get('guard_passed') is not True:raise RuntimeError('Guard success not established')
    return done


@contextmanager
def guard_scope(record):
    # Never persisted or shared between runs; a restart establishes guards anew.
    token=_guards.set({'cache':{},'record':record})
    try: yield
    finally: _guards.reset(token)



@contextmanager
def scope(meter):
    state={'first':True,'meter':meter,'first_report':None}
    token=_scope.set(state)
    try: yield state
    finally: _scope.reset(token)


def retry_connection(read):
    """Admit each connection retry before transport; preserve the failed slot.

    The enclosing diagnostic's initial reservation stays charged. The retry's
    meter installs a fresh physical scope, so its first guard consumes its own
    reservation, and subsequent commands remain individually admitted.
    """
    state=_scope.get()
    if state is None:return read()
    if state['first']:
        state['first']=False
        state['first_report']={'status':'FAILED','request_kind':'sql_connection'}
    return state['meter']('sql_connection_retry',read)


def connection_failure(number):
    """The reserved slot observed a failed connection, before any SQL command."""
    state=_scope.get()
    if state is not None and state['first']:
        state['first']=False
        state['first_report']={'status':'FAILED','request_kind':'sql_connection',
                               'sql_error_number':number,'stage':'connect'}


def run(command, *, input, timeout, fallback=None, **kwargs):
    state=_scope.get()
    if state is None:
        from .tape_worker import run as worker_run
        return worker_run(command,input=input,timeout=timeout,fallback=fallback,**kwargs)
    command=list(command)+(['-Metered'] if any(str(c).endswith('.ps1') for c in command) else ['--metered'])
    payload=json.loads(input)
    # Credential fingerprint stays in memory only, never in receipts.
    def secret_connection():
        credential=payload.get('access_token','')
        if payload.get('credential_file'):
            credential=Path(payload['credential_file']).read_bytes().hex()
        return sha256(json.dumps([command,payload.get('server'),payload.get('database'),credential],sort_keys=True).encode()).hexdigest()
    from .process_tape import ACTIVE as RUN_TAPE,value
    tape=RUN_TAPE.get()
    if tape:
        def opaque_connection():
            # Only a random label crosses the tape boundary. Secret hashes stay
            # in memory, with exactly the existing credential-sensitive keying.
            from uuid import uuid4 as fresh_id
            if not hasattr(tape,'connections'):tape.connections={}
            fingerprint=secret_connection()
            return tape.connections.setdefault(fingerprint,str(fresh_id()))
        connection=value('AUTH_STATE','guard_connection',opaque_connection)
    else:connection=secret_connection()
    guards=_guards.get()
    from .tape_worker import popen
    child=popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
                           text=True,encoding='utf-8',worker_timeout=timeout)
    def expire():
        child.deadline_expired=True
        child.kill()
    timer=Timer(timeout,expire);timer.daemon=True;timer.start()
    def line():
        value=child.stdout.readline(2*1024*1024+1)
        if not value:
            from .tape_worker import check_deadline
            check_deadline(child)
        if not value or len(value)>2*1024*1024: raise RuntimeError('Physical read response unavailable')
        return value
    final=None
    try:
        child.stdin.write(input+'\n');child.stdin.flush()
        while True:
            raw=line();message=json.loads(raw)
            if message.get('physical_read')!='REQUEST':
                child.wait(timeout=5)
                return subprocess.CompletedProcess(command,child.returncode,raw,'')
            kind=message.get('kind')
            if kind not in ('sql_identity','sql_database_permissions','sql_object_permissions',
                            'sql_quantity','onelake_listing','onelake_commit','metadata_read'):
                raise ValueError('Unknown physical request')
            cache_key=(connection,kind,message.get('object'))
            cacheable=kind in ('sql_database_permissions','sql_object_permissions') and message.get('cache_guard') is True
            if cacheable and kind=='sql_object_permissions' and message.get('object') not in payload.get('read_only_objects',[]):
                raise ValueError('Guard object outside admitted request')
            if cacheable and guards and cache_key in guards['cache']:
                guards['record']({'status':'REUSED','kind':kind,'established_receipt':guards['cache'][cache_key],
                                  'server':payload.get('server'),'database':payload.get('database'),'object':message.get('object')})
                child.stdin.write('REUSE\n');child.stdin.flush()
                continue
            established=None
            def send():
                nonlocal final,established
                child.stdin.write('ALLOW\n');child.stdin.flush()
                raw_done=line();done=decode_completion(raw_done,kind,guard=cacheable)
                if done is None:
                    final=raw_done
                    return {'status':'UNAVAILABLE','request_kind':kind}
                if cacheable:
                    established=str(uuid4())
                return {'status':'AVAILABLE','request_kind':kind,'guard_receipt':established}
            if state['first']:
                state['first']=False
                state['first_report']={'status':'UNCERTAIN','request_kind':kind}
                state['first_report']=send()
            else: state['meter'](kind,send)
            if established and guards:
                guards['record']({'status':'ESTABLISHED','kind':kind,'established_receipt':established,
                                  'server':payload.get('server'),'database':payload.get('database'),'object':message.get('object')})
                guards['cache'][cache_key]=established
            if final is not None:
                child.wait(timeout=5)
                return subprocess.CompletedProcess(command,child.returncode,final,'')
    finally:
        timer.cancel()
        try:
            if child.poll() is None: child.kill()
        except OSError: pass
        child.wait()
        for pipe in (child.stdin,child.stdout):
            try: pipe.close()
            except OSError: pass  # Cleanup must not replace an admission refusal.

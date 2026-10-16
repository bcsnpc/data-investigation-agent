"""Retain local SQLite accounting failures independently of provider evidence.

This is a new-recording contract, never a migration of earlier tapes.
Only SQLite system messages are retained; arbitrary database messages cannot
write SQL literals or secrets into this control event.
"""
import json
import re
import sqlite3
from . import process_tape as journal

PIN='SQLITE_BOUNDARY_V1'
CONTROL='LOCAL_ACCOUNTING_BOUNDARY'
MESSAGES=frozenset(('database is locked','database table is locked','disk I/O error',
    'database or disk is full','unable to open database file','attempt to write a readonly database',
    'cannot start a transaction within a transaction','cannot commit - no transaction is active'))

def enabled(tape):
    return tape is not None and getattr(tape,'bootstrap',{}).get('state',{}).get('local_accounting')==PIN

def pending(stage):
    tape=journal.ACTIVE.get()
    if not enabled(tape) or not tape.replaying:return None
    raw=tape.peek('CONFIGURATION')
    if raw is None:return None
    body=json.loads(raw)
    return body if body.get('control')==CONTROL and body.get('stage')==stage else None

def raise_saved(body):
    error=body['error']
    if (set(error)!={'type','message','message_withheld','sqlite_errorcode','sqlite_errorname'}
            or error['type'] not in ('Error','OperationalError','DatabaseError','IntegrityError','ProgrammingError',
                                     'InterfaceError','InternalError','NotSupportedError','DataError')
            or not isinstance(error['message'],str) or len(error['message'])>160
            or type(error['message_withheld']) is not bool
            or (error['sqlite_errorcode'] is not None and (type(error['sqlite_errorcode']) is not int or not 0<=error['sqlite_errorcode']<=2147483647))
            or (error['sqlite_errorname'] is not None and (not isinstance(error['sqlite_errorname'],str) or not re.fullmatch(r'SQLITE_[A-Z0-9_]{1,48}',error['sqlite_errorname'])))):
        raise journal.TapeError('LOCAL_ACCOUNTING_ERROR_SCHEMA')
    exc=getattr(sqlite3,error['type'])(error['message'])
    for name in ('sqlite_errorcode','sqlite_errorname'):
        if error[name] is not None:setattr(exc,name,error[name])
    exc.sqlite_phase=body['stage']
    raise exc from None

def boundary(stage,producer):
    tape=journal.ACTIVE.get()
    if not enabled(tape):return producer()
    saved=pending(stage)
    if saved is not None and saved['status']=='FAILED':
        tape.take('CONFIGURATION')
        raise_saved(saved)
    try:result=producer()
    except sqlite3.Error as exc:
        exc.sqlite_phase=stage
        message=str(exc);safe=message in MESSAGES
        code=getattr(exc,'sqlite_errorcode',None);name=getattr(exc,'sqlite_errorname',None)
        if type(code) is not int or not 0<=code<=2147483647:code=None
        if not isinstance(name,str) or not re.fullmatch(r'SQLITE_[A-Z0-9_]{1,48}',name):name=None
        saved={'control':CONTROL,'stage':stage,'status':'FAILED',
            'error':{'type':type(exc).__name__,'message':message if safe else 'SQLite accounting error (message withheld)',
                     'message_withheld':not safe,'sqlite_errorcode':code,'sqlite_errorname':name}}
        journal.event('CONFIGURATION',saved)
        # Prevent an arbitrary SQLite literal from escaping into a public error
        # or traceback after it was intentionally withheld from the evidence.
        if not safe:raise_saved(saved)
        raise
    journal.event('CONFIGURATION',{'control':CONTROL,'stage':stage,'status':'COMPLETED','error':None})
    return result

def replay_optional(stage):
    """Private dollar DB is intentionally absent in isolated replay.

    Consume its recorded settlement boundary if present; do not manufacture a
    dollar mutation or a boundary for an installation that had no dollar guard.
    """
    if pending(stage) is not None:return boundary(stage,lambda:None)

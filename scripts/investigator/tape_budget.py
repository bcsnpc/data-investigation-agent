"""Journal admission and settlement, including refused attempts, in run order."""
from functools import wraps
import json
from .process_tape import event,ACTIVE,TapeError,bytes_of


TABLES=('adaptive_usage','read_batches','read_batch_runs','read_allocations')
MAX_INPUT_ROWS=100000


def validate_input(body,environment,owned,schemas):
    if (set(body)!={'environment','owned_sessions','tables'} or body['environment']!=environment
            or body['owned_sessions']!=sorted(owned) or set(body['tables'])!=set(TABLES)):
        raise TapeError('TAPE_BUDGET_INPUT_SCOPE')
    for table in TABLES:
        saved=body['tables'][table];columns=schemas[table]
        if (set(saved)!={'columns','rows'} or saved['columns']!=columns or not isinstance(saved['rows'],list)
                or len(saved['rows'])>MAX_INPUT_ROWS):raise TapeError('TAPE_BUDGET_INPUT_SCHEMA')
        for row in saved['rows']:
            if (not isinstance(row,list) or len(row)!=len(columns)
                    or row[columns.index('environment')]!=environment
                    or ('session_id' in columns and row[columns.index('session_id')] in owned)):
                raise TapeError('TAPE_BUDGET_INPUT_OWNED_ROW')


def checkpoint(self,db,session_id):
    """Record shared inputs; replay never overwrites this tape's own decisions.

    Another session can charge usage or obtain credits while a provider is in
    flight. These rows are environmental inputs, not this procedure's outputs.
    They are already retained as budget metadata in the sealed catalog.
    """
    tape=ACTIVE.get()
    if tape is None:return
    owned=getattr(tape,'budget_owned_sessions',set())
    owned.add(session_id);tape.budget_owned_sessions=owned
    from .budget_checkpoint import enabled,checkpoint as delta_checkpoint
    if enabled(tape):
        return delta_checkpoint(tape,db,self.environment,owned)
    schemas={table:[r[1] for r in db.execute('PRAGMA table_info('+table+')')] for table in TABLES}
    def external_rows(table,columns):
        sql='SELECT * FROM '+table+' WHERE environment=?';args=[self.environment]
        if 'session_id' in columns:
            sql+=' AND session_id NOT IN ('+','.join('?' for _ in owned)+')';args+=sorted(owned)
        return sorted([list(row) for row in db.execute(sql,args)],key=bytes_of)
    if tape.replaying:
        # Old tapes keep their original coverage/failures. Never backfill a
        # missing checkpoint from the current catalog to turn one into a pass.
        if tape.events[tape.index]['kind']!='BUDGET_INPUT':return
        body=json.loads(tape.take('BUDGET_INPUT'))
        validate_input(body,self.environment,owned,schemas)
        for table in TABLES:
            saved=body['tables'][table];columns=schemas[table]
            sql='DELETE FROM '+table+' WHERE environment=?';args=[self.environment]
            if 'session_id' in columns:
                sql+=' AND session_id NOT IN ('+','.join('?' for _ in owned)+')';args+=sorted(owned)
            db.execute(sql,args)
            db.executemany('INSERT INTO '+table+' VALUES('+','.join('?' for _ in columns)+')',saved['rows'])
    else:
        tables={table:{'columns':columns,'rows':external_rows(table,columns)} for table,columns in schemas.items()}
        body={'environment':self.environment,'owned_sessions':sorted(owned),'tables':tables}
        validate_input(body,self.environment,owned,schemas)
        event('BUDGET_INPUT',body)


def decision(method):
    @wraps(method)
    def run(self,db,session_id,key,*args,**kwargs):
        # Public admission accepts a caller-owned connection. Prepare its codec
        # BEFORE any physical work or journaled reservation, also outside tapes.
        from .budget_delta_v2 import register_codec
        register_codec(db)
        if ACTIVE.get() is None:return method(self,db,session_id,key,*args,**kwargs)
        checkpoint(self,db,session_id)
        def snapshot():
            row=db.execute('SELECT status,reserved,actual FROM adaptive_usage WHERE environment=? AND session_id=? AND reservation_key=?',
                           (self.environment,session_id,key)).fetchone()
            return {'reservation':list(row) if row else None,
                    'usage_rows':db.execute('SELECT count(*) FROM adaptive_usage WHERE environment=?',(self.environment,)).fetchone()[0],
                    'policy':self.policy}
        request={'operation':method.__name__,'session_id':session_id,'key':key,'args':list(args),'kwargs':kwargs}
        event('BUDGET',{'phase':'BEFORE','request':request,'state':snapshot()})
        error=None
        try:return method(self,db,session_id,key,*args,**kwargs)
        except BaseException as exc:
            error=type(exc).__name__
            raise
        finally:
            checkpoint(self,db,session_id)
            event('BUDGET',{'phase':'AFTER','request':request,'state':snapshot(),'error':error})
    return run

"""v8 lossless REAL journal beside unchanged v1 machinery."""
import json,sqlite3
from contextlib import closing
from pathlib import Path
from .process_tape import TapeError,bytes_of,sha
TABLES=('adaptive_usage','read_batches','read_batch_runs','read_allocations')
VERSION='bounded-worker-tape-v8'

def enabled(tape):
    return getattr(tape,'version',None) in (VERSION,'privacy-projected-tape-v2') and getattr(tape,'bootstrap',{}).get('state',{}).get('budget_checkpoint')=='DELTA_V2'

def register_codec(db):
    # Must be invoked on EVERY connection that can write any budget table.
    # Missing registration causes SQLite to refuse the write; never skip a guard.
    import math
    def encode(value):
        if type(value) is not float or not math.isfinite(value):raise ValueError('Budget REAL must be finite binary64')
        return value.hex()
    db.create_function('budget_real_hex_v2',1,encode,deterministic=True)

def decode_row(text):
    import math
    values=json.loads(text)
    if not isinstance(values,list):raise TapeError('TAPE_BUDGET_REAL_ROW')
    out=[]
    for value in values:
        if isinstance(value,dict):
            if set(value)!={'$binary64'} or not isinstance(value['$binary64'],str):raise TapeError('TAPE_BUDGET_REAL_TAG')
            try:real=float.fromhex(value['$binary64'])
            except ValueError as exc:raise TapeError('TAPE_BUDGET_REAL_ENCODING') from exc
            if not math.isfinite(real) or real.hex()!=value['$binary64']:raise TapeError('TAPE_BUDGET_REAL_CANONICAL')
            value=real
        out.append(value)
    return out

def layout(db):
    result={}
    for table in TABLES:
        info=list(db.execute('PRAGMA table_info('+table+')'))
        columns=[r[1] for r in info];keys=[r[1] for r in sorted(info,key=lambda r:r[5]) if r[5]]
        if not columns or not keys or 'environment' not in columns:raise TapeError('TAPE_BUDGET_DELTA_SCHEMA')
        result[table]={'columns':columns,'keys':keys}
    return result

def trigger_sql(schemas):
    """Producer DDL and consumer validation share the complete mutation grammar."""
    result={}
    for table,schema in schemas.items():
        def row(prefix):
            def slot(c):
                expr=prefix+'."'+c+'"'
                return "CASE WHEN typeof("+expr+")='real' THEN json_object('$binary64',budget_real_hex_v2("+expr+")) ELSE "+expr+" END"
            return 'json_array('+','.join(slot(c) for c in schema['columns'])+')'
        for operation,before,after in [('INSERT','NULL',row('NEW')),('DELETE',row('OLD'),'NULL')]:
            name='budget_v2_delta_'+table+'_'+operation.lower()
            result[name]='CREATE TRIGGER '+name+' AFTER '+operation+' ON '+table+' BEGIN INSERT INTO budget_mutations_v2(environment,table_name,before_row,after_row) VALUES ('+('OLD' if operation=='DELETE' else 'NEW')+'.environment,\''+table+'\','+before+','+after+'); END'
        name='budget_v2_delta_'+table+'_update'
        result[name]='CREATE TRIGGER '+name+' AFTER UPDATE ON '+table+' BEGIN '+"INSERT INTO budget_mutations_v2(environment,table_name,before_row,after_row) SELECT NEW.environment,'"+table+"',"+row('OLD')+','+row('NEW')+' WHERE OLD.environment=NEW.environment; '+"INSERT INTO budget_mutations_v2(environment,table_name,before_row,after_row) SELECT OLD.environment,'"+table+"',"+row('OLD')+',NULL WHERE OLD.environment<>NEW.environment; '+"INSERT INTO budget_mutations_v2(environment,table_name,before_row,after_row) SELECT NEW.environment,'"+table+"',NULL,"+row('NEW')+' WHERE OLD.environment<>NEW.environment; END'
    for operation in ('UPDATE','DELETE'):
        name='budget_mutations_v2_no_'+operation.lower()
        result[name]="CREATE TRIGGER "+name+" BEFORE "+operation+" ON budget_mutations_v2 BEGIN SELECT RAISE(ABORT,'Budget mutation journal is append-only'); END"
    return result

def initialize(db):
    register_codec(db)
    # Every SQL mutation, including old retained rows, is captured. No timestamp
    # assumption, history truncation, or mutable-only selection is involved.
    schemas=layout(db)
    db.execute('CREATE TABLE IF NOT EXISTS budget_mutations_v2(seq INTEGER PRIMARY KEY AUTOINCREMENT,environment TEXT NOT NULL,table_name TEXT NOT NULL,before_row TEXT,after_row TEXT)')
    db.execute('CREATE INDEX IF NOT EXISTS budget_mutations_v2_environment_seq ON budget_mutations_v2(environment,seq)')
    for sql in trigger_sql(schemas).values():
        db.execute(sql.replace('CREATE TRIGGER ','CREATE TRIGGER IF NOT EXISTS ',1))
    journal_schema(db)

def journal_schema(db):
    objects={r[0]:r[1] for r in db.execute("SELECT name,sql FROM sqlite_master WHERE type='trigger' AND (name LIKE 'budget_v2_delta_%' OR name LIKE 'budget_mutations_v2_no_%')")}
    expected=trigger_sql(layout(db))
    if set(objects)!=set(expected):raise TapeError('TAPE_BUDGET_JOURNAL_INCOMPLETE')
    if objects!=expected:raise TapeError('TAPE_BUDGET_JOURNAL_CHANGED')
    return objects

def require_journal(db,state):
    version=db.execute('PRAGMA schema_version').fetchone()[0]
    if version!=state.get('schema_version'):
        if layout(db)!=state['schemas'] or journal_schema(db)!=state['journal_schema']:raise TapeError('TAPE_BUDGET_JOURNAL_CHANGED')
        state['schema_version']=version

def key(row,schema):return tuple(row[schema['columns'].index(c)] for c in schema['keys'])

def prepare(tape,database,environment):
    if not enabled(tape):return
    if getattr(tape,'budget_delta',None) is not None:return
    # Called against the hash-pinned bootstrap copy BEFORE running operations,
    # never against mutable live state inside a BEGIN IMMEDIATE transaction.
    database=Path(database)
    expected=tape.bootstrap.get('state',{}).get('artifacts',{}).get('catalog.sqlite')
    if expected is not None and sha(database.read_bytes())!=expected:raise TapeError('TAPE_BUDGET_BASELINE_HASH')
    with closing(sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        schemas=layout(db)
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name='budget_mutations_v2' AND type='table'").fetchone():raise TapeError('TAPE_BUDGET_BASELINE_JOURNAL_MISSING')
        states={table:{key(list(r),schemas[table]):list(r) for r in db.execute('SELECT * FROM '+table+' WHERE environment=?',(environment,))} for table in TABLES}
        cursor=db.execute('SELECT coalesce(max(seq),0) FROM budget_mutations_v2').fetchone()[0]
        machinery=journal_schema(db)
        schema_version=db.execute('PRAGMA schema_version').fetchone()[0]
    canonical={'environment':environment,'schemas':schemas,'tables':{table:sorted(rows.values(),key=bytes_of) for table,rows in states.items()},'cursor':cursor,'journal_schema':machinery}
    tape.budget_delta={'environment':environment,'schemas':schemas,'states':states,'cursor':cursor,'baseline':sha(bytes_of(canonical)),'journal_schema':machinery,'schema_version':schema_version}

def prepare_memory(tape,db,environment):
    """Projected BOOTSTRAP already seals this memory store; raw state stays there."""
    if not enabled(tape):return
    if getattr(tape,'budget_delta',None) is not None:return
    if db.in_transaction:raise TapeError('TAPE_BUDGET_BASELINE_INSIDE_TRANSACTION')
    db.execute('BEGIN')
    try:
        schemas=layout(db)
        states={table:{key(list(r),schemas[table]):list(r) for r in db.execute('SELECT * FROM '+table+' WHERE environment=?',(environment,))} for table in TABLES}
        cursor=db.execute('SELECT coalesce(max(seq),0) FROM budget_mutations_v2').fetchone()[0]
        machinery=journal_schema(db)
        schema_version=db.execute('PRAGMA schema_version').fetchone()[0]
        canonical={'environment':environment,'schemas':schemas,'tables':{table:sorted(rows.values(),key=bytes_of) for table,rows in states.items()},'cursor':cursor,'journal_schema':machinery}
        tape.budget_delta={'environment':environment,'schemas':schemas,'states':states,'cursor':cursor,'baseline':sha(bytes_of(canonical)),'journal_schema':machinery,'schema_version':schema_version}
    finally:db.rollback()

def validate_row(row,schema,environment,owned):
    if row is None:return
    columns=schema['columns']
    if not isinstance(row,list) or len(row)!=len(columns) or row[columns.index('environment')]!=environment:raise TapeError('TAPE_BUDGET_DELTA_ROW')
    if 'session_id' in columns and row[columns.index('session_id')] in owned:raise TapeError('TAPE_BUDGET_INPUT_OWNED_ROW')
    if any(row[columns.index(c)] is None for c in schema['keys']):raise TapeError('TAPE_BUDGET_DELTA_KEY')

def _checkpoint(tape,db,environment,owned):
    state=getattr(tape,'budget_delta',None)
    if state is None:raise TapeError('TAPE_BUDGET_BASELINE_NOT_PREPARED')
    if state['environment']!=environment:raise TapeError('TAPE_BUDGET_INPUT_SCOPE')
    require_journal(db,state)
    if tape.replaying:body=json.loads(tape.take('BUDGET_INPUT'))
    else:
        end=db.execute('SELECT coalesce(max(seq),0) FROM budget_mutations_v2').fetchone()[0]
        changes=[]
        for seq,table,before,after in db.execute('SELECT seq,table_name,before_row,after_row FROM budget_mutations_v2 WHERE environment=? AND seq>? AND seq<=? ORDER BY seq',(environment,state['cursor'],end)):
            before=decode_row(before) if before is not None else None;after=decode_row(after) if after is not None else None
            columns=state['schemas'][table]['columns'];rows=[r for r in (before,after) if r is not None]
            if 'session_id' in columns:
                ownership=[r[columns.index('session_id')] in owned for r in rows]
                if any(ownership) and not all(ownership):raise TapeError('TAPE_BUDGET_DELTA_OWNERSHIP_CHANGE')
                if all(ownership):continue
            changes.append({'seq':seq,'table':table,'before':before,'after':after})
        body={'format':'BUDGET_DELTA_V2','environment':environment,'owned_sessions':sorted(owned),'baseline':state['baseline'],'from':state['cursor'],'to':changes[-1]['seq'] if changes else state['cursor'],'count':len(changes),'changes':changes}
    if (not isinstance(body,dict) or set(body)!={'format','environment','owned_sessions','baseline','from','to','count','changes'} or body['format']!='BUDGET_DELTA_V2' or body['environment']!=environment or body['owned_sessions']!=sorted(owned) or body['baseline']!=state['baseline'] or body['from']!=state['cursor'] or type(body['to']) is not int or body['to']<body['from'] or type(body['count']) is not int or not isinstance(body['changes'],list) or body['count']!=len(body['changes'])):raise TapeError('TAPE_BUDGET_DELTA_SCOPE')
    previous=body['from'];staged={}
    for change in body['changes']:
        if not isinstance(change,dict) or set(change)!={'seq','table','before','after'} or change['table'] not in TABLES or type(change['seq']) is not int or not previous<change['seq']<=body['to']:raise TapeError('TAPE_BUDGET_DELTA_ORDER')
        previous=change['seq'];table=change['table'];schema=state['schemas'][table];before=change['before'];after=change['after']
        if before is None and after is None:raise TapeError('TAPE_BUDGET_DELTA_EMPTY')
        validate_row(before,schema,environment,owned);validate_row(after,schema,environment,owned)
        def current(k):return staged.get((table,k),state['states'][table].get(k))
        if before is not None:
            k=key(before,schema)
            if current(k)!=before:raise TapeError('TAPE_BUDGET_DELTA_BEFORE_DIFFERS')
            staged[table,k]=None
        if after is not None:
            k=key(after,schema)
            if current(k) is not None:raise TapeError('TAPE_BUDGET_DELTA_DUPLICATE_KEY')
            staged[table,k]=after
    if tape.replaying:
        # Only changed external primary keys are touched. Before-images also
        # prove the bootstrap + prior deltas equals the current replay state.
        for (table,k),row in staged.items():
            schema=state['schemas'][table];where=' AND '.join('"'+c+'"=?' for c in schema['keys'])
            actual=db.execute('SELECT * FROM '+table+' WHERE '+where,k).fetchone()
            expected=state['states'][table].get(k)
            if (list(actual) if actual is not None else None)!=expected:raise TapeError('TAPE_BUDGET_DELTA_REPLAY_STATE_DIFFERS')
            db.execute('DELETE FROM '+table+' WHERE '+where,k)
            if row is not None:db.execute('INSERT INTO '+table+' VALUES('+','.join('?' for _ in schema['columns'])+')',row)
    for (table,k),row in staged.items():
        if row is None:state['states'][table].pop(k,None)
        else:state['states'][table][k]=row
    state['cursor']=body['to']
    if not tape.replaying:tape.event('BUDGET_INPUT',bytes_of(body))


# Consumer-owned bounded codes, never exception prose or database values.
FAILURE_CODES=frozenset(['TAPE_BUDGET_BASELINE_HASH', 'TAPE_BUDGET_BASELINE_INSIDE_TRANSACTION', 'TAPE_BUDGET_BASELINE_JOURNAL_MISSING', 'TAPE_BUDGET_BASELINE_NOT_PREPARED', 'TAPE_BUDGET_DELTA_BEFORE_DIFFERS', 'TAPE_BUDGET_DELTA_DUPLICATE_KEY', 'TAPE_BUDGET_DELTA_EMPTY', 'TAPE_BUDGET_DELTA_KEY', 'TAPE_BUDGET_DELTA_ORDER', 'TAPE_BUDGET_DELTA_OWNERSHIP_CHANGE', 'TAPE_BUDGET_DELTA_REPLAY_STATE_DIFFERS', 'TAPE_BUDGET_DELTA_ROW', 'TAPE_BUDGET_DELTA_SCHEMA', 'TAPE_BUDGET_DELTA_SCOPE', 'TAPE_BUDGET_INPUT_OWNED_ROW', 'TAPE_BUDGET_INPUT_SCOPE', 'TAPE_BUDGET_JOURNAL_CHANGED', 'TAPE_BUDGET_JOURNAL_INCOMPLETE', 'TAPE_BUDGET_REAL_CANONICAL', 'TAPE_BUDGET_REAL_ENCODING', 'TAPE_BUDGET_REAL_ROW', 'TAPE_BUDGET_REAL_TAG'])

def validate_failure(body):
    if (not isinstance(body,dict) or set(body)!={'code','environment','owned_sessions'}
            or body['code'] not in FAILURE_CODES or not isinstance(body['environment'],str)
            or not isinstance(body['owned_sessions'],list)
            or any(not isinstance(x,str) for x in body['owned_sessions'])
            or body['owned_sessions']!=sorted(set(body['owned_sessions']))):
        raise TapeError('TAPE_BUDGET_FAILURE_SCHEMA')
    return body

def checkpoint(tape,db,environment,owned):
    if tape.replaying and tape.peek('BUDGET_INPUT_FAILURE') is not None:
        body=validate_failure(json.loads(tape.take('BUDGET_INPUT_FAILURE')))
        if body['environment']!=environment or body['owned_sessions']!=sorted(owned):
            raise TapeError('TAPE_BUDGET_INPUT_SCOPE')
        raise TapeError(body['code'])
    try: return _checkpoint(tape,db,environment,owned)
    except TapeError as exc:
        if not tape.replaying and str(exc) in FAILURE_CODES:
            tape.event('BUDGET_INPUT_FAILURE',bytes_of({'code':str(exc),'environment':environment,'owned_sessions':sorted(owned)}))
        raise

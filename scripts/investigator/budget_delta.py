"""v7 shared-budget deltas; baseline is sealed before admission transactions."""
import json,sqlite3
from contextlib import closing
from pathlib import Path
from .process_tape import TapeError,bytes_of,sha
TABLES=('adaptive_usage','read_batches','read_batch_runs','read_allocations')
VERSION='bounded-worker-tape-v7'

def enabled(tape):
    return getattr(tape,'version',None) in (VERSION,'privacy-projected-tape-v1') and getattr(tape,'bootstrap',{}).get('state',{}).get('budget_checkpoint')=='DELTA_V1'

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
        def row(prefix):return 'json_array('+','.join(prefix+'."'+c+'"' for c in schema['columns'])+')'
        for operation,before,after in [('INSERT','NULL',row('NEW')),('DELETE',row('OLD'),'NULL')]:
            name='budget_delta_'+table+'_'+operation.lower()
            result[name]='CREATE TRIGGER '+name+' AFTER '+operation+' ON '+table+' BEGIN INSERT INTO budget_mutations(environment,table_name,before_row,after_row) VALUES ('+('OLD' if operation=='DELETE' else 'NEW')+'.environment,\''+table+'\','+before+','+after+'); END'
        name='budget_delta_'+table+'_update'
        result[name]='CREATE TRIGGER '+name+' AFTER UPDATE ON '+table+' BEGIN '+"INSERT INTO budget_mutations(environment,table_name,before_row,after_row) SELECT NEW.environment,'"+table+"',"+row('OLD')+','+row('NEW')+' WHERE OLD.environment=NEW.environment; '+"INSERT INTO budget_mutations(environment,table_name,before_row,after_row) SELECT OLD.environment,'"+table+"',"+row('OLD')+',NULL WHERE OLD.environment<>NEW.environment; '+"INSERT INTO budget_mutations(environment,table_name,before_row,after_row) SELECT NEW.environment,'"+table+"',NULL,"+row('NEW')+' WHERE OLD.environment<>NEW.environment; END'
    for operation in ('UPDATE','DELETE'):
        name='budget_mutations_no_'+operation.lower()
        result[name]="CREATE TRIGGER "+name+" BEFORE "+operation+" ON budget_mutations BEGIN SELECT RAISE(ABORT,'Budget mutation journal is append-only'); END"
    return result

def initialize(db):
    # Every SQL mutation, including old retained rows, is captured. No timestamp
    # assumption, history truncation, or mutable-only selection is involved.
    schemas=layout(db)
    db.execute('CREATE TABLE IF NOT EXISTS budget_mutations(seq INTEGER PRIMARY KEY AUTOINCREMENT,environment TEXT NOT NULL,table_name TEXT NOT NULL,before_row TEXT,after_row TEXT)')
    db.execute('CREATE INDEX IF NOT EXISTS budget_mutations_environment_seq ON budget_mutations(environment,seq)')
    for sql in trigger_sql(schemas).values():
        db.execute(sql.replace('CREATE TRIGGER ','CREATE TRIGGER IF NOT EXISTS ',1))
    journal_schema(db)

def journal_schema(db):
    objects={r[0]:r[1] for r in db.execute("SELECT name,sql FROM sqlite_master WHERE type='trigger' AND (name LIKE 'budget_delta_%' OR name LIKE 'budget_mutations_no_%')")}
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
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name='budget_mutations' AND type='table'").fetchone():raise TapeError('TAPE_BUDGET_BASELINE_JOURNAL_MISSING')
        states={table:{key(list(r),schemas[table]):list(r) for r in db.execute('SELECT * FROM '+table+' WHERE environment=?',(environment,))} for table in TABLES}
        cursor=db.execute('SELECT coalesce(max(seq),0) FROM budget_mutations').fetchone()[0]
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
        cursor=db.execute('SELECT coalesce(max(seq),0) FROM budget_mutations').fetchone()[0]
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

def checkpoint(tape,db,environment,owned):
    state=getattr(tape,'budget_delta',None)
    if state is None:raise TapeError('TAPE_BUDGET_BASELINE_NOT_PREPARED')
    if state['environment']!=environment:raise TapeError('TAPE_BUDGET_INPUT_SCOPE')
    require_journal(db,state)
    if tape.replaying:body=json.loads(tape.take('BUDGET_INPUT'))
    else:
        end=db.execute('SELECT coalesce(max(seq),0) FROM budget_mutations').fetchone()[0]
        changes=[]
        for seq,table,before,after in db.execute('SELECT seq,table_name,before_row,after_row FROM budget_mutations WHERE environment=? AND seq>? AND seq<=? ORDER BY seq',(environment,state['cursor'],end)):
            before=json.loads(before) if before is not None else None;after=json.loads(after) if after is not None else None
            columns=state['schemas'][table]['columns'];rows=[r for r in (before,after) if r is not None]
            if 'session_id' in columns:
                ownership=[r[columns.index('session_id')] in owned for r in rows]
                if any(ownership) and not all(ownership):raise TapeError('TAPE_BUDGET_DELTA_OWNERSHIP_CHANGE')
                if all(ownership):continue
            changes.append({'seq':seq,'table':table,'before':before,'after':after})
        body={'format':'BUDGET_DELTA_V1','environment':environment,'owned_sessions':sorted(owned),'baseline':state['baseline'],'from':state['cursor'],'to':changes[-1]['seq'] if changes else state['cursor'],'count':len(changes),'changes':changes}
    if (not isinstance(body,dict) or set(body)!={'format','environment','owned_sessions','baseline','from','to','count','changes'} or body['format']!='BUDGET_DELTA_V1' or body['environment']!=environment or body['owned_sessions']!=sorted(owned) or body['baseline']!=state['baseline'] or body['from']!=state['cursor'] or type(body['to']) is not int or body['to']<body['from'] or type(body['count']) is not int or not isinstance(body['changes'],list) or body['count']!=len(body['changes'])):raise TapeError('TAPE_BUDGET_DELTA_SCOPE')
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

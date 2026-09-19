"""Receipt-backed, parser-governed SQL/DAX tools for proposed diagnostic queries."""
from datetime import datetime,timezone
from decimal import Decimal
import json
import subprocess
from uuid import uuid4
from .onboarding import fields,digest,encoded,Conflict
from .model_context import assets
from . import query_sql,query_dax
from .native_identity import allows,require,canonical
from .native_diagnostics import typed

TABLE='flexible_diagnostics'


def capabilities(store,model,config):
    """Local eligibility only; advertising a tool never grants execution rights."""
    sql=query_sql.capabilities();dax=query_dax.capabilities()
    reader=config['fabric'].get('native_reader')
    dax['eligibility']='ELIGIBLE_FOR_VALIDATION' if model['enabled'] and reader and allows(reader,model['workspace'],model['native_id']) else 'UNAVAILABLE'
    try:
        from .source_diagnostics import snapshot
        objects,_=snapshot(store,model,config)
        sql['eligibility']='ELIGIBLE_FOR_VALIDATION' if objects else 'UNAVAILABLE'
    except (ValueError,Conflict):sql['eligibility']='UNAVAILABLE'
    for item in (sql,dax):
        item['execution_permission']='UNKNOWN_UNTIL_DISPATCH'
        item['dispatch_revalidation_required']=True
    return [sql,dax]


def build(store,plan,config,tool):
    fields(plan,['model_id','revision','context_id','query','max_rows'])
    model=store.get(plan['model_id'])
    if not model['enabled'] or plan['revision']!=model['revision'] or plan['context_id']!=model['context_id']:
        raise Conflict('Proposed query context changed or disabled')
    if model['workspace']!=config['fabric']['workspace_id']:raise Conflict('Connection workspace differs')
    if tool=='bounded_dax':
        reader=config['fabric'].get('native_reader')
        if reader is None or not allows(reader,model['workspace'],model['native_id']):raise Conflict('Proposed DAX requires approved isolated reader')
        compiled=query_dax.compile_query(plan['query'],assets(model['context']),max_rows=plan['max_rows'])
        compiled.update(workspace=model['workspace'],native_model_id=model['native_id'],requires_native_reader=True)
    elif tool=='bounded_sql':
        from .source_diagnostics import snapshot
        objects,_=snapshot(store,model,config)
        from sqlglot.errors import SqlglotError, OptimizeError
        try:compiled=query_sql.compile_query(plan['query'],list(objects.values()),max_rows=plan['max_rows'])
        except OptimizeError as exc:
            raise ValueError('SQL column binding failed. Use only columns present in the retrieved source schemas and qualify ambiguous columns with table aliases. A semantic or derived field is not automatically a source column; retrieve transformation context before using it.') from exc
        except SqlglotError as exc:raise ValueError('SQL syntax or catalog binding unsupported') from exc
        from .source_diagnostics import quote
        compiled['read_only_objects']=[quote(objects[k]['metadata']['schema_name'])+'.'+quote(objects[k]['metadata']['name']) for k in compiled['asset_ids']]
        compiled['require_read_only']=True
    else:raise ValueError('Unsupported proposed query tool')
    return dict(compiled,tool=tool,context_id=model['context_id'],context_hash=digest(model['context']),
                policy_hash=digest(config),scope_hash=digest(plan))


def extract(response,request):
    if not isinstance(response,dict) or response.get('error'):raise ValueError('Query response unavailable')
    if request['tool']=='bounded_dax':
        results=response.get('results',[])
        if len(results)!=1 or results[0].get('error'):raise ValueError('Query response incomplete')
        tables=results[0].get('tables',[])
        if len(tables)!=1 or tables[0].get('error'):raise ValueError('Query result shape differs')
        rows=tables[0].get('rows');identity=response.get('_native_execution')
    else:rows=response.get('rows');identity=response.get('execution_identity')
    if not isinstance(rows,list) or len(encoded(canonical(rows)))>2*1024*1024:raise ValueError('Query result byte budget exceeded')
    values=[];columns=set()
    for row in rows[:request['max_rows']]:
        if not isinstance(row,dict) or len(row)>16 or any(not isinstance(k,str) or len(k)>300 for k in row):raise ValueError('Query column budget exceeded')
        columns.update(row)
        normalized={}
        for k,v in row.items():
            if request['tool']=='bounded_sql' and v is not None:
                kind=response.get('column_types',{}).get(k)
                if kind in ('Byte','Int16','Int32','Int64','Decimal'):v=Decimal(v)
                elif kind=='Boolean':
                    if v not in ('True','False'):raise ValueError('Source boolean type differs')
                    v=v=='True'
            normalized[k]=typed(v)
        values.append(normalized)
    if len(columns)>16:raise ValueError('Query shape differs')
    # Source transport serializes exact decimals as text; no guessed numeric type.
    return {'rows':values[:request['max_rows']-1],'returned_rows':len(rows),
            'completeness':'PARTIAL' if len(rows)>=request['max_rows'] else 'COMPLETE_RESPONSE',
            'execution_identity':identity,'columns':sorted(columns),
            'caller_limit':request.get('caller_limit'),'interpretation':'OBSERVED',
            'limitation':request['limitation'],'cause_verified':False}


def run(store,plan,config,tool,execute,*,receipt_id=None):
    request=build(store,plan,config,tool);identity=receipt_id or str(uuid4())
    with store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS '+TABLE+'(id TEXT PRIMARY KEY,model_id TEXT,created TEXT,status TEXT,request TEXT,result TEXT)')
        db.execute('INSERT INTO '+TABLE+' VALUES(?,?,?,?,?,NULL)',(identity,plan['model_id'],datetime.now(timezone.utc).isoformat(),'RUNNING',encoded({'plan':plan,**request})))
    try:
        if build(store,plan,config,tool)!=request:raise Conflict('Context changed before query')
        response=execute(request)
        if tool=='bounded_dax':require(response,request,config['fabric']['native_reader'])
        elif not response.get('read_only_verified'):raise ValueError('Source read-only permission check missing')
        result=extract(response,request)
        if tool=='bounded_sql':
            from .source_diagnostics import connection_attempts
            attempts=connection_attempts(response.get('connection_attempts'))
            if attempts is not None:result['connection_attempts']=attempts
        if build(store,plan,config,tool)!=request:raise Conflict('Context changed during query')
        status='COMPLETED'
    except Exception as exc:
        status='HELD' if isinstance(exc,Conflict) else 'INTERRUPTED' if isinstance(exc,(TimeoutError,subprocess.TimeoutExpired)) else 'FAILED'
        result={'error_type':type(exc).__name__,'cause_verified':False}
        if tool=='bounded_sql':
            from .source_diagnostics import connection_attempts
            if type(getattr(exc,'error_number',None)) is int:result['error_number']=exc.error_number
            if getattr(exc,'error_kind',None) in ('SqlException','InvalidOperationException','MethodException','ArgumentException','TransportError'):
                result['error_kind']=exc.error_kind
            try:
                attempts=connection_attempts(getattr(exc,'connection_attempts',None))
                if attempts is not None:result['connection_attempts']=attempts
            except (ValueError,TypeError):pass
    with store.connect() as db:
        db.execute('UPDATE '+TABLE+' SET status=?,result=? WHERE id=?',(status,encoded(result),identity))
        from .receipt_integrity import seal
        seal(db,tool,identity)
    return {'id':identity,'status':status,'request_hash':digest(request),'result':result}

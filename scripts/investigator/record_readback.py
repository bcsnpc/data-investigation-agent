"""Bounded projected record groups, with multiplicity and no snapshot claims."""
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import json
import re
import subprocess
from uuid import UUID, uuid4

from .onboarding import fields, digest, encoded, Conflict
from . import native_diagnostics as native, source_diagnostics as source
from .filter_scope import compile_filter, SUPPORTED
from .source_scope import kind

TABLE = 'record_readbacks'


def build(store, plan, config, backend):
    fields(plan,['model_id','revision','context_id','object_id','column_ids','key_column_ids','filters','limit']+(['record_mapping_id'] if 'record_mapping_id' in plan else []))
    model=store.get(plan['model_id'])
    if not model['enabled'] or model['revision']!=plan['revision'] or type(plan['revision']) is not int or model['context_id']!=plan['context_id']:
        raise Conflict('Record plan requires current enabled context')
    if backend not in ('native_records','source_records'):raise ValueError('Unknown record backend')
    if type(plan['limit']) is not int or not 1<=plan['limit']<=250:raise ValueError('Record limit must be 1-250')
    columns=plan['column_ids'];keys=plan['key_column_ids']
    for ids,maximum in [(columns,8),(keys,3)]:
        if not isinstance(ids,list) or not 1<=len(ids)<=maximum or any(not isinstance(x,str) for x in ids) or len(ids)!=len(set(ids)):
            raise ValueError('Invalid projected columns or keys')
    if not set(keys)<=set(columns):raise ValueError('Keys must be projected')
    filters=plan['filters']
    if not isinstance(filters,list) or not 1<=len(filters)<=8:raise ValueError('Explicit bounded record filters required')
    limit=plan['limit']+1
    if backend=='source_records':
        base={k:plan[k] for k in ('model_id','revision','context_id','object_id','filters')}
        base.update(operation='count_rows',column_id=None)
        compiled=source.build(store,base,config);objects,assets=source.snapshot(store,model,config)
        if any(c not in assets or assets[c]['parent_id']!=plan['object_id'] for c in columns):raise ValueError('Cross-object projection')
        if any(assets[c]['metadata'].get('computed_definition') for c in columns):raise ValueError('Computed source projection unsupported')
        types=[kind(assets[c]['metadata']) for c in columns]
        refs=[source.quote(assets[c]['metadata']['name']) for c in columns]
        projections=[]
        for index,(ref,value_kind) in enumerate(zip(refs,types)):
            value=ref if value_kind=='string' else 'CONVERT(varchar(100),'+ref+(',126)' if value_kind=='dateTime' else ')')
            projections.append(value+' AS c'+str(index))
        query=('SELECT TOP ('+str(limit)+') '+','.join(projections)+',CONVERT(varchar(30),COUNT_BIG(*)) AS multiplicity FROM '+
               compiled['object_sql']+' WHERE '+compiled['predicate_sql']+' GROUP BY '+','.join(refs)+' ORDER BY '+','.join(refs)+' OPTION (MAXDOP 1)')
        request={'query':query,'parameters':compiled['parameters'],'connection_hash':compiled['connection_hash'],
                 'catalog_hash':compiled['catalog_hash'],'response_mode':'records','max_rows':limit,
                 'result_columns':['c'+str(i) for i in range(len(columns))]+['multiplicity']}
    else:
        if model['workspace']!=config['fabric']['workspace_id']:raise Conflict('Native workspace differs')
        assets={a['id']:a for a in model['context']['reports'][0]['model_assets']}
        obj=assets.get(plan['object_id'])
        if not obj or obj['kind']!='SemanticTable':raise ValueError('Unknown native table')
        if any(c not in assets or assets[c]['kind']!='SemanticColumn' or assets[c]['parent_id']!=obj['id'] for c in columns):
            raise ValueError('Cross-table native projection')
        types=[assets[c]['metadata'].get('dataType') for c in columns]
        if any(t not in SUPPORTED for t in types):raise ValueError('Unsupported native record type')
        def reference(identity):
            asset=assets.get(identity)
            if not asset or asset['kind']!='SemanticColumn':raise ValueError('Unknown filter column')
            parent=assets.get(asset['parent_id'])
            if not parent or parent['kind']!='SemanticTable':raise ValueError('Unknown filter table')
            return native.table(parent['name'])+native.bracket(asset['name'])
        refs=[reference(c) for c in columns];clauses=[];used=set()
        for f in filters:
            fields(f,['column_id','values']+(['operator'] if 'operator' in f else []))
            identity=f['column_id']
            if not isinstance(identity,str) or identity in used:raise ValueError('Duplicate filter column')
            ref=reference(identity);used.add(identity)
            if 'operator' not in f and assets[identity]['metadata'].get('dataType')!='string':raise ValueError('Typed operator required')
            clauses.append(compile_filter(dict(f,operator=f.get('operator','in')),assets[identity]['metadata'],ref))
        # Every projected column participates in grouping and ordering. This
        # prevents TOPN boundary ties from expanding the response indefinitely.
        grouped='SUMMARIZECOLUMNS('+','.join(refs+clauses+['"__count"','COUNTROWS('+native.table(obj['name'])+')'])+')'
        top='TOPN('+str(limit)+','+grouped+','+','.join(ref+',ASC' for ref in refs)+')'
        pairs=[]
        for index,ref in enumerate(refs):pairs.extend(['"c'+str(index)+'"',ref])
        query='EVALUATE SELECTCOLUMNS('+top+','+','.join(pairs+['"multiplicity"','[__count]'])+')'
        request={'query':query,'workspace':model['workspace'],'native_model_id':model['native_id']}
    if 'record_mapping_id' in plan:
        from .record_bindings import validate_plan
        request['reviewed_mapping']=validate_plan(store,plan,config,backend)
    return {**request,'version':'record-readback-v1','backend':backend,'model_id':model['id'],
            'context_id':model['context_id'],'context_hash':digest(model['context']),'scope_hash':digest(plan),
            'column_ids':columns,'key_column_ids':keys,'types':types,'limit':plan['limit']}


def value(raw, value_kind, backend):
    if raw is None:return {'type':'blank','value':None}
    if value_kind=='string':
        if not isinstance(raw,str) or len(raw)>1000:raise ValueError('Invalid bounded string')
        return {'type':'string','value':raw}
    if value_kind=='boolean':
        if backend=='source_records':
            if raw not in ('0','1'):raise ValueError('Invalid SQL bit')
            raw=raw=='1'
        if type(raw) is not bool:raise ValueError('Invalid boolean')
        return {'type':'boolean','value':raw}
    if value_kind=='dateTime':
        if not isinstance(raw,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d{1,7})?)?',raw):
            raise ValueError('Unsupported datetime response')
        base,fraction=(raw.split('.')+[''])[:2]
        parsed=datetime.fromisoformat(base)
        canonical=parsed.isoformat(timespec='seconds')
        if fraction.rstrip('0'):canonical+='.'+fraction.rstrip('0')
        return {'type':'dateTime','value':canonical}
    if type(raw) is bool or isinstance(raw,float) or not isinstance(raw,(str,int,Decimal)):
        raise ValueError('Exact numeric response required')
    if isinstance(raw,Decimal):
        if not raw.is_finite() or (raw!=0 and (raw.adjusted()>37 or raw.as_tuple().exponent < -18)):
            raise ValueError('Decimal exceeds record precision')
        text='0' if raw==0 else format(raw,'f')
    else:text=str(raw)
    if not re.fullmatch(r'-?\d{1,38}(?:\.\d{1,18})?',text):raise ValueError('Invalid numeric response')
    if len(text.replace('-','').replace('.','').lstrip('0'))>38:raise ValueError('Numeric precision exceeds record budget')
    number=Decimal(text)
    if value_kind=='int64' and (number!=int(number) or not -2**63<=number<2**63):raise ValueError('Invalid integer')
    with localcontext() as ctx:
        ctx.prec=80
        canonical='0' if number==0 else format(number.normalize(),'f')
    return {'type':value_kind,'value':canonical}


def extract(response, request):
    backend=request['backend']
    if backend=='native_records':
        if not isinstance(response,dict) or response.get('error') or len(response.get('results',[]))!=1:raise ValueError('Native record response unavailable')
        result=response['results'][0];tables=result.get('tables',[])
        if result.get('error') or len(tables)!=1 or tables[0].get('error'):raise ValueError('Native record response incomplete')
        rows=tables[0].get('rows');names=['[c'+str(i)+']' for i in range(len(request['types']))];count_name='[multiplicity]'
    else:
        fields(response,['rows']);rows=response['rows'];names=['c'+str(i) for i in range(len(request['types']))];count_name='multiplicity'
    if not isinstance(rows,list) or len(rows)>request['limit']+1:raise ValueError('Record response exceeds budget')
    output=[];seen=set()
    for row in rows:
        fields(row,names+[count_name])
        values=[value(row[name],t,backend) for name,t in zip(names,request['types'])]
        multiplicity=value(row[count_name],'int64',backend)['value']
        if int(multiplicity)<=0:raise ValueError('Nonpositive group multiplicity')
        identity=encoded(values)
        if identity in seen:raise ValueError('Repeated projected group')
        seen.add(identity);output.append({'values':values,'multiplicity':multiplicity})
    partial=len(output)>request['limit'];output=output[:request['limit']]
    return {'rows':output,'column_ids':request['column_ids'],'key_column_ids':request['key_column_ids'],'types':request['types'],
            'completeness':'PARTIAL' if partial else 'COMPLETE_RESPONSE','returned_groups':len(rows),
            'retained_groups':len(output),'observed_row_count':str(sum(int(r['multiplicity']) for r in output)),
            'record_hash':digest(output),'snapshot_comparable':False,'root_cause_verified':False,
            'limitation':'Complete response covers grouped projected values under the executed scope; it is not proof of model contents, effective identity or a shared data generation.'}


def run(store,plan,config,backend,execute,*,receipt_id=None):
    request=build(store,plan,config,backend);identity=receipt_id or str(uuid4())
    if str(UUID(identity))!=identity:raise ValueError('Invalid receipt ID')
    created=datetime.now(timezone.utc).isoformat();stored_request={'plan':plan,**request}
    with store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS record_readbacks(id TEXT PRIMARY KEY,model_id TEXT,created TEXT,status TEXT,request TEXT,result TEXT,evidence_hash TEXT)')
        db.execute('INSERT INTO record_readbacks VALUES(?,?,?,?,?,NULL,NULL)',(identity,plan['model_id'],created,'RUNNING',encoded(stored_request)))
    attempts=None
    try:
        if build(store,plan,config,backend)!=request:raise Conflict('Readback context changed')
        response=execute(request)
        if backend=='source_records':
            response=dict(response);attempts=source.connection_attempts(response.pop('connection_attempts',None))
        result=extract(response,request)
        if build(store,plan,config,backend)!=request:raise Conflict('Readback context changed during read')
        status='COMPLETED'
    except Exception as exc:
        uncertain=isinstance(exc,(TimeoutError,subprocess.TimeoutExpired)) or getattr(exc,'error_number',None)==-2
        status='HELD' if isinstance(exc,Conflict) else 'INTERRUPTED' if uncertain else 'FAILED'
        result={'error_type':type(exc).__name__,'root_cause_verified':False}
        try:attempts=source.connection_attempts(getattr(exc,'connection_attempts',None))
        except (ValueError,TypeError):attempts=None
    if attempts is not None:result['connection_attempts']=attempts
    evidence_hash=digest({'created':created,'status':status,'request':stored_request,'result':result})
    with store.connect() as db:db.execute('UPDATE record_readbacks SET status=?,result=?,evidence_hash=? WHERE id=?',(status,encoded(result),evidence_hash,identity))
    return {'id':identity,'status':status,'request_hash':digest(request),'result':result}


def read(store,model_id,identity):
    model=store.get(model_id)
    with store.connect() as db:
        exists=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='record_readbacks'").fetchone()
        row=db.execute('SELECT created,status,request,result,evidence_hash FROM record_readbacks WHERE model_id=? AND id=?',(model_id,identity)).fetchone() if exists else None
    if row is None:raise KeyError('Readback receipt not found')
    request=json.loads(row[2])
    result=json.loads(row[3]) if row[3] else None
    if row[1]!='RUNNING' and digest({'created':row[0],'status':row[1],'request':request,'result':result})!=row[4]:
        raise ValueError('Readback evidence integrity differs')
    return {'id':identity,'created':row[0],'status':row[1],'request':request,'result':result,
            'local_context_current':bool(model['enabled'] and model['revision']==request['plan']['revision'] and digest(model['context'])==request['context_hash'])}

"""Catalog-scoped native DAX diagnostics. No semantic emulation or cause claims."""
from datetime import datetime, timezone
from decimal import Decimal
import subprocess
from uuid import uuid4
from .onboarding import fields, digest, encoded, Conflict
from .filter_scope import compile_filter, VERSION as FILTER_VERSION


def table(name):
    return "'"+name.replace("'","''")+"'"


def bracket(name):
    return '['+name.replace(']',']]')+']'


def literal(value):
    if not isinstance(value,str) or len(value)>200 or any(ord(c)<32 for c in value):
        raise ValueError('Only bounded string filter values are supported')
    return '"'+value.replace('"','""')+'"'


def build(model, plan):
    fields(plan,['model_id','revision','context_id','measure_ids','filters','dimension_id','include_dependencies'])
    if plan['model_id']!=model['id'] or plan['context_id']!=model['context_id'] or type(plan['revision']) is not int or plan['revision']!=model['revision']:
        raise Conflict('Plan refers to stale model context')
    if not model['enabled']:raise Conflict('Enable reviewed catalog before diagnostics')
    if type(plan['include_dependencies']) is not bool:raise ValueError('Expected dependency flag')
    context=model['context'];assets=context['reports'][0]['model_assets']
    tables={a['id']:a['name'] for a in assets if a['kind']=='SemanticTable'}
    measures={a['id']:a for a in assets if a['kind']=='Measure'}
    columns={a['id']:a for a in assets if a['kind']=='SemanticColumn'}
    selected=plan['measure_ids']
    if not isinstance(selected,list) or not 1<=len(selected)<=12 or any(not isinstance(x,str) or x not in measures for x in selected) or len(set(selected))!=len(selected):
        raise ValueError('Select 1-12 unique catalog measures')
    selected=list(selected);gaps=[]
    graph=context.get('semantic_graph',{}).get('measures',{})
    if plan['include_dependencies']:
        pending=list(selected)
        while pending:
            current=pending.pop();node=graph.get(current)
            if not node or node['dependency_state']!='SUPPORTED':
                gaps.append({'measure':current,'reason':'Dependency analysis incomplete'});continue
            if set(node['operations']) & {'FILTERED_MEASURE','TIME_SHIFT','RELATIONSHIP_SWITCH','CONDITIONAL'}:
                gaps.append({'measure':current,'reason':'Child effective context is not certified'});continue
            for child in node['dependencies']:
                if child not in selected:
                    if child not in measures or len(selected)>=12:raise ValueError('Dependency budget exceeded')
                    selected.append(child);pending.append(child)
    def column(identity):
        if identity not in columns:raise ValueError('Unknown dimension/filter')
        a=columns[identity]
        if a['parent_id'] not in tables:raise ValueError('Unknown table binding')
        return table(tables[a['parent_id']])+bracket(a['name'])
    filters=plan['filters']
    if not isinstance(filters,list) or not 1<=len(filters)<=8:raise ValueError('Explicit bounded filters required')
    clauses=[];used=set()
    for f in filters:
        if not isinstance(f,dict):raise ValueError('Expected filter object')
        fields(f,['column_id','operator','values'] if 'operator' in f else ['column_id','values'])
        identity=f['column_id']
        if not isinstance(identity,str) or identity in used:raise ValueError('Duplicate or invalid filter')
        ref=column(identity);used.add(identity)
        if 'operator' in f:
            clauses.append(compile_filter(f,columns[identity]['metadata'],ref))
            continue
        if columns[identity]['metadata'].get('dataType')!='string':raise ValueError('Only string-column filters supported')
        values=f['values']
        if not isinstance(values,list) or not 1<=len(values)<=50:raise ValueError('Filter values outside budget')
        clauses.append('TREATAS({'+','.join(literal(x) for x in values)+'},'+ref+')')
    expressions=[]
    for i,identity in enumerate(selected):
        a=measures[identity]
        expressions.extend(['"m'+str(i)+'"',table(tables[a['parent_id']])+bracket(a['name'])])
    dimension=plan['dimension_id']
    if dimension is None:
        query='EVALUATE CALCULATETABLE(ROW('+','.join(expressions)+'),'+','.join(clauses)+')'
    else:
        if not isinstance(dimension,str):raise ValueError('Invalid dimension')
        ref=column(dimension)
        grouped='SUMMARIZECOLUMNS('+','.join([ref]+clauses+expressions)+')'
        projections=['"dimension"',ref]
        for i in range(len(selected)):projections.extend(['"m'+str(i)+'"','[m'+str(i)+']'])
        query='EVALUATE SELECTCOLUMNS(TOPN(501,'+grouped+','+ref+',ASC),'+','.join(projections)+')'
    request={'query':query,'measure_ids':selected,'dimension_id':dimension,'gaps':gaps,
            'scope_hash':digest(plan),'context_id':context['id'],'context_hash':digest(context),
            'workspace':model['workspace'],'native_model_id':model['native_id']}
    if any('operator' in f for f in filters):request['filter_scope_version']=FILTER_VERSION
    return request


def typed(value):
    if value is None:return {'type':'blank','value':None}
    if isinstance(value,bool):return {'type':'boolean','value':value}
    if isinstance(value,(int,Decimal)):
        if isinstance(value,Decimal) and not value.is_finite():raise ValueError('Non-finite native value')
        return {'type':'decimal','value':str(value)}
    if isinstance(value,str):return {'type':'string','value':value}
    raise ValueError('Unexpected native value type')


def extract(response, request):
    if not isinstance(response,dict) or response.get('error') or len(response.get('results',[]))!=1:
        raise ValueError('Native response unavailable')
    result=response['results'][0];tables=result.get('tables',[])
    if result.get('error') or len(tables)!=1 or tables[0].get('error'):raise ValueError('Native response incomplete')
    rows=tables[0].get('rows')
    if not isinstance(rows,list) or len(rows)>501 or (request['dimension_id'] is None and len(rows)!=1):
        raise ValueError('Native row budget/shape differs')
    expected={'[m'+str(i)+']' for i in range(len(request['measure_ids']))}
    if request['dimension_id'] is not None:expected.add('[dimension]')
    output=[]
    for row in rows:
        if not isinstance(row,dict) or set(row)!=expected:raise ValueError('Native columns differ')
        output.append({key:typed(value) for key,value in row.items()})
    return {'rows':output[:500],'completeness':'PARTIAL' if len(rows)>500 else 'COMPLETE_RESPONSE',
            'returned_rows':len(rows),'limitation':'Response completeness is not snapshot or cross-system comparability. Grouped results can omit all-blank groups.'}


def run(store,plan,execute):
    """One approved operator invocation, one call; save receipt before/after.

    No automatic resume/retry. Execute is an operator-owned bounded transport.
    """
    model=store.get(plan['model_id']);request=build(model,plan);identity=str(uuid4())
    from .capabilities import assess
    decision=assess(model,plan)
    with store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS native_diagnostics(id TEXT PRIMARY KEY,model_id TEXT,created TEXT,status TEXT,request TEXT,result TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS native_capability_decisions(receipt_id TEXT PRIMARY KEY,decision_hash TEXT,body TEXT)')
        db.execute('INSERT INTO native_diagnostics VALUES(?,?,?,?,?,NULL)',
                   (identity,model['id'],datetime.now(timezone.utc).isoformat(),'RUNNING',encoded({'plan':plan,**request})))
        db.execute('INSERT INTO native_capability_decisions VALUES(?,?,?)',
                   (identity,decision['decision_hash'],encoded(decision)))
    try:
        # Revalidate immediately before dispatch, and hold results if local
        # context/enablement changed during the native read.
        if build(store.get(model['id']),plan)!=request:raise Conflict('Context changed')
        result=extract(execute(request),request)
        if build(store.get(model['id']),plan)!=request:raise Conflict('Context changed during read')
        result.update(snapshot_comparable=False,root_cause_verified=False,gaps=request['gaps'],
                      remote_definition_version_verified=False,visual_context_reproduced=False,
                      effective_identity_verified=False,captured_at=datetime.now(timezone.utc).isoformat())
        status='COMPLETED'
    except Exception as exc:
        status=('HELD' if isinstance(exc,Conflict) else
                'INTERRUPTED' if isinstance(exc,(TimeoutError,subprocess.TimeoutExpired)) else 'FAILED')
        result={'error_type':type(exc).__name__,'snapshot_comparable':False,'root_cause_verified':False}
    with store.connect() as db:
        db.execute('UPDATE native_diagnostics SET status=?,result=? WHERE id=?',(status,encoded(result),identity))
    return {'id':identity,'status':status,'request_hash':digest(request),'result':result}

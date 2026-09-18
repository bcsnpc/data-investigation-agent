"""Reusable catalog-reviewed record projections. Review is intent, not proof."""
from .model_context import assets as model_assets
from datetime import datetime, timezone
import json
from uuid import uuid4

from .onboarding import fields, text, digest, encoded, Conflict
from .record_comparison import bindings
from .source_diagnostics import snapshot
from .source_scope import kind
from .filter_scope import SUPPORTED


def initialize(db):
    db.executescript('''
    CREATE TABLE IF NOT EXISTS record_mappings(
      id TEXT PRIMARY KEY,model_id TEXT,body TEXT,hash TEXT,actor TEXT,created TEXT);
    CREATE TABLE IF NOT EXISTS record_mapping_revocations(
      id TEXT PRIMARY KEY,reason TEXT,actor TEXT,created TEXT);
    ''')


def validate(store, model_id, body, config, *, require_confirmation=True):
    fields(body,['revision','context_id','measure_id','native_object_id','source_object_id',
                 'column_bindings','key_column_ids','filter_bindings','limit','grain','date_basis','confirmed'])
    model=store.get(model_id)
    if not model['enabled'] or type(body['revision']) is not int or body['revision']!=model['revision'] or body['context_id']!=model['context_id']:
        raise Conflict('Record mapping requires current enabled context')
    if type(body['confirmed']) is not bool or (require_confirmation and body['confirmed'] is not True):
        raise ValueError('Explicit record mapping confirmation required')
    if body['measure_id'] not in {m['id'] for m in model['context']['measures']}:raise ValueError('Unknown mapped measure')
    for key in ('grain','date_basis'):text(body[key],500)
    if type(body['limit']) is not int or not 1<=body['limit']<=250:raise ValueError('Invalid record mapping limit')
    projected=bindings(body['column_bindings']);scoped=bindings(body['filter_bindings'])
    keys=body['key_column_ids'];native_ids=[b['native_column_id'] for b in projected]
    if not isinstance(keys,list) or not 1<=len(keys)<=3 or any(not isinstance(k,str) for k in keys) or len(set(keys))!=len(keys) or not set(keys)<=set(native_ids):
        raise ValueError('Record keys must be unique projected columns')
    assets={a['id']:a for a in model_assets(model['context'])}
    obj=assets.get(body['native_object_id'])
    if not obj or obj['kind']!='SemanticTable':raise ValueError('Unknown native record table')
    objects,columns=snapshot(store,model,config)
    if body['source_object_id'] not in objects:raise ValueError('Unknown source record table')
    for pair in projected+scoped:
        for value in pair.values():text(value,500)
        n=assets.get(pair['native_column_id']);s=columns.get(pair['source_column_id'])
        if not n or n['kind']!='SemanticColumn' or not s or s['parent_id']!=body['source_object_id']:
            raise ValueError('Record mapping references unavailable columns')
        if pair in projected and n['parent_id']!=body['native_object_id']:raise ValueError('Record projection crosses native table')
        if s['metadata'].get('computed_definition'):raise ValueError('Computed source mapping unsupported')
        if n['metadata'].get('dataType') not in SUPPORTED or n['metadata']['dataType']!=kind(s['metadata']):
            raise ValueError('Record mapping types differ or are unsupported')
    # Shared projected/filter columns cannot silently map to different source fields.
    joined={}
    reverse={}
    for pair in projected+scoped:
        a,b=pair['native_column_id'],pair['source_column_id']
        if joined.get(a,b)!=b or reverse.get(b,a)!=a:raise ValueError('Projection and filter mappings conflict')
        joined[a]=b;reverse[b]=a
    return model


def preview(store,model_id,request,config):
    """Compile a draft under example scope without saving review or reading data."""
    from .record_readback import build
    fields(request,['mapping','filters'])
    body=request['mapping'];validate(store,model_id,body,config,require_confirmation=False)
    envelope={'model_id':model_id,'revision':body['revision'],'context_id':body['context_id'],'filters':request['filters']}
    output=[]
    for tool,plan in zip(('native_records','source_records'),plans({'id':'draft','body':body},envelope)):
        plan.pop('record_mapping_id')
        compiled=build(store,plan,config,tool)
        output.append({'tool':tool,'plan':plan,'types':compiled['types'],'compiled_hash':digest(compiled)})
    return {'status':'DRAFT_VALIDATED','mapping_hash':digest(body),'projections':output,'cloud_calls':0,
            'review_saved':False,'authority':'UNCONFIRMED_DRAFT','equivalence_verified':False}


def read(store,model_id,identity):
    store.get(model_id)
    with store.connect() as db:
        initialize(db)
        row=db.execute('SELECT body,hash,actor,created FROM record_mappings WHERE id=? AND model_id=?',(identity,model_id)).fetchone()
        revoked=db.execute('SELECT reason,actor,created FROM record_mapping_revocations WHERE id=?',(identity,)).fetchone()
    if row is None:raise KeyError('Record mapping not found')
    body=json.loads(row[0])
    if digest(body)!=row[1]:raise ValueError('Record mapping integrity differs')
    return {'id':identity,'body':body,'hash':row[1],'actor':row[2],'created':row[3],
            'revocation':list(revoked) if revoked else None,'authority':'TEAM_CONFIRMED_INTENT','equivalence_verified':False}


def register(store,model_id,body,actor,config):
    validate(store,model_id,body,config);actor=text(actor,100)
    identity=str(uuid4())
    with store.connect() as db:
        initialize(db)
        db.execute('INSERT INTO record_mappings VALUES(?,?,?,?,?,?)',
                   (identity,model_id,encoded(body),digest(body),actor,datetime.now(timezone.utc).isoformat()))
    return read(store,model_id,identity)


def listing(store,model_id):
    store.get(model_id)
    with store.connect() as db:
        initialize(db)
        rows=db.execute('SELECT id FROM record_mappings WHERE model_id=? ORDER BY created,id LIMIT 101',(model_id,)).fetchall()
    if len(rows)>100:raise ValueError('Record mapping catalog exceeds budget')
    return [read(store,model_id,row[0]) for row in rows]


def revoke(store,model_id,identity,reason,actor):
    read(store,model_id,identity);text(reason,1000);text(actor,100)
    with store.connect() as db:
        initialize(db)
        db.execute('INSERT OR IGNORE INTO record_mapping_revocations VALUES(?,?,?,?)',
                   (identity,reason,actor,datetime.now(timezone.utc).isoformat()))
    return read(store,model_id,identity)


def plans(review,envelope):
    body=review['body'];mapping={b['native_column_id']:b['source_column_id'] for b in body['column_bindings']}
    filters={b['native_column_id']:b['source_column_id'] for b in body['filter_bindings']}
    if set(filters)!={f['column_id'] for f in envelope['filters']}:raise Conflict('Record mapping must cover complete ticket scope')
    base={k:envelope[k] for k in ('model_id','revision','context_id')}
    base.update(limit=body['limit'],record_mapping_id=review['id'])
    native=dict(base,object_id=body['native_object_id'],column_ids=list(mapping),key_column_ids=body['key_column_ids'],filters=envelope['filters'])
    source=dict(base,object_id=body['source_object_id'],column_ids=list(mapping.values()),
                key_column_ids=[mapping[k] for k in body['key_column_ids']],
                filters=[dict(f,column_id=filters[f['column_id']]) for f in envelope['filters']])
    return native,source


def validate_plan(store,plan,config,backend):
    review=read(store,plan['model_id'],plan['record_mapping_id']);body=review['body']
    if review['revocation'] is not None:raise Conflict('Record mapping revoked')
    validate(store,plan['model_id'],body,config)
    if backend=='source_records':
        reverse={b['source_column_id']:b['native_column_id'] for b in body['filter_bindings']}
        if any(f['column_id'] not in reverse for f in plan['filters']):raise Conflict('Record source scope is not mapped')
        filters=[dict(f,column_id=reverse[f['column_id']]) for f in plan['filters']]
    else:filters=plan['filters']
    envelope={k:plan[k] for k in ('model_id','revision','context_id')};envelope['filters']=filters
    expected=plans(review,envelope)[backend=='source_records']
    compared=dict(plan)
    if 'aggregate_measure_id' in compared:
        if backend!='native_records' or compared.pop('aggregate_measure_id')!=body['measure_id']:
            raise Conflict('Joint aggregate differs from reviewed measure')
    if encoded(expected)!=encoded(compared):raise Conflict('Record plan differs from reviewed projection')
    return {'id':review['id'],'hash':review['hash'],'authority':review['authority'],'equivalence_verified':False,
            'column_bindings':body['column_bindings'],'filter_bindings':body['filter_bindings']}


def resolve(store,config,envelope,reachable):
    from .record_readback import build
    reviews=listing(store,envelope['model_id']);tests=[];gaps=[]
    for measure in sorted(reachable):
        matches=[r for r in reviews if r['revocation'] is None and r['body']['measure_id']==measure and
                 r['body']['revision']==envelope['revision'] and r['body']['context_id']==envelope['context_id']]
        if len(matches)!=1:
            gaps.append({'measure_id':measure,'reason':'RECORD_MAPPING_AMBIGUOUS' if matches else 'CURRENT_RECORD_MAPPING_MISSING'});continue
        review=matches[0]
        try:
            native,source=plans(review,envelope)
            if envelope.get('joint_native_records'):
                joint=dict(native,aggregate_measure_id=measure)
                try:build(store,joint,config,'native_records')
                except (ValueError,KeyError):
                    gaps.append({'measure_id':measure,'reason':'JOINT_NATIVE_CAPTURE_UNSUPPORTED'})
                else:native=joint
            build(store,native,config,'native_records');build(store,source,config,'source_records')
        except (ValueError,KeyError):
            gaps.append({'measure_id':measure,'mapping_id':review['id'],'reason':'RECORD_MAPPING_SCOPE_OR_CATALOG_GAP'});continue
        tests.extend([{'measure_id':measure,'tool':tool,'plan':plan} for tool,plan in [('native_records',native),('source_records',source)]])
    if len(tests)>4:raise ValueError('Discovered record candidate budget exceeded')
    return tests,gaps

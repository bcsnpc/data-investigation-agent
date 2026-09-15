"""Keyed differences between saved readbacks, never a cross-system proof claim."""
from datetime import datetime, timezone
import json
from uuid import UUID, uuid4

from .onboarding import fields, digest, encoded, Conflict
from .record_readback import read as read_records
from .comparisons import aligned

TABLE='record_comparisons'


def bindings(value):
    if not isinstance(value,list) or not 1<=len(value)<=8:raise ValueError('Bounded column mapping required')
    left=set();right=set()
    for pair in value:
        fields(pair,['native_column_id','source_column_id'])
        a=pair['native_column_id'];b=pair['source_column_id']
        if not isinstance(a,str) or not isinstance(b,str) or not a or not b or a in left or b in right:raise ValueError('Column mapping must be bijective')
        left.add(a);right.add(b)
    return value


def validate_projection(left,right,column_bindings,filter_bindings):
    bindings(column_bindings);bindings(filter_bindings)
    mapping={p['native_column_id']:p['source_column_id'] for p in column_bindings}
    if set(mapping)!=set(left['column_ids']) or set(mapping.values())!=set(right['column_ids']):raise ValueError('Mapping must cover every projected column')
    if {mapping[k] for k in left['key_column_ids']}!=set(right['key_column_ids']):raise ValueError('Key mapping differs')
    return [(left['column_ids'].index(c),right['column_ids'].index(mapping[c])) for c in left['column_ids']]


def compare(native,source,column_bindings,filter_bindings):
    left=native['request'];right=source['request']
    order=validate_projection(left,right,column_bindings,filter_bindings)
    gaps=[];differences=[]
    for receipt,expected in [(native,'native_records'),(source,'source_records')]:
        if receipt['request']['backend']!=expected:raise ValueError('Readback backend differs')
        if receipt['status']!='COMPLETED':gaps.append('READBACK_UNAVAILABLE')
        if not receipt['local_context_current']:gaps.append('STALE_OR_DISABLED_CONTEXT')
        if receipt['result'] and receipt['result'].get('completeness')!='COMPLETE_RESPONSE':gaps.append('PARTIAL_READBACK')
    if native['request']['context_hash']!=source['request']['context_hash']:gaps.append('CONTEXT_VERSIONS_DIFFER')
    if not aligned(native['request']['plan']['filters'],source['request']['plan']['filters'],filter_bindings):gaps.append('FILTER_SCOPE_DIFFERS')
    if any(left['types'][a]!=right['types'][b] for a,b in order):gaps.append('COLUMN_TYPES_DIFFER')
    a_rows={};b_rows={}
    if not gaps:
        key_indexes=[left['column_ids'].index(k) for k in left['key_column_ids']]
        for receipt,indexes,target in [(native,[a for a,b in order],a_rows),(source,[b for a,b in order],b_rows)]:
            for row in receipt['result']['rows']:
                values=[row['values'][i] for i in indexes]
                key=[values[i] for i in key_indexes]
                if any(v['type']=='blank' for v in key):gaps.append('NULL_KEY')
                identity=encoded(key)
                if identity in target or int(row['multiplicity'])!=1:gaps.append('DUPLICATE_KEY')
                target[identity]=values
    if not gaps:
        for key in sorted(set(a_rows)|set(b_rows)):
            a=a_rows.get(key);b=b_rows.get(key)
            if a==b:continue
            differences.append({'key':json.loads(key),'kind':'ONLY_SOURCE' if a is None else 'ONLY_NATIVE' if b is None else 'VALUES_DIFFER',
                                'native_values':a,'source_values':b})
    status='NOT_ASSESSED' if gaps else 'OBSERVED_DIFFERENCE' if differences else 'OBSERVED_EQUAL'
    return {'status':status,'outcome':'INSUFFICIENT_EVIDENCE','difference_count':len(differences) if not gaps else None,
            'differences':differences[:50],'examples_truncated':len(differences)>50,
            'column_order':left['column_ids'],'gaps':sorted(set(gaps)),
            'native_receipt_id':native['id'],'source_receipt_id':source['id'],
            'comparable':False,'root_cause_verified':False,'delivery_eligible':False,
            'proof_gaps':['SHARED_GENERATION_UNVERIFIED','SEMANTIC_EQUIVALENCE_UNVERIFIED','EFFECTIVE_IDENTITY_AND_CONTEXT_UNVERIFIED'],
            'limitation':'Keyed equality/differences describe these complete captured responses only. Mapping intent does not prove matching business semantics, current data or a cause.'}


def assess(store,model_id,body,*,assessment_id=None):
    fields(body,['native_receipt_id','source_receipt_id','column_bindings','filter_bindings'])
    left=read_records(store,model_id,body['native_receipt_id']);right=read_records(store,model_id,body['source_receipt_id'])
    result=compare(left,right,body['column_bindings'],body['filter_bindings'])
    result.update(request=body,model_id=model_id,native_evidence_hash=digest(left),source_evidence_hash=digest(right))
    if digest(read_records(store,model_id,body['native_receipt_id']))!=digest(left) or digest(read_records(store,model_id,body['source_receipt_id']))!=digest(right):
        raise Conflict('Readback evidence changed during assessment')
    identity=assessment_id or str(uuid4())
    if str(UUID(identity))!=identity:raise ValueError('Invalid assessment ID')
    with store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS record_comparisons(id TEXT PRIMARY KEY,model_id TEXT,body TEXT,hash TEXT,created TEXT)')
        db.execute('INSERT INTO record_comparisons VALUES(?,?,?,?,?)',(identity,model_id,encoded(result),digest(result),datetime.now(timezone.utc).isoformat()))
    # Local assessment status is not a remote tool status.
    return dict(result,id=identity,hash=digest(result))


def read(store,model_id,identity):
    store.get(model_id)
    with store.connect() as db:
        exists=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='record_comparisons'").fetchone()
        row=db.execute('SELECT body,hash FROM record_comparisons WHERE id=? AND model_id=?',(identity,model_id)).fetchone() if exists else None
    if row is None:raise KeyError('Record comparison not found')
    result=json.loads(row[0])
    if digest(result)!=row[1]:raise ValueError('Comparison integrity differs')
    return {'id':identity,'hash':row[1],'assessment':result}

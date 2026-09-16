"""Reconcile saved direct aggregates with record captures, not remote snapshots."""
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import json
from uuid import uuid4

from .onboarding import fields, digest, encoded, Conflict
from . import aggregate_semantics, diagnostic_evidence, source_diagnostics, record_readback, record_bindings
from .comparisons import aligned

TABLE='record_aggregate_assessments'
REQUEST_FIELDS=['native_receipt_id','source_receipt_id','native_records_id','source_records_id','measure_id','record_mapping_id']


def same_scope(left,right):
    return aligned(left,right,[{'native_column_id':f['column_id'],'source_column_id':f['column_id']} for f in left])


def reconstruct(receipt,operation,column_id=None):
    """Exact supported arithmetic over complete projected groups and multiplicity."""
    if receipt['status']!='COMPLETED' or receipt['result']['completeness']!='COMPLETE_RESPONSE':
        raise ValueError('Complete record capture required')
    request=receipt['request'];rows=receipt['result']['rows'];index=None
    if operation=='sum':
        if column_id not in request['column_ids']:raise ValueError('Sum column missing from projection')
        index=request['column_ids'].index(column_id)
        if request['types'][index] not in ('decimal','int64'):raise ValueError('Exact numeric projection required')
    elif operation!='count_rows':raise ValueError('Unsupported reconstruction operation')
    count=0;nonblank=0
    with localcontext() as context:
        context.prec=100
        total=Decimal(0)
        for row in rows:
            multiplicity=int(row['multiplicity'])
            if multiplicity<=0 or multiplicity>10**38:raise ValueError('Invalid multiplicity')
            count+=multiplicity
            if index is not None:
                value=row['values'][index]
                if value['type']=='blank':continue
                if value['type'] not in ('decimal','int64'):raise ValueError('Exact numeric record required')
                number=Decimal(value['value'])
                if not number.is_finite() or len(number.as_tuple().digits)>38 or abs(number.adjusted())>100:
                    raise ValueError('Record number exceeds arithmetic budget')
                nonblank+=multiplicity;total+=number*multiplicity
        if operation=='count_rows':total=Decimal(count);nonblank=count
        blank=(operation=='sum' and nonblank==0) or (operation=='count_rows' and count==0 and request['backend']=='native_records')
        return {'value':{'type':'blank' if blank else 'decimal','value':None if blank else format(total,'f')},
                'row_count':str(count),'nonblank_count':str(nonblank)}


def equal(left,right):
    if left['type']=='blank' or right['type']=='blank':return left['type']==right['type']=='blank'
    if left['type'] not in ('decimal','int64') or right['type'] not in ('decimal','int64'):return False
    return Decimal(left['value'])==Decimal(right['value'])


def calculate(model,review,native,source,nrecords,srecords,measure_id):
    shape=aggregate_semantics.describe(model,measure_id);gaps=[]
    contract=review['body']
    if review['revocation'] is not None:gaps.append('RECORD_MAPPING_REVOKED')
    if contract['context_id']!=model['context_id'] or contract['revision']!=model['revision']:gaps.append('RECORD_MAPPING_STALE')
    if contract['measure_id']!=measure_id:gaps.append('MAPPING_MEASURE_DIFFERS')
    if shape['state']!='SUPPORTED':gaps.append('AGGREGATE_RECONSTRUCTION_UNSUPPORTED')
    for label,receipt in [('NATIVE',native),('SOURCE',source),('NATIVE_RECORDS',nrecords),('SOURCE_RECORDS',srecords)]:
        if receipt['status']!='COMPLETED':gaps.append(label+'_UNAVAILABLE')
        if receipt['request']['context_hash']!=digest(model['context']):gaps.append(label+'_CONTEXT_DIFFERS')
        if receipt['request']['plan']['revision']!=model['revision']:gaps.append(label+'_REVISION_DIFFERS')
    if not model['enabled']:gaps.append('MODEL_DISABLED')
    for label,receipt in [('NATIVE',native),('SOURCE',source)]:
        if receipt.get('integrity',{}).get('state')!='SEALED':gaps.append(label+'_RECEIPT_UNSEALED')
    for label,receipt,backend in [('NATIVE_RECORDS',nrecords,'native_records'),('SOURCE_RECORDS',srecords,'source_records')]:
        if receipt['request']['backend']!=backend:gaps.append(label+'_BACKEND_DIFFERS')
        if (receipt.get('result') or {}).get('completeness')!='COMPLETE_RESPONSE':gaps.append(label+'_INCOMPLETE')
        pinned=receipt['request'].get('reviewed_mapping') or {}
        if pinned.get('id')!=review['id'] or pinned.get('hash')!=review['hash']:gaps.append(label+'_REVIEW_NOT_PINNED')
    np=native['request']['plan'];sp=source['request']['plan'];nr=nrecords['request']['plan'];sr=srecords['request']['plan']
    if np.get('context_path'):gaps.append('DEPENDENCY_CONTEXT_RECONSTRUCTION_UNSUPPORTED')
    if native['request']['dimension_id'] is not None or measure_id not in native['request']['measure_ids']:
        gaps.append('NATIVE_SCALAR_REQUIRED')
    if (native.get('result') or {}).get('completeness')!='COMPLETE_RESPONSE':gaps.append('NATIVE_RESPONSE_INCOMPLETE')
    if not same_scope(np['filters'],nr['filters']) or not same_scope(sp['filters'],sr['filters']):gaps.append('AGGREGATE_RECORD_SCOPE_DIFFERS')
    if not aligned(nr['filters'],sr['filters'],contract['filter_bindings']):gaps.append('NATIVE_SOURCE_SCOPE_DIFFERS')
    columns={b['native_column_id']:b['source_column_id'] for b in contract['column_bindings']}
    if nr['object_id']!=contract['native_object_id'] or sr['object_id']!=contract['source_object_id'] or sp['object_id']!=sr['object_id']:
        gaps.append('RECORD_OBJECT_BINDING_DIFFERS')
    native_column=None;source_column=None
    if shape['state']=='SUPPORTED':
        if shape['operation']!=sp['operation']:gaps.append('AGGREGATE_OPERATIONS_DIFFER')
        if shape['operation']=='count_rows':
            if shape['input_id']!=nr['object_id']:gaps.append('NATIVE_INPUT_TABLE_DIFFERS')
        else:
            native_column=shape['input_id'];source_column=columns.get(native_column)
            if not source_column or sp['column_id']!=source_column:gaps.append('SUM_INPUT_MAPPING_DIFFERS')
    observations=None;status='NOT_ASSESSED';delta=None
    if not gaps:
        try:
            left=reconstruct(nrecords,shape['operation'],native_column)
            right=reconstruct(srecords,shape['operation'],source_column)
        except ValueError:gaps.append('RECORD_RECONSTRUCTION_UNAVAILABLE')
        else:
            value=native['result']['rows'][0]['[m'+str(native['request']['measure_ids'].index(measure_id))+']']
            source_value=source['result']['value']
            nmatch=equal(value,left['value']);smatch=equal(source_value,right['value'])
            counts=(equal(source['result']['row_count'],{'type':'decimal','value':right['row_count']}) and
                    equal(source['result']['nonblank_count'],{'type':'decimal','value':right['nonblank_count']}))
            observations={'native':{'observed':value,'reconstructed':left,'matches':nmatch},
                          'source':{'observed':source_value,'reconstructed':right,'matches':smatch,'counts_match':counts}}
            status='CAPTURES_RECONCILE' if nmatch and smatch and counts else 'CAPTURE_INCONSISTENCY'
            if status=='CAPTURES_RECONCILE' and value['type']=='decimal' and source_value['type']=='decimal':
                with localcontext() as context:
                    context.prec=100;delta=format(Decimal(value['value'])-Decimal(source_value['value']),'f')
    return {'version':'record-aggregate-v1','status':status,'gaps':sorted(set(gaps)),'shape':shape,
            'observations':observations,'record_explained_native_minus_source':delta,
            'mapping_hash':review['hash'],'outcome':'INSUFFICIENT_EVIDENCE','root_cause_verified':False,'delivery_eligible':False,
            'proof_gaps':['SHARED_GENERATION_UNVERIFIED','REMOTE_DEFINITION_STABILITY_UNVERIFIED','EFFECTIVE_CONTEXT_AND_EQUIVALENCE_UNVERIFIED'],
            'limitation':'Arithmetic consistency of separate captures only. A mismatch may reflect drift or context; it is not a verified defect.'}


def assess(store,model_id,body,*,assessment_id=None):
    fields(body,REQUEST_FIELDS);model=store.get(model_id)
    native=diagnostic_evidence.read(store,model_id,body['native_receipt_id'])
    source=source_diagnostics.evidence(store,model_id,body['source_receipt_id'])
    nr=record_readback.read(store,model_id,body['native_records_id']);sr=record_readback.read(store,model_id,body['source_records_id'])
    review=record_bindings.read(store,model_id,body['record_mapping_id'])
    result=calculate(model,review,native,source,nr,sr,body['measure_id'])
    result.update(request=body,model_id=model_id,context_id=model['context_id'],evidence_hashes={
        name:digest(value) for name,value in [('native',native),('source',source),('native_records',nr),('source_records',sr)]})
    if digest(store.get(model_id))!=digest(model):raise Conflict('Model changed during reconstruction')
    identity=assessment_id or str(uuid4())
    with store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS record_aggregate_assessments(id TEXT PRIMARY KEY,model_id TEXT,body TEXT,hash TEXT,created TEXT)')
        db.execute('INSERT INTO record_aggregate_assessments VALUES(?,?,?,?,?)',(identity,model_id,encoded(result),digest(result),datetime.now(timezone.utc).isoformat()))
    return dict(result,id=identity,hash=digest(result))


def read(store,model_id,identity):
    store.get(model_id)
    with store.connect() as db:
        exists=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(TABLE,)).fetchone()
        row=db.execute('SELECT body,hash FROM '+TABLE+' WHERE model_id=? AND id=?',(model_id,identity)).fetchone() if exists else None
    if row is None:raise KeyError('Record aggregate assessment not found')
    body=json.loads(row[0])
    if digest(body)!=row[1]:raise ValueError('Record aggregate assessment integrity differs')
    return dict(body,id=identity,hash=row[1])


def derive(store,model_id,observations):
    """Attach local arithmetic evidence to adaptive state without another query."""
    model=store.get(model_id);results=[];groups={}
    for observation in observations:
        review=observation.get('record_mapping')
        if review:groups.setdefault((review['id'],observation['measure_id']),[]).append(observation)
    for (mapping_id,measure),group in groups.items():
        if len(group)!=2 or {o['tool'] for o in group}!={'native_records','source_records'}:continue
        natives=[o for o in observations if o['tool']=='native' and o['measure_id']==measure and o['dimension_id'] is None and not o.get('dependency_context')]
        sources=[o for o in observations if o['tool']=='source' and o['measure_id']==measure and o.get('source_operation') in ('count_rows','sum')]
        if not natives or not sources:continue
        if len(natives)!=1 or len(sources)!=1:
            results.append({'status':'NOT_ASSESSED','gaps':['AMBIGUOUS_AGGREGATE_OBSERVATIONS'],'root_cause_verified':False});continue
        try:
            review=record_bindings.read(store,model_id,mapping_id)
            native=diagnostic_evidence.read(store,model_id,natives[0]['id'])
            source=source_diagnostics.evidence(store,model_id,sources[0]['id'])
            nr=record_readback.read(store,model_id,next(o['id'] for o in group if o['tool']=='native_records'))
            sr=record_readback.read(store,model_id,next(o['id'] for o in group if o['tool']=='source_records'))
            result=calculate(model,review,native,source,nr,sr,measure)
            result.update(measure_id=measure,record_mapping_id=mapping_id,receipt_ids=[native['id'],source['id'],nr['id'],sr['id']])
        except (ValueError,KeyError):result={'status':'NOT_ASSESSED','gaps':['RECONCILIATION_EVIDENCE_UNAVAILABLE'],'root_cause_verified':False}
        results.append(result)
    return results

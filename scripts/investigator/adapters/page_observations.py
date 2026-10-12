"""Addressed visual quantities through the installed, admitted reader only."""
from ..onboarding import digest
import json
from ..form_candidates import NotMeasurable
from .form_candidate_values import plan,observation
from datetime import datetime

def timestamp(value):
    if not isinstance(value,str):raise ValueError('Timestamp was not returned')
    value=datetime.fromisoformat(value.replace('Z','+00:00'))
    if value.tzinfo is None:raise ValueError('Timestamp timezone is not established')
    return value

def read(adapter,candidate):
    if candidate.get('model_id')!=adapter.model['id']:raise NotMeasurable('Page read leaves the admitted model')
    if adapter.meter_read is None:raise NotMeasurable('A governed admitted session is required for page reads')
    if adapter.execute_native is None:raise NotMeasurable('The admitted native reader is unavailable')
    compiled=plan(adapter.model,candidate)
    from ..flexible_tools import run
    result=adapter.meter_read('bounded_dax',lambda:run(adapter.store,compiled,adapter.config,'bounded_dax',adapter.execute_native))
    if result.get('status')!='COMPLETED':
        from ..receipt_integrity import verify
        with adapter.store.connect()as db:seal=verify(db,'bounded_dax',result['id'])
        return {'status':'UNAVAILABLE','complete':False,'id':result['id'],'tool':'bounded_dax',
                'query':compiled['query'],'read_address':compiled['read_address'],'result':result['result'],
                'reason':'The addressed reader query did not complete','receipt_seal':seal,'cause_established':False}
    observed=observation(adapter.model,adapter.config,compiled,result)
    body=result.get('result',{});attestation=observed['attestation']
    if (body.get('surface_report_binding')!='VALUE_QUERY' or attestation.get('consistency')!='MATCHED'
            or attestation.get('missing_required_fields')):
        raise NotMeasurable('Page quantity lacks query-bound reader identity, engine or object attestation')
    from ..receipt_integrity import verify
    with adapter.store.connect() as db:seal=verify(db,'bounded_dax',result['id'])
    if seal['state']!='SEALED':raise NotMeasurable('Page quantity receipt is not sealed')
    return {**observed,'id':result['id'],'tool':'bounded_dax','query':compiled['query'],
            'read_address':compiled['read_address'],'cell_address':compiled['cell_address'],
            'context_id':compiled['context_id'],'context_hash':digest(adapter.model['context']),
            'receipt_seal':seal,'surface_report_binding':body['surface_report_binding'],
            'snapshot_status':'SNAPSHOT_UNVERIFIED'}

def verify_quantity(adapter,candidate,probe):
    from ..flexible_tools import build
    from ..receipt_integrity import verify
    from .report_cells import catalog,declared_scopes
    current=adapter.store.get(candidate['model_id'])
    if current['revision']!=adapter.model['revision']or digest(current['context'])!=digest(adapter.model['context']):raise NotMeasurable('Page verification context changed')
    visual=next((v for v in declared_scopes(current,catalog(current))if v['target_id']==candidate['target_id']),None)
    if not visual or visual.get('declared_scopes',{}).get(candidate['measure_id'])!=candidate['declaration']:
        raise NotMeasurable('Page declaration differs from the original retained visual')
    compiled=plan(current,candidate);expected={'plan':compiled,**build(adapter.store,compiled,adapter.config,'bounded_dax')}
    with adapter.store.connect()as db:
        row=db.execute('SELECT model_id,status,request,result FROM flexible_diagnostics WHERE id=?',(probe.get('id'),)).fetchone()
        seal=verify(db,'bounded_dax',probe.get('id'))
    if not row or seal['state']!='SEALED'or row[0]!=candidate['model_id']or json.loads(row[2])!=expected:
        raise NotMeasurable('Page receipt does not bind the exact current statement and addressed scope')
    result={'id':probe['id'],'status':row[1],'result':json.loads(row[3])}
    if row[1]!='COMPLETED':
        if probe.get('result')!=result['result']or probe.get('read_address')!=compiled['read_address']or probe.get('query')!=compiled['query']:
            raise NotMeasurable('Failed page receipt was changed')
        return probe
    actual=observation(current,adapter.config,compiled,result)
    rows=result['result']['rows']
    if len(rows)!=1 or len(rows[0])!=1:raise NotMeasurable('Page receipt does not retain a scalar')
    scalar=next(iter(rows[0].values()))
    if scalar.get('type')not in('decimal','blank'):raise NotMeasurable('Numeric page comparison requires an original numeric or blank scalar')
    required={'value':actual['value'],'query':compiled['query'],'query_hash':digest(compiled),
        'read_address':compiled['read_address'],'cell_address':compiled['cell_address'],
        'attestation':actual['attestation'],'receipt_seal':seal,'surface_report_binding':result['result'].get('surface_report_binding')}
    if any(probe.get(k)!=v for k,v in required.items()):raise NotMeasurable('Page producer changed its original value, scope or attestation')
    return {**probe,'typed_value':scalar}

def refresh(adapter,path):
    raw=adapter.refresh_timing(path)
    profile=adapter.config.get('fabric',{}).get('refresh_timing_reader',{})
    provenance=raw.get('identity_provenance',{})
    account=profile.get('account')
    bound=(isinstance(account,str)and bool(account)and raw.get('model_id')==adapter.model.get('native_id')and
        str(provenance.get('token_identity','')).casefold()==account.casefold()and str(provenance.get('account','')).casefold()==account.casefold())
    if raw.get('status')!='AVAILABLE'or not bound or not isinstance(raw.get('history'),list)or len(raw['history'])!=1:
        return {'status':'UNAVAILABLE','reason':raw.get('reason','Refresh timing did not establish the admitted model and metadata reader'),'raw':raw}
    last=raw['history'][0]
    try:valid=timestamp(last.get('endTime'))>=timestamp(last.get('startTime'))
    except (ValueError,TypeError):valid=False
    if not valid or last.get('status')not in('Completed','Succeeded'):
        return {'status':'UNAVAILABLE','reason':'A successful refresh end timestamp was not established','raw':raw}
    identity='refresh-timing:'+digest(raw)
    return {'status':'OBSERVED','timestamp':last['endTime'],'started_at':last['startTime'],'run_id':last.get('requestId'),
            'run_status':last['status'],'timestamp_kind':'RETAINED_REFRESH_COMPLETION',
            'evidence':{'id':identity,'tool':'refresh_timing','result':raw,'authority':'ADMITTED_METADATA_READER','snapshot_status':'SNAPSHOT_UNVERIFIED'}}

def load(adapter,boundary):
    raw=adapter.job_history(boundary);evidence=raw.get('evidence')
    try:valid=timestamp(raw.get('completed_at'))>=timestamp(raw.get('started_at'))
    except (ValueError,TypeError):valid=False
    if raw.get('status')!='CURRENT'or not valid or not evidence or not evidence.get('id'):
        return {'status':'UNAVAILABLE','reason':raw.get('reason','A successful load timestamp and original receipt were not established'),'raw':raw}
    if evidence.get('tool')=='bounded_fabric_sql':
        from ..receipt_integrity import verify
        with adapter.store.connect()as db:seal=verify(db,'bounded_fabric_sql',evidence['id'])
        if (seal['state']!='SEALED'or evidence.get('completeness')!='COMPLETE_RESPONSE'or
            evidence.get('surface_report_binding')!='VALUE_QUERY'or evidence.get('surface_attestation',{}).get('consistency')!='MATCHED'):
            return {'status':'UNAVAILABLE','reason':'The declared audit timing lacks its sealed attested query-bound receipt','raw':raw}
        kind='DECLARED_AUDIT_COMPLETION'
    elif evidence.get('tool')=='context':
        if evidence.get('completeness')!='COMPLETE_RESPONSE'or not evidence.get('context_version')or not evidence.get('runs'):
            return {'status':'UNAVAILABLE','reason':'Retained job timing lacks its original context receipt','raw':raw}
        kind='RETAINED_JOB_COMPLETION'
    else:return {'status':'UNAVAILABLE','reason':'Load timing source is not a declared audit or retained history receipt','raw':raw}
    return {'status':'OBSERVED','timestamp':raw['completed_at'],'started_at':raw['started_at'],'run_id':raw.get('run_id'),
            'timestamp_kind':kind,'capture_currency_established':False,'evidence':evidence,'limitations':[raw.get('reason','')]}

def inventory(adapter,scope):
    from .report_cells import catalog
    current=adapter.store.get(adapter.model['id']);quantity={v['target_id']:v for v in catalog(current)}
    result=[]
    for report in current['context'].get('reports',[]):
        if report['report']['id']!=scope['report_id']:continue
        for part in report.get('report_definitions',[]):
            path=part['name'].split('/')
            if len(path)!=6 or path[-1]!='visual.json':continue
            page=scope['report_id']+'/page/'+path[2]
            if scope['kind']!='REPORT'and page!=scope.get('page_id'):continue
            if scope['kind']=='VISUALS'and part['id']not in scope.get('visual_ids',[]):continue
            visual=quantity.get(part['id'])
            if visual:label=', '.join(n for n in visual['names']if n not in visual['page_names'])or'Retained quantity visual'
            else:
                doc=json.loads(part['metadata']['content']);labels=[]
                for title in doc.get('visual',{}).get('visualContainerObjects',{}).get('title',[]):
                    raw=title.get('properties',{}).get('text',{}).get('expr',{}).get('Literal',{}).get('Value')
                    if isinstance(raw,str)and raw.startswith("'")and raw.endswith("'"):labels.append(raw[1:-1].replace("''","'"))
                label=', '.join(labels)or'Non-quantity visual'
            result.append({'visual_id':part['id'],'label':label,'has_metric':bool(visual),'definition_hash':digest(part)})
    return result

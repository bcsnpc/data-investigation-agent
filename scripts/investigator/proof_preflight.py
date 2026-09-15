"""Bounded collector observations for native acceptance feasibility, not proof flags."""
import base64
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import time
from uuid import UUID, uuid4

from .onboarding import digest, encoded, Conflict

VERSION='proof-preflight-v1'


def definition_summary(body):
    parts=body['definition']['parts']
    if not isinstance(parts,list) or not 1<=len(parts)<=100:raise ValueError('Definition part budget exceeded')
    hashes={};size=0;modes=[];roles=0;tables=0;found=False
    for part in parts:
        path=part['path']
        if not isinstance(path,str) or len(path)>500 or path in hashes or part['payloadType']!='InlineBase64':raise ValueError('Invalid definition part')
        if not isinstance(part['payload'],str) or len(part['payload'])>8_000_000:raise ValueError('Definition payload budget exceeded')
        raw=base64.b64decode(part['payload'],validate=True);size+=len(raw)
        if size>6_000_000:raise ValueError('Definition byte budget exceeded')
        hashes[path]=hashlib.sha256(raw).hexdigest()
        if path.lower().endswith('model.bim'):
            if found:raise ValueError('Multiple model definitions')
            found=True;model=json.loads(raw.decode('utf-8-sig'))['model']
            tables=len(model.get('tables',[]));roles=len(model.get('roles',[]))
            for table in model.get('tables',[]):
                for partition in table.get('partitions',[]):
                    mode=partition.get('mode','unknown')
                    modes.append(mode if mode in ('import','directLake','directQuery','dual','default') else 'unknown')
    # Persist hashes/counts only, never expressions, connection strings or role members.
    return {'definition_hash':digest(hashes),'part_count':len(hashes),'bytes':size,'tmsl_model_observed':found,
            'partition_modes':sorted(set(modes)),'table_count':tables,'role_count':roles}


def summarize(kind,body,model):
    if not isinstance(body,dict):raise ValueError('Expected metadata object')
    if kind.startswith('definition_'):return definition_summary(body)
    if kind=='item':
        if body.get('id')!=model['native_id'] or body.get('type')!='SemanticModel':raise ValueError('Returned model identity differs')
        return {'identity_matches':True}
    if kind=='dataset':
        if body.get('id')!=model['native_id']:raise ValueError('Returned dataset identity differs')
        result={'identity_matches':True}
        for key in ('isRefreshable','isEffectiveIdentityRequired','isEffectiveIdentityRolesRequired'):
            value=body.get(key)
            if value is not None and type(value) is not bool:raise ValueError('Malformed dataset property')
            result[key]=value
        return result
    rows=body.get('value')
    if not isinstance(rows,list) or len(rows)>1000:raise ValueError('Metadata list budget exceeded')
    partial=bool(body.get('continuationToken') or body.get('continuationUri') or body.get('@odata.nextLink'))
    if kind=='workspace_access':
        roles=Counter(r.get('role') if r.get('role') in ('Admin','Member','Contributor','Viewer') else 'Unknown' for r in rows)
        return {'role_counts':dict(roles),'observed_write_role_assignments':sum(roles[k] for k in ('Admin','Member','Contributor')),
                'coverage':'PARTIAL_PAGE' if partial else 'WORKSPACE_ASSIGNMENTS_ONLY',
                'effective_principal_permissions_verified':False}
    if kind=='refreshes':
        statuses=Counter(r.get('status') if r.get('status') in ('Unknown','Completed','Failed','Disabled','InProgress','Cancelled') else 'Other' for r in rows)
        return {'sample_count':len(rows),'statuses':dict(statuses),'coverage':'RECENT_HISTORY_ONLY',
                'input_generation_bound':False}
    raise ValueError('Unknown metadata probe')


def evaluate(observations):
    indexed={o['kind']:o for o in observations}
    before=indexed.get('definition_before',{});after=indexed.get('definition_after',{})
    same=None
    if before.get('status')==after.get('status')=='OBSERVED':
        same=before['summary']['definition_hash']==after['summary']['definition_hash']
    blockers=['EXCLUSIVE_PUBLICATION_CONTROL_NOT_IMPLEMENTED','INPUT_PUBLICATION_GENERATION_UNBOUND',
              'EFFECTIVE_RUNTIME_IDENTITY_AND_CONTEXT_UNVERIFIED','COMPLETE_FIXTURE_CONTENT_PROOF_MISSING']
    if same is None:blockers.append('TWO_DEFINITION_CAPTURES_UNAVAILABLE')
    elif not same:blockers.append('DEFINITION_CHANGED_BETWEEN_PROBES')
    if not before.get('summary',{}).get('tmsl_model_observed') or not after.get('summary',{}).get('tmsl_model_observed'):
        blockers.append('TMSL_MODEL_CONTENT_UNAVAILABLE')
    if any(o['status']!='OBSERVED' for o in observations):blockers.append('METADATA_PROBE_GAPS')
    access=indexed.get('workspace_access',{}).get('summary',{})
    if access.get('observed_write_role_assignments',0):blockers.append('WORKSPACE_WRITE_ROLES_OBSERVED')
    if access.get('coverage')=='PARTIAL_PAGE':blockers.append('WORKSPACE_ACCESS_PAGE_INCOMPLETE')
    return {'gate_status':'BLOCKED','live_acceptance_ready':False,'definition_hashes_equal_at_probes':same,
            'blockers':blockers,'remote_stability_verified':False,'exclusive_write_boundary_verified':False,
            'collector_role':'METADATA_COLLECTOR_NOT_READONLY_INVESTIGATOR',
            'definition_permission_requirement':'READ_AND_WRITE_MODEL_PERMISSION',
            'limitation':'Matching endpoint observations do not prove stability between probes or prevent external writes. No data snapshot or effective identity is certified.'}


def run(store,model_id,transport,*,clock=time.monotonic,sleep=time.sleep):
    model=store.get(model_id)
    if not model['enabled'] or not model.get('context'):raise Conflict('Current enabled model context required')
    model_hash=digest(model)
    workspace=str(UUID(model['workspace']));native=str(UUID(model['native_id']))
    identity=str(uuid4());started=clock();calls=0;observations=[]
    state={'version':VERSION,'id':identity,'model_id':model_id,'context_id':model['context_id'],
           'context_hash':digest(model['context']),'revision':model['revision'],
           'created':datetime.now(timezone.utc).isoformat(),'status':'RUNNING','http_calls':0,'observations':observations}
    def save():
        with store.connect() as db:
            db.execute('UPDATE proof_preflights SET body=?,hash=? WHERE id=?',(encoded(state),digest(state),identity))
    with store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS proof_preflights(id TEXT PRIMARY KEY,model_id TEXT,body TEXT,hash TEXT,created TEXT)')
        db.execute('INSERT INTO proof_preflights VALUES(?,?,?,?,?)',(identity,model_id,encoded(state),digest(state),state['created']))
    def call(endpoint,method,audience):
        nonlocal calls
        if calls>=12 or clock()-started>=240:raise TimeoutError('Preflight budget exhausted')
        if digest(store.get(model_id))!=model_hash:raise Conflict('Model changed')
        calls+=1;state['http_calls']=calls;save()  # Reserve before the metadata call.
        result=transport(endpoint,method,audience)
        if not isinstance(result,dict) or result.get('status_code') not in (200,202):
            code=result.get('status_code') if isinstance(result,dict) else None
            error=RuntimeError('Metadata request unavailable');error.http_status=code if type(code) is int else None;raise error
        return result
    probes=[('item',f'workspaces/{workspace}/semanticModels/{native}','get','fabric'),
            ('dataset',f'groups/{workspace}/datasets/{native}','get','powerbi'),
            ('workspace_access',f'workspaces/{workspace}/roleAssignments','get','fabric'),
            ('refreshes',f'groups/{workspace}/datasets/{native}/refreshes?$top=5','get','powerbi'),
            ('definition_before',f'workspaces/{workspace}/semanticModels/{native}/getDefinition?format=TMSL','post','fabric'),
            ('definition_after',f'workspaces/{workspace}/semanticModels/{native}/getDefinition?format=TMSL','post','fabric')]
    for kind,endpoint,method,audience in probes:
        observation={'kind':kind,'started':datetime.now(timezone.utc).isoformat(),'status':'DISPATCHED'}
        observations.append(observation);save()
        try:
            result=call(endpoint,method,audience)
            if result['status_code']==202:
                if not kind.startswith('definition_'):raise ValueError('Unexpected asynchronous response')
                headers={k.lower():v for k,v in result.get('headers',{}).items()}
                operation=str(UUID(headers['x-ms-operation-id']))
                delay=int(headers.get('retry-after',1))
                if not 0<=delay<=30:raise TimeoutError('Retry interval exceeds preflight budget')
                for _ in range(2):
                    if clock()-started+delay>=240:raise TimeoutError('Preflight deadline')
                    sleep(delay)
                    poll=call('operations/'+operation,'get','fabric')
                    if poll['text'].get('status') in ('Succeeded','Completed'):
                        result=call('operations/'+operation+'/result','get','fabric');break
                    if poll['text'].get('status') in ('Failed','Cancelled'):raise RuntimeError('Definition read failed')
                if result['status_code']!=200:raise TimeoutError('Definition still pending')
            observation.update(status='OBSERVED',summary=summarize(kind,result['text'],model))
        except Exception as exc:
            observation.update(status='UNAVAILABLE',error_type=type(exc).__name__)
            if type(getattr(exc,'http_status',None)) is int:observation['http_status']=exc.http_status
        observation['finished']=datetime.now(timezone.utc).isoformat();save()
    state.update(status='COMPLETED',assessment=evaluate(observations),finished=datetime.now(timezone.utc).isoformat())
    if digest(store.get(model_id))!=model_hash:
        state['assessment']['blockers'].append('LOCAL_MODEL_CHANGED_DURING_PREFLIGHT')
    save();return state


def read(store,model_id,identity):
    model=store.get(model_id)
    with store.connect() as db:
        exists=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='proof_preflights'").fetchone()
        row=db.execute('SELECT body,hash FROM proof_preflights WHERE id=? AND model_id=?',(identity,model_id)).fetchone() if exists else None
    if row is None:raise KeyError('Preflight not found')
    result=json.loads(row[0])
    if digest(result)!=row[1]:raise Conflict('Preflight integrity differs')
    return dict(result,hash=row[1],local_context_current=bool(model['enabled'] and model['revision']==result['revision'] and digest(model['context'])==result['context_hash']))


def listing(store,model_id):
    store.get(model_id)
    with store.connect() as db:
        exists=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='proof_preflights'").fetchone()
        rows=db.execute('SELECT id FROM proof_preflights WHERE model_id=? ORDER BY created DESC,id DESC LIMIT 20',(model_id,)).fetchall() if exists else []
    return [read(store,model_id,row[0]) for row in rows]

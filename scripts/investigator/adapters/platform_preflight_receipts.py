"""Import explicit hash-pinned control facts, never infer estate permissions."""
import hashlib
import json
from pathlib import Path
import re


def load(path, expected, kind):
    if not isinstance(expected,str) or not re.fullmatch(r'[a-f0-9]{64}',expected):
        raise ValueError('PREFLIGHT_RECEIPT_HASH_REQUIRED')
    with Path(path).open('rb') as source:raw=source.read(262145)
    if len(raw)>262144 or hashlib.sha256(raw).hexdigest()!=expected:
        raise ValueError('PREFLIGHT_RECEIPT_HASH_OR_BOUND_DIFFERS')
    value=json.loads(raw)
    if not isinstance(value,dict) or value.get('version')!=1 or value.get('kind')!=kind:
        raise ValueError('PREFLIGHT_RECEIPT_KIND_DIFFERS')
    if value.get('estate_reads')!=0 or value.get('model_calls')!=0:
        raise ValueError('PREFLIGHT_CONTROL_RECEIPT_REQUIRED')
    return value,'sha256:'+expected


def health_probes(platform, receipt, identity):
    from ..cloud_preflight import Observation
    principal=platform.get('worker_identity',{}).get('principal_id')
    if not principal or receipt.get('principal_id')!=principal:
        raise ValueError('PREFLIGHT_RECEIPT_PRINCIPAL_DIFFERS')
    checks=receipt.get('checks',{})
    blob=checks.get('blob',{})
    passed=(blob.get('status')=='PASS' and blob.get('immutable') is True
            and isinstance(blob.get('sha256'),str) and re.fullmatch(r'[a-f0-9]{64}',blob['sha256']) is not None)
    results={}
    if 'blob' in checks:
        observation=Observation(principal,identity,passed,
            'Retained worker health establishes immutable challenge Blob PUT/GET only; no estate or model capability.')
        results['blob.access']=lambda:observation
    if passed:
        authenticated=Observation(principal,identity,True,
            'Retained bound worker token and authenticated Blob roundtrip establish worker authentication for storage only.')
        results['worker_identity.authentication']=lambda:authenticated
    # Health metadata-list success is deliberately not key_vault.access: that
    # check requires a versioned secret read. PG counts are not migration proof.
    return results


def authentication_facts(manifest, receipt, identity):
    """Separate informational facts; never fill semantic/layer/model-access checks."""
    expected={}
    for adapter in manifest.get('adapters',[]):
        fabric=adapter.get('options',{}).get('fabric',{})
        for label,key in (('semantic','auth'),('sql','sql_reader')):
            declaration=fabric.get(key,{})
            if declaration.get('mode') in ('key_vault_user_cache','federated_reader'):
                declaration=dict(declaration)
                if declaration['mode']=='federated_reader':
                    declaration['scope']=('https://analysis.windows.net/powerbi/api/.default'
                                          if label=='semantic' else 'https://database.windows.net/.default')
                expected[(adapter['id'],label)]=declaration
        declaration=adapter.get('options',{}).get('sql',{}).get('auth',{})
        if declaration.get('mode')=='federated_reader':
            expected[(adapter['id'],'application_sql')]=dict(declaration,scope='https://database.windows.net/.default')
    rows=receipt.get('checks')
    if not isinstance(rows,list) or len(rows)>16:raise ValueError('PREFLIGHT_AUTH_RECEIPT_SHAPE')
    result=[]
    for (adapter,label),declaration in expected.items():
        federated=declaration['mode']=='federated_reader'
        kind='FEDERATED_READER_AUTHENTICATION' if federated else 'EXISTING_READER_AUTHENTICATION'
        fields=('scope','tenant_id','principal_id','client_id') if federated else ('scope','tenant_id','principal_id')
        matches=[r for r in rows if r.get('kind')==kind
                 and all(r.get(k)==declaration[k] for k in fields)]
        if len(matches)>1:raise ValueError('PREFLIGHT_AUTH_RECEIPT_AMBIGUOUS')
        status='MISSING'
        if matches:
            row=matches[0]
            status='PASS' if row.get('status')=='PASS' and row.get('audience')==declaration['scope'].removesuffix('/.default').rstrip('/') else 'FAIL'
        result.append({'adapter':adapter,'surface':label,'status':status,
            'evidence':identity,'principal_id':declaration['principal_id'],'scope':declaration['scope'],
            'detail':'Credential authentication only; no model, database, report, table or scope permission is established.'})
    if any(r.get('kind')=='MODEL_KEY_AVAILABILITY' for r in rows):
        result.append({'surface':'model_key','status':'INFORMATIONAL','evidence':identity,
            'detail':'The authentication receipt contains a key availability check; this is not model API availability.'})
    return result

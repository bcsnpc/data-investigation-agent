"""Closed, platform-neutral lineage records; confidence is never inferred from absence."""
import copy
from datetime import datetime, timezone
import hashlib
import json
import re

CONFIDENCE=frozenset({'DECLARED','INFERRED','VERIFIED','UNKNOWN'})
NODE_KINDS=frozenset({'REPORT','PAGE','VISUAL','SLICER','FILTER','INTERACTION','MEASURE','CALCULATED_COLUMN',
    'CALCULATION_GROUP','FIELD_PARAMETER','MODEL','TABLE','COLUMN','RELATIONSHIP','SECURITY_ROLE',
    'QUERY_STEP','VIEW','PROCEDURE','NOTEBOOK','PIPELINE','COPY_ACTIVITY','SOURCE','REFRESH_SCHEDULE','BOUNDARY'})
EDGE_KINDS=frozenset({'COMPUTED_FROM','FILTERED_BY','JOINED_VIA','COPIED_TO','DERIVED_IN_STEP','INTERACTS_WITH','CONTAINS'})
SOURCES=frozenset({'STATIC_DEFINITION','ENGINE_DEPENDENCY','MODEL_PROPOSAL','RUNTIME_OBSERVATION','QUERY_VERIFICATION','DECLARED_CONFIG'})


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def identity(estate,owner,kind,locator):return digest([estate,owner,kind,locator])


def timestamp(value):
    if not isinstance(value,str):raise ValueError('GRAPH_TIMESTAMP_REQUIRED')
    try:parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError:raise ValueError('GRAPH_TIMESTAMP_REQUIRED') from None
    if parsed.tzinfo is None:raise ValueError('GRAPH_TIMESTAMP_TIMEZONE_REQUIRED')
    return parsed.astimezone(timezone.utc).isoformat(timespec='microseconds').replace('+00:00','Z')


def text(value):return isinstance(value,str) and 0<len(value)<=2048


def provenance(value):
    if not isinstance(value,dict) or set(value)!={'source','source_id','definition_hash','observed_at','span'}:
        raise ValueError('GRAPH_PROVENANCE_REQUIRED')
    if value['source'] not in SOURCES or not text(value['source_id']):raise ValueError('GRAPH_PROVENANCE_SOURCE')
    if not isinstance(value['definition_hash'],str) or not re.fullmatch('[0-9a-f]{64}',value['definition_hash']):
        raise ValueError('GRAPH_DEFINITION_HASH_REQUIRED')
    timestamp(value['observed_at']);span=value['span']
    if not isinstance(span,dict):raise ValueError('GRAPH_SPAN_REQUIRED')
    if span.get('kind')=='TEXT':
        if set(span)!={'kind','start','end'} or type(span['start']) is not int or type(span['end']) is not int or not 0<=span['start']<span['end']:
            raise ValueError('GRAPH_TEXT_SPAN_REQUIRED')
    elif span.get('kind') in ('JSON_POINTER','METADATA'):
        if set(span)!={'kind','path'} or not isinstance(span['path'],str) or len(span['path'])>4096:
            raise ValueError('GRAPH_POINTER_REQUIRED')
    else:raise ValueError('GRAPH_SPAN_KIND')
    return value


def record(value,*,edge=False):
    required={'id','owner','kind','label','confidence','provenance','properties','unknown','verification'}
    if edge:required|={'source','target','base_confidence'}
    if not isinstance(value,dict) or set(value)!=required:raise ValueError('GRAPH_RECORD_SHAPE')
    if any(not text(value[k]) for k in ('id','owner','label')):raise ValueError('GRAPH_RECORD_IDENTITY')
    if value['kind'] not in (EDGE_KINDS if edge else NODE_KINDS):raise ValueError('GRAPH_KIND')
    if value['confidence'] not in CONFIDENCE:raise ValueError('GRAPH_CONFIDENCE')
    if not isinstance(value['properties'],dict) or len(canonical(value).encode())>65536:raise ValueError('GRAPH_RECORD_BOUND')
    provenance(value['provenance'])
    unknown=value['unknown'];verification=value['verification']
    if value['confidence']=='UNKNOWN':
        if not isinstance(unknown,dict) or set(unknown)!={'reason','remedy'} or any(not text(v) for v in unknown.values()):
            raise ValueError('GRAPH_UNKNOWN_NEEDS_REASON_AND_REMEDY')
    elif unknown is not None:raise ValueError('GRAPH_UNKNOWN_CONFIDENCE_DIFFERS')
    if not isinstance(verification,dict) or set(verification)!={'state','evidence_ids','scope_hash'}:
        raise ValueError('GRAPH_VERIFICATION_SHAPE')
    if verification['state'] not in ('NOT_VERIFIED','CURRENT','STALE') or not isinstance(verification['evidence_ids'],list):
        raise ValueError('GRAPH_VERIFICATION_STATE')
    if any(not text(v) for v in verification['evidence_ids']):raise ValueError('GRAPH_VERIFICATION_EVIDENCE')
    if value['confidence']=='VERIFIED':
        if (verification['state']!='CURRENT' or not verification['evidence_ids'] or
                not isinstance(verification['scope_hash'],str) or not re.fullmatch('[0-9a-f]{64}',verification['scope_hash'])):
            raise ValueError('GRAPH_VERIFIED_QUERY_PROOF_REQUIRED')
        if value['provenance']['source']!='QUERY_VERIFICATION':raise ValueError('GRAPH_VERIFIED_PRODUCER_REQUIRED')
    elif verification['state']=='CURRENT':raise ValueError('GRAPH_VERIFIED_CONFIDENCE_DIFFERS')
    if value['provenance']['source']=='MODEL_PROPOSAL' and value['confidence']!='INFERRED':
        raise ValueError('GRAPH_MODEL_CANNOT_VERIFY')
    if edge:
        if any(not text(value[k]) for k in ('source','target')):raise ValueError('GRAPH_ENDPOINT_REQUIRED')
        if value['base_confidence'] not in CONFIDENCE-{'VERIFIED'}:raise ValueError('GRAPH_BASE_CONFIDENCE')
    return copy.deepcopy(value)


def node(id,owner,kind,label,proof,*,properties=None,confidence='DECLARED',unknown=None):
    return record({'id':id,'owner':owner,'kind':kind,'label':label,'confidence':confidence,'provenance':proof,
        'properties':properties or {},'unknown':unknown,'verification':{'state':'NOT_VERIFIED','evidence_ids':[],'scope_hash':None}})


def edge(id,owner,kind,source,target,proof,*,properties=None,confidence='DECLARED',unknown=None):
    value=node(id,owner,'BOUNDARY',kind,proof,properties=properties,confidence=confidence,unknown=unknown)
    value.update(kind=kind,source=source,target=target,base_confidence=confidence)
    return record(value,edge=True)


def snapshot(value):
    if not isinstance(value,dict) or set(value)!={'estate','owner','definition_hash','observed_at','nodes','edges'}:
        raise ValueError('GRAPH_SNAPSHOT_SHAPE')
    if not text(value['estate']) or not text(value['owner']):raise ValueError('GRAPH_ESTATE_OWNER')
    if not re.fullmatch('[0-9a-f]{64}',value['definition_hash']):raise ValueError('GRAPH_SNAPSHOT_HASH')
    timestamp(value['observed_at'])
    if len(value['nodes'])>10000 or len(value['edges'])>30000:raise ValueError('GRAPH_SNAPSHOT_BOUND')
    for key in ('nodes','edges'):
        entries=value[key]
        if not isinstance(entries,list) or len({v['id'] for v in entries})!=len(entries):raise ValueError('GRAPH_DUPLICATE_IDENTITY')
        for item in entries:
            record(item,edge=key=='edges')
            if item['owner']!=value['owner']:raise ValueError('GRAPH_OWNER_DIFFERS')
    return copy.deepcopy(value)

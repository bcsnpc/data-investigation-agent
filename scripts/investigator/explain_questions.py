"""Timestamped calculation and change answers from an admitted graph slice.

No model, refresh, run, role assignment, arbitrary file read or SQL is exposed.
The public ask() function is also the future MCP entry point.
"""
from collections import deque
from datetime import datetime,timezone
from copy import deepcopy
import json
from pathlib import Path
import re

from .estate_graph_contract import timestamp,digest
from .essentials_intake import rank,normalize
from .clarification_grounding import label

VERSION='dia-graph-ask-v1'
KINDS=frozenset({'VISUAL','SLICER','MEASURE','CALCULATED_COLUMN','TABLE','COLUMN','QUERY_STEP','VIEW','PROCEDURE','NOTEBOOK','PIPELINE','COPY_ACTIVITY','SOURCE','BOUNDARY'})


def _held(question,reason,now,**extra):
    return {'version':VERSION,'status':'HELD','question':question,'recorded_at':now,'reason':reason,
            'coverage_gaps':[{'reason':reason}], 'provenance':[], **extra}


def _candidates(graph):
    if not graph.allowed or len(graph.allowed)>graph.max_nodes:
        raise ValueError('NAME_MATCH_ADMITTED_SLICE_BOUND')
    graph.gateway.graph_objects(graph.estate,sorted(graph.allowed),identity=graph.identity)
    records=graph.repository.records(graph.estate,at=graph.at,identities=sorted(graph.allowed),limit=graph.max_nodes)
    if records['truncated']:raise ValueError('NAME_MATCH_ADMITTED_SLICE_BOUND')
    return [{'id':node['id'],'kind':node['kind'],'names':[node['label']], 'record':node}
            for node in records['nodes'] if node['kind'] in KINDS]


def resolve(question,candidates,enrichment=(),subject=None):
    matches=[]
    words=' '+normalize(question)+' '
    for candidate in candidates:
        names=list(candidate['names'])
        for entry in enrichment:
            if (entry.get('subject')==candidate['id'] and not entry.get('stale_definition')
                    and entry.get('recording_class')!='RECORDED_STUB'):
                names+=entry.get('synonyms',[])
        for name in names:
            if ' '+normalize(name)+' ' in words:
                matches.extend(rank(name,[candidate],enrichment))
    by_id={}
    for row in matches:
        if row['id'] not in by_id or row['confidence']>by_id[row['id']]['confidence']:by_id[row['id']]=row
    ranked=sorted(by_id.values(),key=lambda r:(-r['confidence'],r['id']))
    if subject:
        selected=[c for c in candidates if c['id']==subject]
        if len(selected)!=1:return None,'SUBJECT_OUTSIDE_ADMITTED_SLICE',ranked
        if ranked and subject not in by_id:return None,'QUESTION_AND_BOUND_TARGET_DIFFER',ranked
        return selected[0],None,ranked
    if not ranked:return None,'QUESTION_SUBJECT_UNRESOLVED',ranked
    top=[r for r in ranked if r['confidence']==ranked[0]['confidence']]
    return (top[0],None,ranked) if len(top)==1 else (None,'TIED_CATALOG_CANDIDATES',ranked)


def _enrichment(node,entries):
    current_hash=node['provenance']['definition_hash']
    eligible=[r for r in entries if r.get('subject')==node['id'] and r.get('definition_hash')==current_hash
              and not r.get('stale_definition') and r.get('recording_class')!='RECORDED_STUB'
              and r.get('status') in ('INFERRED','HUMAN_CONFIRMED')]
    return max(eligible,key=lambda r:r['status']=='HUMAN_CONFIRMED') if eligible else None


def _value(probe):
    from .process_debugging import Probe,attest
    if not isinstance(probe,Probe) or probe.surface_report_binding!='VALUE_QUERY':return None
    checked=attest(probe)
    if checked.status!='OBSERVED':return None
    return {'value':deepcopy(checked.value),'value_state':checked.value_state,
            'evidence':checked.evidence,'execution_surface':checked.execution_surface,
            'surface_report':checked.surface_report,'surface_report_binding':checked.surface_report_binding,
            'qualification':'Observed value; not proof of business correctness or aligned snapshots.'}


def calculation(graph,subject,*,now,enrichment=(),value_lookup=None):
    path=graph.calculation_path(subject);nodes={n['id']:n for n in path['nodes']}
    queue=deque([subject]);seen=set();ordered=[]
    while queue:
        current=queue.popleft()
        if current in seen:continue
        seen.add(current);ordered.append(current)
        queue.extend(e['target'] for e in path['edges'] if e['source']==current and e['target'] in nodes)
    steps=[];gaps=deepcopy(path['stops']);lines=[]
    for identity in ordered:
        node=nodes[identity];definition=graph.definition_of(identity);entry=_enrichment(node,enrichment)
        explanation=entry.get('calculation_explanation') if entry else None
        qualifications=[]
        if entry and entry['status']=='INFERRED':qualifications.append('INFERRED explanation, not query-verified')
        if not explanation:
            gaps.append({'node':identity,'reason':'No current enriched plain-language calculation explanation'})
            explanation='The retained definition is available in the technical evidence.' if definition['definition'] is not None else 'No retained calculation definition is available.'
        if definition['collection_unavailable']:
            qualifications.append('Definition collection currently unavailable; retained version only')
        if definition['definition'] is None:gaps.append({'node':identity,'reason':'No retained definition text'})
        value=_value(value_lookup(identity)) if value_lookup else None
        if value_lookup and value is None:gaps.append({'node':identity,'reason':'No attested existing value for this step'})
        step={'node':identity,'name':node['label'],'kind':node['kind'],'explanation':explanation,
              'definition':definition,'enrichment':deepcopy(entry),'qualifications':qualifications,
              'value':value,'provenance':node['provenance']}
        steps.append(step)
        lines.append(node['label']+': '+('Inferred explanation: ' if qualifications and entry and entry['status']=='INFERRED' else '')+explanation)
        if entry:
            for note in entry.get('hidden_logic',[]):
                if isinstance(note,str):lines.append(('Inferred hidden-logic note: ' if entry['status']=='INFERRED' else 'Owner-confirmed hidden-logic note: ')+note)
    inferred=[deepcopy(e) for e in path['edges'] if e['confidence']=='INFERRED']
    if inferred:lines.append('This walk includes inferred links; they have not been query-verified.')
    if path['truncated']:gaps.append({'reason':'Admitted calculation path was truncated by its bound'})
    if gaps:
        lines.append('This is a partial explanation. '+ ' '.join(
            (nodes.get(gap.get('node'),{}).get('label','This path')+': '+gap['reason']+'.') for gap in gaps[:5]))
    return {'kind':'CALCULATION_EXPLANATION','status':'PARTIAL' if gaps else 'ANSWERED',
            'business_answer':'As of '+now+'. '+' '.join(lines),
            'technical_evidence':{'steps':steps,'links':path['edges'],'inferred_links':inferred,'as_of':graph.at},
            'coverage_gaps':gaps,'provenance':[n['provenance'] for n in path['nodes']]}


def change_history(graph,subject,*,now,history_port=None):
    from .adapters.explain_history import HistoryPort
    # The authority check and narrow node read precede every optional adapter.
    definition=graph.definition_of(subject)
    graph.gateway.graph_objects(graph.estate,[subject],identity=graph.identity)
    records=graph.repository.records(graph.estate,identities=[subject],at=graph.at,limit=1)
    if len(records['nodes'])!=1:raise ValueError('CHANGE_SUBJECT_NOT_PRESENT')
    node=records['nodes'][0];history=(history_port or HistoryPort()).read(node)
    observations=history['observations'];gaps=history['coverage_gaps'];lines=[]
    cutoff=timestamp(graph.at or now)
    if any(row['at']>cutoff for row in observations):
        gaps.append({'reason':'Events after the requested observation time were excluded'})
        observations=[row for row in observations if row['at']<=cutoff]
    for row in observations:
        detail='Item metadata records ' if row['source']=='ITEM_METADATA' else 'The '+row['source'].lower()+' record reports '
        change=(row['actor']+' at ' if row['actor'] else 'an update at ')+row['at']+'. '
        if row['actor'] is None:change+='The actor was not recorded. '
        lines.append(detail+change+('Recorded reason: '+row['reason']+'.' if row['reason'] else 'The reason was not recorded.'))
        if row['source']=='ITEM_METADATA':lines.append('Item modification does not identify which calculation changed.')
    if not observations:
        lines.append('Who changed this and when are not established by the retained evidence. The reason was not recorded.')
    return {'kind':'CHANGE_HISTORY','status':'PARTIAL' if gaps or not observations else 'ANSWERED',
            'business_answer':'As of '+now+'. '+' '.join(lines),
            'technical_evidence':{'subject':subject,'definition':definition,'observations':observations},
            'coverage_gaps':gaps,'provenance':[r['provenance'] for r in observations] or [node['provenance']]}


def ask(question,graph,*,subject=None,enrichment=(),history_port=None,value_lookup=None,now=None):
    """Future MCP API. Dependencies are bound code ports, never model arguments."""
    now=timestamp(now or datetime.now(timezone.utc).isoformat())
    if not isinstance(question,str) or not 1<=len(question)<=16000:
        return _held(question,'EXPLAIN_QUESTION_BOUND',now)
    if re.search(r'\b(who|changed|change history|modified)\b',question,re.I):kind='CHANGE_HISTORY'
    elif re.search(r'\b(calculated|calculation|included|definition|computed)\b',question,re.I):kind='CALCULATION_EXPLANATION'
    else:return _held(question,'EXPLAIN_QUESTION_UNRECOGNIZED',now)
    candidates=_candidates(graph)
    definitions={c['id']:c['record']['provenance']['definition_hash'] for c in candidates}
    enrichment=[r for r in enrichment if definitions.get(r.get('subject'))==r.get('definition_hash')
                and not r.get('stale_definition') and r.get('recording_class')!='RECORDED_STUB']
    target,reason,ranked=resolve(question,candidates,enrichment,subject)
    if reason:
        choices=[]
        for candidate in ranked:
            try:name=label(candidate['names'])
            except Exception:continue
            choices.append({'name':name,'node_id':candidate['id'],'confidence':candidate['confidence']})
        return _held(question,reason,now,candidates=choices)
    if kind=='CHANGE_HISTORY':result=change_history(graph,target['id'],now=now,history_port=history_port)
    else:result=calculation(graph,target['id'],now=now,enrichment=enrichment,value_lookup=value_lookup)
    return {'version':VERSION,'question':question,'subject':target['id'],'estate':graph.estate,
            'recorded_at':now,'evidence_class':'RETAINED_GRAPH_AND_EXPLICIT_OBSERVATIONS',
            'request_sha256':digest({'question':question,'subject':target['id'],'estate':graph.estate}),**result}


def load(path):
    value=json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if isinstance(value,dict) and value.get('version')=='dia-runner-estate-v1':value=value.get('explain')
    required={'version','estate','identity','allowed_objects'}
    if (not isinstance(value,dict) or not required<=set(value)<=required|{'subject','as_of','max_nodes','max_edges','max_bytes'}
            or value['version']!=VERSION or not isinstance(value['allowed_objects'],list)
            or not value['allowed_objects'] or len(value['allowed_objects'])>200
            or any(not isinstance(v,str) or not v for v in value['allowed_objects'])
            or not all(isinstance(value[k],str) and value[k] for k in ('estate','identity'))):
        raise ValueError('GRAPH_ASK_EXPLICIT_ADMISSION_CONFIGURATION_REQUIRED')
    if 'subject' in value and value['subject'] not in value['allowed_objects']:
        raise ValueError('GRAPH_ASK_SUBJECT_OUTSIDE_ADMITTED_SLICE')
    return value


def main(args):
    config=load(args.estate)
    from .shared_state import configured_state
    from .estate_graph_repository import GraphRepository
    from .estate_graph_api import GraphAPI
    from .live_gateway import current
    state=configured_state()
    if state is None:raise ValueError('GRAPH_ASK_CONFIGURED_SHARED_STATE_REQUIRED')
    graph=GraphAPI(GraphRepository(state),current(),identity=config['identity'],estate=config['estate'],
                   allowed_objects=config['allowed_objects'],at=config.get('as_of'),
                   **{k:config[k] for k in ('max_nodes','max_edges','max_bytes') if k in config})
    entries=[]
    try:
        from .enrichment import EnrichmentStore
        enrichment=EnrichmentStore(state)
        for candidate in _candidates(graph):
            row=enrichment.projection(config['estate'],candidate['id'],candidate['record']['provenance']['definition_hash'])
            if row is not None:entries.append(row)
    except ImportError:
        # The development image may predate enrichment. Missing enrichment is a
        # visible coverage gap, never a reason to invent an explanation.
        pass
    from .adapters.item_metadata_history import ItemMetadataHistory
    from .adapters.explain_history import HistoryPort
    retained_history=ItemMetadataHistory(state)
    history=HistoryPort(metadata=lambda node:retained_history.read(config['estate'],node))
    result=ask(args.question,graph,subject=config.get('subject'),enrichment=entries,history_port=history)
    print(json.dumps(result,sort_keys=True))
    return 1 if result['status']=='HELD' else 0

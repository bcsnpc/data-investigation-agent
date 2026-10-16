"""Governed pre-question value witnesses; definitions never supply numbers."""
import copy,json,re
from types import SimpleNamespace
from .onboarding import Conflict,digest
from . import reported_figure
from .process_tape import event

VERSION='claim-candidate-quantity-checks-v1'


def inventory(body,catalog):
    request=body.get('planning_request')or{}
    if request.get('kind')not in('FIGURE_VISUAL_MATCH','METRIC_VISUAL_CHECKS'):
        raise Conflict('Typed candidate-check planning request required')
    scope=body['claim']['settled'].get('scope')or{}
    if not scope.get('report_id')or not scope.get('page_id'):
        raise Conflict('Candidate quantities require a retained report and page')
    if body['claim']['settled'].get('time')or body['claim']['settled'].get('filters')or body.get('captured_context'):
        raise Conflict('Supplied candidate context is not faithfully compiled')
    rows=[]
    for group in request.get('groups',[]):
        model=next((m for m in catalog['models']if m['id']==group.get('model_id')),None)
        if model is None:raise Conflict('Candidate model is not retained')
        measure=next((m for m in model['measures']if m['id']==group.get('measure_id')),None)
        if measure is None:raise Conflict('Candidate metric is not retained')
        actual=[v for v in model.get('visuals',[])if v['report_id']==scope['report_id']
            and v.get('page_id')==scope['page_id']and measure['id']in v['measure_ids']]
        if set(group.get('target_ids',[]))!={v['target_id']for v in actual}:
            raise Conflict('Candidate visual inventory omits or adds a metric visual')
        for visual in sorted(actual,key=lambda v:v['target_id']):
            declaration=visual.get('declared_scopes',{}).get(measure['id'])
            if visual.get('unsupported')or visual.get('grouping_columns')!=[] or not declaration or declaration.get('state')!='COMPLETE':
                rows.append({'group':copy.deepcopy(group),'target_id':visual['target_id'],
                    'status':'UNSUPPORTED','reason':'No complete ungrouped declared quantity scope'})
                continue
            candidate={'model_id':model['id'],'measure_id':measure['id'],'target_id':visual['target_id'],
                'measure_name':measure['name'],'label':', '.join(visual.get('names',[]))or measure['name'],
                'mode':'UNGROUPED','scope':{'filters':[]},'declaration':copy.deepcopy(declaration)}
            rows.append({'group':copy.deepcopy(group),'target_id':visual['target_id'],
                'status':'PLANNED','candidate':candidate})
    if not rows:raise Conflict('No retained candidate quantity inventory')
    return rows


def verified_probe(workspace,candidate,probe):
    """Reconstruct from the sealed native row, then use the ordinary verifier."""
    from .adapters.form_candidate_values import plan,observation
    from .adapters.page_observations import verify_quantity
    from .receipt_integrity import verify
    model=workspace.store.get(candidate['model_id']);compiled=plan(model,candidate)
    identity=probe.get('receipt_id')or probe.get('id')
    with workspace.store.connect()as db:
        row=db.execute('SELECT status,result FROM flexible_diagnostics WHERE id=?',(identity,)).fetchone()
        seal=verify(db,'bounded_dax',identity)
    if not row or seal['state']!='SEALED':raise Conflict('Candidate read has no sealed native receipt')
    native={'id':identity,'status':row[0],'result':json.loads(row[1])}
    actual=observation(model,workspace.agent.config,compiled,native)
    if any(probe.get(k)!=actual[k]for k in('value','attestation','query_hash','execution_surface')):
        raise Conflict('Candidate producer changed the original quantity or attestation')
    enriched={**actual,'id':identity,'tool':'bounded_dax','query':compiled['query'],
        'read_address':compiled['read_address'],'cell_address':compiled['cell_address'],
        'receipt_seal':seal,'surface_report_binding':native['result'].get('surface_report_binding')}
    adapter=SimpleNamespace(store=workspace.store,model=model,config=workspace.agent.config)
    checked=verify_quantity(adapter,candidate,enriched)
    if checked['attestation'].get('consistency')!='MATCHED'or checked['attestation'].get('missing_required_fields'):
        raise Conflict('Candidate read lacks required query-bound attestation')
    return checked


def match(body,rows):
    """Label evidence plus stated-precision equality, never proximity/permutation."""
    observations=[];notes=[]
    for original in (body.get('planning_request')or{}).get('reported_observations',[]):
        value=original.get('value',original)
        structure=value.get('quantity_structure')or{}
        if value.get('role')=='OBSERVED'and structure.get('kind')=='MULTIPLE_QUANTITIES':
            statement=value.get('statement','')
            if isinstance(statement,dict):statement=statement.get('quote','')
            if re.search(r'\b(?:about|approximately|approx|around|roughly|nearly|circa)\b|~',statement,re.I):
                notes.append({'source_observation':copy.deepcopy(original),'status':'UNSUPPORTED_PRECISION',
                    'reason':'Plural approximate wording has no independently established precision per numeral.'})
                continue  # Unknown plural precision is not silently made exact.
            source=original.get('source',{})
            docs=[d for d in body.get('documents',[])if d.get('hash')==source.get('document_id')]
            if len(docs)!=1:
                notes.append({'source_observation':copy.deepcopy(original),'status':'SOURCE_UNAVAILABLE',
                    'reason':'Plural numeral source document is not retained exactly.'});continue
            text=docs[0]['request'].get('text','')
            for numeral in structure.get('numerals',[]):
                try:figure=reported_figure.from_candidates([numeral],text)
                except (ValueError,KeyError):continue
                observations.append({'value':dict(value,figure=figure),
                    'parent_observation':copy.deepcopy(original),'source':copy.deepcopy(numeral)})
        else:
            if value.get('figure',{}).get('state')=='UNSPECIFIED':
                notes.append({'source_observation':copy.deepcopy(original),'status':'UNSUPPORTED_QUANTITY_STATE',
                    'reason':'A qualitative statement, range or unknown precision is not one exact candidate value.'})
            observations.append(original)
    matches=notes;bindings=[]
    for original in observations:
        value=original.get('value',original);figure=value.get('figure')or{}
        if value.get('role')!='OBSERVED'or figure.get('state')not in('NUMBER','EMPTY'):continue
        phrase=value.get('metric_phrase')
        named=[m.get('phrase')for m in body['claim']['settled'].get('metric',[])if m.get('phrase')]
        if phrase is None and len(set(named))==1:phrase=named[0]
        hits=[]
        for row in rows:
            if row.get('status')!='OBSERVED':continue
            candidate=row['candidate'];labels={candidate['measure_name'].casefold(),candidate['label'].casefold()}
            if row['group'].get('metric_phrase'):labels.add(row['group']['metric_phrase'].casefold())
            label_match=isinstance(phrase,str)and phrase.casefold()in labels
            if reported_figure.label(figure,row['observation']['value'])=='REPRODUCED':
                hits.append({'group':row['group'],'target_id':candidate['target_id'],
                    'receipt_id':row['observation']['id'],'label_match':label_match})
        labelled=[h for h in hits if h['label_match']]
        chosen=labelled if phrase is not None else hits
        groups={digest(h['group']):h['group']for h in chosen}
        # Several visuals for the same metric do not manufacture an arbitrary
        # target. Different metrics tied at a value remain unresolved.
        resolved=len(groups)==1 and bool(chosen)
        matches.append({'source_observation':copy.deepcopy(original),'matches':chosen,
            'status':'UNIQUE_METRIC'if resolved else'AMBIGUOUS'if chosen else'NO_MATCH',
            'basis':'VALUE_AND_LABEL'if labelled else'UNIQUE_VALUE_ROUTE'if resolved else'UNRESOLVED',
            'precision_qualification':reported_figure.qualification(figure)})
        if resolved:
            group=next(iter(groups.values()))
            if group not in bindings:bindings.append(copy.deepcopy(group))
    return matches,bindings


def run(workspace,body,catalog):
    request=body.get('planning_request')or{}
    prior=body.get('candidate_checks')or{}
    if prior.get('request_hash')==digest(request) and prior.get('catalog_hash')==digest(catalog):
        return accept(prior,body,catalog,workspace.store,workspace=workspace)
    cap=min(12,workspace.dynamic_read_limit)
    previous=prior.get('diagnostic_reads',0)
    if type(previous)is not int or not 0<=previous<=cap:raise Conflict('Candidate diagnostic accounting is invalid')
    rows=inventory(body,catalog);result={'version':VERSION,'claim_id':body['id'],
        'request_hash':digest(request),'catalog_hash':digest(catalog),'rows':rows,
        'diagnostic_reads':previous,'accounting_session_id':'claim-candidates:'+body['id'],'candidate_bindings':[],'derived_facts':[],
        'snapshot_status':'SNAPSHOT_UNVERIFIED','limitations':[]}
    from .candidate_read_budget import scope
    with scope('claim-candidates:'+body['id'],previous,cap)as budget:
        for row in rows:
            if row['status']!='PLANNED':continue
            if budget['used']>=cap:
                row.update(status='UNAVAILABLE',reason='CANDIDATE_DIAGNOSTIC_CAP',failure_class='BUDGET');continue
            try:
                raw=workspace.form_candidate_reader(copy.deepcopy(row['candidate']))
                row['observation']=verified_probe(workspace,row['candidate'],raw)
                row['status']='OBSERVED'
            except Exception as exc:
                from .model_spend import SpendHold
                from .usage_governance import UsageHold
                if isinstance(exc,(SpendHold,UsageHold)):raise
                from .generation_policy import error_summary
                row.update(status='UNAVAILABLE',failure=error_summary(exc),failure_class='READ_OR_VALIDATION_FAILURE')
            finally:result['diagnostic_reads']=budget['used']
        result['matches'],result['candidate_bindings']=match(body,rows)
        result['status']='COMPLETE'if all(r['status']=='OBSERVED'for r in rows)else'PARTIAL'
        if result['status']!='COMPLETE':
            result['candidate_bindings']=[]
            result['limitations'].append('Incomplete candidate coverage cannot establish a unique value route.')
    result['hash']=digest(result)
    event('CONFIGURATION',{'claim_candidate_checks':copy.deepcopy(result)})
    return result


def accept(result,body,catalog,store,*,workspace=None):
    value=copy.deepcopy(result);sealed=value.pop('hash',None)
    if sealed!=digest(value)or value.get('version')!=VERSION or value.get('claim_id')!=body['id']or value.get('request_hash')!=digest(body.get('planning_request'))or value.get('catalog_hash')!=digest(catalog):
        raise Conflict('Candidate check record is not bound to current claim/context')
    planned=inventory(body,catalog)
    if len(planned)!=len(value['rows'])or any(a['group']!=b['group']or a['target_id']!=b['target_id']for a,b in zip(planned,value['rows'])):
        raise Conflict('Candidate check inventory differs')
    count=value.get('diagnostic_reads')
    if type(count)is not int or not 0<=count<=min(12,workspace.dynamic_read_limit if workspace else 12):
        raise Conflict('Candidate diagnostic accounting differs')
    for original,row in zip(planned,value['rows']):
        if original['status']=='UNSUPPORTED':
            if row!=original:raise Conflict('Unsupported candidate disposition changed')
        elif row.get('status')not in('OBSERVED','UNAVAILABLE')or row.get('candidate')!=original['candidate']:
            raise Conflict('Candidate disposition or plan changed')
    complete=all(r['status']=='OBSERVED'for r in value['rows'])
    if value.get('status')!=('COMPLETE'if complete else'PARTIAL') or count<sum(r['status']=='OBSERVED'for r in value['rows']):
        raise Conflict('Candidate completion or diagnostic conservation differs')
    if workspace is None:
        raise Conflict('Candidate receipt validation requires the installed read-only consumer')
    for row in value['rows']:
        if row['status']=='OBSERVED':
            if row.get('candidate')!=next(p['candidate'] for p in planned if p['target_id']==row['target_id'] and p['group']==row['group']):
                raise Conflict('Candidate plan differs from retained declaration')
            verified_probe(workspace,row['candidate'],row['observation'])
    matches,bindings=match(body,value['rows'])
    if value['status']!='COMPLETE':bindings=[]
    if value['matches']!=matches or value['candidate_bindings']!=bindings or value['derived_facts']!=[]:
        raise Conflict('Candidate value attribution differs from original receipts')
    return result


def install(workspace):
    workspace.claim_candidate_checks=lambda body,catalog:run(workspace,body,catalog)
    workspace.validate_claim_candidate_checks=lambda result,body,catalog:accept(result,body,catalog,workspace.store,workspace=workspace)

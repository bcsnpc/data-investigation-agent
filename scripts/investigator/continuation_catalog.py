"""Revalidate retained user authority against current metadata, never by names alone."""
import copy
from jsonschema import ValidationError
from .onboarding import Conflict,digest,encoded
from . import intake_confirmation,intake_extraction,ticket_protocol as protocol

def referents(catalog):
    return [{'model_id':m['id'],'target_id':v['target_id'],'report_id':v['report_id'],
             'page_id':v.get('page_id'),'measure_ids':copy.deepcopy(v.get('measure_ids',[])),
             'grouping_columns':copy.deepcopy(v['grouping_columns'])}
            for m in catalog['models'] for v in m.get('visuals',[])]

def identity(proposal, catalog_referents=None):
    if not proposal or proposal.get('action')!='PROPOSE':return None
    target=proposal.get('target_visual') or {}
    rows=[v for v in (catalog_referents or []) if v['model_id']==proposal.get('model_id')
          and v['target_id']==target.get('target_id')]
    if target and len(rows)!=1:raise Conflict('Earlier target page and cell identity are not established')
    return {'model':proposal.get('model_id'),'measure':proposal.get('measure_id'),
        'report':target.get('report_id') or (proposal.get('report_binding') or {}).get('report_id'),
        'visual':target.get('target_id'),'mode':target.get('mode'),
        'page':rows[0]['page_id'] if rows else None,
        'grouping_columns':rows[0]['grouping_columns'] if rows else [],
        'filters':copy.deepcopy(proposal.get('filters',[])),
        'dimensions':copy.deepcopy(proposal.get('dimension_ids',[])),
        'reported_figure':copy.deepcopy(proposal.get('reported_figure')),
        'definition_column':(proposal.get('definition_target') or {}).get('column_id')}

def confirmation(ticket,text,models):
    proof=intake_confirmation.build(ticket,text) if ticket.get('confirmed') else None
    if proof:
        # The old frame remains in history. Its selected stable identities are
        # validated against today's catalog before a new frame is persisted.
        proof['catalog_hash']=digest(models)
        intake_confirmation.values(proof,ticket=text,models=models)
    return proof

def resolve(source,ticket,catalog,configuration,request):
    from .question_intake import validate
    from . import question_kind
    raw=intake_extraction.retained_response(source)
    if raw is None:raise Conflict('No retained extraction exists for catalog re-resolution')
    payload={'text':source['text'],'models':catalog['models']}
    proof=confirmation(ticket,source['text'],catalog['models'])
    if proof:payload['_ticket_confirmation']=proof
    from .input_reference import from_input
    reference=from_input(request,source['text'],catalog['models'])
    if reference is not None:payload.update(_input_request=request,_ticket_reference=reference)
    from .ticket_inputs import model_subject
    if model_subject(request,source['text']):payload['_input_request']=request
    comparison=ticket.get('settled',{}).get('COMPARISON',{})
    if comparison.get('authority') in ('USER_SUPPLIED_INPUT','EXPLICIT_REQUEST_COMPARISON','ESTATE_COMPARISON_POLICY','CODE_ESTABLISHED_REQUEST_COMPARISON'):
        payload.update(_ticket_route=comparison['value'],_input_request=request,
                       _comparison_configuration=configuration)
        if comparison['authority']=='CODE_ESTABLISHED_REQUEST_COMPARISON':payload['_question_gate']=True
    candidate=intake_extraction.resolve(raw,payload);validate(candidate,payload);question_kind.intake_route(candidate)
    old=identity(source.get('proposal'),source.get('catalog_referents'))
    new=identity(candidate,referents(catalog))
    if old and old!=new:raise Conflict('Catalog target resolved to different stable objects')
    return candidate,raw

def rebind(controller,saved,source,catalog):
    """Append a new intake/pin and ticket revision; retain the original untouched."""
    from .ticket_inputs import active_request
    from .question_kind import UnimplementedRoute
    reason=None;route_refusal=False
    try:proposal,raw=resolve(source,saved['ticket'],catalog,controller.configuration,active_request(saved))
    except UnimplementedRoute as error:
        reason=str(error);proposal=None;raw=intake_extraction.retained_response(source);route_refusal=True
    except (ValueError,Conflict,ValidationError) as error:
        reason=str(error);proposal=None;raw=intake_extraction.retained_response(source)
    if raw is None:raise Conflict('No retained extraction exists for catalog re-resolution')
    resolved=bool(proposal and proposal.get('action')=='PROPOSE')
    if route_refusal:status='ROUTE_UNAVAILABLE'
    elif not proposal:status='TARGET_CONFIRMATION_REQUIRED'
    elif not resolved:status='CURRENT_CATALOG_UNRESOLVED'
    elif (source.get('proposal') or {}).get('action')=='PROPOSE':status='SAME_STABLE_OBJECTS'
    elif saved['ticket'].get('confirmed',{}).get('NUMBER'):status='USER_TARGET_REVALIDATED'
    else:status='CURRENT_TARGET_RESOLVED_NO_PRIOR_TARGET'
    key='catalog-re-resolution:'+saved['ticket']['id']+':'+str(saved['revision'])
    body=controller.workspace.intake._new_record({'request_key':key,'source_intake':source['id']},source['text'],catalog)
    body.update(status='PROPOSED' if resolved else 'NEEDS_INPUT',proposal=proposal,
        retained_extraction=copy.deepcopy(raw),provider_calls=0,source_intake=source['id'],
        catalog_revalidation={'previous_catalog_hash':source['catalog_hash'],'catalog_hash':digest(catalog),
            'previous_target':copy.deepcopy((source.get('proposal') or {}).get('target_visual')),
            'target':identity(proposal,referents(catalog)),
            'status':status,'reason':reason})
    if route_refusal:body.update(status='HELD',error='UNIMPLEMENTED_ROUTE',refusal_reason=reason)
    with controller.store.connect() as db:
        db.execute('INSERT INTO workspace_intakes VALUES(?,?,?,?)',(body['id'],key,encoded(body),digest(body)))
    def update(ticket):
        ticket.setdefault('catalog_continuation_history',[]).append({
            'source_intake':ticket.get('source_intake'),'choice_context':copy.deepcopy(ticket.get('choice_context')),
            'choice_values':copy.deepcopy(ticket.get('choice_values')),
            'confirmed':copy.deepcopy(ticket['confirmed']),'settled':copy.deepcopy(ticket['settled'])})
        ticket['source_intake']=body['id']
        ticket['history'].append({'from':ticket['state'],'to':ticket['state'],'actor':'AGENT',
            'detail':{'catalog_revalidation':copy.deepcopy(body['catalog_revalidation']),'intake_id':body['id']}})
        if route_refusal:
            ticket['questions']=[]
            return ticket
        if proposal:
            if ticket.get('choice_context'):ticket['choice_context']['catalog_hash']=digest(catalog['models'])
            return ticket
        # A changed/missing target is never silently replaced. Offer one current
        # target question, with complete stable semantics and visible names.
        prior_number=None
        if ticket['confirmed'].get('NUMBER'):
            proof=ticket['confirmed']['NUMBER'];prior_number=copy.deepcopy(ticket.get('choice_values',{}).get(proof['question_hash']+'/'+proof['choice_id']))
        previous_mode=(prior_number or {}).get('mode') or (source.get('proposal') or {}).get('target_visual',{}).get('mode')
        for field in ('NUMBER','REPORT_PAGE','REPORT_OR_SCREENSHOT'):
            ticket['confirmed'].pop(field,None);ticket['settled'].pop(field,None)
        ticket.pop('choice_context',None);ticket['choice_values']={}
        from .clarification_grounding import label
        choices=[]
        for model in catalog['models']:
            reports={r['id']:r for r in model.get('reports',[])}
            for visual in model.get('visuals',[]):
                if visual.get('unsupported'):continue
                mode=previous_mode or ('TOTAL' if visual['grouping_columns'] else 'UNGROUPED')
                if bool(visual['grouping_columns'])!=(mode!='UNGROUPED'):continue
                name=' / '.join([label([reports[visual['report_id']]['name']]),
                    *([label(visual.get('page_names',[]))] if visual.get('page_id') else []),
                    label(visual.get('names',[]))])
                if mode=='TOTAL':name+=' (total cell)'
                if mode=='KEYED':name+=' (the selected record or cell)'
                value={'target_id':visual['target_id'],'report_id':visual['report_id'],
                    'page_id':visual.get('page_id'),'mode':mode,
                    'figure_source':copy.deepcopy((prior_number or {}).get('figure_source'))}
                choices.append((name,value))
        if not choices:
            return protocol.ask(ticket,[{'id':'current-report','field':'REPORT_OR_SCREENSHOT',
                'question':'Which current report page shows the issue? Please share a screenshot.',
                'choices':[{'id':'screenshot','label':'Share a screenshot of the current report','highlight':None}]}],maximum=controller.configuration['max_clarifying_rounds'])
        if len(choices)>100:raise Conflict('Current target choices exceed the clarification bound')
        question={'id':'current-target','field':'NUMBER','question':'The earlier target is no longer established. Which current visual do you mean?',
            'choices':[{'id':digest(value),'label':name,'highlight':None} for name,value in choices]}
        values={digest(question)+'/'+choice['id']:value for choice,(_,value) in zip(question['choices'],choices)}
        return intake_confirmation.offer(ticket,[question],values,request_text=source['text'],models=catalog['models'],
                                         maximum=controller.configuration['max_clarifying_rounds'])
    return controller.tickets.update(saved['ticket']['id'],saved['revision'],update),body

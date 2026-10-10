"""Recomputable form authority; no model response may supply this proof.

The selected identities are user inputs, not invented ticket quotes. The
derived document labels its field sources, and retains the original wording.
"""
import copy
from jsonschema import Draft202012Validator
from . import ticket_protocol as protocol, form_intake
from .onboarding import digest, Conflict

VERSION = 'ticket-form-authority-v2'
HASH = {'type':'string', 'pattern':'^[0-9a-f]{64}$'}
PROOF = protocol.obj({'version':{'const':VERSION}, 'request_hash':HASH,
    'catalog_hash':HASH, 'document_hash':HASH, 'report_id':protocol.ID,
    'page_id':protocol.ID, 'target_id':form_intake.NULL_ID,'measure_id':protocol.ID,
    'mode':{'enum':['UNGROUPED','TOTAL','KEYED','MEASURE_AT_SCOPE']},
    'declared_scope':protocol.obj({'state':{'const':'COMPLETE'},'context_id':protocol.ID,
        'context_hash':HASH,'inventory_hash':HASH,'restrictions':{'type':'array','maxItems':32,
            'items':protocol.obj({'field_id':protocol.ID,'operator':{'const':'IN'},
                'values':{'type':'array','maxItems':1000}})}})})
PROOF['oneOf']=[{'properties':{'mode':{'const':'MEASURE_AT_SCOPE'},'target_id':{'type':'null'}}},
                {'properties':{'mode':{'enum':['UNGROUPED','TOTAL','KEYED']},'target_id':protocol.ID}}]
REPORT = protocol.obj({'resolution_kind':{'type':'string','enum':['USER_SUPPLIED_FORM']},
    'report_id':protocol.ID, 'source':{'type':'null'}, 'form':PROOF})
ROUTE_VERSION = 'ticket-comparison-form-v1'
ROUTE = protocol.obj({'version':{'const':ROUTE_VERSION},
    'route':{'enum':[*protocol.ROUTES,'DECLARED_SUBJECT']}, 'form':PROOF})


def description_route(proposal,request,configuration):
    if not proposal:return None
    route=proposal.get('ticket_route')
    if route:return route
    raw=proposal.get('extracted_ticket',{}).get('response')
    if raw is None:return None
    from .ticket_route import settlement
    return settlement(raw,document(request,configuration)['text'],configuration,code_gate=True)


def resolved_scope(request, models, configuration, description_proposal=None):
    """User picks stay facts; absence may be settled by validated description.

    A measure-only description is accepted only with the existing complete R1
    declaration proof. No candidate is selected by matching an expected value.
    """
    try:
        result=form_intake.resolve(request,models,configuration,
            measure_id=description_proposal.get('measure_id') if description_proposal else None)
    except ValueError as exc:
        if str(exc)=='Description measure is not bound by the selected visual':
            raise Conflict('Description conflicts with the selected form target') from exc
        raise
    if result['status']=='BOUND':return result['scope']
    if result['status']!='NEEDS_INPUT' or not description_proposal or description_proposal.get('action')!='PROPOSE':
        raise Conflict('Form still has unresolved consequential fields')
    p=description_proposal;binding=p.get('report_binding') or {};target=p.get('target_visual')
    report=request['report_id'] or binding.get('report_id')
    if not report or binding.get('report_id')!=report:
        raise Conflict('Description does not establish the selected report')
    model=next((m for m in models if m['id']==p['model_id'] and any(r['id']==report for r in m.get('reports',[]))),None)
    if model is None:raise Conflict('Description report/model binding is absent')
    page=request['page_id']
    if target:
        v=next((v for v in model.get('visuals',[]) if v['target_id']==target['target_id']),None)
        if v is None or v.get('unsupported') or v['report_id']!=report:
            raise Conflict('Description target is not an executable report binding')
        page=page or v['page_id']
        if page!=v['page_id']:raise Conflict('Description conflicts with the selected form page')
        if request['target_id'] and request['target_id']!=v['target_id']:
            raise Conflict('Description conflicts with the selected form target')
        mode=request['cell_mode'] or target['mode']
        if mode!=target['mode']:raise Conflict('Description conflicts with the selected form cell')
        target_id=v['target_id']
    else:
        if request['target_id']:raise Conflict('Picked visual requires its own bound description interpretation')
        proofs=[e for e in p.get('extracted_ticket',{}).get('resolution_evidence',[]) if e.get('resolution')=='COMPLETE_DECLARED_SCOPE_EQUIVALENCE']
        if len(proofs)!=1 or proofs[0]['measure_id']!=p['measure_id'] or not page:
            raise Conflict('Measure scope lacks a complete R1 definition proof')
        candidates=[v for v in model.get('visuals',[]) if v['target_id'] in proofs[0]['candidate_ids']]
        if len(candidates)!=len(proofs[0]['candidate_ids']) or any(v['report_id']!=report or v.get('page_id')!=page for v in candidates):
            raise Conflict('R1 proof does not belong to the selected report/page')
        declared=[v.get('declared_scopes',{}).get(p['measure_id'],{}) for v in candidates]
        if not declared or any(d.get('state')!='COMPLETE' or d.get('restrictions')!=[] or
                               not all(d.get(k) for k in ('context_id','context_hash','inventory_hash')) for d in declared):
            raise Conflict('R1 proof lacks complete retained scope declarations')
        if len({(d['context_id'],d['context_hash']) for d in declared})!=1:
            raise Conflict('R1 proof spans different retained contexts')
        target_id=None;mode='MEASURE_AT_SCOPE'
    route=request['comparison'] or (description_route(p,request,configuration) or {}).get('route')
    if not route:raise Conflict('Description does not establish a comparison or declared subject')
    figure=result.get('scope',{}).get('reported_figure') if result.get('scope') else None
    if request['value_seen'] is not None:
        # Parse the actual form field independently, using the same consumer.
        probe={**request,'target_id':target_id,'cell_mode':None if mode=='MEASURE_AT_SCOPE' else mode,
               'comparison':request['comparison'] or 'LOOKS_WRONG'}
        if target_id is None:raise Conflict('A displayed figure needs a cell binding or value-match receipts')
        parsed=form_intake.resolve(probe,models,configuration,measure_id=p['measure_id'])
        if parsed['status']!='BOUND':raise Conflict('Form figure scope is not bound')
        figure=parsed['scope']['reported_figure']
    else:figure=copy.deepcopy(p.get('reported_figure',{'state':'UNSPECIFIED'}))
    return {'model_id':p['model_id'],'measure_id':p['measure_id'],'report_id':report,'page_id':page,
            'target_id':target_id,'cell_mode':mode,'comparison':route,
            'filters':copy.deepcopy(p.get('filters',[])), 'reported_figure':figure}


def document(request, configuration):
    from .ticket_clarification import settings
    Draft202012Validator(form_intake.SCHEMA).validate(request)
    choices = settings(configuration)['comparison_choices']
    choice = next((c for c in choices if c['route'] == request['comparison']), None)
    pieces = []; parts = []; position = 0
    inputs = [('/description', 'Description supplied by user:', request['description']),
              ('/comparison', 'Comparison selected by user:', choice['label'] if choice else None),
              ('/value_seen', 'Value supplied by user:', request['value_seen'])]
    for pointer, label, value in inputs:
        if value is None or value == '': continue
        prefix = ('\n\n' if pieces else '') + label + '\n'
        pieces.append(prefix); position += len(prefix)
        start = position; pieces.append(value); position += len(value)
        parts.append({'pointer':pointer, 'start':start, 'end':position,
                      'quote':value})
    text = ''.join(pieces)
    if not text or len(text) > protocol.TEXT['maxLength']:
        raise ValueError('Form document is empty or exceeds the intake bound; nothing was cut')
    return {'text':text, 'parts':parts, 'source_input_hash':digest(request)}


def build(request, models, configuration, *, description_proposal=None):
    scope=resolved_scope(request,models,configuration,description_proposal)
    doc = document(request, configuration); text = doc['text']
    if request['description'] and description_proposal is None and request.get('description_resolution')!='FORM_SELECTIONS':
        raise Conflict('Form description has not been interpreted')
    if description_proposal is not None:
        if not request['description']:
            raise ValueError('A model proposal cannot be attached to a form with no description')
        if description_proposal.get('action') != 'PROPOSE':
            raise Conflict('Form description needs clarification')
        if any(description_proposal[k] != scope[k] for k in ('model_id','measure_id')):
            raise Conflict('Description conflicts with the selected form target')
        target = description_proposal.get('target_visual')
        if target and (target['target_id'] != scope['target_id'] or target['mode'] != scope['cell_mode']):
            raise Conflict('Description conflicts with the selected form cell')
        binding = description_proposal.get('report_binding')
        if binding and binding['report_id'] != scope['report_id']:
            raise Conflict('Description conflicts with the selected form report')
        route = description_route(description_proposal,request,configuration)
        if route and route['route'] != scope['comparison']:
            raise Conflict('Description conflicts with the selected form comparison')
        # Additional text restrictions must be handled explicitly; do not erase
        # them merely because a form bound a different scope successfully.
        if description_proposal.get('filters', []) != scope['filters']:
            raise Conflict('Description adds restrictions not settled by the form')
        if description_proposal.get('dimension_ids', []):
            raise Conflict('Description adds a breakdown not settled by the form')
        described=description_proposal.get('reported_figure',{'state':'UNSPECIFIED'})
        selected=scope['reported_figure']
        if described['state']!='UNSPECIFIED' and (
                described['state']!=selected['state'] or any(described.get(k)!=selected.get(k) for k in ('value','precision'))):
            raise Conflict('Description conflicts with the value or precision supplied in the form')
    model=next(m for m in models if m['id']==scope['model_id'])
    if scope['target_id'] is not None:
        candidate=next(v for v in model['visuals'] if v['target_id']==scope['target_id'])
    else:
        evidence=next(e for e in description_proposal['extracted_ticket']['resolution_evidence']
                      if e.get('resolution')=='COMPLETE_DECLARED_SCOPE_EQUIVALENCE')
        candidate=next(v for v in model['visuals'] if v['target_id'] in evidence['candidate_ids'])
    declared=candidate.get('declared_scopes',{}).get(scope['measure_id'])
    if not declared or declared.get('state')!='COMPLETE':
        raise Conflict('Selected visual scope is unavailable or incomplete in retained definitions')
    from .declared_reproduction import compose
    compose(declared['restrictions'])
    proof = {'version':VERSION, 'request_hash':digest(request),
        'catalog_hash':digest(models), 'document_hash':digest(text),
        'report_id':scope['report_id'], 'page_id':scope['page_id'],
        'target_id':scope['target_id'], 'mode':scope['cell_mode'],'measure_id':scope['measure_id'],
        'declared_scope':copy.deepcopy(declared)}
    Draft202012Validator(PROOF).validate(proof)
    figure = copy.deepcopy(scope['reported_figure'])
    if figure['state'] != 'UNSPECIFIED':
        part = next((p for p in doc['parts'] if p['pointer'] == '/value_seen'),None)
        if part:figure['source'] = {k:part[k] for k in ('start','end','quote')}
    from .reported_figure import validate as validate_figure
    validate_figure(figure,text)
    comparison = next((p for p in doc['parts'] if p['pointer'] == '/comparison'),None)
    kind = {'APPLICATION':'SOURCE_CORRECTNESS','STALE':'FRESHNESS',
            'LOOKS_WRONG':'FIGURE_DIFFERENCE','BUSINESS_MEANING':'BUSINESS_MEANING'}.get(scope['comparison'])
    subject = {'kind':kind, 'source':{k:comparison[k] for k in ('start','end','quote')}} if comparison else None
    if description_proposal is not None:
        subject = copy.deepcopy(description_proposal['question_kind'])
        kind=subject['kind']
        from .question_kind import validate as validate_subject
        validate_subject(subject,text)
        part=next(p for p in doc['parts'] if p['pointer']=='/description')
        if subject['source']['start']<part['start'] or subject['source']['end']>part['end']:
            raise Conflict('Description subject provenance must belong to the user description')
    proposal = {'action':'PROPOSE', 'model_id':scope['model_id'],
        'measure_id':scope['measure_id'], 'metric_quote':None, 'question':None,
        'ticket_shape':description_proposal['ticket_shape'] if description_proposal else 'BUSINESS_QUESTION' if kind == 'BUSINESS_MEANING' else 'MISMATCH_COMPLAINT',
        'comparison_mode':description_proposal['comparison_mode'] if description_proposal else 'NONE' if kind == 'BUSINESS_MEANING' else 'VERTICAL',
        'reported_figure':figure, 'filters':copy.deepcopy(scope['filters']),
        'dimension_ids':[], 'scope_quotes':[], 'question_kind':subject,
        'report_binding':{'resolution_kind':'USER_SUPPLIED_FORM','report_id':scope['report_id'],
                          'source':None,'form':copy.deepcopy(proof)},
        'ticket_route':{'version':ROUTE_VERSION,'route':scope['comparison'],'form':copy.deepcopy(proof)},
        'target_visual':({'target_id':scope['target_id'],'report_id':scope['report_id'],
            'measure_id':scope['measure_id'],'mode':scope['cell_mode'], 'source':None,
            'mode_source':None,'resolution':'RESOLVED','match_basis':{'form':copy.deepcopy(proof)}} if scope['target_id'] else None)}
    return {'document':doc, 'proposal':proposal, 'form':proof}


def validate_target(value, *, candidates, report_id, measure_id, ticket=None):
    proof = value.get('match_basis', {}).get('form')
    Draft202012Validator(PROOF).validate(proof)
    matches = [c for c in candidates if c['target_id'] == proof['target_id']
        and c['report_id'] == proof['report_id'] and c.get('page_id') == proof['page_id']]
    if len(matches) != 1 or matches[0].get('unsupported') or measure_id not in matches[0]['measure_ids'] or measure_id!=proof['measure_id']:
        raise ValueError('Form target is absent, ambiguous or not executable')
    candidate = matches[0]
    if report_id != proof['report_id'] or bool(candidate['grouping_columns']) != (proof['mode'] != 'UNGROUPED'):
        raise ValueError('Form target report or mode differs from its declared container')
    if ticket is not None and digest(ticket) != proof['document_hash']:
        raise ValueError('Form target belongs to a different input document')
    expected = {'target_id':proof['target_id'], 'report_id':report_id,
        'measure_id':measure_id, 'mode':proof['mode'], 'source':None, 'mode_source':None,
        'resolution':'RESOLVED', 'match_basis':{'form':proof}}
    if value != expected:
        raise ValueError('Form target differs from its sealed selection')
    return value

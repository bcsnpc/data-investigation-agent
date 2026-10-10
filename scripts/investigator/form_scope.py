"""Recomputable form authority; no model response may supply this proof.

The selected identities are user inputs, not invented ticket quotes. The
derived document labels its field sources, and retains the original wording.
"""
import copy
from jsonschema import Draft202012Validator
from . import ticket_protocol as protocol, form_intake
from .onboarding import digest, Conflict

VERSION = 'ticket-form-authority-v1'
HASH = {'type':'string', 'pattern':'^[0-9a-f]{64}$'}
PROOF = protocol.obj({'version':{'const':VERSION}, 'request_hash':HASH,
    'catalog_hash':HASH, 'document_hash':HASH, 'report_id':protocol.ID,
    'page_id':protocol.ID, 'target_id':protocol.ID,
    'mode':{'enum':['UNGROUPED','TOTAL','KEYED']}})
REPORT = protocol.obj({'resolution_kind':{'type':'string','enum':['USER_SUPPLIED_FORM']},
    'report_id':protocol.ID, 'source':{'type':'null'}, 'form':PROOF})
ROUTE_VERSION = 'ticket-comparison-form-v1'
ROUTE = protocol.obj({'version':{'const':ROUTE_VERSION},
    'route':{'enum':list(protocol.ROUTES)}, 'form':PROOF})


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
    result = form_intake.resolve(request, models, configuration)
    if result['status'] != 'BOUND':
        raise Conflict('Form still has unresolved consequential fields')
    doc = document(request, configuration); text = doc['text']; scope = result['scope']
    if request['description'] and description_proposal is None:
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
        route = description_proposal.get('ticket_route')
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
    proof = {'version':VERSION, 'request_hash':digest(request),
        'catalog_hash':digest(models), 'document_hash':digest(text),
        'report_id':scope['report_id'], 'page_id':scope['page_id'],
        'target_id':scope['target_id'], 'mode':scope['cell_mode']}
    Draft202012Validator(PROOF).validate(proof)
    figure = copy.deepcopy(scope['reported_figure'])
    if figure['state'] != 'UNSPECIFIED':
        part = next(p for p in doc['parts'] if p['pointer'] == '/value_seen')
        figure['source'] = {k:part[k] for k in ('start','end','quote')}
    comparison = next(p for p in doc['parts'] if p['pointer'] == '/comparison')
    kind = {'APPLICATION':'SOURCE_CORRECTNESS','STALE':'FRESHNESS',
            'LOOKS_WRONG':'FIGURE_DIFFERENCE','BUSINESS_MEANING':'BUSINESS_MEANING'}[scope['comparison']]
    subject = {'kind':kind, 'source':{k:comparison[k] for k in ('start','end','quote')}}
    if description_proposal is not None:
        subject = copy.deepcopy(description_proposal['question_kind'])
    proposal = {'action':'PROPOSE', 'model_id':scope['model_id'],
        'measure_id':scope['measure_id'], 'metric_quote':None, 'question':None,
        'ticket_shape':'BUSINESS_QUESTION' if kind == 'BUSINESS_MEANING' else 'MISMATCH_COMPLAINT',
        'comparison_mode':'NONE' if kind == 'BUSINESS_MEANING' else 'VERTICAL',
        'reported_figure':figure, 'filters':copy.deepcopy(scope['filters']),
        'dimension_ids':[], 'scope_quotes':[], 'question_kind':subject,
        'report_binding':{'resolution_kind':'USER_SUPPLIED_FORM','report_id':scope['report_id'],
                          'source':None,'form':copy.deepcopy(proof)},
        'ticket_route':{'version':ROUTE_VERSION,'route':scope['comparison'],'form':copy.deepcopy(proof)},
        'target_visual':{'target_id':scope['target_id'],'report_id':scope['report_id'],
            'measure_id':scope['measure_id'],'mode':scope['cell_mode'], 'source':None,
            'mode_source':None,'resolution':'RESOLVED','match_basis':{'form':copy.deepcopy(proof)}}}
    return {'document':doc, 'proposal':proposal, 'form':proof}


def validate_target(value, *, candidates, report_id, measure_id, ticket=None):
    proof = value.get('match_basis', {}).get('form')
    Draft202012Validator(PROOF).validate(proof)
    matches = [c for c in candidates if c['target_id'] == proof['target_id']
        and c['report_id'] == proof['report_id'] and c.get('page_id') == proof['page_id']]
    if len(matches) != 1 or matches[0].get('unsupported') or matches[0]['measure_ids'] != [measure_id]:
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

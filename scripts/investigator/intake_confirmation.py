"""Server-retained user choices are authority, never model-generated IDs.

Workspace integration must load this proof from its sealed ticket revision;
the provider never receives it and an intake response cannot supply it.
Only target/figure, report/page and comparison choices are expressible.
"""
import copy
from jsonschema import Draft202012Validator
from . import ticket_protocol as protocol, reported_figure
from .onboarding import digest

VERSION='ticket-confirmation-v1'
NUMBER=protocol.obj({'target_id':protocol.ID,
    'mode':{'enum':['UNGROUPED','KEYED','TOTAL']},
    'figure_source':{'anyOf':[{'type':'null'},reported_figure.SPAN_SCHEMA]}})
REPORT_PAGE=protocol.obj({'report_id':protocol.ID,
    'page_id':{'anyOf':[{'type':'null'},protocol.ID]}})
COMPARISON=protocol.obj({'route':{'enum':list(protocol.ROUTES)}})
VALUES={'NUMBER':NUMBER,'REPORT_PAGE':REPORT_PAGE,'COMPARISON':COMPARISON}
SCHEMA=protocol.obj({'version':{'const':VERSION},'ticket_id':protocol.ID,
    'request_hash':{'type':'string','pattern':'^[0-9a-f]{64}$'},
    'catalog_hash':{'type':'string','pattern':'^[0-9a-f]{64}$'},
    'fields':{'type':'object','additionalProperties':False,'minProperties':1,
        'properties':{field:protocol.obj({'proof':protocol.obj({
            'question_id':protocol.ID,'choice_id':protocol.ID,
            'authority':{'const':'USER_CONFIRMED'},'question_hash':protocol.ID}),
            'value':spec}) for field,spec in VALUES.items()}}})


def authority_hash(ticket):
    """State/history may advance; a changed consequential decision may not."""
    return digest({k:ticket.get(k) for k in
        ('source_intake','choice_context','choice_values','confirmed','settled')})


def offer(ticket, questions, choice_values, *, request_text, models, maximum=2):
    """Retain choice semantics before showing the question, not at reply time."""
    protocol.validate_questions(questions)
    expected={digest(q)+'/'+c['id'] for q in questions for c in q['choices']}
    if set(choice_values)!=expected:raise ValueError('Every offered choice requires exactly one retained value')
    for q in questions:
        for c in q['choices']:
            proof=protocol.confirmed([q],[{'question_id':q['id'],'choice_id':c['id']}])[q['field']]
            values({'version':VERSION,'ticket_id':ticket['id'],'request_hash':digest(request_text),'catalog_hash':digest(models),
                'fields':{q['field']:{'proof':proof,'value':choice_values[digest(q)+'/'+c['id']]}}},
                ticket=request_text,models=models)
    result=protocol.ask(ticket,questions,maximum=maximum)
    context={'request_hash':digest(request_text),'catalog_hash':digest(models)}
    if result.get('choice_context',context)!=context:
        raise ValueError('Retained choice context changed; open a new question frame')
    result['choice_context']=context
    retained=result.setdefault('choice_values',{})
    for key,value in choice_values.items():
        if key in retained and retained[key]!=value:raise ValueError('A retained choice cannot change meaning')
        retained[key]=copy.deepcopy(value)
    return result


def build(ticket, request_text):
    """Internal controller port, after protocol.answer; not a client payload."""
    if not ticket['confirmed']:raise ValueError('No user confirmation exists')
    result={'version':VERSION,'ticket_id':ticket['id'],
            'request_hash':digest(request_text),'fields':{}}
    context=ticket.get('choice_context')
    if context is None or context['request_hash']!=result['request_hash']:
        raise ValueError('Confirmation has no matching retained request context')
    result['catalog_hash']=context['catalog_hash']
    # Recover the retained question/answer exchange from history. Never ask the
    # caller to supply a question hash that can masquerade as a recorded reply.
    questions={}
    for entry in ticket['history']:
        for question in entry['detail'].get('questions',[]):
            questions[digest(question)]=question
    for field,proof in ticket['confirmed'].items():
        question=questions.get(proof['question_hash'])
        if question is None:raise ValueError('Confirmation has no retained question')
        expected=protocol.confirmed([question],[{'question_id':proof['question_id'],
                                                'choice_id':proof['choice_id']}])[field]
        if proof!=expected:raise ValueError('Confirmation differs from its retained question')
        answer={'question_id':proof['question_id'],'choice_id':proof['choice_id']}
        if not any(e['actor']=='USER' and answer in e['detail'].get('answers',[])
                   for e in ticket['history']):
            raise ValueError('Confirmation has no recorded user answer')
        key=proof['question_hash']+'/'+proof['choice_id']
        if key not in ticket.get('choice_values',{}):raise ValueError('Confirmation has no retained choice value')
        value=copy.deepcopy(ticket['choice_values'][key])
        Draft202012Validator(VALUES[field]).validate(value)
        result['fields'][field]={'proof':copy.deepcopy(proof),'value':value}
    return result


def values(confirmation, *, ticket, models):
    """Revalidate the server proof's shape and every selected catalog identity."""
    Draft202012Validator(SCHEMA).validate(confirmation)
    if confirmation['request_hash']!=digest(ticket):raise ValueError('Confirmation request changed')
    if confirmation['catalog_hash']!=digest(models):raise ValueError('Confirmation catalog changed')
    result={f:copy.deepcopy(v['value']) for f,v in confirmation['fields'].items()}
    report=result.get('REPORT_PAGE')
    if report:
        eligible=[m for m in models if any(r['id']==report['report_id'] for r in m.get('reports',[]))]
        if len(eligible)!=1:raise ValueError('Confirmed report is absent or ambiguously bound')
        if report['page_id'] is not None and not any(v['report_id']==report['report_id'] and
                v.get('page_id')==report['page_id'] for v in eligible[0].get('visuals',[])):
            raise ValueError('Confirmed page is not retained in the confirmed report')
    number=result.get('NUMBER')
    if number:
        candidates=[(m,v) for m in models for v in m.get('visuals',[]) if v['target_id']==number['target_id']]
        if len(candidates)!=1:raise ValueError('Confirmed visual is absent or ambiguous')
        _,visual=candidates[0]
        if visual.get('unsupported'):raise ValueError('Confirmed visual is unsupported: '+visual['unsupported'])
        if bool(visual['grouping_columns'])!=(number['mode']!='UNGROUPED'):
            raise ValueError('Confirmed cell mode contradicts the visual')
        if report and (visual['report_id']!=report['report_id'] or
                report['page_id'] is not None and visual.get('page_id')!=report['page_id']):
            raise ValueError('Confirmed number is outside the confirmed report/page')
        if number['figure_source'] is not None:
            reported_figure.span(number['figure_source'],ticket)
    return result

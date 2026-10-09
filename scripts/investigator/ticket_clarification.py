"""Build choice batches from retained evidence, never from acceptance goldens.

This metadata-only planner does not evaluate values or select a target by a
value match. Unsupported cell addressing remains explicit rather than being
replaced with a total. The controller must persist the offer before a reply.
"""
import copy
from jsonschema import Draft202012Validator
from . import ticket_protocol as protocol, intake_confirmation, intake_extraction
from .onboarding import digest

DEFAULTS={'comparison_choices':[{'route':route,'label':label} for route,label in (
    ('APPLICATION','The application'),('STALE','The information seems stale'),
    ('LOOKS_WRONG','It looks wrong'),('OTHER_REPORT','Another report'),
    ('BUSINESS_MEANING','The business meaning or rule'))],
    'default_route':'ASK','must_confirm':[], 'max_clarifying_rounds':2,
    'screenshot_retention_days':30,'screenshot_redaction':'ESTATE_RECORDING_POLICY',
    'vocabulary_aliases':[]}


def settings(value=None):
    result=copy.deepcopy(DEFAULTS if value is None else value)
    Draft202012Validator(protocol.INTAKE).validate(result)
    routes=[c['route'] for c in result['comparison_choices']]
    if len(routes)!=len(set(routes)):raise ValueError('Duplicate comparison route')
    if result['default_route']!='ASK' and result['default_route'] not in routes:
        raise ValueError('Default comparison is not offered')
    return result


def batch(ticket, source, payload, configuration=None):
    """Return an exhaustive bounded offer, or a named reason it cannot be made.

    No absent numeral is manufactured. Each displayed figure choice binds an
    exact occurrence of a model-retained quotation in the original request.
    Unknown precision remains a refusal in the original consumer.
    """
    config=settings(configuration)
    raw=intake_extraction.retained_response(source)
    if raw is None:return {'questions':[],'values':{},'blocked':'NO_RETAINED_EXTRACTION'}
    try:extraction=intake_extraction.spans(raw,payload['text'],figure_occurrences=True)
    except ValueError as exc:return {'questions':[],'values':{},'blocked':str(exc)}
    questions=[];values={}
    def add(field,label,choices):
        if not choices:raise ValueError('No faithful choices for '+field)
        if len(choices)>100:raise ValueError('Clarification choice bound exceeded for '+field)
        question={'id':field.lower(),'field':field,'question':label,
            'choices':[{'id':digest(value),'label':name,'highlight':None} for name,value in choices]}
        protocol.validate_questions([question])
        for choice,(_,value) in zip(question['choices'],choices):
            values[digest(question)+'/'+choice['id']]=copy.deepcopy(value)
        questions.append(question)
    try:
        if 'REPORT_PAGE' not in ticket['settled']:
            choices=[]
            for model in payload['models']:
                for report in model.get('reports',[]):
                    pages={v.get('page_id') for v in model.get('visuals',[]) if v['report_id']==report['id']}
                    for page in sorted(pages,key=lambda p:p or ''):
                        label=report['name']+(' / '+page if page else '')
                        choices.append((label,{'report_id':report['id'],'page_id':page}))
            add('REPORT_PAGE','Which report or page are you asking about?',choices)
        if 'NUMBER' not in ticket['settled']:
            figures=[]
            for item in extraction['figures']:
                if item['quote'] not in figures:figures.append(item['quote'])
            figures=figures or [None]
            choices=[]
            for model in payload['models']:
                for visual in model.get('visuals',[]):
                    if visual.get('unsupported'):continue
                    # KEYED requires a real key address. Until that input is
                    # representable, do not replace it with an ungrouped/total.
                    mode='TOTAL' if visual['grouping_columns'] else 'UNGROUPED'
                    name=' / '.join(visual.get('names') or [visual['target_id']])
                    if mode=='TOTAL':name+=' (total cell only; keyed cells not offered)'
                    for figure in figures:
                        label=name+(' — '+repr(figure['quote'])+f" at {figure['start']}:{figure['end']}" if figure else ' — no figure supplied')
                        choices.append((label,{'target_id':visual['target_id'],'mode':mode,'figure_source':figure}))
            add('NUMBER','Which displayed number should we investigate?',choices)
        if 'COMPARISON' not in ticket['settled']:
            add('COMPARISON','What are you comparing against?',[
                (c['label'],{'route':c['route']}) for c in config['comparison_choices']])
        if not questions:return {'questions':[],'values':{},'blocked':None}
        # Validate every offered meaning against this catalog, before it can
        # be displayed or recorded as a user's confirmation.
        intake_confirmation.offer(ticket,questions,values,request_text=payload['text'],
            models=payload['models'],maximum=config['max_clarifying_rounds'])
        return {'questions':questions,'values':values,'blocked':None}
    except ValueError as exc:return {'questions':[],'values':{},'blocked':str(exc)}

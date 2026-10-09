"""Build choice batches from retained evidence, never from acceptance goldens.

This metadata-only planner does not evaluate values or select a target by a
value match. Unsupported cell addressing remains explicit rather than being
replaced with a total. The controller must persist the offer before a reply.
"""
import copy
from jsonschema import Draft202012Validator, ValidationError
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


def visual_candidates(ticket, extraction, payload):
    """Narrow offers only with declared containers and unique metadata names.

    This does not select a visual or evaluate a quantity. Ambiguous names leave
    all their candidates visible; a value match never supplies authority.
    """
    pairs=[(m,v) for m in payload['models'] for v in m.get('visuals',[])]
    if ticket['confirmed']:
        selected=intake_confirmation.values(intake_confirmation.build(ticket,payload['text']),
                                            ticket=payload['text'],models=payload['models'])
        report=selected.get('REPORT_PAGE')
        if report:
            pairs=[(m,v) for m,v in pairs if v['report_id']==report['report_id'] and
                   (report['page_id'] is None or v.get('page_id')==report['page_id'])]
    named=intake_extraction.literal_reports(extraction,payload['text'],payload['models'])
    if named:
        names={i['quote']['quote'] for i in named}
        report_ids={r['id'] for m in payload['models'] for r in m.get('reports',[]) if r['name'] in names}
        pairs=[(m,v) for m,v in pairs if v['report_id'] in report_ids]
    measures=[]
    eligible_models={m['id'] for m,v in pairs}
    candidates=[{**metric,'binding_id':digest([m['id'],metric['id']])} for m in payload['models']
                if m['id'] in eligible_models for metric in m['measures']]
    for mention in extraction['measures']:
        if not intake_extraction.primary_fact(mention,extraction):continue
        try:chosen=intake_extraction.match(mention['quote']['quote'],candidates,'binding_id')
        except ValueError:continue
        measures.append(chosen['id'])
    if measures:pairs=[(m,v) for m,v in pairs if set(v['measure_ids'])&set(measures)]
    return pairs


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
    except ValidationError:return {'questions':[],'values':{},'blocked':'RETAINED_EXTRACTION_SCHEMA_INVALID'}
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
        # The number choice includes its native report/page container. Asking
        # for both separately adds no evidence unless estate policy requires it.
        if 'REPORT_PAGE' not in ticket['settled'] and (
                'NUMBER' in ticket['settled'] or 'REPORT_PAGE' in config['must_confirm']):
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
            for model,visual in visual_candidates(ticket,extraction,payload):
                if visual.get('unsupported'):continue
                modes=[('UNGROUPED','')] if not visual['grouping_columns'] else [('TOTAL',' (total cell)')]
                if visual['grouping_columns']:
                    # Use the exact scope producer, not a second key parser.
                    # A value mention alone is never a keyed address.
                    filters,_,_,pending=intake_extraction.selections(extraction,model)
                    from .declared_reproduction import compose
                    restrictions=compose([{'field_id':f['column_id'],'operator':'IN','values':f['values']} for f in filters])
                    singleton={f['field_id']:f['values'][0] for f in restrictions if len(f['values'])==1}
                    if not pending and set(visual['grouping_columns'])<=set(singleton):
                        keys=', '.join(next(c['name'] for c in model['columns'] if c['column_id']==key)+'='+repr(singleton[key])
                                       for key in visual['grouping_columns'])
                        modes.insert(0,('KEYED',' (cell: '+keys+')'))
                report=next(r for r in model['reports'] if r['id']==visual['report_id'])
                page=' / '.join(visual.get('page_names') or [])
                name=' / '.join([report['name'],*([page] if page else []),
                                ' / '.join(visual.get('names') or [visual['target_id']])])
                for mode,suffix in modes:
                    for figure in figures:
                        label=name+suffix+(' — '+repr(figure['quote'])+f" at {figure['start']}:{figure['end']}" if figure else ' — no figure supplied')
                        choices.append((label,{'target_id':visual['target_id'],'mode':mode,'figure_source':figure,
                                              'report_id':visual['report_id'],'page_id':visual.get('page_id')}))
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

"""Question eligibility from retained ticket facts, never oracle answers.

This gate does not evaluate estate values or repair the model's extraction.
It resolves through the original consumer, or records why it cannot ask.
"""
import copy
import re
from jsonschema import ValidationError
from . import intake_extraction, intake_confirmation, ticket_protocol as protocol
from .onboarding import digest
from .visual_target import TargetUnresolved


def scope_block(source,payload):
    """Same predicate admission rule for form and free-text questions."""
    raw=intake_extraction.retained_response(source)
    if raw is None:return None
    try:extraction=intake_extraction.spans(raw,payload['text'],figure_occurrences=True)
    except (ValueError,ValidationError):return None
    ask=extraction['primary']['quote']
    if re.search(r'\b(?:unidentified|unknown|unsupported)\b[^.!?\n]*\b(?:filter|slicer)\b',ask,re.I):
        return 'UNSUPPORTED_FILTER: declared predicate is not established'
    # Ticket-relative dates require typed exact endpoints. A visual choice
    # cannot supply those endpoints or turn an untyped field into a date.
    for selection in extraction['selections']:
        if selection['role']=='PRIMARY' and re.search(
                r'\b(?:last|next|past)\s+(?:\d+|[a-z]+)\s+(?:days?|weeks?|months?|years?)\b',
                selection['quote']['quote'],re.I):
            return 'RELATIVE_DATE_UNSUPPORTED: exact typed endpoints are not established'
    for selection in extraction['selections']:
        if selection['role']!='PRIMARY' or selection['column'] is None:continue
        columns=[c for model in payload['models'] for c in model['columns']]
        try:intake_extraction.match(selection['column']['quote'],columns,'column_id')
        except ValueError as exc:
            if getattr(exc,'resolution_evidence',{}).get('resolution')=='UNRESOLVED':
                return 'COLUMN_UNRESOLVED: '+str(exc)
    return None


def prepare(ticket, source, payload, configuration, *, comparison_conflict=False):
    result=copy.deepcopy(ticket);events=[]
    raw=intake_extraction.retained_response(source)
    if raw is None:return result,events,None
    try:intake_extraction.spans(raw,payload['text'],figure_occurrences=True)
    except (ValueError,ValidationError):return result,events,None
    blocked=scope_block(source,payload)
    if blocked:return result,events,blocked
    # Policy confirmation is not evidence of ambiguity. A complete validated
    # referent or an explicit request settles its question without another ask.
    from .ticket_route import settlement
    config=copy.deepcopy(configuration);config['must_confirm']=[]
    if 'COMPARISON' not in result['settled'] and not comparison_conflict:
        try:route=settlement(raw,payload['text'],config,code_gate=True)
        except (ValueError,ValidationError):route=None
        if route is not None:
            result['settled']['COMPARISON']={'authority':
                'ESTATE_COMPARISON_POLICY' if route['version']=='ticket-comparison-policy-v1'
                else 'CODE_ESTABLISHED_REQUEST_COMPARISON','value':route}
            events.append({'field':'COMPARISON','reason':'COMPARISON_ESTABLISHED_FROM_REQUEST'})
    if result['confirmed']:
        payload=copy.deepcopy(payload)
        payload['_ticket_confirmation']=intake_confirmation.build(result,payload['text'])
    try:
        proposal=intake_extraction.resolve(raw,payload)
        result=protocol.settle_from_intake(result,proposal,payload)
        for field in ('NUMBER','REPORT_PAGE'):
            events.append({'field':field,'reason':'VALIDATED_REFERENT_AND_SCOPE'})
        return result,events,None
    except TargetUnresolved:
        return result,events,None
    except (ValueError,ValidationError) as exc:
        from .reported_figure import AmbiguousFigure, UnavailablePrecision
        if isinstance(exc,AmbiguousFigure):return result,events,None
        if isinstance(exc,UnavailablePrecision):
            return result,events,'REPORTED_PRECISION_UNAVAILABLE: '+str(exc)
        # No user choice can make a nonexistent column, unsupported restriction
        # or historical comparison executable. Keep its actual refusal visible.
        message=str(exc)
        if raw['kind']=='TEMPORAL_COMPARISON':
            return result,events,'CHANGE_OVER_TIME_UNSUPPORTED'
        if any(term in message.casefold() for term in
               ('unsupported','column','relative date','relative_date','not implemented')):
            return result,events,'UNSUPPORTED_FILTER_OR_COLUMN: '+message
        return result,events,None


def offer(ticket, source, payload, configuration, proposed):
    """Replace a combined target/figure offer with exactly one figure question."""
    raw=intake_extraction.retained_response(source)
    if raw is None:return proposed
    extraction=intake_extraction.spans(raw,payload['text'],figure_occurrences=True)
    if 'REPORT_PAGE' not in ticket['settled'] and not payload.get('_ticket_reference'):
        named=intake_extraction.literal_reports(extraction,payload['text'],payload['models'])
        if not named and 'REPORT_OR_SCREENSHOT' not in ticket['confirmed']:
            if ticket['rounds']:
                return {'questions':[],'values':{},'blocked':'TARGET_UNRESOLVED: report unidentified after clarification'}
            choices=[]
            for model in payload['models']:
                for report in model.get('reports',[]):
                    for page in sorted({v.get('page_id') for v in model.get('visuals',[])
                                        if v['report_id']==report['id']},key=lambda p:p or ''):
                        value={'report_id':report['id'],'page_id':page}
                        choices.append(({'id':digest(value),'label':report['name']+(' / '+page if page else ''),
                                         'highlight':None},value))
            if not choices:return {'questions':[],'values':{},'blocked':'TARGET_UNRESOLVED: no retained report candidates'}
            q={'id':'report-or-screenshot','field':'REPORT_OR_SCREENSHOT',
               'question':'Which report is this? You may also supply its link or a screenshot.',
               'choices':[c for c,_ in choices]}
            values={digest(q)+'/'+c['id']:v for c,v in choices}
            intake_confirmation.offer(ticket,[q],values,request_text=payload['text'],
                models=payload['models'],maximum=configuration['max_clarifying_rounds'])
            return {'questions':[q],'values':values,'blocked':None}
    figures=[]
    for item in extraction['figures']:
        if item['quote'] not in figures:figures.append(item['quote'])
    if len(figures)>1 and 'FIGURE' not in ticket['confirmed']:
        if ticket['rounds']:
            return {'questions':[],'values':{},'blocked':'MULTIPLE_REPORTED_FIGURES_UNRESOLVED'}
        q={'id':'figure','field':'FIGURE','question':'Which figure is the reported result?',
           'choices':[{'id':digest(f),'label':f['quote']+f" at {f['start']}:{f['end']}",
                       'highlight':None} for f in figures]}
        values={digest(q)+'/'+c['id']:{'figure_source':copy.deepcopy(f)}
                for c,f in zip(q['choices'],figures)}
        # Figure ambiguity is clarified first, once. Other questions cannot
        # depend on a figure the user has not identified yet.
        questions=[q]
        intake_confirmation.offer(ticket,questions,values,request_text=payload['text'],
                                  models=payload['models'],maximum=configuration['max_clarifying_rounds'])
        return {'questions':questions,'values':values,'blocked':None}
    return proposed

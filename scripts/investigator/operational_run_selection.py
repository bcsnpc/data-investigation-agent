"""Explicit run references and stated timestamp precision, never latest fallback."""
import calendar,copy,re
from datetime import datetime,timezone
from .reported_figure import span
from .estate_graph_contract import canonical

STAMP=re.compile(r'(?<![0-9])(?P<day>[0-9]{4}-[0-9]{2}-[0-9]{2})(?:T|[ ]+(?:at[ ]+)?)(?P<clock>[0-9]{2}:[0-9]{2}:[0-9]{2})(?P<fraction>\.[0-9]{1,9})?[ ]*(?P<zone>Z|UTC|[+-][0-9]{2}:[0-9]{2})(?![0-9])',re.I)
DATE=re.compile(r'(?<![0-9])[0-9]{4}-[0-9]{2}-[0-9]{2}(?![0-9])')

def parsed(match):
    fraction=(match.group('fraction')or'')[1:];zone=match.group('zone').upper();zone='+00:00'if zone in('Z','UTC')else zone
    base=datetime.fromisoformat(match.group('day')+'T'+match.group('clock')+zone).astimezone(timezone.utc)
    seconds=calendar.timegm(base.timetuple())
    value=base.strftime('%Y-%m-%dT%H:%M:%S')+('.'+fraction if fraction else'')+'Z'
    return value,seconds,fraction

def _role(text,start):
    prefix=re.split(r'[.!?;\n]',text[max(0,start-120):start])[-1]
    if re.search(r'\b(?:ticket|request|screenshot|message)\s+(?:was\s+)?(?:logged|created|opened|captured|written)(?:\s+(?:on|at))?\s*$',prefix,re.I):return 'CONTEXT'
    if re.search(r'\b(?:(?:run|job|refresh)\s+(?:(?:that|which)\s+)?(?:(?:started|starting|began|on|at|from|dated)\s+){0,3}|start(?:ed|ing)?(?:\s+(?:on|at|time|of))*\s*)$',prefix,re.I):return 'TARGET'
    return 'UNRESOLVED'

def from_text(text):
    if not isinstance(text,str):raise ValueError('OPERATIONAL_TICKET_TEXT_REQUIRED')
    stamps=list(STAMP.finditer(text));target=[];unknown=[]
    for match in stamps:
        role=_role(text,match.start())
        if role=='TARGET':target.append(match)
        elif role=='UNRESOLVED':unknown.append(match)
    for day in DATE.finditer(text):
        if any(m.start()<=day.start()<m.end()for m in stamps):continue
        if _role(text,day.start())!='CONTEXT':raise ValueError('RUN_TIME_PRECISION_OR_ZONE_UNRESOLVED')
    if unknown:raise ValueError('RUN_REFERENCE_AMBIGUOUS'if target else'RUN_TIME_ROLE_UNRESOLVED')
    if not target:return None
    values={parsed(m)[0]for m in target}
    if len(values)!=1:raise ValueError('RUN_REFERENCE_AMBIGUOUS')
    m=target[0]
    return {'kind':'START_TIME','at':parsed(m)[0],'source':{'start':m.start(),'end':m.end(),'quote':m.group()}}

def validate(selector,text):
    if not isinstance(selector,dict)or set(selector)!={'kind','at','source'}or selector['kind']!='START_TIME':raise ValueError('RUN_SELECTOR_SHAPE')
    quote=span(selector['source'],text);matches=list(STAMP.finditer(quote))
    if len(matches)!=1 or matches[0].span()!=(0,len(quote)):raise ValueError('RUN_SELECTOR_QUOTED_TIME_REQUIRED')
    value,seconds,fraction=parsed(matches[0])
    if value!=selector['at']:raise ValueError('RUN_SELECTOR_DIFFERS_FROM_QUOTE')
    if from_text(text)!=selector:raise ValueError('RUN_SELECTOR_DIFFERS_FROM_QUOTED_TARGET')
    return seconds,fraction

def select(selector,facts,text):
    seconds,fraction=validate(selector,text);precision=len(fraction);found={};insufficient=False
    for fact in facts:
        payload=fact['value'];runs=payload.get('recent_runs',[payload])
        for run in runs:
            if not isinstance(run,dict)or not run.get('run_id')or not isinstance(run.get('start'),str):continue
            match=STAMP.fullmatch(run['start'])
            if match is None:continue
            _,actual_seconds,actual_fraction=parsed(match)
            if actual_seconds!=seconds:continue
            if len(actual_fraction)<precision:
                insufficient=True;continue
            if actual_fraction[:precision]!=fraction:continue
            identity=run['run_id']
            if identity in found and canonical(found[identity][1])!=canonical(run):raise ValueError('REQUESTED_RUN_OBSERVATIONS_CONFLICT')
            found[identity]=(fact,run)
    if len(found)>1:raise ValueError('REQUESTED_RUN_AMBIGUOUS_AT_STATED_PRECISION')
    if not found:raise ValueError('REQUESTED_RUN_TIME_PRECISION_UNAVAILABLE'if insufficient else'REQUESTED_RUN_NOT_IN_RETAINED_HISTORY')
    source,run=next(iter(found.values()));result=copy.deepcopy(source);source_id=result.pop('id',None)
    result['value']=copy.deepcopy(run)
    result['selection']={'kind':'RECORD_SELECTED_FROM_RETAINED_HISTORY','source_fact_id':source_id,'run_id':run['run_id'],'timestamp_fraction_digits':precision,'source':copy.deepcopy(selector['source'])}
    return result

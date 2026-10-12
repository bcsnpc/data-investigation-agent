"""Consumer-owned claim vocabulary and append-only, source-backed facts."""
import copy,json
from .onboarding import digest
from .intake_span_references import tokens,REFERENCE
from . import reported_figure

VERSION='claim-intake-v1'
FIELDS=('metric','observation','direction','comparator','scope','time','filters','examples','guessed_cause','when_last_right')
DIRECTIONS=('LESS','MORE','DIFFERENT','STALE','DEFINITION','WRONG_BREAKDOWN','CONTEXT','FIELD_WRONG','UNKNOWN')
COMPARATORS=('OWN_COUNT','APPLICATION','OTHER_REPORT','SPREADSHEET','FINANCE','NONE','UNKNOWN')
SCOPES=('RECORDS','VISUALS','PAGE','REPORT','UNKNOWN')
ROLES=('OBSERVED','EXPECTED','CONTEXT')
SYMBOLS=tuple(dict.fromkeys((*DIRECTIONS,*COMPARATORS,*SCOPES,*ROLES)))
EXTRACTION_SCHEMA={'type':'object','additionalProperties':False,'properties':{
    'facts':{'type':'array','maxItems':40,'items':{'type':'object','additionalProperties':False,'properties':{
        'field':{'enum':list(FIELDS)},'reference':copy.deepcopy(REFERENCE),
        'symbol':{'anyOf':[{'enum':list(SYMBOLS)},{'type':'null'}]},
        'metric_reference':{'anyOf':[copy.deepcopy(REFERENCE),{'type':'null'}]}},
        'required':['field','reference','symbol','metric_reference']}}},'required':['facts']}


def span(reference,text):
    ts=tokens(text)
    if not isinstance(reference,list) or len(reference)!=2 or any(type(v)is not int for v in reference) or not 1<=reference[0]<=reference[1]<=len(ts):
        raise ValueError('Claim token reference is outside the actual input')
    start,end=ts[reference[0]-1]['start'],ts[reference[1]-1]['end']
    return {'start':start,'end':end,'quote':text[start:end]}


def pointer(value,path):
    for item in path.strip('/').split('/'):
        key=item.replace('~1','/').replace('~0','~')
        value=value[int(key)] if isinstance(value,list)else value[key]
    return value


def fact(field,value,source,*,authority):
    if field not in FIELDS:raise ValueError('Unknown claim fact field')
    if authority not in ('USER_SUBMITTED','USER_TEXT','SCREENSHOT_REVIEW','USER_CONFIRMED'):
        raise ValueError('Claim fact authority is not a user source')
    if not isinstance(source,dict) or not source.get('kind'):raise ValueError('Claim fact requires provenance')
    body={'field':field,'value':copy.deepcopy(value),'source':copy.deepcopy(source),'authority':authority}
    return {'id':digest(body),**body}


def merge(existing,new):
    result=copy.deepcopy(existing);seen={f['id'] for f in result}
    for f in new:
        if f['id']!=digest({k:f[k]for k in ('field','value','source','authority')}):raise ValueError('Claim fact integrity differs')
        if f['id']not in seen:result.append(copy.deepcopy(f));seen.add(f['id'])
    return result


def extraction(raw,text,document_id):
    from jsonschema import Draft202012Validator
    Draft202012Validator(EXTRACTION_SCHEMA).validate(raw)
    result=[]
    for item in raw['facts']:
        source=span(item['reference'],text);field=item['field'];symbol=item['symbol'];value=source['quote']
        if field=='observation':
            if symbol not in ROLES:raise ValueError('Observation requires an explicit consumer role')
            figure=reported_figure.from_candidates([source],text)
            metric=span(item['metric_reference'],text)['quote']if item['metric_reference']else None
            value={'role':symbol,'figure':figure,'metric_phrase':metric}
        elif field in ('direction','comparator','scope'):
            allowed={'direction':DIRECTIONS,'comparator':COMPARATORS,'scope':SCOPES}[field]
            if symbol not in allowed:raise ValueError('Claim symbol does not belong to its field')
            value={'kind':symbol,'phrase':source['quote']}if field=='scope'else symbol
        elif symbol is not None:raise ValueError('Text claim fact cannot supply an enum symbol')
        if field=='metric':value={'phrase':value}
        provenance={'kind':'TOKEN_SPAN','document_id':document_id,'span':source}
        if field=='observation'and item['metric_reference']:provenance['metric_span']=span(item['metric_reference'],text)
        result.append(fact(field,value,provenance,authority='USER_TEXT'))
    return result


def submitted(claim,request_hash):
    if not isinstance(claim,dict)or set(claim)-{'metric_phrase','observations','direction','comparator','scope','time','filters','examples','guessed_cause','when_last_right'}:
        raise ValueError('Invalid submitted claim fields')
    result=[]
    for key,value in claim.items():
        if value is None:continue
        field='metric'if key=='metric_phrase'else 'observation'if key=='observations'else key
        values=value if key=='observations'else[value]
        if key=='observations'and(not isinstance(value,list)or len(value)>20):raise ValueError('Bounded observations required')
        if key=='direction'and value not in DIRECTIONS:raise ValueError('Unknown submitted direction')
        if key=='comparator'and value not in COMPARATORS:raise ValueError('Unknown submitted comparator')
        if key=='scope'and(not isinstance(value,dict)or value.get('kind')not in SCOPES):raise ValueError('Unknown submitted scope')
        for i,item in enumerate(values):
            path='/claim/'+key+('/'+str(i)if key=='observations'else'')
            if key=='metric_phrase':item={'phrase':item}
            if key=='observations':
                if not isinstance(item,dict)or set(item)-{'metric_phrase','observed','expected','role','figure'}:raise ValueError('Invalid submitted observation')
                emitted=[]
                for role,k in (('OBSERVED','observed'),('EXPECTED','expected')):
                    if k not in item:continue
                    raw=item[k]
                    if isinstance(raw,dict):
                        from jsonschema import Draft202012Validator
                        Draft202012Validator(reported_figure.SCHEMA).validate(raw);reported_figure.validate(raw);figure=copy.deepcopy(raw)
                    else:
                        text=str(raw);figure=reported_figure.from_candidates([{'start':0,'end':len(text),'quote':text}],text)
                    emitted.append((k,{'role':role,'figure':figure,'metric_phrase':item.get('metric_phrase')}))
                if not emitted and set(item)>={'role','figure'}:
                    if item['role']not in ROLES:raise ValueError('Unknown submitted observation role')
                    from jsonschema import Draft202012Validator
                    Draft202012Validator(reported_figure.SCHEMA).validate(item['figure']);reported_figure.validate(item['figure'])
                    emitted=[('figure',copy.deepcopy(item))]
                if not emitted:raise ValueError('Observation requires a stated figure')
                for k,observation in emitted:
                    result.append(fact(field,observation,{'kind':'SUBMITTED_POINTER','request_hash':request_hash,'pointer':path+'/'+k},authority='USER_SUBMITTED'))
            else:result.append(fact(field,item,{'kind':'SUBMITTED_POINTER','request_hash':request_hash,'pointer':path},authority='USER_SUBMITTED'))
    return result


def settled(facts):
    """Conflicting values remain a question; no last-write-wins overwrite."""
    fields={};conflicts=[]
    for name in FIELDS:
        rows=[f for f in facts if f['field']==name and not f.get('superseded_by')]
        if not rows:continue
        values=[]
        for f in rows:
            if f['value']not in values:values.append(copy.deepcopy(f['value']))
        if name in ('observation','metric','examples','filters'):fields[name]=values
        elif name=='scope':
            combined={};bad=False
            for value in values:
                for key,item in value.items():
                    if key=='phrase':continue
                    if key=='kind'and item=='UNKNOWN'and combined.get('kind')not in(None,'UNKNOWN'):continue
                    if key=='kind'and combined.get('kind')=='UNKNOWN':combined.pop('kind')
                    if key in combined and combined[key]!=item:bad=True
                    combined[key]=copy.deepcopy(item)
            if bad:conflicts.append(name)
            else:fields[name]=combined
        elif len(values)==1:fields[name]=values[0]
        else:conflicts.append(name)
    return fields,conflicts


def labelled_text(text,document_id):
    """Explicit report/page/visual input lines are facts before model judgment."""
    import re
    result=[]
    for match in re.finditer(r'(?im)^(Report|Page|Visual):[ \t]*([^\r\n]+)',text):
        field=match.group(1).lower();quote=match.group(2).strip();start=text.index(quote,match.start(2),match.end(2))
        value={'kind':'VISUALS'if field=='visual'else'UNKNOWN','phrase':quote,field+'_phrase':quote}
        result.append(fact('scope',value,{'kind':'TOKEN_SPAN','document_id':document_id,'span':{'start':start,'end':start+len(quote),'quote':quote},'explicit_label':field},authority='USER_TEXT'))
    return result


def linked_text(text,document_id):
    """Visible Power BI links carry declared identity, never discarded filters."""
    import re
    from .adapters.report_link import parse
    result=[]
    for match in re.finditer(r'https://app\.powerbi\.com/[^\s<>]+',text):
        quote=match.group().rstrip('.,;)');reference=parse(quote)
        if reference['predicates']or reference['bookmark_reference']is not None:raise ValueError('CLAIM_LINK_CONTEXT_UNSUPPORTED')
        value={'kind':'UNKNOWN','report_id':reference['report_id']}
        if reference.get('page_id'):value['page_id']=reference['page_id']
        result.append(fact('scope',value,{'kind':'REPORT_LINK','document_id':document_id,'span':{'start':match.start(),'end':match.start()+len(quote),'quote':quote}},authority='USER_TEXT'))
    return result

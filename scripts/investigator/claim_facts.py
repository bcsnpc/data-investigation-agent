"""Consumer-owned claim vocabulary and append-only, source-backed facts."""
import copy,json,re
from .onboarding import digest
from .intake_span_references import tokens,REFERENCE
from . import reported_figure

VERSION='claim-intake-v1'
FIELDS=('metric','observation','direction','comparator','scope','location','time','filters','examples','guessed_cause','when_last_right')
DIRECTIONS=('LESS','MORE','DIFFERENT','STALE','DEFINITION','WRONG_BREAKDOWN','CONTEXT','FIELD_WRONG','UNKNOWN')
COMPARATORS=('OWN_COUNT','APPLICATION','OTHER_REPORT','SPREADSHEET','FINANCE','NONE','UNKNOWN')
SCOPES=('RECORDS','VISUALS','PAGE','REPORT','METRIC','UNKNOWN')
ROLES=('OBSERVED','EXPECTED','CONTEXT')
SYMBOLS=tuple(dict.fromkeys((*DIRECTIONS,*COMPARATORS,*SCOPES,*ROLES)))
def extraction_schema():
    """The producer can express only the field's own consumer vocabulary."""
    variants=[]
    enums={'direction':DIRECTIONS,'comparator':COMPARATORS,'scope':SCOPES,'observation':ROLES}
    for field in FIELDS:
        variants.append({'type':'object','additionalProperties':False,'properties':{
            'field':{'type':'string','enum':[field]},'reference':copy.deepcopy(REFERENCE),
            'symbol':{'type':'string','enum':list(enums[field])}if field in enums else{'type':'null'},
            'metric_reference':{'anyOf':[copy.deepcopy(REFERENCE),{'type':'null'}]}if field=='observation'else{'type':'null'}},
            'required':['field','reference','symbol','metric_reference']})
    return {'type':'object','additionalProperties':False,'properties':{'facts':{'type':'array','maxItems':40,'items':{'anyOf':variants}}},'required':['facts']}

EXTRACTION_SCHEMA=extraction_schema()


def normalise(raw):
    """Repair only lossless representation choices, never roles or referents."""
    result=copy.deepcopy(raw);repairs=[]
    if not isinstance(result,dict)or set(result)!={'facts'}:return result,repairs
    if isinstance(result['facts'],dict):result['facts']=[result['facts']];repairs.append('SINGLE_FACT_ARRAY')
    if not isinstance(result['facts'],list):return result,repairs
    enums={'direction':DIRECTIONS,'comparator':COMPARATORS,'scope':SCOPES,'observation':ROLES}
    for index,item in enumerate(result['facts']):
        if not isinstance(item,dict):continue
        field=item.get('field')
        if isinstance(field,str)and field.lower()in FIELDS and field!=field.lower():
            field=item['field']=field.lower();repairs.append('FIELD_CASE:'+str(index))
        if field not in FIELDS:continue
        if 'metric_reference'not in item:item['metric_reference']=None;repairs.append('NULL_METRIC_REFERENCE:'+str(index))
        elif field!='observation'and item['metric_reference']is not None:
            # This field's contract has no metric association; its own exact
            # reference retains the fact, and the rejected raw annotation stays
            # in the recorded provider response and repair audit.
            item['metric_reference']=None;repairs.append('NON_OBSERVATION_METRIC_REFERENCE:'+str(index))
        if field not in enums and item.get('symbol')is not None:
            item['symbol']=None;repairs.append('NON_ENUM_FIELD_SYMBOL:'+str(index))
        elif field not in enums and 'symbol'not in item:
            item['symbol']=None;repairs.append('NULL_TEXT_SYMBOL:'+str(index))
        elif isinstance(item.get('symbol'),str)and item['symbol'].upper()in enums.get(field,())and item['symbol']!=item['symbol'].upper():
            item['symbol']=item['symbol'].upper();repairs.append('ENUM_CASE:'+str(index))
    return result,repairs


def observation(source,text,role,metric):
    """A statement, range or plural quantities is not one exact scalar.

Keep each original numeral span even when scalar precision is unavailable.
These branches cannot be consumed as a numeric reproduction claim.
"""
    try:
        figure=reported_figure.from_candidates([source],text)
        return {'role':role,'figure':figure,'metric_phrase':metric}
    except reported_figure.UnavailablePrecision:
        quote=source['quote']
        pattern=r'(?<![\w.])[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*[KMBkmb]?(?!\w|\.\w)'
        numbers=[]
        for match in re.finditer(pattern,quote):
            end=match.end()
            while end>match.start()and quote[end-1].isspace():end-=1
            numbers.append({'start':source['start']+match.start(),'end':source['start']+end,
                'quote':quote[match.start():end]})
        range_words=bool(re.search(r'\b(?:between|from|range|ranging)\b|\d\s*(?:-|–|—|to)\s*\d',quote,re.I))
        kind=('QUALITATIVE'if not numbers else'RANGE'if len(numbers)>1 and range_words else
              'MULTIPLE_QUANTITIES'if len(numbers)>1 else'PRECISION_UNAVAILABLE')
        return {'role':role,'figure':{'state':'UNSPECIFIED'},'metric_phrase':metric,
            'statement':copy.deepcopy(source),'quantity_structure':{'kind':kind,'numerals':numbers}}



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
            metric=span(item['metric_reference'],text)['quote']if item['metric_reference']else None
            value=observation(source,text,symbol,metric)
        elif field in ('direction','comparator','scope'):
            allowed={'direction':DIRECTIONS,'comparator':COMPARATORS,'scope':SCOPES}[field]
            if symbol not in allowed:raise ValueError('Claim symbol does not belong to its field')
            value={'kind':symbol,'phrase':source['quote']}if field=='scope'else symbol
        elif symbol is not None:raise ValueError('Text claim fact cannot supply an enum symbol')
        if field=='metric':value={'phrase':value}
        if field=='location':value={'phrase':value}
        provenance={'kind':'TOKEN_SPAN','document_id':document_id,'span':source}
        if field=='observation'and item['metric_reference']:provenance['metric_span']=span(item['metric_reference'],text)
        result.append(fact(field,value,provenance,authority='USER_TEXT'))
    return result


def submitted(claim,request_hash):
    if not isinstance(claim,dict)or set(claim)-{'metric_phrase','observations','direction','comparator','scope','location','time','filters','examples','guessed_cause','when_last_right'}:
        raise ValueError('Invalid submitted claim fields')
    result=[]
    # A taped JSON request is canonicalized by key. Facts are ordered evidence,
    # so their order must not depend on the caller's dictionary insertion order.
    for key in sorted(claim):
        value=claim[key]
        if value is None:continue
        field='metric'if key=='metric_phrase'else 'observation'if key=='observations'else key
        values=value if key=='observations'else[value]
        if key=='observations'and(not isinstance(value,list)or len(value)>20):raise ValueError('Bounded observations required')
        if key=='direction'and value not in DIRECTIONS:raise ValueError('Unknown submitted direction')
        if key=='comparator'and value not in COMPARATORS:raise ValueError('Unknown submitted comparator')
        if key=='scope'and(not isinstance(value,dict)or value.get('kind')not in SCOPES):raise ValueError('Unknown submitted scope')
        if key=='location'and(not isinstance(value,dict)or set(value)-{'model_id','report_id','page_id','phrase','report_phrase','page_phrase','visual_phrase'}or any(not isinstance(v,str)or not v for v in value.values())):
            raise ValueError('Invalid submitted location')
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
        elif name in ('time','when_last_right'):
            # These are verbatim temporal statements, not one compiled date or
            # interval. Preserve all clauses for confirmation; never choose one.
            fields[name]=values[0]if len(values)==1 else values
        elif name=='direction':
            known=[v for v in values if v!='UNKNOWN']
            if len(known)>1 and'DIFFERENT'in known:
                specific=[v for v in known if v!='DIFFERENT']
                if len(specific)==1 and specific[0]in('LESS','MORE','WRONG_BREAKDOWN','FIELD_WRONG'):known=specific
            if len(known)==1:fields[name]=known[0]
            elif not known:fields[name]='UNKNOWN'
            else:conflicts.append(name)
        elif name in('scope','location'):
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


def requested_extent(text):
    """An explicit whole-container complaint, never merely a location mention."""
    patterns=[r'\b(?:everything|whole|entire|all\s+(?:the\s+)?(?:numbers|metrics|cards|visuals))\b[^\n?.]{0,65}\b(?P<unit>page|overview|report|dashboard)\b',
        r'\b(?:is|are)\s+(?:(?:this|that|the|whole|entire)\s+)?(?P<unit>page|overview|report|dashboard)\s+(?:up[\s-]+to[\s-]+date|current|stale|wrong)\b',
        r'\b(?:(?:this|that|the|whole|entire)\s+)(?P<unit>page|overview|report|dashboard)\s+(?:is|looks|seems)\s+(?:wrong|stale|out[\s-]+of[\s-]+date)\b']
    found=[]
    for pattern in patterns:
        for match in re.finditer(pattern,text,re.I):
            found.append({'kind':'REPORT'if match['unit'].lower()in('report','dashboard')else'PAGE',
                'source':{'start':match.start(),'end':match.end(),'quote':match.group()}})
    return found


def location_fact(original,text=''):
    """Separate model-extracted location from explicitly requested extent.

    Submitted/confirmed scope choices are fixed. Form container pickers and
    screenshots supply location; they do not assert a whole-container request.
    """
    if original['field']!='scope'or original.get('superseded_by'):return None
    value=original['value'];kind=value.get('kind');source=original['source'];authority=original['authority']
    if kind not in('PAGE','REPORT','UNKNOWN'):return None
    fixed=authority in('USER_SUBMITTED','USER_CONFIRMED')and source.get('kind')not in(
        'RETAINED_FORM_PICKERS','RETAINED_FORM_CONTAINER_CORRECTION','SCREENSHOT_REVIEW')
    if fixed and kind!='UNKNOWN':return None
    extents=requested_extent(text or source.get('span',{}).get('quote',''))
    if kind in('PAGE','REPORT')and any(e['kind']==kind for e in extents)and source.get('kind')not in('RETAINED_FORM_PICKERS','RETAINED_FORM_CONTAINER_CORRECTION'):
        return None
    location={k:copy.deepcopy(v)for k,v in value.items()if k!='kind'}
    if not location:return None
    return fact('location',location,{'kind':'LOCATION_NOT_EXTENT','source_fact_id':original['id'],
        'original_source':copy.deepcopy(source),'rule':'OWNER_LOCATION_NOT_EXTENT'},authority=authority)


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
    """Visible report links carry declared identity, never discarded filters."""
    from .adapters.report_link import references
    result=[]
    for start,quote,reference in references(text):
        if reference['predicates']or reference['bookmark_reference']is not None:raise ValueError('CLAIM_LINK_CONTEXT_UNSUPPORTED')
        value={'kind':'UNKNOWN','report_id':reference['report_id']}
        if reference.get('page_id'):value['page_id']=reference['page_id']
        result.append(fact('scope',value,{'kind':'REPORT_LINK','document_id':document_id,'span':{'start':start,'end':start+len(quote),'quote':quote}},authority='USER_TEXT'))
    return result


def resolve_native_scope(original,catalog):
    """Bind a declared URL via the existing adapter's exact native-ID contract.

    The caller retains/supersedes the original fact, rather than overwriting its
    submitted identity. Unsupported filters/bookmarks still refuse in bind().
    """
    if original['field']!='scope'or original['source'].get('kind')!='REPORT_LINK':return None
    from .adapters.report_link import bind
    resolved=bind(original['source']['span']['quote'],catalog['models'])
    value=copy.deepcopy(original['value'])
    value.update(model_id=resolved['model_id'],report_id=resolved['report_id'])
    if resolved['page_id']is not None:value['page_id']=resolved['page_id']
    return fact('scope',value,{'kind':'CATALOG_REFERENCE_BINDING','source_fact_id':original['id'],
        'catalog_hash':digest(catalog),'binding':resolved},authority=original['authority'])

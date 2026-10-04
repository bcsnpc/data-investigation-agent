"""Quoted numeral interpretations; only FIGURE mentions enter comparison."""
import copy
from .reported_figure import SPAN_SCHEMA, span, stated
ROLES=('FIGURE','IDENTIFIER','DATE','COUNT','OTHER')
LIMIT=32
SCHEMA={'type':'array','maxItems':LIMIT,'items':{'type':'object','additionalProperties':False,
    'properties':{'role':{'type':'string','enum':list(ROLES)},'source':copy.deepcopy(SPAN_SCHEMA)},
    'required':['role','source']}}
EXPECTED_SCHEMA={'type':'array','maxItems':LIMIT,'items':{'type':'object','additionalProperties':False,
    'properties':{'value':{'type':'string','minLength':1,'maxLength':128},'source':copy.deepcopy(SPAN_SCHEMA)},
    'required':['value','source']}}


def wire_schema(quote_schema):
    return {'type':'array','maxItems':LIMIT,'items':{'type':'object','additionalProperties':False,
        'properties':{'role':{'type':'string','enum':list(ROLES)},'quote':copy.deepcopy(quote_schema['properties']['quote'])},
        'required':['role','quote']}}


def validate(mentions,ticket=None):
    if not isinstance(mentions,list) or len(mentions)>LIMIT:raise ValueError('Numeral mentions exceed the consumer bound')
    seen=set()
    for mention in mentions:
        if not isinstance(mention,dict) or set(mention)!={'role','source'} or mention['role'] not in ROLES:
            raise ValueError('Every numeral mention requires one closed role and quoted source')
        span(mention['source'],ticket)
        key=(mention['source']['start'],mention['source']['end'])
        if key in seen:raise ValueError('A numeral span cannot have competing roles')
        seen.add(key)
    return mentions


def expected(mentions,ticket=None):
    validate(mentions,ticket)
    result=[]
    for mention in mentions:
        if mention['role']!='IDENTIFIER':continue
        value,precision=stated(mention['source']['quote'])
        if precision!={'state':'EXACT'}:raise ValueError('Expected record identifier must be exact, not rounded')
        result.append({'value':value,'source':copy.deepcopy(mention['source'])})
    return result


def evidence(value,ticket):
    from . import reported_figure
    if 'numeral_mentions' not in value and 'expected_records' not in value:return
    mentions=validate(value.get('numeral_mentions'),ticket)
    named=value.get('name_binding')
    if named:
        import re
        start,end=named['source']['start'],named['source']['end']
        for mention in mentions:
            if mention['role'] not in ('FIGURE','IDENTIFIER'):continue
            source=mention['source']
            for numeral in re.finditer(r'\d+(?:[,\.]\d+)*',source['quote']):
                a,b=source['start']+numeral.start(),source['start']+numeral.end()
                if start<=a and b<=end:
                    raise ValueError('Numeral role ambiguity: a numeral in the resolved catalog name cannot be a reported figure or expected-record key.')
    if value.get('expected_records')!=expected(mentions,ticket):raise ValueError('Expected records differ from IDENTIFIER mentions')
    candidates=[m['source'] for m in mentions if m['role']=='FIGURE']
    if value['reported_figure']!=reported_figure.from_candidates(candidates,ticket):raise ValueError('Reported figure differs from FIGURE mentions')


def measure_scope(value,ticket):
    """Scope requires its own declaration; record membership cannot supply it."""
    import re
    identifiers=[m['source'] for m in value.get('numeral_mentions',[]) if m['role']=='IDENTIFIER']
    dimensions=value.get('dimension_ids',[]);quotes=value.get('dimension_quotes')
    # Historical no-identifier proposals remain readable. New producer always
    # supplies grouping provenance; an expected-record proposal cannot bypass it.
    if dimensions and (identifiers or quotes is not None):
        if not isinstance(quotes,list) or [q.get('column_id') for q in quotes]!=dimensions:
            raise ValueError('Grouping requires independent quoted provenance; an identifier is membership only')
        for q in quotes:
            span(q['source'],ticket)
            if not re.search(r'\b(?:by|per|grouped|breakdown|break down)\b',q['source']['quote'],re.I):
                raise ValueError('Grouping quote does not declare a breakdown')
            if any(q['source']['start']<i['end'] and i['start']<q['source']['end'] for i in identifiers):
                raise ValueError('Identifier provenance cannot declare grouping')
    elif quotes:
        raise ValueError('Grouping provenance without grouping')
    for q in value.get('scope_quotes',[]):
        # Every occurrence is checked: a repeated quote cannot dodge the record's
        # span by resolving to an earlier occurrence.
        for match in re.finditer(re.escape(q['quote']),ticket):
            if any(match.start()<i['end'] and i['start']<match.end() for i in identifiers):
                raise ValueError('Identifier provenance cannot declare a measure restriction')

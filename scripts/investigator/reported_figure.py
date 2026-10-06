"""Reported states and precision are evidence from a ticket, never tolerances."""
import re
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from .proposal_limits import INTAKE_QUOTE
from .intake_statement_registry import empty_matches
CANDIDATE_LIMIT=8


SPAN_SCHEMA={'type':'object','additionalProperties':False,'properties':{
    'start':{'type':'integer','minimum':0},'end':{'type':'integer','minimum':1},
    'quote':{'type':'string','minLength':1,'maxLength':INTAKE_QUOTE}},'required':['start','end','quote']}
PRECISION_SCHEMA={'anyOf':[
    {'type':'object','additionalProperties':False,'properties':{'state':{'type':'string','enum':['EXACT']}},'required':['state']},
    {'type':'object','additionalProperties':False,'properties':{'state':{'type':'string','enum':['STATED_PLACE']},
        'place':{'type':'integer','minimum':-100,'maximum':100}},'required':['state','place']}]}
SCHEMA={'anyOf':[
    {'type':'object','additionalProperties':False,'properties':{'state':{'type':'string','enum':['UNSPECIFIED']}},'required':['state']},
    {'type':'object','additionalProperties':False,'properties':{'state':{'type':'string','enum':['EMPTY']},
        'source':SPAN_SCHEMA},'required':['state','source']},
    {'type':'object','additionalProperties':False,'properties':{'state':{'type':'string','enum':['NUMBER']},
        'value':{'type':'string','minLength':1,'maxLength':128},'source':SPAN_SCHEMA,'precision':PRECISION_SCHEMA},
        'required':['state','value','source','precision']}]}
for _variant in SCHEMA['anyOf'][1:]:
    _variant['properties']['supporting_sources']={'type':'array','minItems':1,
        'maxItems':CANDIDATE_LIMIT-1,'items':SPAN_SCHEMA}


class AmbiguousFigure(ValueError):
    """Different resolved values, never merely different wording."""


class UnavailablePrecision(ValueError):
    """The reported wording does not supply a usable digit precision."""


def span(source, ticket=None):
    if (not isinstance(source,dict) or set(source)!={'start','end','quote'}
            or type(source['start']) is not int or type(source['end']) is not int
            or not 0<=source['start']<source['end'] or not isinstance(source['quote'],str)
            or not 1<=len(source['quote'])<=INTAKE_QUOTE
            or len(source['quote'])!=source['end']-source['start']):
        raise ValueError('Reported figure requires an exact ticket span')
    if ticket is not None and ticket[source['start']:source['end']]!=source['quote']:
        raise ValueError('Reported figure provenance differs from the ticket')
    return source['quote']


def stated(quote):
    """Read digits/scale exactly as supplied. No implicit approximation interval."""
    matches=list(re.finditer(r'(?<![\w.])[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*[KMBkmb]?(?![\w.])',quote))
    if len(matches)!=1: raise UnavailablePrecision('Reported numeral or its stated precision is ambiguous')
    raw=matches[0].group().strip(); scale=0
    if raw[-1].upper() in 'KMB': scale={'K':3,'M':6,'B':9}[raw[-1].upper()];raw=raw[:-1].strip()
    raw=raw.replace(',','')
    if len(raw)>100:raise ValueError('Reported number exceeds the consumer bound')
    with localcontext() as ctx:
        ctx.prec=256
        value=Decimal(raw)*(Decimal(10)**scale)
    approximate=bool(re.search(r'\b(about|approximately|roughly|around)\b',quote,re.I))
    if approximate and '.' not in raw and not scale:
        raise UnavailablePrecision('Approximate figure has no determinable stated precision')
    decimals=len(raw.split('.')[1]) if '.' in raw else 0
    precision=({'state':'STATED_PLACE','place':scale-decimals} if (decimals or scale)
               and not re.search(r'\bexact(?:ly)?\b',quote,re.I) else {'state':'EXACT'})
    return format(value,'f'),precision


def validate(value, ticket=None):
    if not isinstance(value,dict): raise ValueError('Reported figure requires an explicit state')
    state=value.get('state')
    expected={variant['properties']['state']['enum'][0]:set(variant['required']) for variant in SCHEMA['anyOf']}
    fields=set(value)-({'supporting_sources'} if state in ('EMPTY','NUMBER') else set())
    if state not in expected or fields!=expected[state]:raise ValueError('Malformed reported figure state')
    if state=='UNSPECIFIED':return value
    if 'supporting_sources' in value:
        supporting=value['supporting_sources']
        if not isinstance(supporting,list) or not 1<=len(supporting)<CANDIDATE_LIMIT:
            raise ValueError('Reported supporting spans exceed the consumer bound')
        resolved=_resolve([value['source'],*supporting],ticket)
        if resolved!=value:raise ValueError('Reported value, precision or primary span differs from supporting evidence')
        return value
    quote=span(value['source'],ticket)
    if state=='EMPTY':
        if not empty_matches(quote):
            raise ValueError('Empty reported state lacks explicit ticket provenance')
    else:
        number,precision=stated(quote)
        if (not isinstance(value['value'],str) or value['value']!=number or value['precision']!=precision):
            raise ValueError('Reported number or precision differs from the ticket span')
    return value


def from_candidates(candidates,ticket):
    """Resolve all supplied spans before deciding whether values are ambiguous."""
    if not isinstance(candidates,list):raise ValueError('Reported candidates require a list')
    if len(candidates)>CANDIDATE_LIMIT:raise ValueError('Reported candidates exceed the consumer bound')
    if not candidates:return {'state':'UNSPECIFIED'}
    return validate(_resolve(candidates,ticket),ticket)


def _resolve(candidates,ticket):
    groups={}
    for source in candidates:span(source,ticket)
    for source in sorted(candidates,key=lambda s:(s['start'],s['end'])):
        quote=span(source,ticket)
        if empty_matches(quote):key=('EMPTY',);number=precision=None
        else:
            number,precision=stated(quote);key=('NUMBER',Decimal(number))
        rows=groups.setdefault(key,[])
        if not any(r[0]==source for r in rows):rows.append((source,number,precision))
    if len(groups)>1:
        raise AmbiguousFigure('Ambiguous reported figure: more than one resolved value requires clarification: '+
            '; '.join(('EMPTY' if key[0]=='EMPTY' else str(key[1]))+' from '+repr(rows[0][0]['quote'])
                      for key,rows in groups.items()))
    key,rows=next(iter(groups.items()));source,number,precision=rows[0]
    result={'state':key[0],'source':source}
    if key[0]=='NUMBER':
        if any(r[2]!=precision for r in rows[1:]):
            # Equal values with different digit presentations use the coarser
            # recorded place. Different numeric values NEVER collapse by rounding.
            places=[r[2]['place'] if r[2]['state']=='STATED_PLACE' else Decimal(r[1]).as_tuple().exponent for r in rows]
            precision={'state':'STATED_PLACE','place':max(places)}
        result.update(value=number,precision=precision)
    if len(rows)>1:result['supporting_sources']=[r[0] for r in rows[1:]]
    return result


def provenance(reported):
    """Engine-rendered original wording, including every supporting span."""
    validate(reported)
    if reported['state']=='UNSPECIFIED':return ''
    sources=[reported['source'],*reported.get('supporting_sources',[])]
    return 'What the ticket said: '+ '; '.join(repr(s['quote']) for s in sources)+'.'


def label(reported, measured):
    validate(reported)
    if reported['state']=='UNSPECIFIED':return None
    if reported['state']=='EMPTY':return 'REPRODUCED' if measured is None else 'NOT_REPRODUCED'
    if measured is None:return 'NOT_REPRODUCED'
    with localcontext() as ctx:
        ctx.prec=256
        number=Decimal(measured); expected=Decimal(reported['value'])
        if reported['precision']['state']=='STATED_PLACE':
            quantum=Decimal(1).scaleb(reported['precision']['place'])
            number=number.quantize(quantum,rounding=ROUND_HALF_EVEN)
        return 'REPRODUCED' if number==expected else 'NOT_REPRODUCED'


def qualification(reported):
    validate(reported)
    if reported['state']!='NUMBER' or reported['precision']['state']=='EXACT':return []
    place=reported['precision']['place']
    return [f'The comparison uses the stated digit position (10 to the power {place}), rounding to the nearest digit with ties to even; a match at this precision is weaker than an exact match. No tolerance was inferred or widened.']


def display(reported):
    validate(reported)
    return 'empty' if reported['state']=='EMPTY' else reported.get('value','not supplied')

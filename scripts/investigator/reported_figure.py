"""Reported states and precision are evidence from a ticket, never tolerances."""
import re
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from .proposal_limits import INTAKE_QUOTE
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


class AmbiguousFigure(ValueError):
    """Interpretation named more than one candidate; none may be selected."""


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
    if state not in expected or set(value)!=expected[state]:raise ValueError('Malformed reported figure state')
    if state=='UNSPECIFIED':return value
    quote=span(value['source'],ticket)
    if state=='EMPTY':
        if not re.search(r'\b(empty|blank|no data|no rows|nothing shown)\b',quote,re.I):
            raise ValueError('Empty reported state lacks explicit ticket provenance')
    else:
        number,precision=stated(quote)
        if (not isinstance(value['value'],str) or value['value']!=number or value['precision']!=precision):
            raise ValueError('Reported number or precision differs from the ticket span')
    return value


def from_candidates(candidates,ticket):
    """Interpretation supplies candidate spans; ambiguity is never selected away."""
    if not isinstance(candidates,list):raise ValueError('Reported candidates require a list')
    if len(candidates)>CANDIDATE_LIMIT:raise ValueError('Reported candidates exceed the consumer bound')
    for source in candidates:span(source,ticket)
    if len(candidates)>1:raise AmbiguousFigure('Ambiguous reported figure: more than one plausible ticket span')
    if not candidates:return {'state':'UNSPECIFIED'}
    source=candidates[0]; quote=span(source,ticket)
    if re.search(r'\b(empty|blank|no data|no rows|nothing shown)\b',quote,re.I):
        return validate({'state':'EMPTY','source':source},ticket)
    number,precision=stated(quote)
    return validate({'state':'NUMBER','source':source,'value':number,'precision':precision},ticket)


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

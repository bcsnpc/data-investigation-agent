"""Consumer-owned roles for quoted values; subjects cannot restrict a read."""
import copy
from .onboarding import fields
from .reported_figure import SPAN_SCHEMA, span

ROLES=('SELECTION','SUBJECT','MENTION')
LIMIT=32
SCHEMA={'type':'array','maxItems':LIMIT,'items':{'type':'object','additionalProperties':False,
    'properties':{'role':{'type':'string','enum':list(ROLES)},'source':copy.deepcopy(SPAN_SCHEMA)},
    'required':['role','source']}}


def wire_schema(quote_schema):
    result=copy.deepcopy(SCHEMA)
    result['items']['properties']['source']=copy.deepcopy(quote_schema)
    return result


def validate(mentions,ticket):
    if not isinstance(mentions,list) or len(mentions)>LIMIT:raise ValueError('Value inventory exceeds its bound')
    seen={}
    for mention in mentions:
        fields(mention,['role','source'])
        if mention['role'] not in ROLES:raise ValueError('Unknown value role')
        span(mention['source'],ticket)
        source=mention['source']
        key=(source['start'],source['end'])
        if key in seen and seen[key]!=mention['role']:
            raise ValueError('A mentioned value has conflicting roles')
        seen[key]=mention['role']
    return mentions


def scope(value,ticket,requested=None):
    mentions=validate(value['value_mentions'],ticket)
    kind=(value.get('question_kind') or {}).get('kind')
    if kind=='BUSINESS_MEANING' and (value.get('filters') or value.get('dimension_ids') or requested
            or value.get('selection_request') or value.get('definition_target')):
        raise ValueError('Business-meaning subjects cannot enter measurement scope')
    sources=[m['source'] for m in mentions if m['role']=='SELECTION']
    def selected(quote):
        if not any(quote in source['quote'] or source['quote'] in quote for source in sources):
            raise ValueError('Only a quoted SELECTION may enter measurement scope')
    for proof in value.get('scope_quotes',[]):selected(proof['quote'])
    if requested:selected(requested['value_source']['quote'])
    if value.get('selection_request'):selected(value['selection_request']['value_source']['quote'])
    if value.get('definition_target'):selected(value['definition_target']['source']['quote'])

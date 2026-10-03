"""Consumer-owned, nonbinding selection descriptor with verbatim provenance."""
import copy
import re
from jsonschema import Draft202012Validator
from . import reported_figure


def schema(source_schema):
    def variant(state, source):
        return {'type':'object','additionalProperties':False,'properties':{
            'state':{'type':'string','enum':[state]},'source':source},
            'required':['state','source']}
    return {'anyOf':[variant('SEPARATED',copy.deepcopy(source_schema)),
                    variant('VALUE_ONLY',{'type':'null'}),
                    variant('UNSEPARATED',{'type':'null'})]}


SCHEMA=schema(reported_figure.SPAN_SCHEMA)


def validate(descriptor,value_source,*,ticket=None):
    Draft202012Validator(SCHEMA).validate(descriptor)
    reported_figure.span(value_source,ticket)
    if descriptor['state']=='SEPARATED':
        source=descriptor['source'];reported_figure.span(source,ticket)
        if max(source['start'],value_source['start'])<min(source['end'],value_source['end']):
            raise ValueError('Selection value and descriptor quotes overlap; separation is not established.')
    return descriptor


def note(descriptor,column_name=None):
    """Text comparison AFTER binding; not semantic or column-resolution evidence."""
    if descriptor is None:return None  # Historical request: no new interpretation.
    state=descriptor['state']
    agreement='NOT_EVALUATED'
    if state=='SEPARATED' and column_name is not None:
        tokens=lambda text:re.findall(r'[^\W_]+',text.casefold())
        hint=tokens(descriptor['source']['quote']);name=tokens(column_name)
        agrees=bool(hint) and any(name[i:i+len(hint)]==hint for i in range(len(name)-len(hint)+1))
        agreement='TEXT_AGREEMENT' if agrees else 'TEXT_DISAGREEMENT'
    return {'descriptor':copy.deepcopy(descriptor),'agreement':agreement,
            'authority':'NONBINDING_TICKET_HINT','binding_evidence':False}


def render(value,*,business=False):
    descriptor=value['descriptor']
    if descriptor['state']=='VALUE_ONLY':return ''
    if descriptor['state']=='UNSEPARATED':
        return 'The selected value could not be separated from its description; the whole quoted phrase was tried.'
    text='You described the selected value as "'+descriptor['source']['quote']+'"; that description was a hint, not a reason to choose a column.'
    if not business and value['agreement']!='NOT_EVALUATED':
        text+=' Its wording '+('agrees' if value['agreement']=='TEXT_AGREEMENT' else 'does not agree')+' with the resolved column name; this was recorded after resolution and did not affect it.'
    # Verbatim evidence is retained above. A technical identifier or serialized
    # descriptor is not business vocabulary and must not poison the narrative.
    from .narrative_form import validate as validate_form
    try:
        validate_form(text,business)
        if business:
            from .business_vocabulary import validate_text
            validate_text(text,text)
    except ValueError:
        return 'Your description of the selection was retained as a hint and did not choose a column.'
    return text

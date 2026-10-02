"""Consumer-owned column resolution contract, separate from visual selection."""
import copy
from . import reported_figure, declaration_inventory
from .onboarding import fields, text

KINDS=('EVIDENCE','STATED','REFUSED')
ID={'type':'string','minLength':1,'maxLength':4000}
def variant(kind, properties):
    properties={'resolution_kind':{'type':'string','enum':[kind]},**properties}
    return {'type':'object','additionalProperties':False,'properties':properties,'required':list(properties)}

SCHEMA={'anyOf':[
    {'type':'null'},
    variant('EVIDENCE',{'column_id':ID,'inventory_entry_id':ID,'source':reported_figure.SPAN_SCHEMA}),
    variant('STATED',{'column_id':ID,'source':reported_figure.SPAN_SCHEMA}),
    variant('REFUSED',{'candidates':{'anyOf':[
        {'type':'array','maxItems':0,'items':ID},
        {'type':'array','minItems':2,'maxItems':512,'uniqueItems':True,'items':ID}]},
        'source':reported_figure.SPAN_SCHEMA})]}

def shape(value, ticket=None):
    """Closed structural validation is usable before trusted inventory lookup."""
    if value is None:return None
    if not isinstance(value,dict) or value.get('resolution_kind') not in KINDS:
        raise ValueError('Definition target requires a resolution kind')
    spec=next(s for s in SCHEMA['anyOf'][1:] if s['properties']['resolution_kind']['enum']==[value['resolution_kind']])
    fields(value,spec['required'])
    reported_figure.span(value['source'],ticket)
    if value['resolution_kind']=='REFUSED':
        candidates=value['candidates']
        if not isinstance(candidates,list) or len(candidates)==1 or len(candidates)>512:
            raise ValueError('Target ambiguity requires zero or multiple candidates')
        for candidate in candidates:text(candidate,4000)
        if len(candidates)!=len(set(candidates)):raise ValueError('Duplicate target candidates')
    else:
        text(value['column_id'],4000)
        if value['resolution_kind']=='EVIDENCE':text(value['inventory_entry_id'],4000)
    return value

def validate(value, *, ticket=None, inventory=None, active=None):
    shape(value,ticket)
    if value is not None and value['resolution_kind']=='EVIDENCE':
        entries=declaration_inventory.validate(inventory,active)
        entry=next((e for e in entries if e['id']==value['inventory_entry_id']),None)
        if (entry is None or entry['disposition']!='ACTIVE'
                or not any(r['field_id']==value['column_id'] for r in entry['restrictions'])):
            raise ValueError('Evidence target requires a matching ACTIVE inventory entry')
    return value

def evidence(column_id, source, inventory_entry_id, *, ticket, inventory, active):
    """Deterministic producer; no model response may assign EVIDENCE."""
    result={'resolution_kind':'EVIDENCE','column_id':column_id,
            'inventory_entry_id':inventory_entry_id,'source':copy.deepcopy(source)}
    return validate(result,ticket=ticket,inventory=inventory,active=active)

def procedure_scope(envelope):
    """Forward server-owned evidence unchanged, including explicit UNSPECIFIED."""
    result={k:copy.deepcopy(envelope[k]) for k in ('filters','dimension_ids')}
    result['ticket_shape']=envelope.get('ticket_shape')
    for key in ('reported_figure','definition_target'):
        if key in envelope:result[key]=copy.deepcopy(envelope[key])
    return result

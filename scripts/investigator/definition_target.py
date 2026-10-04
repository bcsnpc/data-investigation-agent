"""Consumer-owned column resolution contract, separate from visual selection."""
import copy
from . import reported_figure, declaration_inventory
from .onboarding import fields, text
from .onboarding import digest

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

# Translation inputs cannot express a resolution or an evidence verdict.
REQUEST_SCHEMA={'anyOf':[{'type':'null'},
    {'type':'object','additionalProperties':False,'properties':{'source':reported_figure.SPAN_SCHEMA},'required':['source']},
    {'type':'object','additionalProperties':False,'properties':{'source':reported_figure.SPAN_SCHEMA,'column_id':ID},'required':['source','column_id']}]}

class ResolutionRefused(ValueError):
    def __init__(self, record, audit):
        self.record,self.audit=record,audit
        super().__init__(('Target unavailable: ' if not audit['candidates'] else 'Target ambiguity: ')+('no ACTIVE declaration matches the stated value.' if not audit['candidates'] else
            'multiple ACTIVE declaration candidates match: '+', '.join(c['column_id']+' ['+c['entry_id']+']' for c in audit['candidates'])))

def lookup(request, *, ticket, options, columns):
    """Lookup after translation, over conserved inventories from the pinned adapter."""
    if not isinstance(request,dict):raise ValueError('Target request requires an exact span')
    if not isinstance(options,list) or len(options)>512:raise ValueError('Target inventory context exceeds bound')
    fields(request,['source']+(['column_id'] if 'column_id' in request else []))
    quote=reported_figure.span(request['source'],ticket)
    named=request.get('column_id')
    if named is not None:
        column=next((c for c in columns if c['column_id']==named),None)
        if not column or quote!=column['name']:raise ValueError('STATED target must name the selected catalog column verbatim')
        if sum(c['name']==quote for c in columns)!=1:raise ValueError('Target ambiguity: the stated column name is not unique')
    matches={}
    for option in options:
        from .report_scope import validate_inventory
        entries=validate_inventory(option['inventory'],option['restrictions'],binding=option['evidence']['report_binding'],reports=option['evidence']['report_catalog'])
        for entry in entries:
            if entry['disposition']!='ACTIVE':continue
            for restriction in entry['restrictions']:
                matching=[v for v in restriction['values'] if literal_text(v)==quote]
                if (named==restriction['field_id'] if named is not None else bool(matching)):
                    key=(entry['id'],restriction['field_id'])
                    matches.setdefault(key,{'entry_id':entry['id'],'column_id':restriction['field_id'],
                        'value':matching[0] if matching else None,'option':option})
    candidates=[{'id':digest({'entry_id':e,'column_id':c}),'entry_id':e,'column_id':c}
                for e,c in sorted(matches)]
    if len(candidates)>512:raise ValueError('Target candidates exceed the consumer bound')
    audit={'match_count':len(candidates),'candidates':candidates,
           'status':'STATED_NO_ACTIVE_MATCH' if named is not None and not candidates else
                    'STATED_ACTIVE_MATCH' if named is not None else 'EVIDENCE' if len(candidates)==1 else 'REFUSED'}
    if named is not None:
        record={'resolution_kind':'STATED','column_id':named,'source':copy.deepcopy(request['source'])}
        return shape(record,ticket),audit,None
    if len(matches)!=1:
        record={'resolution_kind':'REFUSED','candidates':[c['id'] for c in candidates],'source':copy.deepcopy(request['source'])}
        raise ResolutionRefused(shape(record,ticket),audit)
    match=next(iter(matches.values()));option=match['option']
    record=evidence(match['column_id'],request['source'],match['entry_id'],ticket=ticket,
                    inventory=option['inventory'],active=option['restrictions'],binding=option['evidence']['report_binding'],reports=option['evidence']['report_catalog'])
    return record,audit,{'declaration_inventory':option['inventory'],'active_restrictions':option['restrictions'],
                        'resolved_value':match['value'],'inventory_report_binding':option['evidence']['report_binding'],'inventory_report_catalog':option['evidence']['report_catalog']}

def literal_text(value):
    return value if isinstance(value,str) else str(value).lower() if type(value) is bool else str(value)

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

def validate(value, *, ticket=None, inventory=None, active=None, binding=None, reports=None):
    shape(value,ticket)
    if value is not None and value['resolution_kind']=='EVIDENCE':
        from .report_scope import validate_inventory
        entries=validate_inventory(inventory,active,binding=binding,reports=reports)
        entry=next((e for e in entries if e['id']==value['inventory_entry_id']),None)
        if (entry is None or entry['disposition']!='ACTIVE'
                or not any(r['field_id']==value['column_id'] and
                    any(literal_text(v)==value['source']['quote'] for v in r['values']) for r in entry['restrictions'])):
            raise ValueError('Evidence target requires a matching ACTIVE inventory entry')
    return value

def evidence(column_id, source, inventory_entry_id, *, ticket, inventory, active, binding, reports):
    """Deterministic producer; no model response may assign EVIDENCE."""
    result={'resolution_kind':'EVIDENCE','column_id':column_id,
            'inventory_entry_id':inventory_entry_id,'source':copy.deepcopy(source)}
    return validate(result,ticket=ticket,inventory=inventory,active=active,binding=binding,reports=reports)

PROCEDURE_EVIDENCE_FIELDS=('reported_figure','definition_target','report_binding','selection_request','question_kind','numeral_mentions','expected_records','name_binding')


def server_evidence(source):
    """The procedure's one field declaration also owns its review handoff."""
    return {key:copy.deepcopy(source[key]) for key in PROCEDURE_EVIDENCE_FIELDS if key in source}


def procedure_scope(envelope):
    """Forward server-owned evidence unchanged, including explicit UNSPECIFIED."""
    result={k:copy.deepcopy(envelope[k]) for k in ('filters','dimension_ids')}
    result['ticket_shape']=envelope.get('ticket_shape')
    result.update(server_evidence(envelope))
    return result

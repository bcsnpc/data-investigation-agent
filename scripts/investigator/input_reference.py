"""Neutral supplied-reference proof, separate from names and clicked choices."""
import copy
from jsonschema import Draft202012Validator
from . import ticket_inputs, ticket_protocol as protocol
from .onboarding import digest

VERSION='ticket-report-reference-v1'
HASH={'type':'string','pattern':'^[0-9a-f]{64}$'}
SPAN=protocol.obj({'start':{'type':'integer','minimum':0},
                   'end':{'type':'integer','minimum':1},'quote':protocol.TEXT})
SCHEMA=protocol.obj({'version':{'const':VERSION},'model_id':protocol.ID,
    'report_id':protocol.ID,'page_id':{'anyOf':[protocol.ID,{'type':'null'}]},
    'source':SPAN,'request_hash':HASH,'source_input_hash':HASH,'report_catalog_hash':HASH,
    'scope_state':{'const':'NO_ADDITIONAL_RESTRICTIONS'}})


def catalog_hash(reports):
    return digest(sorted(reports,key=lambda r:r['id']))


def preflight(request):
    """An explicit primary link may never lose unsupported context at intake."""
    ticket_inputs.document(request)
    link=request.get('structured',{}).get('report_link')
    if link is not None:
        from .adapters.report_link import parse, LinkRefused
        parsed=parse(link)
        if parsed['predicates'] or parsed['bookmark_reference'] is not None:
            raise LinkRefused('DECLARED_LINK_CONTEXT_UNSUPPORTED: supplied predicate or bookmark context cannot yet be applied faithfully')


def from_input(request, ticket, models):
    document=ticket_inputs.document(request)
    if document['text']!=ticket:raise ValueError('Declared reference input document changed')
    link=request.get('structured',{}).get('report_link')
    if link is None:return None
    from .adapters.report_link import bind
    resolved=bind(link,models)
    model=next(m for m in models if m['id']==resolved['model_id'])
    part=next(p for p in document['provenance']['parts'] if p['pointer']=='/structured/report_link')
    result={'version':VERSION,**resolved,'source':{'start':part['start'],'end':part['end'],'quote':link},
            'request_hash':digest(ticket),'source_input_hash':digest(request),
            'report_catalog_hash':catalog_hash(model.get('reports',[]))}
    validate(result,reports=model.get('reports',[]),ticket=ticket)
    return result


def validate(reference, *, reports, ticket=None):
    Draft202012Validator(SCHEMA).validate(reference)
    source=reference['source']
    if source['end']-source['start']!=len(source['quote']):raise ValueError('Declared reference span differs')
    if ticket is not None and (reference['request_hash']!=digest(ticket) or
                              ticket[source['start']:source['end']]!=source['quote']):
        raise ValueError('Declared reference belongs to another request')
    if reference['report_catalog_hash']!=catalog_hash(reports):raise ValueError('Declared reference catalog changed')
    if sum(r['id']==reference['report_id'] for r in reports)!=1:
        raise ValueError('Declared reference report is absent or ambiguous')
    return reference


def binding(reference):
    return {'resolution_kind':'DECLARED_REFERENCE','report_id':reference['report_id'],
            'source':None,'reference':copy.deepcopy(reference)}

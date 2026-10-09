"""Closed optional user fields and their explicitly derived input document."""
from jsonschema import Draft202012Validator, ValidationError
from . import ticket_protocol as protocol
from .onboarding import digest

VERSION='ticket-input-document-v1'
ROUTE_VERSION='ticket-comparison-input-v1'
STRUCTURED=protocol.obj({'number':protocol.TEXT,'report_page':protocol.TEXT,'report_link':protocol.TEXT,
                         'comparison':{'enum':list(protocol.ROUTES)}},
                        optional=('number','report_page','report_link','comparison'))
STRUCTURED['minProperties']=1
REQUEST=protocol.obj({'text':{**protocol.TEXT,'minLength':0},
                     'request_key':{'type':'string','minLength':1,'maxLength':100},
                     'structured':STRUCTURED},optional=('structured',))
ROUTE_SCHEMA=protocol.obj({'version':{'const':ROUTE_VERSION},
                          'route':{'enum':list(protocol.ROUTES)},
                          'request_hash':{'type':'string','pattern':'^[0-9a-f]{64}$'},
                          'source_input_hash':{'type':'string','pattern':'^[0-9a-f]{64}$'}})


def active_request(saved):
    """The original envelope stays immutable; a user restatement is explicit."""
    request=saved['ticket'].get('current_input',saved['request'])
    document(request)
    return request


def document(request):
    """Keep user strings unchanged; labels are explicit document structure.

    This is a derived input document, not a claim that the user typed its
    labels. The original request and each supplied field's interval survive.
    No number, precision, target or comparator is generated here.
    """
    try:Draft202012Validator(REQUEST).validate(request)
    except ValidationError as exc:raise ValueError('User input does not satisfy the closed field contract') from exc
    pieces=[];parts=[];position=0
    for path,label,value in [('/text','',request['text']),
            ('/structured/number','Number specified by user:\n',request.get('structured',{}).get('number')),
            ('/structured/report_page','Report or page specified by user:\n',request.get('structured',{}).get('report_page')),
            ('/structured/report_link','Report link supplied by user:\n',request.get('structured',{}).get('report_link'))]:
        if not value:continue
        if pieces:pieces.append('\n\n');position+=2
        pieces.append(label);position+=len(label)
        start=position;pieces.append(value);position+=len(value)
        parts.append({'pointer':path,'start':start,'end':position,'source_hash':digest(value)})
    result=''.join(pieces)
    if not result:raise ValueError('Supply a question or a number/report description')
    if len(result)>protocol.TEXT['maxLength']:raise ValueError('Combined input document exceeds the intake consumer bound; nothing was truncated')
    return {'text':result,'provenance':{'version':VERSION,'source_input_hash':digest(request),
                                      'document_hash':digest(result),'parts':parts}}


def route(request, text, configuration):
    from .ticket_clarification import settings
    current=document(request)
    if current['text']!=text:raise ValueError('Input document differs from the retained request')
    choice=request.get('structured',{}).get('comparison')
    config=settings(configuration)
    if choice is None:return None
    if choice not in {c['route'] for c in config['comparison_choices']}:
        raise ValueError('Supplied comparison is not enabled for this estate')
    if 'COMPARISON' in config['must_confirm']:return None
    return {'version':ROUTE_VERSION,'route':choice,'request_hash':digest(text),
            'source_input_hash':digest(request)}

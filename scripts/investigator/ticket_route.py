"""A recorded comparison choice is independent of ticket subject and triage."""
import copy
import re
from jsonschema import Draft202012Validator
from . import ticket_protocol, intake_confirmation
from .onboarding import digest

VERSION='ticket-comparison-route-v1'
USER_SCHEMA=ticket_protocol.obj({'version':{'const':VERSION},
    'route':{'enum':list(ticket_protocol.ROUTES)},
    'confirmation':intake_confirmation.SCHEMA})
EVIDENCE_VERSION='ticket-comparison-request-v1'
EVIDENCE_SCHEMA={'oneOf':[ticket_protocol.obj({
    'version':{'const':EVIDENCE_VERSION},'route':{'const':route},
    'kind':{'const':kind},'request_hash':{'type':'string','pattern':'^[0-9a-f]{64}$'},
    'source':ticket_protocol.obj({'start':{'type':'integer','minimum':0},
        'end':{'type':'integer','minimum':1},'quote':ticket_protocol.TEXT})})
    for kind,route in [('FRESHNESS','STALE'),('SOURCE_CORRECTNESS','APPLICATION')]]}
SCHEMA={'oneOf':[USER_SCHEMA,EVIDENCE_SCHEMA]}


def from_request(raw, ticket):
    """A narrow explicit primary ask, never a triage-derived comparison.

    Secondary comparisons keep the question open. The extraction's kind alone
    is insufficient; the retained verbatim ask must independently name it.
    """
    from .intake_extraction import spans
    extraction=spans(raw,ticket,figure_occurrences=True)
    if extraction['comparisons']:return None
    source=extraction['primary'];ask=source['quote']
    freshness=bool(re.search(r'\b(stale|freshness|refresh|lag|up[ -]to[ -]date|current)\b',ask,re.I))
    application=bool(re.search(r'\b(application|source system|source records?|source data)\b',ask,re.I))
    if freshness and application:return None
    route=('STALE' if raw['kind']=='FRESHNESS' and freshness else
           'APPLICATION' if raw['kind']=='SOURCE_CORRECTNESS' and application else None)
    if route is None:return None
    return validate({'version':EVIDENCE_VERSION,'route':route,'kind':raw['kind'],
                     'request_hash':digest(ticket),'source':source},ticket)


def declared(confirmation):
    choice=confirmation['fields'].get('COMPARISON')
    if choice is None:raise ValueError('Comparison is not user-confirmed')
    result={'version':VERSION,'route':choice['value']['route'],
            'confirmation':copy.deepcopy(confirmation)}
    return validate(result)


def validate(value, ticket=None):
    Draft202012Validator(SCHEMA).validate(value)
    if value['version']==EVIDENCE_VERSION:
        if ticket is not None:
            source=value['source']
            if (value['request_hash']!=digest(ticket) or source['end']>len(ticket) or
                    source['start']>=source['end'] or ticket[source['start']:source['end']]!=source['quote']):
                raise ValueError('Comparison evidence is not a verbatim span of this ticket')
        return value
    choice=value['confirmation']['fields'].get('COMPARISON')
    if choice is None or choice['value']['route']!=value['route']:
        raise ValueError('Comparison route differs from the recorded user choice')
    if ticket is not None and value['confirmation']['request_hash']!=digest(ticket):
        raise ValueError('Comparison route belongs to a different ticket')
    return value


def admit(value):
    validate(value)
    from .question_kind import UnimplementedRoute
    if value['route']=='OTHER_REPORT':
        raise UnimplementedRoute('OTHER_REPORT requires the separate two-report design; no one-report walk was substituted.')
    if value['route']=='BUSINESS_MEANING':
        raise UnimplementedRoute('Business meaning requires business-owner validation; a technical walk cannot decide a business rule.')


def wants_freshness(scope):
    value=scope.get('ticket_route')
    if value:
        validate(value)
        if value['route'] in ('STALE','LOOKS_WRONG'):return True
    return (scope.get('question_kind') or {}).get('kind')=='FRESHNESS'

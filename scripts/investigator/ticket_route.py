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
    for kind,route in [('FRESHNESS','STALE'),('SOURCE_CORRECTNESS','APPLICATION'),
                       ('FIGURE_DIFFERENCE','APPLICATION'),('FIGURE_DIFFERENCE','LOOKS_WRONG')]]}
DEFAULT_VERSION='ticket-comparison-policy-v1'
DEFAULT_SCHEMA=ticket_protocol.obj({'version':{'const':DEFAULT_VERSION},
    'route':{'enum':['APPLICATION','STALE','LOOKS_WRONG']},
    'request_hash':{'type':'string','pattern':'^[0-9a-f]{64}$'},
    'configuration_hash':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
SUBJECT_VERSION='ticket-subject-route-v1'
SUBJECT_KINDS=('METRIC_COMPONENTS','DERIVED_CALCULATION','TRANSFORMATION_MECHANISM','FILTER_EFFECT','VISUAL_CONTENT','EXPECTED_BEHAVIOR')
SUBJECT_SCHEMA=ticket_protocol.obj({'version':{'const':SUBJECT_VERSION},
    'route':{'const':'DECLARED_SUBJECT'},'kind':{'enum':list(SUBJECT_KINDS)},
    'request_hash':{'type':'string','pattern':'^[0-9a-f]{64}$'},
    'source':copy.deepcopy(EVIDENCE_SCHEMA['oneOf'][0]['properties']['source'])})
from .ticket_inputs import ROUTE_SCHEMA as INPUT_SCHEMA, ROUTE_VERSION as INPUT_VERSION
SCHEMA={'oneOf':[USER_SCHEMA,EVIDENCE_SCHEMA,DEFAULT_SCHEMA,SUBJECT_SCHEMA,INPUT_SCHEMA]}


def settlement(raw, ticket, configuration, *, code_gate=False):
    """Configured defaults are policy evidence, never a fabricated user choice."""
    from .ticket_clarification import settings
    from .intake_extraction import spans
    config=settings(configuration)
    if 'COMPARISON' in config['must_confirm']:return None
    explicit=from_request(raw,ticket,code_gate=code_gate)
    if explicit is not None:return explicit
    extraction=spans(raw,ticket,figure_occurrences=True)
    scoped_self=(raw['kind']=='VISUAL_CONTENT' and extraction['comparisons'] and
                 all(re.fullmatch(r'(?:the )?global (?:value|total)',s['quote'],re.I) for s in extraction['comparisons']) and
                 any(i['role']=='PRIMARY' for i in extraction['selections']))
    declared_definitions=(raw['kind'] in SUBJECT_KINDS and bool(re.search(r'\bexplain\b[\s\S]*\bdefinitions?\b',extraction['primary']['quote'],re.I)) and
        not any(re.search(r'\b(?:application|source|another|other|second|report|stale|yesterday|earlier)\b',s['quote'],re.I) for s in extraction['comparisons']))
    if (extraction['comparisons'] and not scoped_self and not declared_definitions) or raw['kind'] in ('BUSINESS_MEANING','TEMPORAL_COMPARISON'):return None
    # A default may fill absence, never replace a named comparator or intent.
    if re.search(r'\b(application|source|stale|freshness|refresh|lag|another|other report|second report)\b',
                 extraction['primary']['quote'],re.I):return None
    if scoped_self or declared_definitions or raw['kind'] in SUBJECT_KINDS and not re.search(
            r'\b(compared|versus|against|than|elsewhere|yesterday|earlier|previous)\b',
            extraction['primary']['quote'],re.I) and re.search(
            (r'\b(what|which|how many)\b|\b(?:can|does|whether)\b[\s\S]*\breproduce\b' if raw['kind']=='VISUAL_CONTENT' else
             r'\b(how|why|explain|components?|composition|calculation|derived|mechanism|filters?)\b'),
            extraction['primary']['quote'],re.I):
        # A definition/filter/content question has an intrinsic subject, not a missing
        # external comparator. Do not manufacture "looks wrong" or freshness.
        return validate({'version':SUBJECT_VERSION,'route':'DECLARED_SUBJECT','kind':raw['kind'],
                         'request_hash':digest(ticket),'source':extraction['primary']},ticket)
    route=config['default_route']
    # A configured fallback is policy, not a checkable answer to a user question.
    # The asymmetric question gate must ask when text has not settled the route.
    if code_gate:return None
    if route not in ('APPLICATION','STALE','LOOKS_WRONG'):return None
    return validate({'version':DEFAULT_VERSION,'route':route,'request_hash':digest(ticket),
                     'configuration_hash':digest(config)},ticket)


def from_request(raw, ticket, *, code_gate=False):
    """A narrow explicit primary ask, never a triage-derived comparison.

    Secondary comparisons keep the question open. The extraction's kind alone
    is insufficient; the retained verbatim ask must independently name it.
    """
    from .intake_extraction import spans
    extraction=spans(raw,ticket,figure_occurrences=True)
    if extraction['comparisons'] and not code_gate:return None
    source=extraction['primary'];ask=source['quote']
    if code_gate and raw['kind'] not in ('BUSINESS_MEANING','TEMPORAL_COMPARISON'):
        scoped_self=(bool(extraction['selections']) and extraction['comparisons'] and
            all(re.fullmatch(r'(?:the )?global (?:value|total)',s['quote'],re.I)
                for s in extraction['comparisons']) and
            bool(re.search(r'\bexplain\b[^.!?\n]*\b(?:selected|declared|filter)\b[^.!?\n]*\bscope\b',ask,re.I)))
        if scoped_self:
            return validate({'version':SUBJECT_VERSION,'route':'DECLARED_SUBJECT',
                'kind':'VISUAL_CONTENT','request_hash':digest(ticket),'source':source},ticket)
    # A comparison phrase is not missing comparison evidence. Preserve genuinely
    # different named comparators, but do not re-ask a source/freshness ask merely
    # because extraction put its explicit words in the comparison list.
    if any(re.search(r'\b(?:another|other|second) report\b|\byesterday\b|\bearlier\b',s['quote'],re.I)
           for s in extraction['comparisons']):return None
    freshness=bool(re.search(r'\b(stale|freshness|refresh|lag|up[ -]to[ -]date)\b|\b(?:is|how|whether)\s+(?:it\s+is\s+|this\s+is\s+)?current\b',ask,re.I))
    application=bool(re.search(r'\b(application|source (?:system|records?|data|movements?|entries|total))\b',ask,re.I))
    # A bare declared comparator is evidence; "source mechanism" is not.
    if code_gate and any(re.fullmatch(r'(?:the )?source',s['quote'],re.I)
                         for s in extraction['comparisons']):application=True
    if freshness and application:return None
    looks_wrong=bool(re.search(r'\b(?:looks? (?:too )?(?:high|wrong)|overstated)\b',ask,re.I))
    route=('STALE' if raw['kind']=='FRESHNESS' and freshness else
           'APPLICATION' if raw['kind'] in ('SOURCE_CORRECTNESS','FIGURE_DIFFERENCE') and application else
           'LOOKS_WRONG' if code_gate and raw['kind']=='FIGURE_DIFFERENCE' and looks_wrong else None)
    kind=raw['kind']
    # Never replace the model's nomination with a keyword-derived kind. Both
    # independent sources must agree, and conflicting cues leave the question open.
    if code_gate:
        cues={name for name,present in [('STALE',freshness),('APPLICATION',application),
                                       ('LOOKS_WRONG',looks_wrong)] if present}
        # Wrong-looking values can also explicitly name their application comparator.
        if application:cues.discard('LOOKS_WRONG')
        if len(cues)!=1 or route not in cues:return None
    if route is None:return None
    return validate({'version':EVIDENCE_VERSION,'route':route,'kind':kind,
                     'request_hash':digest(ticket),'source':source},ticket)


def declared(confirmation):
    choice=confirmation['fields'].get('COMPARISON')
    if choice is None:raise ValueError('Comparison is not user-confirmed')
    result={'version':VERSION,'route':choice['value']['route'],
            'confirmation':copy.deepcopy(confirmation)}
    return validate(result)


def validate(value, ticket=None):
    Draft202012Validator(SCHEMA).validate(value)
    if value['version'] in (DEFAULT_VERSION,INPUT_VERSION):
        if ticket is not None and value['request_hash']!=digest(ticket):
            raise ValueError('Comparison policy belongs to a different ticket')
        return value
    if value['version'] in (EVIDENCE_VERSION,SUBJECT_VERSION):
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

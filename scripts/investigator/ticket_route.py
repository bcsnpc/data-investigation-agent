"""A recorded comparison choice is independent of ticket subject and triage."""
import copy
from jsonschema import Draft202012Validator
from . import ticket_protocol, intake_confirmation
from .onboarding import digest

VERSION='ticket-comparison-route-v1'
SCHEMA=ticket_protocol.obj({'version':{'const':VERSION},
    'route':{'enum':list(ticket_protocol.ROUTES)},
    'confirmation':intake_confirmation.SCHEMA})


def declared(confirmation):
    choice=confirmation['fields'].get('COMPARISON')
    if choice is None:raise ValueError('Comparison is not user-confirmed')
    result={'version':VERSION,'route':choice['value']['route'],
            'confirmation':copy.deepcopy(confirmation)}
    return validate(result)


def validate(value, ticket=None):
    Draft202012Validator(SCHEMA).validate(value)
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

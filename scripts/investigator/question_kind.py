"""Consumer-owned ticket subjects and implemented procedure routes."""
from .onboarding import fields

LEGACY_KINDS = ('VISUAL_CONTENT', 'FRESHNESS', 'SOURCE_CORRECTNESS', 'FIGURE_DIFFERENCE',
         'METRIC_COMPONENTS', 'DERIVED_CALCULATION', 'TRANSFORMATION_MECHANISM',
         'BUSINESS_MEANING', 'EXPECTED_BEHAVIOR')
KINDS = LEGACY_KINDS + ('FILTER_EFFECT', 'TEMPORAL_COMPARISON')
ROUTES = {'VERTICAL': True, 'NONE': True, 'HORIZONTAL': False}


class UnimplementedRoute(ValueError):
    pass


def intake_route(value):
    if value.get('action')!='PROPOSE':return
    kind=(value.get('question_kind') or {}).get('kind')
    if kind=='BUSINESS_MEANING':
        raise UnimplementedRoute('The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct.')
    if kind=='TEMPORAL_COMPARISON':
        raise UnimplementedRoute('The earlier-state comparison route is unimplemented; a current-state walk cannot answer a change between states.')


def validate(value, ticket=None):
    fields(value, ['kind', 'source'])
    if value['kind'] not in KINDS:
        raise ValueError('Unknown question kind: ' + str(value['kind']))
    from .reported_figure import span
    if ticket is not None:
        span(value['source'], ticket)
    return value


def route(mode):
    if mode not in ROUTES:
        raise ValueError('Unknown investigation route: ' + str(mode))
    if not ROUTES[mode]:
        raise UnimplementedRoute('Investigation route is unimplemented: ' + mode)


def reproduction(scope, walk_blocked=False):
    value = scope.get('question_kind')
    kind = value['kind'] if value else 'UNCLASSIFIED'
    if value:
        validate(value)
    selection = scope.get('selection_request') or scope.get('definition_target')
    applicable = kind in ('VISUAL_CONTENT','FILTER_EFFECT') or (
        walk_blocked and selection and scope.get('report_binding'))
    if scope.get('name_binding',{}).get('kind') in ('MODEL','LAYER'):
        return {'applicable':False,'kind':kind,
            'reason':'Declared-context reproduction is undeclared for model-only or layer-only named context.'}
    return {'applicable': bool(applicable), 'kind': kind,
            'reason': 'Declared-context reproduction is undeclared for question kind ' + kind +
                      (' before a blocked walk.' if selection else '.')}

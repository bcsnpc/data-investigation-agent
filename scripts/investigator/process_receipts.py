"""Closed producer registry for process evidence and its synthesis dispatch.

Recognition is not evidence validation. Each route still invokes the original
receipt validator; registration never makes an unavailable probe a finding.
"""
from dataclasses import dataclass
from .onboarding import Conflict


@dataclass(frozen=True)
class Shape:
    route: str
    table: str | None = None
    refusal_stage: str | None = None


REGISTRY = {
    'DECLARED_CONTEXT_REPRODUCTION': Shape('reproduction'),
    'DECLARED_CONTEXT_REPRODUCTION_UNAVAILABLE': Shape('retained'),
    'REPORT_SELECTION_RESOLUTION': Shape('resolution'),
    'REPORT_SELECTION_REFUSED': Shape('retained', refusal_stage='selection resolution'),
    'PROBE_NOT_EXECUTED': Shape('retained'),
    'COMPILED_DUPLICATE_REFUSED': Shape('duplicate'),
    'COLUMN_VALUE_EXISTENCE': Shape('query', 'flexible_diagnostics'),
    **{name: Shape('comparison') for name in
       ('CROSS_SURFACE_VERIFIED', 'NOT_COMPARABLE', 'WITHIN_LAYER_CHECK')},
    'DEFINITION_ABSENCE': Shape('retained'),
    'CAPABILITY_DECLARATION': Shape('retained'),
    'SOURCE_DELIVERY': Shape('retained'),
    'FRESHNESS_ATTEMPT': Shape('retained'),
    'EXPECTED_RECORD_PRESENCE': Shape('query','flexible_diagnostics'),
    'EXPECTED_RECORD_UNAVAILABLE': Shape('retained'),
    **{name: Shape('context') for name in ('CONTEXT_METADATA',
       'DECLARED_CONTEXT_DEFINITION', 'TRANSFORMATION_DEFINITION', 'INGESTION',
       'FRESHNESS', 'JOB_HISTORY', 'PRESENTATION_DEFINITION')},
    **{name: Shape('query', table) for name, table in {
       'native': 'native_diagnostics', 'source': 'source_diagnostics',
       'bounded_dax': 'flexible_diagnostics', 'bounded_sql': 'flexible_diagnostics',
       'bounded_fabric_sql': 'flexible_diagnostics', 'failure_detail': 'failure_details'}.items()},
    **{name: Shape('retained', refusal_stage=stage) for name, stage in {
       'INTAKE_REFUSED': 'intake', 'RESOLUTION_REFUSED': 'resolution',
       'INVENTORY_REFUSED': 'declaration inventory',
       'REPRODUCTION_REFUSED': 'declared-context reproduction',
       'WALK_REFUSED': 'process walk', 'UNIMPLEMENTED_ROUTE':'unimplemented route', 'PROCESS_FAILED':'process failure','BUDGET_STOP':'read budget'}.items()},
}

QUERY_TABLES = {name: spec.table for name, spec in REGISTRY.items()
                if spec.table and name != 'COLUMN_VALUE_EXISTENCE'}


def validate_for_synthesis(observation):
    name,spec=identify(observation)
    if name=='BUDGET_STOP':
        validate_budget(observation)
    if name=='PROCESS_FAILED':
        from .process_failure import validate
        validate(observation.get('failure'))
        if observation.get('reason')!=observation['failure']['message']:
            raise Conflict('Process failure reason differs from its safe diagnostic')
    # All registered query shapes require the same compiled-request and result
    # fields. A newly registered query cannot forget this consumer contract.
    if spec.route=='query' and observation.get('status')=='COMPLETED':
        for field in ('request_hash','values'):
            if field not in observation:
                raise Conflict('Registered process receipt '+name+' lacks required '+field)
    if name=='EXPECTED_RECORD_PRESENCE':
        from .record_presence import validate
        try:validate(observation)
        except (ValueError,KeyError,TypeError) as exc:raise Conflict('Expected-record presence differs from its original counts') from exc
    return name,spec


def identify(observation):
    """Use discriminants, never native kind strings or absence of recognition."""
    name = observation.get('check_kind')
    if name is None:
        name = observation.get('comparison_status')
    if name is None:
        tool = observation.get('tool')
        if tool == 'process':
            name = observation.get('comparison_status')
            if name is None and 'definition_absence' in observation.get('process_roles', []):
                name = 'DEFINITION_ABSENCE'
        elif tool == 'capability': name = 'CAPABILITY_DECLARATION'
        elif tool == 'context':
            roles = observation.get('process_roles', [])
            name = next((kind for role, kind in (
                ('declared_context_definition', 'DECLARED_CONTEXT_DEFINITION'),
                ('transformation_definition', 'TRANSFORMATION_DEFINITION'),
                ('ingestion', 'INGESTION'), ('freshness', 'FRESHNESS'),
                ('job_history', 'JOB_HISTORY'),
                ('presentation_definition', 'PRESENTATION_DEFINITION')) if role in roles), 'CONTEXT_METADATA')
        else: name = tool
    if name not in REGISTRY:
        raise Conflict('Unregistered process receipt shape: ' + str(name))
    return name, REGISTRY[name]


def summary(observation):
    """Every registered shape has a terminal display, without a finding upgrade."""
    name, spec = identify(observation)
    reason = observation.get('reason')
    return {'shape': name, 'stage': spec.refusal_stage,
            'text': reason if isinstance(reason, str) and reason.strip() else
                    'The ' + name.replace('_', ' ').lower() + ' receipt was retained.',
            'evidence_id': observation.get('id')}


def validate_budget(value):
    for key in ('diagnostic_reads','diagnostic_limit'):
        if type(value.get(key)) is not int or value[key]<0:
            raise Conflict('Budget stop lacks valid '+key)
    if value['diagnostic_reads']>value['diagnostic_limit']:
        raise Conflict('Budget stop exceeds declared diagnostic limit')
    for key in ('phase_counts','phase_limits'):
        mapping=value.get(key)
        if not isinstance(mapping,dict) or set(mapping)!= {'WALK','REPRODUCTION'} or any(type(n) is not int or n<0 for n in mapping.values()):
            raise Conflict('Budget stop lacks valid '+key)
    if sum(value['phase_counts'].values())!=value['diagnostic_reads'] or sum(value['phase_limits'].values())!=value['diagnostic_limit']:
        raise Conflict('Budget stop phase accounting does not conserve diagnostic counts')
    if not isinstance(value.get('admission_reason'),str) or not value['admission_reason'].strip():
        raise Conflict('Budget stop requires admission reason')
    if not isinstance(value.get('not_run_probes'),list) or any(not isinstance(p,dict) or not isinstance(p.get('operation'),str) for p in value['not_run_probes']):
        raise Conflict('Budget stop requires named pending probes')


def refusal(shape, reason, identity,*,failure=None,budget=None):
    spec = REGISTRY.get(shape)
    if spec is None or spec.refusal_stage is None:
        raise Conflict('Unregistered refusal receipt shape: ' + str(shape))
    if not isinstance(reason, str) or not reason.strip():
        raise Conflict('Refusal requires the original reason')
    extra={}
    if shape=='BUDGET_STOP':
        if not isinstance(budget,dict):raise Conflict('Budget stop requires accounting and pending probes')
        validate_budget(budget)
        extra.update(budget)
    if shape=='PROCESS_FAILED':
        from .process_failure import validate
        validate(failure)
        if reason!=failure['message']:raise Conflict('Process failure reason differs from its safe diagnostic')
        extra['failure']=failure
    return {'id': identity, 'tool': 'process', 'status': 'COMPLETED',
            'completeness': 'COMPLETE_RESPONSE', 'check_kind': shape, 'reason': reason,**extra}

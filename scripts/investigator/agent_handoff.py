"""Code-owned eligibility for an optional, bounded pipeline-gap agent.

Neither requests nor agent decisions can supply an activation record. Eligibility
is reconstructed from retained controller state and original observations.
"""
import copy
from contextlib import contextmanager
from contextvars import ContextVar
from jsonschema import Draft202012Validator
from .onboarding import digest, Conflict

VERSION = 'automatic-agent-handoff-v1'
ACTIVE = ContextVar('code_owned_automatic_handoff', default=None)
WORKSPACE = ContextVar('code_owned_automatic_handoff_workspace', default=None)
TRIGGERS = ('PIPELINE_GAP', 'UNREADABLE_TRANSFORMATION',
            'UNKNOWN_ROUTE_AFTER_QUESTION', 'CONFLICTING_LAYER_EVIDENCE', 'UNMATCHED_REPLY')
STEP_CEILINGS = {'PIPELINE_GAP': 12, 'UNREADABLE_TRANSFORMATION': 8,
                'UNKNOWN_ROUTE_AFTER_QUESTION': 4, 'CONFLICTING_LAYER_EVIDENCE': 12,
                'UNMATCHED_REPLY': 3}
SETTING = {'type': 'object', 'additionalProperties': False, 'properties': {
    'enabled': {'type': 'boolean'},
    'step_cap': {'type': 'integer', 'minimum': 1, 'maximum': 12},
    'wall_seconds': {'type': 'integer', 'minimum': 1, 'maximum': 900}},
    'required': ['enabled'],}
GAP_REASONS = frozenset(('LEGACY_ROUTE_ADMISSION_UNAVAILABLE',
    'VISUAL_PROJECTION_SCOPE_UNSUPPORTED', 'CLAIM_SCOPE_NOT_COMPILED',
    'CLAIM_MULTI_MODEL_OR_METRIC_UNSUPPORTED', 'CAPABILITY_NOT_IMPLEMENTED'))


def settings(workspace):
    value = workspace.agent.config.get('_estate', {}).get('investigation', {}).get('automatic_handoff')
    if value is None:
        return {'enabled': False, 'step_cap': 6, 'wall_seconds': 120}
    Draft202012Validator(SETTING).validate(value)
    return {'step_cap': 6, 'wall_seconds': 120, **copy.deepcopy(value)}


def candidates(source, result=None):
    """Only structured consumer facts qualify; generic HELD/prose is insufficient."""
    result = result or {}
    history = source.get('history', [])
    observations = result.get('observations', [])
    if not observations:
        observations = (result.get('session') or {}).get('observations', [])
    checks = result.get('checks') or {}
    finding = checks.get('validated_findings') or {}
    if not observations:
        observations=checks.get('observations',[]) or finding.get('observations',[])
    found = []
    if result.get('status') == 'HELD' and result.get('reason') in GAP_REASONS:
        found.append('PIPELINE_GAP')
    assessment = result.get('assessment') or finding.get('assessment') or {}
    process = assessment.get('support', {}).get('process', {})
    if assessment.get('classification') in ('NO_KNOWN_PATTERN', 'NO_COMPARABLE_PATH') and process.get('visibility_boundary', {}).get('stopped_by') == 'CAPABILITY_NOT_IMPLEMENTED':
        found.append('PIPELINE_GAP')
    definitions = [o for o in observations if 'transformation_definition' in o.get('process_roles', [])]
    skipped_definition = ('transformation_definition' in process.get('capabilities_declared', [])
        and any(s.get('step') == 5 and s.get('capability') == 'transformation_definition'
                for s in process.get('skipped_steps', [])))
    if skipped_definition or any(o.get('status') == 'UNAVAILABLE'
        or (o.get('judgment') or {}).get('status') == 'UNAVAILABLE' for o in definitions):
        found.append('UNREADABLE_TRANSFORMATION')
    replies = [h for h in history if h.get('kind') == 'REPLIED']
    asked = {h.get('question_id') for h in history if h.get('kind') == 'QUESTION_PLANNED'}
    if result.get('reason') == 'UNIMPLEMENTED_CLAIM_ROUTE' and any(h.get('question_id') in asked for h in replies):
        found.append('UNKNOWN_ROUTE_AFTER_QUESTION')
    ids = {o.get('id') for o in observations}
    differences = [o for o in observations if o.get('values_equal') is False
                   and o.get('comparison_status') == 'CROSS_SURFACE_VERIFIED'
                   and o.get('upper_evidence_id') in ids and o.get('lower_evidence_id') in ids
                   and o.get('upper_evidence_id') != o.get('lower_evidence_id')]
    no_explanation = skipped_definition or any((o.get('judgment') or {}).get('status') == 'COMPLETED'
        and (o.get('judgment') or {}).get('explains') is False for o in definitions)
    if differences and no_explanation:
        found.append('CONFLICTING_LAYER_EVIDENCE')
    unmatched = [h for h in history if h.get('kind') == 'REPLY_TYPE_MATCH'
                 and h.get('status') == 'NO_EXPECTED_TYPE' and h.get('question_id')
                 and isinstance(h.get('actual_fields'), list) and h.get('request_hash')]
    if unmatched and replies and unmatched[-1]['request_hash'] == replies[-1].get('request_hash'):
        found.append('UNMATCHED_REPLY')
    return [kind for kind in TRIGGERS if kind in found]


def authority(workspace, source, result=None):
    policy = settings(workspace)
    if not policy['enabled'] or not getattr(workspace, 'execution_enabled', False):
        return None
    if (source.get('automatic_handoff') or source.get('state') == 'BUSINESS_VALIDATION'
        or (source.get('claim') or {}).get('settled',{}).get('direction')=='DEFINITION'):
        return None
    kinds = candidates(source, result)
    if not kinds:
        return None
    policy['step_cap']=min(policy['step_cap'],STEP_CEILINGS[kinds[0]])
    original = {'source': copy.deepcopy(source), 'result': copy.deepcopy(result)}
    record = {'version': VERSION, 'kind': kinds[0], 'eligible_kinds': kinds,
              'origin': 'CODE_RECONSTRUCTED', 'source_hash': digest(original),
              'configuration_hash': digest(workspace.agent.config), 'policy': policy,
              'original': original}
    return dict(record, hash=digest(record))


def validate(workspace, record, *, retained):
    if not isinstance(record, dict):
        raise Conflict('Automatic handoff requires retained code authority')
    value = copy.deepcopy(record); sealed = value.pop('hash', None)
    if sealed != digest(value):
        raise Conflict('Automatic handoff authority changed')
    original = value.get('original') or {}
    rebuilt = authority(workspace, original.get('source') or {}, original.get('result'))
    if rebuilt != record:
        raise Conflict('Automatic handoff eligibility or policy changed')
    if not callable(retained) or retained() != record:
        raise Conflict('Automatic handoff authority is not retained by the controller')
    return record


def ticket_authority(workspace, record):
    identity = record.get('original', {}).get('source', {}).get('id')
    def retained():
        saved = workspace.smart_intake.tickets.get(identity)
        return saved['ticket'].get('automatic_handoff', {}).get('authority')
    return validate(workspace, record, retained=retained)


@contextmanager
def ticket_phase(workspace, record):
    ticket_authority(workspace, record)
    token = ACTIVE.set(record)
    port = WORKSPACE.set(workspace)
    try:
        yield
    finally:
        ACTIVE.reset(token)
        WORKSPACE.reset(port)


def controller_owned(workspace):
    record = ACTIVE.get()
    if record is None:
        return False
    ticket_authority(workspace, record)
    return True

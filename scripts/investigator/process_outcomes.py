"""Closed, evidence-bound outcomes for process debugging.

Historical assessment labels are mapped only when read. Stored records keep the
label and evidence contract that were valid when they were written.
"""

OUTCOMES = (
    'REFRESH_LATENCY', 'LOAD_LATENCY', 'PRESENTATION_LOGIC',
    'TRANSFORMATION_LOGIC', 'INGESTION_GAP', 'DEFECT',
    'CONSISTENT_TO_BOUNDARY', 'NO_COMPARABLE_PATH', 'DEFINITION_DIFFERENCE', 'SCOPE_DIFFERENCE',
    'DIFFERENT_SUBJECT', 'BUSINESS_QUESTION', 'NO_KNOWN_PATTERN')

ACTIONS = {
    'REFRESH_LATENCY': 'RECHECK_AFTER_REFRESH',
    'LOAD_LATENCY': 'RECHECK_AFTER_JOB',
    'PRESENTATION_LOGIC': 'CONFIRM_INTENT_OR_REQUEST_ENHANCEMENT',
    'TRANSFORMATION_LOGIC': 'CONFIRM_INTENT_OR_REQUEST_ENHANCEMENT',
    'INGESTION_GAP': 'ROUTE_OPERATIONAL_FIX',
    'DEFECT': 'RAISE_BUG_WITH_EVIDENCE',
    'CONSISTENT_TO_BOUNDARY': 'ASK_UPSTREAM_OWNER',
    'NO_COMPARABLE_PATH': 'NAME_MISSING_BINDING_OR_ACCESS',
    'DEFINITION_DIFFERENCE': 'DECIDE_BUG_OR_ENHANCEMENT',
    'SCOPE_DIFFERENCE': 'CONFIRM_SCOPE_INTENT',
    'DIFFERENT_SUBJECT': 'INFORMATIONAL',
    'BUSINESS_QUESTION': 'ASK_DOMAIN_SPECIALIST',
    'NO_KNOWN_PATTERN': 'FOLLOW_NAMED_NEXT_STEP',
}

# Roles are attached by deterministic adapters/procedures, not inferred from
# receipt prose. Every required group needs at least one completed receipt.
REQUIRED_ROLES = {
    'REFRESH_LATENCY': ('freshness', 'comparison'),
    'LOAD_LATENCY': ('job_history', 'comparison', 'prior_state'),
    'PRESENTATION_LOGIC': ('presentation_definition', 'comparison'),
    'TRANSFORMATION_LOGIC': ('transformation_definition', 'comparison'),
    'INGESTION_GAP': ('ingestion', 'flow_consistency', 'comparison'),
    'DEFECT': ('mechanism', 'comparison', 'definition_absence'),
    'CONSISTENT_TO_BOUNDARY': ('path', 'flow_consistency', 'comparison'),
    'NO_COMPARABLE_PATH': ('path',),
    'DEFINITION_DIFFERENCE': ('left_definition', 'right_definition'),
    'SCOPE_DIFFERENCE': ('left_scope', 'right_scope'),
    'DIFFERENT_SUBJECT': ('left_path', 'right_path'),
    'BUSINESS_QUESTION': ('flow_consistency', 'comparison'),
    'NO_KNOWN_PATTERN': ('established',),
}

BOUNDARY_ATTRIBUTIONS = {
    'REFRESH_LATENCY', 'LOAD_LATENCY', 'PRESENTATION_LOGIC',
    'TRANSFORMATION_LOGIC', 'DEFECT'}

OLD_TO_CURRENT = {
    'REFRESH_OR_FRESHNESS_ISSUE': 'REFRESH_LATENCY',
    'EXPECTED_BEHAVIOR': 'TRANSFORMATION_LOGIC',
    'LIKELY_TECHNICAL_DEFECT': 'NO_KNOWN_PATTERN',
    'SOURCE_OR_APPLICATION_ISSUE': 'CONSISTENT_TO_BOUNDARY',
    'BUSINESS_CONTEXT_REQUIRED': 'BUSINESS_QUESTION',
    'INSUFFICIENT_EVIDENCE': 'NO_KNOWN_PATTERN',
    'UNSUPPORTED': 'NO_KNOWN_PATTERN',
    'UNRESOLVED': 'NO_KNOWN_PATTERN',
}

STOP_REASONS = ('REACHED', 'NO_ACCESS', 'NO_LINEAGE', 'NOT_COMPARABLE',
                'BUDGET_EXHAUSTED', 'CAPABILITY_UNAVAILABLE', 'CAPABILITY_NOT_IMPLEMENTED')
BASELINE_STATUSES = ('ESTABLISHED', 'NOT_ESTABLISHED')
EVIDENCE_ROLES = tuple(sorted({role for roles in REQUIRED_ROLES.values() for role in roles}))


def read_label(label):
    """Project an old label without mutating its saved record."""
    return label if label in OUTCOMES else OLD_TO_CURRENT.get(label, 'NO_KNOWN_PATTERN')


def schema():
    refs = {'type': 'array', 'maxItems': 12, 'items': {'type': 'string'}}
    return {'type': 'object', 'additionalProperties': False, 'properties': {
        'procedure_step': {'type': 'integer', 'minimum': 0, 'maximum': 6},
        'recommended_action': {'type': 'string', 'enum': sorted(set(ACTIONS.values()))},
        'visibility_boundary': {'type': 'object', 'additionalProperties': False,
            'properties': {
                'deepest_layer': {'type': 'string', 'minLength': 1, 'maxLength': 300},
                'stopped_by': {'type': 'string', 'enum': list(STOP_REASONS)},
                'evidence_ids': refs},
            'required': ['deepest_layer', 'stopped_by', 'evidence_ids']},
        'baseline_above': {'type': 'object', 'additionalProperties': False,
            'properties': {
                'status': {'type': 'string', 'enum': list(BASELINE_STATUSES)},
                'layer': {'type': ['string', 'null'], 'maxLength': 300},
                'reason': {'type': ['string', 'null'], 'maxLength': 500},
                'evidence_ids': refs},
            'required': ['status', 'layer', 'reason', 'evidence_ids']},
        'evidence_by_role': {'type': 'object', 'additionalProperties': False,
            'properties': {role: refs for role in EVIDENCE_ROLES},
            'required': list(EVIDENCE_ROLES)},
        'missing_capability': {'type': ['string', 'null'], 'maxLength': 500},
        'skipped_steps': {'type':'array','maxItems':5,'items':{
            'type':'object','additionalProperties':False,'properties':{
                'step':{'type':'integer','minimum':1,'maximum':6},
                'capability':{'type':'string','minLength':1,'maxLength':80},
                'reason':{'type':'string','minLength':1,'maxLength':300}},
            'required':['step','capability','reason']}},
        'capabilities_declared': {'type':'array','maxItems':20,'items':{
            'type':'string','minLength':1,'maxLength':80}},
    }, 'required': ['procedure_step', 'recommended_action', 'visibility_boundary',
                    'baseline_above', 'evidence_by_role', 'missing_capability','skipped_steps',
                    'capabilities_declared']}


def validate(assessment, observations):
    """Enforce the outcome contract against deterministic receipt roles."""
    outcome = assessment['classification']
    if outcome not in OUTCOMES:
        raise ValueError('Unsupported process-debugging outcome')
    process = assessment.get('support', {}).get('process')
    if not isinstance(process, dict):
        raise ValueError('Process outcome requires process support')
    expected = set(schema()['required'])
    if set(process) != expected:
        raise ValueError('Process support fields differ')
    skipped=process['skipped_steps']
    if not isinstance(skipped,list) or len(skipped)>5 or any(
            not isinstance(x,dict) or set(x)!={'step','capability','reason'}
            or type(x['step']) is not int or not 1<=x['step']<=6
            or not isinstance(x['capability'],str) or not 1<=len(x['capability'])<=80
            or not isinstance(x['reason'],str) or not 1<=len(x['reason'])<=300 for x in skipped):
        raise ValueError('Skipped procedure steps differ')
    capabilities=process['capabilities_declared']
    if (not isinstance(capabilities,list) or len(capabilities)>20
            or capabilities!=sorted(set(capabilities))
            or any(not isinstance(x,str) or not 1<=len(x)<=80 for x in capabilities)):
        raise ValueError('Declared capabilities must be a sorted unique list')
    required_capability={'REFRESH_LATENCY':'presentation_freshness','LOAD_LATENCY':'job_history',
        'PRESENTATION_LOGIC':'presentation_context','TRANSFORMATION_LOGIC':'transformation_definition',
        'INGESTION_GAP':'ingestion'}
    needed=required_capability.get(outcome)
    if needed and needed not in capabilities:
        raise ValueError(f'{outcome} requires declared {needed} capability')
    if outcome=='DEFECT' and ({'transformation_definition','job_history'}-set(capabilities)
            or any(x['step'] in (3,5) for x in skipped)):
        raise ValueError('DEFECT requires every competing definition/context and job check to execute')
    if process['recommended_action'] != ACTIONS[outcome]:
        raise ValueError('Recommended action does not match outcome')
    boundary = process['visibility_boundary']
    if not isinstance(boundary, dict) or set(boundary) != {'deepest_layer', 'stopped_by', 'evidence_ids'}:
        raise ValueError('Every outcome requires a visibility boundary')
    if not isinstance(boundary['deepest_layer'], str) or not boundary['deepest_layer'].strip():
        raise ValueError('Visibility boundary must name the deepest layer checked')
    if boundary['stopped_by'] not in STOP_REASONS:
        raise ValueError('Unknown visibility-boundary stop reason')
    baseline = process['baseline_above']
    if not isinstance(baseline, dict) or set(baseline) != {'status', 'layer', 'reason', 'evidence_ids'}:
        raise ValueError('Baseline support fields differ')
    if baseline['status'] not in BASELINE_STATUSES:
        raise ValueError('Unknown baseline status')
    if baseline['status'] == 'ESTABLISHED' and (not baseline['layer'] or baseline['reason'] is not None):
        raise ValueError('Established baseline needs a layer and no failure reason')
    if baseline['status'] == 'NOT_ESTABLISHED' and (not isinstance(baseline['reason'], str) or not baseline['reason'].strip()):
        raise ValueError('Missing baseline requires a specific reason')
    if outcome in BOUNDARY_ATTRIBUTIONS and baseline['status'] == 'NOT_ESTABLISHED' and len(baseline['reason'].strip()) < 8:
        raise ValueError('Boundary attribution needs a baseline above it or a specific establishment barrier')
    groups = process['evidence_by_role']
    if not isinstance(groups, dict) or set(groups)!=set(EVIDENCE_ROLES):
        raise ValueError('Process evidence roles must be an object')
    outer = set(assessment['evidence_ids'])
    def checked(refs, role):
        if not isinstance(refs, list) or not refs:
            raise ValueError(f'{outcome} requires {role} evidence')
        for ref in refs:
            observation = observations.get(ref)
            if ref not in outer or not observation or observation.get('status') != 'COMPLETED':
                raise ValueError('Process support must cite completed assessment evidence')
            roles = observation.get('process_roles', [])
            if role not in roles and not (outcome=='NO_KNOWN_PATTERN' and role=='established'):
                raise ValueError(f'Receipt is not deterministically tagged for {role}')
    for role in REQUIRED_ROLES[outcome]:
        checked(groups.get(role), role)
    for ref in boundary['evidence_ids']:
        if ref not in outer or ref not in observations:
            raise ValueError('Visibility boundary must cite assessment evidence')
    for ref in baseline['evidence_ids']:
        if ref not in outer or ref not in observations:
            raise ValueError('Baseline must cite assessment evidence')
    if baseline['status'] == 'ESTABLISHED':
        checked(baseline['evidence_ids'], 'baseline')
    gap_outcomes=('NO_KNOWN_PATTERN','NO_COMPARABLE_PATH')
    if outcome in gap_outcomes and (not isinstance(process['missing_capability'], str)
                                     or len(process['missing_capability'].strip())<12):
        raise ValueError(f'{outcome} requires a specific missing capability')
    if outcome not in gap_outcomes and process['missing_capability'] is not None:
        raise ValueError('Only capability-gap outcomes carry a missing capability')
    if outcome == 'NO_COMPARABLE_PATH' and baseline['status']!='ESTABLISHED':
        raise ValueError('NO_COMPARABLE_PATH requires an established presentation baseline')
    comparisons=[observations[ref] for ref in groups.get('comparison',[]) if ref in observations]
    if outcome in ('CONSISTENT_TO_BOUNDARY','INGESTION_GAP','BUSINESS_QUESTION') and not any(
            comparison.get('values_equal') is True for comparison in comparisons):
        raise ValueError(f'{outcome} requires at least one successful equal boundary comparison')
    if outcome in ('REFRESH_LATENCY','LOAD_LATENCY','PRESENTATION_LOGIC','TRANSFORMATION_LOGIC','DEFECT') and not any(
            comparison.get('values_equal') is False for comparison in comparisons):
        raise ValueError(f'{outcome} requires an observed divergent boundary comparison')
    if outcome in BOUNDARY_ATTRIBUTIONS and not any(
            comparison.get('values_equal') is False and comparison.get('upper_layer')==baseline['layer']
            for comparison in comparisons):
        raise ValueError('Boundary attribution baseline must be immediately above the divergent boundary')
    if outcome in ('PRESENTATION_LOGIC','TRANSFORMATION_LOGIC'):
        claim=assessment.get('claim','').lower()
        if any(phrase in claim for phrase in ('is correct','was correct','expected behavior','works as intended')):
            raise ValueError('Implemented logic must be described neutrally and ask for confirmation of intent')
    return process

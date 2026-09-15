"""Versioned capability decisions; reference analysis never proves semantics."""
from .onboarding import digest

VERSION = 'capabilities-v1'
CONTEXT_OPERATIONS = {'FILTERED_MEASURE', 'TIME_SHIFT', 'RELATIONSHIP_SWITCH', 'CONDITIONAL', 'FILTER_CONTEXT'}


def axis(state, reason):
    return {'state': state, 'reason': reason}


def evaluate(model):
    context = model.get('context') or {}
    nodes = context.get('semantic_graph', {}).get('measures', {})
    measures = {}
    for measure in context.get('measures', []):
        identity = measure['id']
        node = nodes.get(identity)
        gaps = list(node.get('gaps', [])) if node else ['Dependency analysis missing']
        # The analyzer only discovers references. Even a clean graph is not a
        # certificate for inherited filter/row/relationship semantics.
        context_sensitive = bool(node and set(node['operations']) & CONTEXT_OPERATIONS)
        measures[identity] = {
            'name': measure['name'],
            'operations': node['operations'] if node else [],
            'gaps': gaps,
            'capabilities': {
                'MEASURE_DEFINITION_AVAILABLE': axis('SUPPORTED', 'Retained definition in this immutable context'),
                'NATIVE_QUERY_ADMISSION': axis('SUPPORTED' if model['enabled'] else 'UNSUPPORTED',
                    'Explicit plan validation is still required' if model['enabled'] else 'Model catalog is disabled'),
                'NATIVE_EXECUTION': axis('UNKNOWN', 'A metadata scan does not prove a native query succeeds'),
                'DEPENDENCY_DISCOVERY': axis(node['dependency_state'] if node else 'UNKNOWN',
                    'Conservative reference analysis only'),
                'DEPENDENCY_CONTEXT': axis('PARTIAL' if node else 'UNKNOWN',
                    'Context-changing operations require certification' if context_sensitive else
                    'Discovered references do not certify effective child contexts'),
                'VISUAL_CONTEXT_REPLAY': axis('UNKNOWN', 'Full visual filters and effective identity are not certified'),
                'UPSTREAM_RECONCILIATION': axis('UNSUPPORTED', 'No v2 upstream equivalence adapter registered'),
                'SOURCE_PROVENANCE_VERIFIED': axis('UNKNOWN', 'No comparable source generation established'),
                'ROOT_CAUSE_VERIFICATION': axis('UNSUPPORTED', 'No v2 causal verifier registered'),
            },
        }
    result = {'version': VERSION, 'model_id': model['id'], 'revision': model['revision'],
              'context_id': model['context_id'], 'context_hash': digest(context),
              'readiness': 'PARTIAL' if measures else 'UNKNOWN', 'measures': measures,
              'execution_available': False,
              'limitation': 'Catalog capabilities do not dispatch queries or certify business correctness.'}
    return dict(result, decision_hash=digest(result))


def assess(model, plan):
    # Import here to keep the compiler independent of capability projections.
    from .native_diagnostics import build
    request = build(model, plan)
    capabilities = evaluate(model)
    selected = {identity: capabilities['measures'][identity] for identity in request['measure_ids']}
    result = {'version': VERSION, 'model_id': model['id'], 'revision': model['revision'],
              'context_id': model['context_id'], 'context_hash': request['context_hash'],
              'scope_hash': request['scope_hash'], 'request_hash': digest(request),
              'admitted': True, 'intent': 'NATIVE_DIAGNOSTIC_ONLY',
              'measures': selected, 'dependency_gaps': request['gaps'],
              'verification_eligible': False, 'execution_available': False,
              'reason': 'Valid for an explicit operator read; no cause, visual or cross-system proof'}
    return dict(result, decision_hash=digest(result))

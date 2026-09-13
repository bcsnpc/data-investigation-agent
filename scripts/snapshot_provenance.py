"""Validate publication-run continuity without inventing immutable snapshots."""
from uuid import UUID


def marker(result, name):
    if result.get('error'):
        return {'status': 'UNKNOWN', 'reason': 'Query unavailable'}
    values = result.get('values', {})
    try:
        # Reject decimal, negative or malformed counts rather than coercing them.
        counts = [values[key] for key in ('provenance_rows', name+'_count', name+'_nulls')]
        if any(type(v) not in (int, str) or not str(v).isdigit() for v in counts):
            raise ValueError('Invalid counts')
        rows, distinct, nulls = map(int, counts)
        if nulls > rows or distinct > rows:
            raise ValueError('Inconsistent counts')
        if rows == 0:
            return {'status': 'UNKNOWN', 'reason': 'Empty scope has no row provenance'}
        if nulls or distinct != 1:
            return {'status': 'MIXED_OR_MISSING', 'rows': rows, 'distinct': distinct, 'nulls': nulls}
        run = str(UUID(values[name]))
        return {'status': 'SINGLE_RUN', 'run_id': run, 'rows': rows}
    except (KeyError, ValueError, TypeError, AttributeError):
        return {'status': 'UNKNOWN', 'reason': 'Invalid or missing run evidence'}


def continuity(raw):
    silver = marker(raw.get('silver', {}), 'silver_run')
    gold_input = marker(raw.get('gold', {}), 'silver_run')
    gold = marker(raw.get('gold', {}), 'gold_run')
    semantic = marker(raw.get('semantic', {}), 'gold_run')
    checks = []
    for upstream, downstream, left, right in [('silver', 'gold', silver, gold_input), ('gold', 'semantic', gold, semantic)]:
        status = 'UNKNOWN'
        if left['status'] == right['status'] == 'SINGLE_RUN':
            status = 'RUN_ALIGNED' if left['run_id'] == right['run_id'] else 'RUN_MISMATCH'
        elif 'MIXED_OR_MISSING' in (left['status'], right['status']):
            status = 'MIXED_OR_MISSING'
        checks.append({'upstream': upstream, 'downstream': downstream, 'status': status,
                       'upstream_evidence': left, 'downstream_evidence': right})
    return {'checks': checks, 'source_snapshot': None,
            'gaps': ['SQL extraction snapshot not captured', 'Bronze read not pinned to Delta versions',
                     'Run markers do not prove immutable table contents or complete dependency versions'],
            'classification': 'UNRESOLVED'}

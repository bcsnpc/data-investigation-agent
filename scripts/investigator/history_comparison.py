"""Match native current/history reads of the same declared-source calculation.

This checks observed net change for the queried scope, not every historic edit.
No current-only query is treated as history and no missing retention is guessed.
"""
from sqlglot import parse_one, exp
from datetime import datetime, timezone


def instant(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def load_anchor(case):
    anchors = []
    def visit(value):
        if isinstance(value, list):
            for row in value:visit(row)
        elif isinstance(value, dict):
            if value.get('kind') in ('JOB_RUN', 'TABLE_LOAD') and value.get('state') == 'OBSERVED':
                native = value.get('value', {})
                if str(native.get('status', '')).casefold() in ('completed', 'succeeded', 'success'):
                    for key in ('end', 'end_time', 'endTimeUtc', 'endTime', 'ended_at'):
                        try:anchors.append(instant(native[key]))
                        except (KeyError, ValueError, TypeError):pass
            for key, child in value.items():
                if key not in ('previous', 'retained'):visit(child)
    visit(case.get('triage', {}))
    visit(list(case.get('evidence', {}).values()))
    return max(anchors) if anchors else None


def signature(query, dialect):
    tree = parse_one(query, read=dialect)
    versions = list(tree.find_all(exp.Version))
    for table in tree.find_all(exp.Table):
        table.set('version', None)
    return tree.sql(dialect=dialect, normalize=True, comments=False), versions


def disposition(case, evidence_ids):
    declaration = case.get('context', {}).get('system_of_record', {})
    layer = declaration.get('layer')
    if not layer:
        return {'ruled_out': False, 'reason': 'No declared source layer is resolved.'}
    anchor = load_anchor(case)
    if anchor is None:
        return {'ruled_out': False, 'reason': 'No successful native load end time anchors the historical source comparison.'}
    selected = []
    for q in case.get('queries', []):
        if q['id'] not in evidence_ids or q.get('layer') != layer or q.get('status') != 'SUCCEEDED':continue
        rows = q.get('result', {}).get('rows', [])
        if len(rows) != 1 or not isinstance(rows[0], dict) or len(rows[0]) != 1:continue
        if declaration.get('asset_id') and declaration['asset_id'] not in q.get('asset_ids', []):continue
        dialect = 'spark' if case['context'].get('layers', {}).get(layer, {}).get('dialect') == 'Spark SQL' else 'tsql'
        try: shape, versions = signature(q.get('text', ''), dialect)
        except Exception:continue
        selected.append((q, shape, versions, next(iter(rows[0].values()))))
    for historical, shape, versions, value in selected:
        if not versions or any(v.args.get('kind') != 'AS OF' for v in versions):continue
        try:
            if any(v.args.get('this') != 'TIMESTAMP' or
                   not isinstance(v.expression, exp.Literal) or
                   abs((instant(v.expression.this) - anchor).total_seconds()) > 1 for v in versions):continue
        except (ValueError, TypeError):continue
        for current, current_shape, current_versions, current_value in selected:
            if not current_versions and current_shape == shape and current_value == value:
                return {'ruled_out': True, 'basis': 'SAME_DECLARED_SOURCE_CALCULATION_CURRENT_AND_NATIVE_AS_OF_AGREE',
                        'query_ids': [historical['id'], current['id']],
                        'load_anchor_utc': anchor.isoformat(),
                        'qualification': 'No net change for this measured calculation between the retained snapshot and current read; other edits are not excluded.'}
    return {'ruled_out': False, 'reason': 'A comparable native source-history read has not ruled out a net change for this scope.'}

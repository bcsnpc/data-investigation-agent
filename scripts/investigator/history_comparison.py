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
    arrival=record_arrival(case,evidence_ids,declaration,anchor)
    if arrival:return arrival
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


def record_arrival(case,evidence_ids,declaration,anchor):
    """Native keyed absence at load versus current presence can support latency.

    Arrival is itself a source change; requiring *unchanged* source values would
    make ordinary new-record latency impossible. This establishes no earlier
    deletion timeline, no business cause, and no downstream absence by itself.
    """
    if not declaration.get('asset_id'):return None
    dialect='spark' if case['context'].get('layers',{}).get(declaration['layer'],{}).get('dialect')=='Spark SQL' else 'tsql'
    selected=[]
    for q in case.get('queries',[]):
        if q.get('id') not in evidence_ids or q.get('status')!='SUCCEEDED' or q.get('layer')!=declaration['layer'] or q.get('asset_ids')!=[declaration['asset_id']]:continue
        result=q.get('result') or {}
        if result.get('truncated') or q.get('truncated'):continue
        rows=result.get('rows')
        if not isinstance(rows,list) or len(rows)>1:continue
        try:
            tree=parse_one(q['text'],read=dialect)
            if not isinstance(tree,exp.Select) or len(list(tree.find_all(exp.Select)))!=1:continue
            if any(tree.args.get(k) for k in ('joins','limit','offset','group','having','distinct','qualify')):continue
            if any(not isinstance(e.this if isinstance(e,exp.Alias) else e,exp.Column) for e in tree.expressions):continue
            tables=list(tree.find_all(exp.Table));where=tree.args.get('where')
            if len(tables)!=1 or not where or not isinstance(where.this,exp.EQ):continue
            eq=where.this
            if not ((isinstance(eq.this,exp.Column) and isinstance(eq.expression,exp.Literal)) or (isinstance(eq.expression,exp.Column) and isinstance(eq.this,exp.Literal))):continue
            versions=list(tree.find_all(exp.Version));tables[0].set('version',None)
            shape=(tables[0].sql(dialect=dialect,normalize=True),where.sql(dialect=dialect,normalize=True))
            historical=bool(versions)
            if historical and any(v.args.get('kind')!='AS OF' or v.args.get('this')!='TIMESTAMP' or not isinstance(v.expression,exp.Literal) or abs((instant(v.expression.this)-anchor).total_seconds())>1 for v in versions):continue
            selected.append((q,shape,historical,rows))
        except Exception:continue
    for historical,shape,is_history,rows in selected:
        if not is_history or rows:continue
        for current,current_shape,current_history,current_rows in selected:
            if not current_history and current_shape==shape and len(current_rows)==1:
                return {'ruled_out':True,'basis':'KEY_ABSENT_AT_NATIVE_LOAD_END_PRESENT_NOW',
                    'query_ids':[historical['id'],current['id']],'load_anchor_utc':anchor.isoformat(),
                    'qualification':'The keyed source row was absent at the completed load and is present now. This supports arrival after that load, not an earlier deletion/reinsertion timeline or a completed next load.'}
    return None

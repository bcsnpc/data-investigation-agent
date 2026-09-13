"""Deterministic checks over acquired evidence; never execute supplied SQL or code."""
import argparse
from collections import Counter
from contextlib import closing
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import sqlite3
import uuid

from lineage_graph import load_graph
from lineage_gap_policy import eligibility


def timestamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timezone required')
    return result.astimezone(timezone.utc)


def number(value):
    # Binary floating point, booleans, null and non-finite values are not evidence.
    if type(value) not in (str, int):
        raise ValueError('Use decimal strings or integers')
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError('Invalid decimal') from exc
    if not result.is_finite():
        raise ValueError('Finite decimal required')
    return result


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def observation(value):
    for key in ('asset', 'captured_at', 'query_id', 'result_hash'):
        if not isinstance(value.get(key), str) or not value[key]:
            raise ValueError('Observation requires ' + key)
    timestamp(value['captured_at'])
    payload = value.get('data')
    digest = hashlib.sha256(canonical(payload).encode()).hexdigest()
    if value['result_hash'] != digest:
        raise ValueError('Observation payload hash mismatch')


def compatible(left, right):
    """An acquisition time is not a common source snapshot or business contract."""
    missing = []
    for key in ('metric_contract', 'grain', 'currency', 'filters', 'source_snapshot'):
        a, b = left.get(key), right.get(key)
        if a is None or b is None or a == '' or b == '':
            missing.append(key + ': missing')
        elif canonical(a) != canonical(b):
            missing.append(key + ': different')
        elif key == 'filters' and not isinstance(a, dict):
            missing.append(key + ': expected filter object')
        elif key in ('metric_contract', 'grain', 'currency') and (not isinstance(a, str) or not a.strip()):
            missing.append(key + ': expected nonempty identifier')
        elif key == 'source_snapshot' and (not isinstance(a, (str, dict)) or not a):
            missing.append(key + ': expected snapshot identifier or version map')
    return missing


def compare(left, right, mode):
    observation(left)
    observation(right)
    if mode not in ('total', 'keys'):
        raise ValueError('Unknown comparison mode')
    reasons = compatible(left, right)
    if reasons:
        return {'status': 'NOT_COMPARABLE', 'reasons': reasons}
    if mode == 'total':
        a, b = number(left['data']), number(right['data'])
        # Decimal subtraction needs sufficient precision even for large inputs.
        from decimal import localcontext
        with localcontext() as context:
            context.prec = max(len(a.as_tuple().digits), len(b.as_tuple().digits)) + abs(a.adjusted()-b.adjusted()) + abs(a.as_tuple().exponent-b.as_tuple().exponent) + 4
            difference = b-a
        return {'status': 'MATCH' if a == b else 'MISMATCH',
                'upstream': str(a), 'downstream': str(b), 'downstream_minus_upstream': str(difference)}
    def keys(data):
        if not isinstance(data, list):
            raise ValueError('Keys require a complete list of composite key arrays')
        for row in data:
            if not isinstance(row, list) or not row or any(type(x) not in (str, int) for x in row):
                raise ValueError('Non-null string/integer composite keys required')
        return Counter(canonical(row) for row in data)
    if left.get('complete') is not True or right.get('complete') is not True:
        return {'status': 'NOT_COMPARABLE', 'reasons': ['Complete key extracts required']}
    a, b = keys(left['data']), keys(right['data'])
    missing, extra = a-b, b-a
    return {'status': 'MATCH' if a == b else 'MISMATCH',
            'missing_count': sum(missing.values()), 'extra_count': sum(extra.values()),
            'upstream_duplicate_count': sum(n-1 for n in a.values()),
            'downstream_duplicate_count': sum(n-1 for n in b.values()),
            'missing_sample': [json.loads(k) for k in sorted(missing)[:20]],
            'extra_sample': [json.loads(k) for k in sorted(extra)[:20]]}


def freshness(evidence, as_of, max_age_seconds=None):
    observation(evidence)
    if not isinstance(evidence['data'], dict):
        raise ValueError('Refresh evidence requires an object')
    if max_age_seconds is not None and (type(max_age_seconds) is not int or max_age_seconds < 0):
        raise ValueError('Freshness policy must be nonnegative integer seconds')
    now = timestamp(as_of)
    if timestamp(evidence['captured_at']) > now:
        return {'status': 'UNKNOWN', 'reason': 'Evidence acquired after evaluation time'}
    completed = evidence['data'].get('last_success_at')
    if completed is None:
        return {'status': 'UNKNOWN', 'reason': 'Successful refresh time unavailable'}
    age = (now-timestamp(completed)).total_seconds()
    if age < 0 or timestamp(completed) > timestamp(evidence['captured_at']):
        return {'status': 'UNKNOWN', 'reason': 'Inconsistent refresh timestamps'}
    if max_age_seconds is None:
        return {'status': 'UNKNOWN', 'age_seconds': age, 'reason': 'No configured freshness policy'}
    return {'status': 'WITHIN_POLICY' if age <= max_age_seconds else 'STALE',
            'age_seconds': age, 'max_age_seconds': max_age_seconds,
            'limitation': 'Refresh completion does not prove business-data currency'}


def run_checks(database, request):
    """Pin checks to a stored graph; persist all inputs and outputs atomically."""
    lineage_run = request['lineage_run']
    as_of = timestamp(request['as_of'])
    graph = load_graph(database, lineage_run)
    results = []
    for check in request['checks']:
        kind = check['kind']
        observations = [check['observation']] if kind == 'freshness' else [check['upstream'], check['downstream']]
        for item in observations:
            observation(item)
            if timestamp(item['captured_at']) > as_of:
                raise ValueError('Observation acquired after evaluation time')
            if item['asset'] not in graph.assets:
                raise ValueError('Evidence asset absent from pinned lineage build')
        if kind == 'freshness':
            result = freshness(observations[0], request['as_of'], check.get('max_age_seconds'))
        else:
            upstream, downstream = observations
            trace = graph.traverse(downstream['asset'])
            connected = upstream['asset'] != downstream['asset'] and upstream['asset'] in {a['id'] for a in trace['assets']}
            if not connected:
                raise ValueError('Comparison boundary has no upstream lineage path')
            result = compare(upstream, downstream, kind)
            result['lineage_gaps'] = trace['unresolved']
            gate=eligibility(graph,downstream['asset'])
            result['lineage_eligibility']=gate
            if not gate['lineage_conclusions_allowed']:
                result['comparison_status']=result['status']
                result['status']='INSUFFICIENT_EVIDENCE'
            result['affected_assets'] = [a['id'] for a in graph.traverse(downstream['asset'], 'downstream')['assets']]
        results.append({'kind': kind, 'result': result})
    if not results:
        raise ValueError('At least one check required')
    timestamp(request['as_of'])
    run = str(uuid.uuid4())
    output = {'id': run, 'lineage_run': lineage_run, 'classification': 'UNRESOLVED',
              'checks': results, 'limitation': 'Check outcomes alone do not establish root cause or expected business behavior'}
    with closing(sqlite3.connect(database)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS investigation_runs(id TEXT PRIMARY KEY, lineage_run TEXT NOT NULL, created TEXT NOT NULL, request TEXT NOT NULL, result TEXT NOT NULL)')
        db.execute('INSERT INTO investigation_runs VALUES(?,?,?,?,?)',
                   (run, lineage_run, datetime.now(timezone.utc).isoformat(), canonical(request), canonical(output)))
        db.commit()
    return output


def resolve_context(database, lineage_run, report_id, metric):
    """Resolve a measure only within the selected report's captured dependencies."""
    graph = load_graph(database, lineage_run)
    report = graph.assets.get(report_id)
    if not report or report['kind'] != 'Report':
        raise ValueError('Known report ID required')
    trace = graph.traverse(report_id)
    matches = [a for a in trace['assets'] if a['kind'] == 'Measure' and a['name'].casefold() == metric.casefold()]
    return {'status': 'RESOLVED' if len(matches) == 1 else 'UNRESOLVED',
            'report': report_id, 'metric_candidates': matches, 'lineage_run': lineage_run,
            'lineage_gaps': trace['unresolved'],
            'lineage_eligibility': eligibility(graph,report_id),
            'limitation': 'Captured dependencies do not reproduce active report slicers'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--request', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run_checks(args.database, json.loads(args.request.read_text(encoding='utf-8'))), indent=2))

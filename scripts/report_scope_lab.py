"""Local report-filter replay over Gold; no Power BI or DAX execution."""
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from uuid import uuid4
import duckdb
from lab_investigator import reconcile

SCOPES = {'all_orders': '', 'exclude_partial_returns': " WHERE status <> 'PARTIALLY_RETURNED'"}
LIMIT = 'Local SQL simulation of a report filter over one Gold snapshot. Does not verify a deployed report, DAX measure, relationships, RLS or production root cause.'


def capture(path, requested_scope, report_scope):
    if requested_scope is not None and requested_scope not in SCOPES:
        raise ValueError('Unsupported requested scope')
    if report_scope not in SCOPES:
        raise ValueError('Unsupported report scope')
    if not Path(path).is_file():
        raise ValueError('Existing lab required')
    with closing(duckdb.connect(str(path), read_only=True)) as db:
        db.execute('BEGIN TRANSACTION')
        projections = {}
        for name, clause in SCOPES.items():
            projections[name] = [{'order_id': r[0], 'currency': r[1], 'net_cash': str(r[2])}
                for r in db.execute('SELECT order_id,currency,SUM(net_cash_amount) FROM g_order_line_summary' + clause + ' GROUP BY 1,2 ORDER BY 1,2').fetchall()]
    return {'scope': 'local_report_filter_replay', 'requested_scope': requested_scope,
            'report_scope': report_scope, 'projections': projections}


def investigate(path, database, requested_scope, report_scope, *, expected_currency=None):
    # Always capture and replay here; callers cannot submit their own proof flags or SQL.
    evidence = capture(path, requested_scope, report_scope)
    if expected_currency is not None and any(r['currency'] != expected_currency for rows in evidence['projections'].values() for r in rows):
        raise ValueError('Captured currency exceeds approved scope')
    identity = str(uuid4())
    result = {'id': identity, 'classification': 'UNRESOLVED', 'root_cause_verified': False,
              'automatic_defect_routing': False, 'limitation': LIMIT,
              'compared_boundary': {'upstream': 'gold_requested_scope', 'downstream': 'report_simulation'}}
    if requested_scope is None:
        result.update(comparison_status='NOT_COMPARABLE', reason='Requested filter scope is missing')
    else:
        left = {(r['order_id'], r['currency']): r['net_cash'] for r in evidence['projections'][requested_scope]}
        right = {(r['order_id'], r['currency']): r['net_cash'] for r in evidence['projections'][report_scope]}
        checked = reconcile({'mode': 'local_lab', 'rows': [
            {'order_id': k[0], 'currency': k[1], 'silver_net_cash': left.get(k), 'gold_net_cash': right.get(k),
             'silver_present': k in left, 'gold_present': k in right} for k in sorted(left.keys() | right.keys())]})
        result['comparison_status'] = checked['comparison_status']
        result['impact_by_currency'] = {c: {
            'requested_total': v['silver_total'], 'report_total': v['gold_total'],
            'downstream_minus_upstream': v['downstream_minus_upstream'], 'affected_records': v['affected_records']}
            for c, v in checked['impact_by_currency'].items()}
        result['affected_records'] = [dict(r, status=r['status'].replace('GOLD', 'REPORT'),
            reference='/request/report_scope_evidence/projections') for r in checked['affected_records']]
        result['local_filter_mismatch_verified'] = requested_scope != report_scope and bool(checked['affected_records'])
        result['reason'] = ('Replayed report filter differs from explicit requested scope' if result['local_filter_mismatch_verified']
                            else 'Report replay matches requested records; this does not prove general business correctness')
    request = {'kind': 'local_report_scope', 'report_scope_evidence': evidence,
               'evidence_hash': hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest()}
    Path(database).parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(database)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS investigation_runs(id TEXT PRIMARY KEY,lineage_run TEXT,created TEXT,request TEXT,result TEXT)')
        db.execute('INSERT INTO investigation_runs VALUES(?,?,?,?,?)',
                   (identity, None, datetime.now(timezone.utc).isoformat(), json.dumps(request), json.dumps(result)))
        db.commit()
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab', type=Path, required=True)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--requested-scope', choices=SCOPES)
    parser.add_argument('--report-scope', choices=SCOPES, required=True)
    args = parser.parse_args()
    print(json.dumps(investigate(args.lab, args.database, args.requested_scope, args.report_scope), indent=2))

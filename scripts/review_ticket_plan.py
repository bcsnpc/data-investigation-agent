"""Inspect a saved draft or explicitly approve it into a linked worker ticket."""
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import time
from uuid import UUID, uuid4

from lineage_graph import load_graph
from metadata_config import ROOT, load_config
from ticket_planner import catalog, validate_plan, PROMPT_VERSION
from ticket_workflow import TicketStore, Conflict, validate_ticket


def get_plan(store, identity):
    with closing(store.connect()) as db:
        row = db.execute('SELECT ticket_id,record FROM ticket_plans WHERE id=?', (str(UUID(identity)),)).fetchone()
    if row is None:
        raise ValueError('Unknown plan')
    record = json.loads(row[1])
    if record['id'] != identity or record['ticket_id'] != row[0]:
        raise ValueError('Inconsistent plan identity')
    return record


def approve(store, plan_id, config, estate, reviewer, expected_hash=None):
    if not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 100:
        raise ValueError('Reviewer label required')
    record = get_plan(store, plan_id)
    if expected_hash is not None and hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest() != expected_hash:
        raise Conflict('Reviewed draft changed')
    original = store.get(record['ticket_id'])
    if original is None or record['lineage_run'] != original['lineage_run']:
        raise Conflict('Ticket context changed')
    if record['lineage_run'] != estate['investigation']['lineage_run']:
        raise Conflict('Configured lineage changed; create a new plan')
    if record['status'] != 'DRAFT_REQUIRES_REVIEW' or record['prompt_version'] != PROMPT_VERSION:
        raise Conflict('Plan is not an approvable current draft')
    graph = load_graph(config['storage']['database'], record['lineage_run'])
    reports = catalog(graph)
    payload = {'ticket': original['ticket'], 'reports': reports}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    if digest != record['input_hash']:
        raise Conflict('Plan input changed')
    validated = validate_plan(record['plan'], original['ticket'], reports)
    if validated['status'] != 'DRAFT_REQUIRES_REVIEW':
        raise Conflict('Questions must be resolved in a new plan')
    if 'native_context' in record:
        from native_plan_context import check
        saved=record['native_context']
        try:
            current=check(config['storage']['database'],record['lineage_run'],record['plan']['report_id'],saved['page_path'],original['ticket'].get('order_id'))
        except Exception as error:
            raise Conflict('Native definition context is unavailable or changed') from error
        if current!=saved or current['status']!='CONTEXT_SUPPLIED':
            raise Conflict('Native definition context changed; create a new plan')
    plan = validated['plan']
    body = dict(original['ticket'], report=plan['report_id'], metric=plan['metric'], currency=plan['currency'])
    if plan['order_id'] is not None:
        body['order_id'] = plan['order_id']
    body = validate_ticket(body)
    encoded = json.dumps(body, sort_keys=True)
    plan_hash = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
    now = time.time()
    with closing(store.connect()) as db:
        db.execute('CREATE TABLE IF NOT EXISTS plan_approvals(plan_id TEXT PRIMARY KEY,plan_hash TEXT NOT NULL,original_ticket_id TEXT NOT NULL,child_ticket_id TEXT UNIQUE NOT NULL,reviewer TEXT NOT NULL,created REAL NOT NULL)')
        db.commit()
        db.execute('BEGIN IMMEDIATE')
        # Recheck stored bytes inside the write transaction before creating work.
        current = db.execute('SELECT record FROM ticket_plans WHERE id=?', (plan_id,)).fetchone()
        if current is None or json.loads(current[0]) != record:
            raise Conflict('Plan changed during review')
        old = db.execute('SELECT child_ticket_id,plan_hash FROM plan_approvals WHERE plan_id=?', (plan_id,)).fetchone()
        if old:
            if old[1] != plan_hash:
                raise Conflict('Approved plan changed')
            return {'ticket_id': old[0], 'created': False, 'plan_id': plan_id}
        identity = str(uuid4())
        db.execute('INSERT INTO tickets(id,idempotency_key,body_hash,body,lineage_run,status,created,updated) VALUES(?,?,?,?,?,?,?,?)',
                   (identity, str(uuid4()), hashlib.sha256(encoded.encode()).hexdigest(), encoded,
                    record['lineage_run'], 'QUEUED', now, now))
        detail = {'reason': 'Reviewed plan approved', 'plan_id': plan_id, 'original_ticket_id': original['id'],
                  'reviewer': reviewer.strip(), 'plan_hash': plan_hash}
        store.event(db, identity, 'QUEUED', detail, now)
        db.execute('INSERT INTO plan_approvals VALUES(?,?,?,?,?,?)',
                   (plan_id, plan_hash, original['id'], identity, reviewer.strip(), now))
        db.commit()
    return {'ticket_id': identity, 'created': True, 'plan_id': plan_id}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan-id', required=True)
    parser.add_argument('--approve', action='store_true')
    parser.add_argument('--reviewer')
    args = parser.parse_args()
    config = load_config(ROOT / 'infra/metadata/development.json')
    estate = json.loads((ROOT / 'infra/fabric/environment.json').read_text())
    store = TicketStore(Path(config['storage']['database']).with_name('workflow.sqlite'))
    try:
        result = approve(store, args.plan_id, config, estate, args.reviewer) if args.approve else get_plan(store, args.plan_id)
        print(json.dumps(result))
    except (ValueError, Conflict) as exc:
        parser.error(str(exc))

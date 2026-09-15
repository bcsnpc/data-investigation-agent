"""Reviewed watermark policy evidence, never inferred report causality."""
from datetime import datetime, timezone
from decimal import Decimal
import json
from uuid import uuid4

from .onboarding import Conflict, digest, encoded, fields, text


def read(store, model_id, identity):
    store.get(model_id)
    text(identity, 100)
    with store.connect() as db:
        exists = db.execute("SELECT 1 FROM sqlite_master WHERE name='freshness_policies' AND type='table'").fetchone()
        row = db.execute('SELECT body,body_hash,reviewer,created FROM freshness_policies WHERE id=? AND model_id=?',
                         (identity, model_id)).fetchone() if exists else None
        has_revocations = db.execute("SELECT 1 FROM sqlite_master WHERE name='freshness_revocations' AND type='table'").fetchone()
        revoked = db.execute('SELECT reason,reviewer,created FROM freshness_revocations WHERE policy_id=?', (identity,)).fetchone() if has_revocations else None
    if row is None:
        raise KeyError('Freshness policy not found')
    body = json.loads(row[0])
    if digest(body) != row[1]:
        raise Conflict('Freshness policy integrity differs')
    return {'id': identity, 'body': body, 'body_hash': row[1], 'reviewer': row[2], 'created': row[3],
            'authority': 'ADMIN_REVIEWED_ASSERTION', 'revocation': list(revoked) if revoked else None}


def revoke(store, model_id, identity, reason, reviewer):
    read(store, model_id, identity)
    text(reason, 1000); text(reviewer, 200)
    with store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS freshness_revocations(policy_id TEXT PRIMARY KEY,reason TEXT,reviewer TEXT,created TEXT)')
        db.execute('INSERT OR IGNORE INTO freshness_revocations VALUES(?,?,?,?)',
                   (identity, reason, reviewer, datetime.now(timezone.utc).isoformat()))
    return read(store, model_id, identity)


def register(store, model_id, body, reviewer, config):
    """Admin attests meaning, scope and threshold; no LLM-created authority."""
    fields(body, ['plan', 'max_age_seconds', 'timestamp_meaning', 'timezone', 'authority_reference'])
    text(reviewer, 200)
    text(body['authority_reference'], 1000)
    text(body['timestamp_meaning'], 1000)
    if body['timezone'] != 'UTC':
        raise ValueError('Only reviewed UTC timestamps supported')
    if type(body['max_age_seconds']) is not int or not 1 <= body['max_age_seconds'] <= 31536000:
        raise ValueError('Invalid watermark age limit')
    plan = body['plan']
    if not isinstance(plan, dict) or plan.get('model_id') != model_id or 'freshness_policy_id' in plan:
        raise ValueError('Invalid policy scope')
    if plan.get('operation') != 'watermark_age_microseconds':
        raise ValueError('Policy requires a watermark read')
    from .source_diagnostics import build
    compiled = build(store, plan, config)
    # Bind the reviewed policy to the retained catalog and connection too.
    stored = {**body, 'binding_hash': digest(compiled)}
    identity = str(uuid4())
    with store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS freshness_policies(id TEXT PRIMARY KEY,model_id TEXT,body TEXT,body_hash TEXT,reviewer TEXT,created TEXT)')
        db.execute('INSERT INTO freshness_policies VALUES(?,?,?,?,?,?)',
                   (identity, model_id, encoded(stored), digest(stored), reviewer, datetime.now(timezone.utc).isoformat()))
    return read(store, model_id, identity)


def policy_for_plan(store, plan):
    identity = plan.get('freshness_policy_id')
    if identity is None:
        if 'freshness_policy_id' in plan:
            raise ValueError('Use an explicit policy ID or omit the field')
        return None
    policy = read(store, plan['model_id'], identity)
    if policy['revocation'] is not None:
        raise Conflict('Freshness policy revoked')
    scope = {k: v for k, v in plan.items() if k != 'freshness_policy_id'}
    if policy['body']['plan'] != scope:
        raise Conflict('Freshness policy scope or revision differs')
    return policy


def validate_binding(request):
    policy = request['freshness_policy']
    if policy is None:
        return
    unbound = dict(request, freshness_policy=None)
    unbound['scope_hash'] = digest(policy['body']['plan'])
    if digest(unbound) != policy['body']['binding_hash']:
        raise Conflict('Freshness policy catalog or connection changed')


def assess(request, result):
    """Only the observed MAX watermark age is checked, not ingestion completeness."""
    policy = request['freshness_policy']
    gaps = []
    if policy is None:
        gaps.append('REVIEWED_UTC_WATERMARK_POLICY_MISSING')
    count = Decimal(result['row_count']['value'])
    nonblank = Decimal(result['nonblank_count']['value'])
    raw = result['value']['value']
    age = Decimal(raw) if raw is not None else None
    if count == 0:
        gaps.append('EMPTY_SCOPE')
    if nonblank != count or age is None:
        gaps.append('MISSING_WATERMARK_VALUES')
    if age is not None and age < 0:
        gaps.append('FUTURE_WATERMARK_CLOCK_UNCERTIFIED')
    classification = 'INSUFFICIENT_EVIDENCE'
    if not gaps:
        threshold = policy['body']['max_age_seconds'] * 1000000
        classification = 'WATERMARK_AGE_EXCEEDED' if age > threshold else 'WATERMARK_WITHIN_POLICY'
    return {'classification': classification, 'condition_verified': not gaps,
            'policy_id': policy['id'] if policy else None,
            'policy_hash': policy['body_hash'] if policy else None,
            'age_microseconds': raw, 'gaps': gaps,
            'evaluated_at': 'SQL_OBSERVATION_TIME', 'claim_scope': 'SCOPED_MAX_WATERMARK_AGE_ONLY',
            'root_cause_verified': False, 'delivery_eligible': False,
            'limitation': 'An admin-reviewed watermark rule does not prove ingestion completeness, current freshness or the cause of a report discrepancy.'}

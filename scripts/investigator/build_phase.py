"""Owner-selected monthly build mode; historical tapes retain their own policy."""
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import os
import json
from pathlib import Path

POLICY = json.loads(Path(__file__).with_name('build_phase_policy.json').read_text(encoding='utf8'))

MODE = 'BUILD_PHASE'
MODEL_MICRODOLLARS = POLICY['monthly_model_microdollars']
TICKET_MODEL_MICRODOLLARS = 1_000_000
TICKET_MODEL_WARNING_MICRODOLLARS = 500_000
PLATFORM_MICRODOLLARS = 20_000_000
PHYSICAL_REQUESTS = POLICY['monthly_physical_requests']
PREVIOUS_PHYSICAL_REQUESTS = 6000
REQUEST_INCREASE_AT = '2026-10-26T00:00:00+00:00'
SCAN_REQUESTS = 1000
REALLOCATED_SCAN_REQUESTS = POLICY['scan_collectors']
SCAN_REALLOCATION_AT = '2026-10-24T01:24:00+00:00'
RESTORATION_REQUESTS = POLICY['restoration_reserve']
ADOPTED_AT = '2026-10-19'
_mode = ContextVar('build_phase_mode', default=None)
_purpose = ContextVar('build_phase_purpose', default=None)
PURPOSES = frozenset(('INVESTIGATION', 'SCAN', 'RESTORATION'))


def active(config=None):
    from .process_tape import ACTIVE
    tape = ACTIVE.get()
    if tape is not None and tape.replaying:
        return getattr(tape, 'bootstrap', {}).get('config', {}).get('_estate', {}).get('operating_mode') == MODE
    declared = (config or {}).get('_estate', {}).get('operating_mode')
    return declared == MODE or _mode.get() == MODE or os.environ.get('INVESTIGATOR_OPERATING_MODE') == MODE


def purpose(default='INVESTIGATION'):
    value = _purpose.get() or os.environ.get('INVESTIGATOR_BUDGET_CATEGORY') or default
    if value not in PURPOSES:
        raise ValueError('MONTHLY_BUDGET_CATEGORY_INVALID')
    return value


@contextmanager
def operating_mode(mode=MODE, *, category='INVESTIGATION'):
    if mode != MODE or category not in PURPOSES:
        raise ValueError('BUILD_PHASE_DECLARATION_INVALID')
    token = _mode.set(mode)
    category_token = _purpose.set(category)
    try:
        yield
    finally:
        _purpose.reset(category_token)
        _mode.reset(token)


def month_window(now):
    dt = datetime.fromtimestamp(now, timezone.utc)
    start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = start.replace(year=start.year + 1, month=1) if start.month == 12 else start.replace(month=start.month + 1)
    adopted = datetime.fromisoformat(ADOPTED_AT).replace(tzinfo=timezone.utc)
    return start.strftime('%Y-%m'), max(start, adopted).timestamp(), end.timestamp()


def physical_status(rows, allocations, now):
    """All environments share one month; pending and uncertain reads stay charged."""
    import json
    month, start, end = month_window(now)
    index = {(r['environment'], r['session_id'], r['reservation_key']): r['purpose'] for r in allocations}
    used = dict.fromkeys(PURPOSES, 0)
    historical_restoration = 0
    reset = POLICY.get('restoration_reset', {})
    resetting = (month == reset.get('month_utc') and now >= datetime.fromisoformat(reset['effective_at']).timestamp()) if reset else False
    for row in rows:
        if not start <= float(row['created']) < end:
            continue
        count = json.loads(row['reserved']).get('cloud_calls', 0)
        category = index.get((row['environment'], row['session_id'], row['reservation_key']), 'INVESTIGATION')
        # An unclassified historical read remains charged to the general line.
        if category not in used:
            raise ValueError('MONTHLY_HISTORICAL_CATEGORY_UNKNOWN')
        used[category] += count
        if resetting and category == 'RESTORATION' and float(row['created']) < datetime.fromisoformat(reset['effective_at']).timestamp():
            historical_restoration += count
    # Preserve historical decisions under their recorded clock. This reallocates
    # the existing total; it never clears usage or borrows the restoration line.
    scan_limit = (REALLOCATED_SCAN_REQUESTS if now >= datetime.fromisoformat(SCAN_REALLOCATION_AT).timestamp()
                  else SCAN_REQUESTS)
    total_limit = (PHYSICAL_REQUESTS if now >= datetime.fromisoformat(REQUEST_INCREASE_AT).timestamp()
                   else PREVIOUS_PHYSICAL_REQUESTS)
    limits = {'INVESTIGATION': total_limit - scan_limit - RESTORATION_REQUESTS,
              'SCAN': scan_limit, 'RESTORATION': RESTORATION_REQUESTS}
    total = sum(used.values())
    credit = min(historical_restoration, reset['historical_requests']) if resetting else 0
    used['RESTORATION'] -= credit
    return {'mode': MODE, 'month_utc': month, 'used': used, 'limits': limits,
            'total': total, 'total_limit': total_limit,
            'historical_restoration_requests': credit,
            'restoration_remaining': max(0, RESTORATION_REQUESTS - used['RESTORATION']),
            'warnings': [key + '_MONTHLY_80_PERCENT' for key in limits if used[key] * 5 >= limits[key] * 4]
                        + (['PHYSICAL_MONTHLY_80_PERCENT'] if total * 5 >= total_limit * 4 else [])}


def admit_physical(rows, allocations, now, category):
    if category not in PURPOSES:
        raise ValueError('MONTHLY_BUDGET_CATEGORY_INVALID')
    status = physical_status(rows, allocations, now)
    if (status['total'] >= status['total_limit'] or status['used'][category] >= status['limits'][category]
            or (category != 'RESTORATION' and status['historical_restoration_requests']
                and status['total_limit'] - status['total'] <= status['restoration_remaining'])):
        from .usage_governance import UsageHold
        raise UsageHold('MONTHLY_PHYSICAL_' + category + '_EXHAUSTED')
    return status


def local_reserve(governor, db, session, key, kind, amount, category):
    from .onboarding import encoded
    now = governor.clock()
    if kind == 'cloud':
        rows = [dict(r) for r in db.execute('SELECT environment,session_id,reservation_key,reserved,created FROM adaptive_usage')]
        allocations = [dict(r) for r in db.execute('SELECT environment,session_id,reservation_key,purpose FROM read_allocations')]
        admit_physical(rows, allocations, now, category)
        db.execute('INSERT INTO read_allocations VALUES(?,?,?,?,?)', (governor.environment, session, key, None, category))
    db.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,NULL,?,?,?)',
               (governor.environment, session, key, governor.day(), kind, encoded(amount), 'RESERVED', governor.hash, now))


def shared_reserve(usage, local, session, key, kind, amount, category):
    from .onboarding import encoded
    from .shared_usage import rows
    from .usage_governance import UsageHold
    g = usage.governor
    now = g.clock()
    with usage.state.transaction() as db:
        found = rows(usage.state, db, 'SELECT * FROM state_usage WHERE environment=? AND session_id=? AND reservation_key=?',
                     (usage.environment, session, key))
        if found:
            import json
            prior = found[0]
            if prior['owner'] != usage.owner or prior['kind'] != kind or json.loads(prior['reserved']) != amount:
                raise UsageHold('Shared reservation owner or request differs')
            return
        if kind == 'cloud':
            retained, allocations = shared_physical_rows(usage.state, db, now)
            status = admit_physical(retained, allocations, now, category)
            check_shared_request_policy(usage.state, db, now, status, category)
            usage.state.sql(db, 'INSERT INTO state_read_allocations VALUES(?,?,?,?,?)', (usage.environment, session, key, None, category))
        usage.state.sql(db, 'INSERT INTO state_usage VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                        (usage.environment, session, key, g._day(now) if hasattr(g, '_day') else datetime.fromtimestamp(now, timezone.utc).date().isoformat(),
                         kind, encoded(amount), None, 'RESERVED', g.hash, now, usage.owner))
    usage.mirror(local)


def shared_physical_rows(state, db, now):
    """Read the authoritative period, including all owners and pending reads.

    Admission remains under the caller's transaction/lock. Avoid transferring
    historical model payloads while holding that lock; the monthly decision
    already excludes these rows. Keep physical_status's independent date check.
    """
    from .shared_usage import rows
    _, start, end = month_window(now)
    retained = rows(state, db,
        'SELECT environment,session_id,reservation_key,reserved,created FROM state_usage WHERE created>=? AND created<?',
        (start, end))
    allocations = rows(state, db,
        'SELECT a.environment,a.session_id,a.reservation_key,a.purpose FROM state_read_allocations a '
        'JOIN state_usage u ON a.environment=u.environment AND a.session_id=u.session_id '
        'AND a.reservation_key=u.reservation_key WHERE u.created>=? AND u.created<?', (start, end))
    return retained, allocations


def model_status(charged, month, *, ceiling=MODEL_MICRODOLLARS):
    return {'mode': MODE, 'month_utc': month, 'charged_microdollars': charged,
            'ceiling_microdollars': ceiling, 'protected_microdollars': 0,
            'warning': charged * 5 >= ceiling * 4,
            'exhausted': charged >= ceiling}


def platform_status(charged, now):
    """Billing observation, never a made-up zero when the billing API lags."""
    if charged is not None and (type(charged) is not int or charged < 0):
        raise ValueError('PLATFORM_COST_OBSERVATION_INVALID')
    return {'month_utc': month_window(now)[0], 'charged_microdollars': charged,
            'ceiling_microdollars': PLATFORM_MICRODOLLARS,
            'warning': charged is None or charged * 5 >= PLATFORM_MICRODOLLARS * 4,
            'exhausted': charged is not None and charged >= PLATFORM_MICRODOLLARS,
            'limitation': 'Observed billing can lag; estimates are reported separately. No resource is paused, scaled or deleted by this budget.'}


def admit_platform(charged, now):
    status=platform_status(charged,now)
    if status['exhausted']:
        from .usage_governance import UsageHold
        raise UsageHold('MONTHLY_PLATFORM_EXHAUSTED')
    return status


def ensure_model_account(state, now, *, provision=False):
    """Fresh period account, with pre-adoption history retained informationally."""
    from .shared_state import sha, encoded
    month, _, _ = month_window(now)
    account = 'model-microdollars:' + month
    with state.transaction() as db:
        if state.sql(db, 'SELECT 1 FROM state_accounts WHERE identity=?', (account,)).fetchone():
            return account
        # The live worker deliberately cannot INSERT accounts: that would let
        # it create its own spending policy. Only the existing owner migration
        # path provisions monthly policy, never a worker or an elevated retry.
        if state.backend == 'postgresql' and not provision:
            from .model_spend import SpendHold
            raise SpendHold('MONTHLY_MODEL_ACCOUNT_NOT_PROVISIONED:'+account)
        source = None
        if month == ADOPTED_AT[:7]:
            try:
                source = state._snapshot(db, 'model-microdollars')
            except KeyError:
                pass
        state.sql(db, 'INSERT INTO state_accounts VALUES(?,?,?,?,?,?)',
                  (account, 'MICRODOLLARS', MODEL_MICRODOLLARS, 0, 0, 0))
        record = {'month_utc': month, 'adopted_at': ADOPTED_AT, 'opening_microdollars': '0',
                  'historical_total_microdollars_informational': source['charged'] if source is not None else None,
                  'legacy_snapshot_sha256': sha(source) if source is not None else None,
                  'reason': 'Owner correction2026-10-21: October begins2026-10-19T00:00Z; earlier cumulative spend is informational. Original accounts unchanged.'}
        state.sql(db, 'INSERT INTO state_documents VALUES(?,?,?,?,?)',
                  ('build_phase_account_opening', account, 0, encoded(record), sha(record)))
    return account


def check_shared_request_policy(state, db, now, status, category):
    """Cloud policy remains authoritative; source alone cannot raise its ceiling."""
    from .usage_governance import UsageHold
    import json
    if now < datetime.fromisoformat(REQUEST_INCREASE_AT).timestamp(): return
    row = state.sql(db, 'SELECT body FROM state_documents WHERE namespace=? AND identity=?',
                    ('build_phase_policy', 'monthly-physical')).fetchone()
    if row is None:
        if state.backend == 'postgresql': raise UsageHold('MONTHLY_REQUEST_POLICY_NOT_PROVISIONED')
        return
    policy = json.loads(row[0])
    if status.get('historical_restoration_requests') and policy.get('restoration_reset') != POLICY.get('restoration_reset'):
        raise UsageHold('AUTHORITATIVE_RESTORATION_RESET_NOT_APPLIED')
    total = min(status['total_limit'], policy['total_limit'])
    limit = min(status['limits'][category], policy['limits'][category])
    if status['total'] >= total or status['used'][category] >= limit:
        raise UsageHold('AUTHORITATIVE_MONTHLY_PHYSICAL_' + category + '_EXHAUSTED')

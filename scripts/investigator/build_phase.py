"""Owner-selected monthly build mode; historical tapes retain their own policy."""
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import os

MODE = 'BUILD_PHASE'
MODEL_MICRODOLLARS = 40_000_000
PLATFORM_MICRODOLLARS = 20_000_000
PHYSICAL_REQUESTS = 6000
SCAN_REQUESTS = 1000
RESTORATION_REQUESTS = 95
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
    for row in rows:
        if not start <= float(row['created']) < end:
            continue
        count = json.loads(row['reserved']).get('cloud_calls', 0)
        category = index.get((row['environment'], row['session_id'], row['reservation_key']), 'INVESTIGATION')
        # An unclassified historical read remains charged to the general line.
        if category not in used:
            raise ValueError('MONTHLY_HISTORICAL_CATEGORY_UNKNOWN')
        used[category] += count
    limits = {'INVESTIGATION': PHYSICAL_REQUESTS - SCAN_REQUESTS - RESTORATION_REQUESTS,
              'SCAN': SCAN_REQUESTS, 'RESTORATION': RESTORATION_REQUESTS}
    total = sum(used.values())
    return {'mode': MODE, 'month_utc': month, 'used': used, 'limits': limits,
            'total': total, 'total_limit': PHYSICAL_REQUESTS,
            'restoration_remaining': max(0, RESTORATION_REQUESTS - used['RESTORATION']),
            'warnings': [key + '_MONTHLY_80_PERCENT' for key in limits if used[key] * 5 >= limits[key] * 4]
                        + (['PHYSICAL_MONTHLY_80_PERCENT'] if total * 5 >= PHYSICAL_REQUESTS * 4 else [])}


def admit_physical(rows, allocations, now, category):
    if category not in PURPOSES:
        raise ValueError('MONTHLY_BUDGET_CATEGORY_INVALID')
    status = physical_status(rows, allocations, now)
    if status['total'] >= PHYSICAL_REQUESTS or status['used'][category] >= status['limits'][category]:
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
            retained = rows(usage.state, db, 'SELECT environment,session_id,reservation_key,reserved,created FROM state_usage')
            allocations = rows(usage.state, db, 'SELECT environment,session_id,reservation_key,purpose FROM state_read_allocations')
            admit_physical(retained, allocations, now, category)
            usage.state.sql(db, 'INSERT INTO state_read_allocations VALUES(?,?,?,?,?)', (usage.environment, session, key, None, category))
        usage.state.sql(db, 'INSERT INTO state_usage VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                        (usage.environment, session, key, g._day(now) if hasattr(g, '_day') else datetime.fromtimestamp(now, timezone.utc).date().isoformat(),
                         kind, encoded(amount), None, 'RESERVED', g.hash, now, usage.owner))
    usage.mirror(local)


def model_status(charged, month):
    return {'mode': MODE, 'month_utc': month, 'charged_microdollars': charged,
            'ceiling_microdollars': MODEL_MICRODOLLARS, 'protected_microdollars': 0,
            'warning': charged * 5 >= MODEL_MICRODOLLARS * 4,
            'exhausted': charged >= MODEL_MICRODOLLARS}


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

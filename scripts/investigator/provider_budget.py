"""Provider policy and reporting; historical Anthropic accounts stay intact."""
import json
from pathlib import Path
from .build_phase import month_window, ensure_model_account
from .shared_state import encoded, sha


def policy(provider):
    return json.loads(Path(__file__).with_name('build_phase_policy.json').read_text())['round26']['providers'][provider]


def account_for(provider, now):
    month = month_window(now)[0]
    if provider == 'anthropic':
        return 'model-microdollars:' + month
    policy(provider)  # Unknown providers cannot create spending accounts.
    return 'provider-' + provider + '-microdollars:' + month


def ensure_account(state, provider, now, *, provision=False):
    if provider == 'anthropic':
        return ensure_model_account(state, now, provision=provision)
    account = account_for(provider, now)
    if state.backend == 'postgresql' and not provision:
        present = state._read_transaction(lambda db: state.sql(db,
            'SELECT 1 FROM state_accounts WHERE identity=?', (account,)).fetchone())
        if not present:
            from .model_spend import SpendHold
            raise SpendHold('PROVIDER_ACCOUNT_NOT_PROVISIONED:' + account)
        return account
    with state.transaction() as db:
        if state.sql(db, 'SELECT 1 FROM state_accounts WHERE identity=?', (account,)).fetchone():
            return account
        if state.backend == 'postgresql' and not provision:
            from .model_spend import SpendHold
            raise SpendHold('PROVIDER_ACCOUNT_NOT_PROVISIONED:' + account)
        approved = policy(provider)
        state.sql(db, 'INSERT INTO state_accounts VALUES(?,?,?,?,?,?)',
                  (account, 'MICRODOLLARS', approved['ceiling_microdollars'], 0, 0, 0))
        body = {'provider': provider, 'month_utc': month_window(now)[0],
                'approval': 'owner Round26 2026-11-01', 'opening_microdollars': 0}
        state.sql(db, 'INSERT INTO state_documents VALUES(?,?,?,?,?)',
                  ('provider_account_opening', account, 0, encoded(body), sha(body)))
    return account


def report(state, now):
    from .anthropic_credit import status
    from .anthropic_credit import pending_exposure
    anthropic = status(state, now)
    providers = {'anthropic': {
        'charged_microdollars': anthropic['charged_microdollars'],
        'committed_microdollars': anthropic['committed_microdollars'],
        **policy('anthropic'),
        'ceiling_microdollars': int(anthropic['ceiling_microdollars'])}}
    with state.transaction(_read_only=True) as db:
        account = account_for('openai', now)
        try:
            totals = state._totals(db, account)
            charged = int(totals['charged'])
            committed = charged + pending_exposure(state, db, account)
            provisioned = True
            ceiling = int(totals['ceiling'])
        except KeyError:
            charged = committed = 0
            provisioned = False
            ceiling = policy('openai')['ceiling_microdollars']
        providers['openai'] = {**policy('openai'), 'charged_microdollars': charged,
                               'committed_microdollars': committed, 'provisioned': provisioned,
                               'ceiling_microdollars': ceiling}
    for row in providers.values():
        row['warning'] = row['committed_microdollars'] >= row['warning_microdollars']
    return {'month_utc': month_window(now)[0], 'providers': providers,
            'combined_charged_microdollars': sum(p['charged_microdollars'] for p in providers.values()),
            'combined_committed_microdollars': sum(p['committed_microdollars'] for p in providers.values())}

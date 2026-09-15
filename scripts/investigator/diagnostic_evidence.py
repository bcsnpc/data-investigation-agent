"""Scoped receipt access and conservative request-specific evidence assessment."""
import json
from .onboarding import digest
from .native_diagnostics import build


def receipts(store, model_id):
    store.get(model_id)  # Enforce environment/model ownership before lookup.
    with store.connect() as db:
        exists = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='native_diagnostics'").fetchone()
        if not exists:
            return []
        rows = db.execute('SELECT id,created,status FROM native_diagnostics WHERE model_id=? ORDER BY created DESC,id DESC LIMIT 100',
                          (model_id,)).fetchall()
    return [{'id': row[0], 'created': row[1], 'status': row[2]} for row in rows]


def read(store, model_id, receipt_id):
    model = store.get(model_id)
    with store.connect() as db:
        exists = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='native_diagnostics'").fetchone()
        row = db.execute('SELECT created,status,request,result FROM native_diagnostics WHERE model_id=? AND id=?',
                         (model_id, receipt_id)).fetchone() if exists else None
        has_decisions = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='native_capability_decisions'").fetchone()
        saved = db.execute('SELECT decision_hash,body FROM native_capability_decisions WHERE receipt_id=?',
                           (receipt_id,)).fetchone() if row and has_decisions else None
    if row is None:
        raise KeyError('Receipt not found')
    created, status, raw_request, raw_result = row
    request = json.loads(raw_request)
    admission = json.loads(saved[1]) if saved else None
    if admission:
        unhashed = {k: v for k, v in admission.items() if k != 'decision_hash'}
        if digest(unhashed) != saved[0] or admission['decision_hash'] != saved[0]:
            raise ValueError('Capability decision integrity differs')
        if admission['request_hash'] != digest({k: v for k, v in request.items() if k != 'plan'}):
            raise ValueError('Capability decision is bound to a different request')
    result = json.loads(raw_result) if raw_result else None
    current = False
    try:
        current = build(model, request['plan']) == {k: v for k, v in request.items() if k != 'plan'}
    except (ValueError, KeyError, TypeError):
        pass
    # Historical success stays historical. It is not a reusable live capability.
    native = 'UNKNOWN'
    reason = 'No successful complete response for the current admitted context'
    if current and status == 'COMPLETED':
        native = 'SUPPORTED' if result['completeness'] == 'COMPLETE_RESPONSE' else 'PARTIAL'
        reason = 'Native execution observed at capture time for this exact request only'
    elif current and status in ('FAILED', 'INTERRUPTED'):
        native = 'TEMPORARILY_UNAVAILABLE' if result.get('error_type') in ('TimeoutError', 'TimeoutExpired') else 'UNKNOWN'
        reason = 'Read failed or completion is uncertain; this does not prove an unsupported measure'
    decision = {'current_context': current, 'native_observation': {'state': native, 'reason': reason},
                'verification_eligible': False, 'root_cause_verified': False,
                'future_execution_guaranteed': False, 'scope_hash': request['scope_hash'],
                'context_id': request['context_id'], 'request_hash': digest({k: v for k, v in request.items() if k != 'plan'})}
    return {'id': receipt_id, 'model_id': model_id, 'created': created, 'status': status,
            'request': request, 'result': result, 'admission': admission, 'assessment': decision}

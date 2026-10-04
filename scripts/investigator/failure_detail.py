"""Sealed receipts for failure detail obtained from a second interface to a surface.

A specific error code is evidence only if the interface that reported it left a
receipt. The request and result are recorded like any other read. The result
holds codes only, never message text. It is sealed, so the refinement carried
into a probe's failure points at sealed evidence rather than a derived record.
"""
from .process_tape import utc_now
from datetime import datetime, timezone
from .process_tape import uuid4
from .onboarding import encoded

TABLE = 'failure_details'
KIND = 'failure_detail'


def _table(db):
    db.execute('CREATE TABLE IF NOT EXISTS '+TABLE+'(id TEXT PRIMARY KEY,model_id TEXT,created TEXT,status TEXT,request TEXT,result TEXT)')


def record(store, model_id, request, execute):
    """Record the request, run it, then store and seal its reduced result.

    The request row is written before the call, so an interrupted call leaves a
    RUNNING receipt rather than no trace.
    """
    identity = str(uuid4())
    with store.connect() as db:
        _table(db)
        db.execute('INSERT INTO '+TABLE+' VALUES(?,?,?,?,?,NULL)',
                   (identity, model_id, utc_now(), 'RUNNING', encoded(request)))
    try:
        answer = execute()
        answer = answer if isinstance(answer, dict) else {'status': 'UNAVAILABLE', 'error_type': 'InvalidResponse'}
    except Exception as exc:
        answer = {'status': 'UNAVAILABLE', 'error_type': type(exc).__name__}
    codes = [c for c in (answer.get('codes') or []) if isinstance(c, str)]
    result = {'interface_status': answer.get('status'), 'stage': answer.get('stage'),
              'error_type': answer.get('error_type'), 'codes': codes}
    # The receipt records whether the interface answered, not whether the
    # surface succeeded: a captured error is a completed read of that error.
    status = 'COMPLETED' if answer.get('status') in ('ERROR_CAPTURED', 'NO_ERROR') else 'FAILED'
    with store.connect() as db:
        db.execute('UPDATE '+TABLE+' SET status=?,result=? WHERE id=?', (status, encoded(result), identity))
        from .receipt_integrity import seal
        seal(db, KIND, identity)
    return identity, status, result

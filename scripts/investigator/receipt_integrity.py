"""Local terminal-receipt integrity; not a provider signature or version proof."""
from .onboarding import digest, Conflict

TABLES={'native':'native_diagnostics','source':'source_diagnostics'}
TABLES.update(bounded_dax='flexible_diagnostics',bounded_sql='flexible_diagnostics')


def seal(db,kind,identity):
    table=TABLES[kind]
    row=db.execute('SELECT id,model_id,created,status,request,result FROM '+table+' WHERE id=?',(identity,)).fetchone()
    if row is None or row[3]=='RUNNING':raise ValueError('Only terminal receipts can be sealed')
    db.execute('CREATE TABLE IF NOT EXISTS aggregate_receipt_seals(kind TEXT,id TEXT,hash TEXT,PRIMARY KEY(kind,id))')
    db.execute('INSERT INTO aggregate_receipt_seals VALUES(?,?,?)',(kind,identity,digest(list(row))))


def verify(db,kind,identity,*,captured_row=None):
    table=TABLES[kind]
    exists=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='aggregate_receipt_seals'").fetchone()
    saved=db.execute('SELECT hash FROM aggregate_receipt_seals WHERE kind=? AND id=?',(kind,identity)).fetchone() if exists else None
    if saved is None:return {'state':'LEGACY_UNSEALED','hash':None}
    row=db.execute('SELECT id,model_id,created,status,request,result FROM '+table+' WHERE id=?',(identity,)).fetchone()
    if row is None or digest(list(row))!=saved[0] or (captured_row is not None and digest(captured_row)!=saved[0]):
        raise Conflict('Aggregate receipt integrity differs')
    return {'state':'SEALED','hash':saved[0]}

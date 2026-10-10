"""Optional round-wide dollar admission, shared across processes and catalogs.

Only counts and request IDs are stored. Unknown provider usage retains the full
reservation. This is a rate-card ceiling, not an assertion about a provider bill.
"""
import contextlib
import json
import os
import sqlite3
import time


class SpendHold(RuntimeError):
    pass


class SpendBudget:
    def __init__(self, path, ceiling_microdollars):
        self.path = str(path)
        self.ceiling = ceiling_microdollars
        if type(self.ceiling) is not int or self.ceiling <= 0:
            raise ValueError('Positive dollar ceiling required')
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS model_spend '
                       '(id TEXT PRIMARY KEY, created REAL, reserved INTEGER, '
                       'charged INTEGER, status TEXT, input_tokens INTEGER, output_tokens INTEGER)')
            db.execute('CREATE TABLE IF NOT EXISTS spend_policy (id INTEGER PRIMARY KEY, ceiling INTEGER)')
            db.execute('INSERT OR IGNORE INTO spend_policy VALUES (1, ?)', (self.ceiling,))
            if db.execute('SELECT ceiling FROM spend_policy WHERE id=1').fetchone()[0] != self.ceiling:
                raise SpendHold('Round dollar ceiling differs from sealed spending policy')

    @contextlib.contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=60)
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def price(input_tokens, output_tokens):
        from .adapters.model_price import price
        return price(input_tokens, output_tokens)

    def reserve(self, body):
        if not isinstance(body.get('input'), str):
            raise SpendHold('Dollar guard requires bounded text input; image cost is not established')
        # One token per UTF-8 byte bounds byte-level tokenization; include tools,
        # schemas and instructions, and framing overhead rather than chars/4.
        inputs = len(json.dumps(body, ensure_ascii=False).encode('utf8')) + 4096
        outputs = body['max_output_tokens']
        bound = self.price(inputs, outputs)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute("SELECT 1 FROM model_spend WHERE status='VIOLATION'").fetchone():
                raise SpendHold('Provider cost exceeded reservation; new calls refused')
            charged = db.execute('SELECT COALESCE(SUM(charged),0) FROM model_spend').fetchone()[0]
            if charged + bound > self.ceiling:
                raise SpendHold('Round model-spend hard stop: request would exceed dollar ceiling')
            # Private spend-row identity is allocated atomically by this ledger,
            # outside investigation identities and replay events. Rows are retained.
            identity = 'cost-'+str(db.execute('SELECT COALESCE(MAX(rowid),0)+1 FROM model_spend').fetchone()[0])
            db.execute('INSERT INTO model_spend VALUES (?,?,?,?,?,?,?)',
                       (identity, time.time(), bound, bound, 'RESERVED', None, None))
        return identity

    def settle(self, identity, usage=None):
        known = isinstance(usage, dict) and all(type(usage.get(k)) is int and usage[k] >= 0
                                                for k in ('input_tokens', 'output_tokens'))
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT reserved,status FROM model_spend WHERE id=?', (identity,)).fetchone()
            if row is None:
                raise SpendHold('Missing model dollar reservation')
            if row[1] != 'RESERVED':
                return
            if not known:
                db.execute("UPDATE model_spend SET status='UNCERTAIN' WHERE id=?", (identity,))
                return
            amount = self.price(usage['input_tokens'], usage['output_tokens'])
            status = 'VIOLATION' if amount > row[0] else 'SETTLED'
            db.execute('UPDATE model_spend SET charged=?,status=?,input_tokens=?,output_tokens=? WHERE id=?',
                       (amount, status, usage['input_tokens'], usage['output_tokens'], identity))

    def snapshot(self):
        with self.connect() as db:
            rows = db.execute('SELECT status,charged,input_tokens,output_tokens FROM model_spend').fetchall()
        return {'ceiling_usd': self.ceiling/1000000, 'charged_usd': sum(r[1] for r in rows)/1000000,
                'calls': len(rows), 'input_tokens': sum(r[2] or 0 for r in rows),
                'output_tokens': sum(r[3] or 0 for r in rows),
                'unsettled_calls': sum(r[0] in ('RESERVED','UNCERTAIN') for r in rows),
                'rate_card_billing_estimate': True}


@contextlib.contextmanager
def admission(body):
    path = os.environ.get('INVESTIGATOR_MODEL_SPEND_DB')
    if not path:
        yield lambda usage: None
        return
    from .process_tape import ACTIVE
    tape = ACTIVE.get()
    if tape is not None and tape.replaying:
        yield lambda usage: None
        return
    budget = SpendBudget(path, int(os.environ['INVESTIGATOR_MODEL_SPEND_MICRODOLLARS']))
    identity = budget.reserve(body)
    try:
        yield lambda usage: budget.settle(identity, usage)
    finally:
        budget.settle(identity)

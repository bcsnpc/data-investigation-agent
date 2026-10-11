"""Durable public agent progress. Projection precedes every persistent byte."""
import copy
import json
from .onboarding import digest, encoded, Conflict
from .process_tape import event, clock


class Journal:
    def __init__(self, store, identity, *, projection=None, now=None):
        self.store, self.identity, self.projection = store, identity, projection
        self.now = now
        with store.connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS agent_progress(
                ticket_id TEXT NOT NULL, ordinal INTEGER NOT NULL,
                body TEXT NOT NULL, hash TEXT NOT NULL, created REAL NOT NULL,
                PRIMARY KEY(ticket_id,ordinal))''')

    def persist(self, value):
        value = copy.deepcopy(value)
        if self.projection is not None:
            value = self.projection(value)
        from .planner_recording import _safe
        _safe(encoded(value).encode('utf-8'))
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            ordinal = db.execute('SELECT coalesce(max(ordinal),0)+1 FROM agent_progress WHERE ticket_id=?', (self.identity,)).fetchone()[0]
            identity = 'agent-progress:' + digest({'ticket': self.identity, 'ordinal': ordinal, 'event': value})
            body = {'id': identity, 'ordinal': ordinal, 'event': value}
            at = clock('agent-progress', self.now) if self.now else clock('agent-progress')
            event('CONFIGURATION', {'control': 'AGENT_PROGRESS', **body})
            db.execute('INSERT INTO agent_progress VALUES(?,?,?,?,?)',
                       (self.identity, ordinal, encoded(body), digest(body), at))
        return identity

    def read(self):
        with self.store.connect() as db:
            rows = db.execute('SELECT body,hash,created FROM agent_progress WHERE ticket_id=? ORDER BY ordinal', (self.identity,)).fetchall()
        result = []
        for row in rows:
            body = json.loads(row['body'])
            if digest(body) != row['hash']:
                raise Conflict('Agent progress integrity differs')
            value = body['event']
            result.append({'id': body['id'], 'ordinal': body['ordinal'], 'at': row['created'],
                'label': value.get('summary', value.get('reason', value['event'])),
                'event': value['event'], 'tool': value.get('tool'),
                'arguments': value.get('arguments'),
                'result_ids': value.get('result', {}).get('evidence_ids', []),
                'status': value.get('result', {}).get('status'),
                'detail': value})
        return result

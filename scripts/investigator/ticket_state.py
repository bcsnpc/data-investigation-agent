"""Versioned durable smart-ticket state using the installation evidence store.

No second database or raw-file fallback: projected installations use the same
in-memory/projected store boundary as their other evidence. Persistence alone
does not run an investigation or authorize an intake scope.
"""
import json
from .onboarding import digest, encoded, Conflict
from .process_tape import event, uuid4
from . import ticket_protocol as protocol


class Tickets:
    def __init__(self, store):
        self.store=store
        with store.connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS smart_tickets(
                id TEXT PRIMARY KEY, request_key TEXT UNIQUE NOT NULL,
                request_hash TEXT NOT NULL, request TEXT NOT NULL,
                revision INTEGER NOT NULL, body TEXT NOT NULL, body_hash TEXT NOT NULL)''')

    def submit(self, request, request_key):
        if not isinstance(request_key,str) or not 1<=len(request_key)<=100:
            raise ValueError('Ticket requires a bounded idempotency key')
        fingerprint=digest(request)
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            prior=db.execute('SELECT id,request_hash FROM smart_tickets WHERE request_key=?',(request_key,)).fetchone()
            if prior:
                if prior[1]!=fingerprint:raise Conflict('Ticket key reused with different input')
                return self._get(db,prior[0])
            body=protocol.new(str(uuid4()))
            body['history'].append({'from':None,'to':'NEW','actor':'USER','detail':{'request_hash':fingerprint}})
            event('CONFIGURATION',{'smart_ticket':'SUBMIT','request':request,'body':body})
            db.execute('INSERT INTO smart_tickets VALUES(?,?,?,?,?,?,?)',
                (body['id'],request_key,fingerprint,encoded(request),0,encoded(body),digest(body)))
            return {'revision':0,'ticket':body,'request':request}

    @staticmethod
    def _get(db, identity):
        row=db.execute('SELECT revision,body,body_hash,request,request_hash FROM smart_tickets WHERE id=?',(identity,)).fetchone()
        if row is None:raise KeyError('Ticket not found')
        body=json.loads(row[1]);request=json.loads(row[3])
        if digest(body)!=row[2] or digest(request)!=row[4] or body['id']!=identity:
            raise Conflict('Ticket state integrity differs')
        return {'revision':row[0],'ticket':body,'request':request}

    def get(self, identity):
        with self.store.connect() as db:return self._get(db,identity)

    def list(self):
        with self.store.connect() as db:
            identities=[r[0] for r in db.execute('SELECT id FROM smart_tickets ORDER BY rowid DESC LIMIT 40')]
            return {'tickets':[self._get(db,identity) for identity in identities]}

    def update(self, identity, revision, operation):
        """Optimistic revision check prevents replies applying to newer choices."""
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            saved=self._get(db,identity)
            if type(revision) is not int or saved['revision']!=revision:
                raise Conflict('Ticket changed; read its current questions before replying')
            body=operation(saved['ticket'])
            if body.get('id')!=identity or body.get('version')!=protocol.VERSION:
                raise ValueError('Ticket identity or contract cannot change')
            event('CONFIGURATION',{'smart_ticket':'UPDATE','id':identity,'revision':revision+1,'body':body})
            db.execute('UPDATE smart_tickets SET revision=?,body=?,body_hash=? WHERE id=?',
                       (revision+1,encoded(body),digest(body),identity))
            return {'revision':revision+1,'ticket':body,'request':saved['request']}

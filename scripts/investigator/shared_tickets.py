"""Existing smart-ticket contract on the shared-state repository."""
import json
from .shared_state import StateConflict, encoded, sha
from .onboarding import Conflict, digest
from .process_tape import event, uuid4
from . import ticket_protocol as protocol


class SharedTickets:
    def __init__(self, state, *, replay_store=None):
        self.state = state
        self.replay_store = replay_store

    def _record(self, result, request_key=None):
        """Snapshot mirror only; live decisions always read the shared authority.

        A committed shared change precedes the private mirror. A failed mirror
        raises, leaving the shared revision intact and the operation failed;
        it never substitutes an older local result or retries the operation.
        """
        if self.replay_store is None:return result
        identity=result['ticket']['id'];request_hash=digest(result['request'])
        if request_key is None:
            # list() is a paginated UI view, not a complete identity index.
            # Inspect the authoritative request links in one database request.
            with self.state.transaction() as db:
                links=[]
                for key,raw,body_hash in self.state.sql(db,
                        'SELECT identity,body,body_hash FROM state_documents WHERE namespace=?',('ticket_request',)).fetchall():
                    body=json.loads(raw)
                    if sha(body)!=body_hash:raise StateConflict('Shared request link hash differs')
                    if body.get('id')==identity:links.append((key,body))
            if len(links)!=1 or links[0][1].get('request_hash')!=request_hash:
                raise Conflict('Shared ticket request identity differs before replay mirror')
            request_key=links[0][0]
        from .ticket_state import Tickets
        with self.replay_store.connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS smart_tickets(
                id TEXT PRIMARY KEY, request_key TEXT UNIQUE NOT NULL,
                request_hash TEXT NOT NULL, request TEXT NOT NULL,
                revision INTEGER NOT NULL, body TEXT NOT NULL, body_hash TEXT NOT NULL)''')
            db.execute('BEGIN IMMEDIATE')
            prior=db.execute('SELECT request_key,revision FROM smart_tickets WHERE id=?',(identity,)).fetchone()
            if prior:
                existing=Tickets._get(db,identity)
                if prior[0]!=request_key or existing['request']!=result['request']:
                    raise Conflict('Private replay ticket identity differs')
                if prior[1]>result['revision']:
                    raise Conflict('Private replay ticket revision is ahead of shared read')
                if prior[1]==result['revision'] and existing!=result:
                    raise Conflict('Private replay ticket revision content differs')
            db.execute('INSERT INTO smart_tickets VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET revision=excluded.revision,body=excluded.body,body_hash=excluded.body_hash',
                (identity,request_key,request_hash,encoded(result['request']),result['revision'],
                 encoded(result['ticket']),digest(result['ticket'])))
        return result

    @staticmethod
    def result(saved):
        return {'revision':saved['revision'],'ticket':saved['body']['ticket'],'request':saved['body']['request']}

    def submit(self, request, request_key):
        if not isinstance(request_key,str) or not 1<=len(request_key)<=100:
            raise ValueError('Ticket requires a bounded idempotency key')
        fingerprint = digest(request)
        with self.state.transaction() as db:
            try:
                link = self.state._get(db,'ticket_request',request_key)['body']
            except KeyError:
                link = None
            if link:
                if link['request_hash'] != fingerprint:
                    raise Conflict('Ticket key reused with different input')
                result=self.result(self.state._get(db,'ticket',link['id']))
            else:
                ticket = protocol.new(str(uuid4()))
                ticket['history'].append({'from':None,'to':'NEW','actor':'USER','detail':{'request_hash':fingerprint}})
                event('CONFIGURATION',{'smart_ticket':'SUBMIT','request':request,'body':ticket})
                body = {'request':request,'ticket':ticket}
                for ns,key,value in [('ticket',ticket['id'],body),('ticket_request',request_key,{'id':ticket['id'],'request_hash':fingerprint})]:
                    self.state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',(ns,key,0,encoded(value),sha(value)))
                result={'revision':0,'ticket':ticket,'request':request}
        return self._record(result,request_key)

    def get(self, identity):
        return self._record(self.result(self.state.get('ticket',identity)))

    def list(self):
        return {'tickets':[self.result(saved) for saved in self.state.list('ticket')]}

    def update(self, identity, revision, operation):
        def apply(body):
            ticket = operation(body['ticket'])
            if ticket.get('id') != identity or ticket.get('version') != protocol.VERSION:
                raise ValueError('Ticket identity or contract cannot change')
            event('CONFIGURATION',{'smart_ticket':'UPDATE','id':identity,'revision':revision+1,'body':ticket})
            return {'ticket':ticket,'request':body['request']}
        try:
            result=self.result(self.state.update('ticket',identity,revision,apply))
        except StateConflict as exc:
            raise Conflict('Ticket changed; read its current questions before replying') from exc
        return self._record(result)

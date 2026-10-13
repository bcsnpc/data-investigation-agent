"""Existing smart-ticket contract on the shared-state repository."""
from .shared_state import StateConflict, encoded, sha
from .onboarding import Conflict, digest
from .process_tape import event, uuid4
from . import ticket_protocol as protocol


class SharedTickets:
    def __init__(self, state):
        self.state = state

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
                return self.result(self.state._get(db,'ticket',link['id']))
            ticket = protocol.new(str(uuid4()))
            ticket['history'].append({'from':None,'to':'NEW','actor':'USER','detail':{'request_hash':fingerprint}})
            event('CONFIGURATION',{'smart_ticket':'SUBMIT','request':request,'body':ticket})
            body = {'request':request,'ticket':ticket}
            for ns,key,value in [('ticket',ticket['id'],body),('ticket_request',request_key,{'id':ticket['id'],'request_hash':fingerprint})]:
                self.state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',(ns,key,0,encoded(value),sha(value)))
            return {'revision':0,'ticket':ticket,'request':request}

    def get(self, identity):
        return self.result(self.state.get('ticket',identity))

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
            return self.result(self.state.update('ticket',identity,revision,apply))
        except StateConflict as exc:
            raise Conflict('Ticket changed; read its current questions before replying') from exc

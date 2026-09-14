"""Review-only authenticated envelope endpoints; no execution route."""
import json
import re
from uuid import UUID


class EnvelopeReviewApi:
    def __init__(self, workflow):
        if workflow.delivery_enabled: raise ValueError('Review API requires disabled delivery')
        self.workflow = workflow

    def matches(self, path):
        return bool(re.fullmatch(r'/api/(?:routing/[^/]+/envelope|envelopes/[^/]+(?:/approve)?)', path))

    def handle(self, environ, respond):
        parts = environ['PATH_INFO'].split('/')
        prepare = parts[2] == 'routing'
        approve = parts[-1] == 'approve'
        identity = parts[3]
        if environ.get('QUERY_STRING'): raise ValueError('Unexpected query')
        if prepare:
            if str(UUID(identity)) != identity: raise ValueError('Invalid draft ID')
        elif not re.fullmatch('[a-f0-9]{64}', identity): raise ValueError('Invalid envelope hash')
        method = 'POST' if prepare or approve else 'GET'
        if environ['REQUEST_METHOD'] != method: return respond('405 Method Not Allowed', {'error':'METHOD_NOT_ALLOWED'})
        if method == 'POST':
            if environ.get('CONTENT_TYPE','').split(';')[0] != 'application/json': return respond('415 Unsupported Media Type', {'error':'JSON_REQUIRED'})
            length = int(environ.get('CONTENT_LENGTH','0'))
            if not 1 <= length <= 1024: return respond('413 Payload Too Large', {'error':'INVALID_BODY_SIZE'})
            raw = environ['wsgi.input'].read(length)
            if len(raw) != length: raise ValueError('Incomplete body')
            body = json.loads(raw)
            fields = {'confirm','draft_hash','sender'} if prepare else {'confirm'}
            if not isinstance(body,dict) or set(body) != fields or body['confirm'] is not True: raise ValueError('Explicit confirmation required')
        try:
            if prepare: result = self.workflow.prepare(identity, authorized_hash=body['draft_hash'], sender=body['sender'])
            elif approve: result = self.workflow.approve(identity, confirm=True)
            else: result = self.workflow.detail(identity)
            return respond('200 OK', result)
        except KeyError: return respond('404 Not Found', {'error':'ENVELOPE_OR_DRAFT_NOT_FOUND'})

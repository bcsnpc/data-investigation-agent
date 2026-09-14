"""Local authenticated API routes for viewing and explicitly approving drafts."""
from contextlib import closing
import hashlib
import json
import re
from urllib.parse import parse_qs
from uuid import UUID
from review_ticket_plan import get_plan, approve
from ticket_workflow import Conflict


class PlanReviews:
    def __init__(self, store, config, estate_loader):
        self.store, self.config, self.estate_loader = store, config, estate_loader

    @staticmethod
    def matches(path):
        return path.startswith('/api/plans/') or (path.startswith('/api/tickets/') and path.endswith('/plans'))

    def handle(self, environ, respond):
        path = environ['PATH_INFO'].split('/')
        method = environ['REQUEST_METHOD']
        query = environ.get('QUERY_STRING', '')
        if len(path) not in (4, 5):
            return respond('404 Not Found', {'error': 'NOT_FOUND'})
        identity = str(UUID(path[3]))
        if identity != path[3]:
            raise ValueError('Canonical UUID required')
        if path[2] == 'tickets' and len(path) == 5 and path[4] == 'plans':
            if method != 'GET':
                return respond('405 Method Not Allowed', {'error': 'GET_REQUIRED'})
            params = parse_qs(query, keep_blank_values=True, strict_parsing=True, max_num_fields=1)
            value = params.get('offset', ['0'])
            if set(params) - {'offset'} or len(value) != 1 or not re.fullmatch(r'[0-9]{1,6}', value[0]):
                raise ValueError('Invalid offset')
            offset = int(value[0])
            if offset > 100000: raise ValueError('Offset too large')
            if self.store.get(identity) is None:
                return respond('404 Not Found', {'error': 'TICKET_NOT_FOUND'})
            with closing(self.store.connect()) as db:
                exists = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='ticket_plans'").fetchone()
                rows = db.execute('SELECT id,record FROM ticket_plans WHERE ticket_id=? ORDER BY id LIMIT 21 OFFSET ?',
                                  (identity, offset)).fetchall() if exists else []
            items = [{'id': row[0], 'status': json.loads(row[1])['status'], 'detail_url': '/api/plans/' + row[0]}
                     for row in rows[:20]]
            return respond('200 OK', {'items': items, 'next_offset': offset + 20 if len(rows) > 20 else None})
        if path[2] != 'plans' or (len(path) == 5 and path[4] != 'approve'):
            return respond('404 Not Found', {'error': 'NOT_FOUND'})
        if query: raise ValueError('Unexpected query')
        with closing(self.store.connect()) as db:
            exists = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='ticket_plans'").fetchone()
            row = db.execute('SELECT id FROM ticket_plans WHERE id=?', (identity,)).fetchone() if exists else None
        if row is None: return respond('404 Not Found', {'error': 'PLAN_NOT_FOUND'})
        record = get_plan(self.store, identity)
        if len(path) == 4 and method == 'GET':
            with closing(self.store.connect()) as db:
                exists = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='plan_approvals'").fetchone()
                approved = db.execute('SELECT child_ticket_id,reviewer,created FROM plan_approvals WHERE plan_id=?',
                                      (identity,)).fetchone() if exists else None
            return respond('200 OK', {'draft': record,
                           'plan_hash': hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest(),
                           'approval': dict(ticket_id=approved[0], reviewer=approved[1], created=approved[2]) if approved else None})
        if len(path) != 5 or method != 'POST':
            return respond('405 Method Not Allowed', {'error': 'METHOD_NOT_ALLOWED'})
        if environ.get('CONTENT_TYPE', '').split(';')[0].strip() != 'application/json':
            return respond('415 Unsupported Media Type', {'error': 'JSON_REQUIRED'})
        try:
            length = int(environ.get('CONTENT_LENGTH', '0'))
            if not 1 <= length <= 4096:
                return respond('413 Payload Too Large', {'error': 'INVALID_BODY_SIZE'})
            raw = environ['wsgi.input'].read(length)
            if len(raw) != length: raise ValueError('Incomplete body')
            body = json.loads(raw.decode('utf-8'))
        except (ValueError, UnicodeError):
            return respond('400 Bad Request', {'error': 'INVALID_JSON'})
        if not isinstance(body, dict) or set(body) != {'confirm', 'plan_hash'} or body['confirm'] is not True:
            raise ValueError('Explicit confirmation required')
        if not isinstance(body['plan_hash'], str) or not re.fullmatch(r'[0-9a-f]{64}', body['plan_hash']):
            raise ValueError('Invalid draft hash')
        try:
            result = approve(self.store, identity, self.config, self.estate_loader(), 'local-api-operator', body['plan_hash'])
        except Conflict:
            return respond('409 Conflict', {'error': 'DRAFT_REVIEW_CONFLICT'})
        return respond('201 Created' if result['created'] else '200 OK',
                       dict(result, status_url='/api/tickets/' + result['ticket_id']))

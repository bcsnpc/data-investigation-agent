"""Authenticated local case API. Execution is an installed port, never an HTTP option."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
from threading import RLock
import uuid

MAX_BODY = 1500000
REQUEST_KEYS = {'text', 'screenshot', 'report', 'page', 'visual', 'estate_id', 'requester'}


class RequestError(ValueError): pass


def request(value):
    if not isinstance(value, dict) or not {'text', 'estate_id', 'requester'} <= value.keys() <= REQUEST_KEYS:
        raise RequestError('Required fields: text, estate_id, requester; optional screenshot, report, page, visual')
    for key, item in value.items():
        if not isinstance(item, str) or not item.strip() or len(item) > (1000000 if key == 'screenshot' else 100000 if key == 'text' else 500):
            raise RequestError('Invalid field: ' + key)
    if 'screenshot' in value:
        import base64
        try:
            raw = base64.b64decode(value['screenshot'], validate=True)
            if not raw.startswith((b'\x89PNG\r\n\x1a\n', b'\xff\xd8\xff')): raise ValueError()
        except ValueError: raise RequestError('Screenshot must be base64 PNG or JPEG') from None
    return deepcopy(value)


def signature(value):
    # Requester is an authorization/audit field, never a different data credential.
    return hashlib.sha256(json.dumps({k: v for k, v in value.items() if k != 'requester'},
                                    sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class ReplayEngine:
    """Exact submitted ticket -> saved result; no fallback to live or model ports."""
    mode = 'REPLAY'

    def __init__(self, records):
        self.records = {}
        for row in records:
            key = signature(request(row['request']))
            if key in self.records: raise ValueError('DUPLICATE_REPLAY_REQUEST')
            self.records[key] = deepcopy(row['result'])

    def submit(self, value, *, case_id, requester):
        if value['requester'] != requester: raise PermissionError('REQUESTER_MISMATCH')
        key = signature(value)
        if key not in self.records: raise RequestError('No exact saved replay for this request')
        return deepcopy(self.records[key])


class TokenAuth:
    """Production resolver reads the named secret; tests inject an ephemeral memory key."""
    def __init__(self, token, *, principal, estates):
        if not isinstance(token, str) or len(token) < 32 or not token.isascii(): raise ValueError('API_TOKEN_BOUND')
        if not principal or not estates: raise ValueError('API_PRINCIPAL_SCOPE_REQUIRED')
        self._token = token
        self.principal, self.estates = principal, frozenset(estates)

    @classmethod
    def from_secret_store(cls, resolve, *, vault, secret_name, principal, estates):
        return cls(resolve(vault, secret_name), principal=principal, estates=estates)

    def check(self, header):
        if not isinstance(header, str) or not header.isascii() or not hmac.compare_digest(header, 'Bearer ' + self._token):
            raise PermissionError('AUTHENTICATION_REQUIRED')
        return self.principal


class Service:
    """Durable private case files plus an append-only access audit. Not a public server."""
    def __init__(self, *, root, engine, estates):
        if engine.mode != 'REPLAY': raise ValueError('LOCAL_API_REPLAY_ONLY')
        from .estate_config import validate
        self.estates = {key: validate(value) for key, value in estates.items()}
        if any(key != value['id'] for key, value in self.estates.items()): raise ValueError('ESTATE_REGISTRY_ID_DIFFERS')
        self.root, self.engine, self.lock = Path(root), engine, RLock()
        self.root.mkdir(parents=True, exist_ok=True)

    def _write(self, name, value):
        target = self.root / (name + '.json')
        temporary = self.root / (name + '.' + uuid.uuid4().hex + '.tmp')
        with temporary.open('x', encoding='utf8') as stream:
            json.dump(value, stream, ensure_ascii=False, allow_nan=False)
            stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, target)

    def audit(self, *, method, route, status, principal=None, case_id=None):
        with self.lock:
            event = {'at': datetime.now(timezone.utc).isoformat(), 'method': method,
                     'route': route, 'status': status, 'principal': principal, 'case_id': case_id}
            with (self.root / 'audit.jsonl').open('a', encoding='utf8') as stream:
                stream.write(json.dumps(event) + '\n'); stream.flush(); os.fsync(stream.fileno())
            # Calls without a case (including unauthenticated health) get an access case.
            name = case_id if case_id and (self.root / (case_id + '.json')).exists() else 'access-' + uuid.uuid4().hex
            path = self.root / (name + '.json')
            value = json.loads(path.read_bytes()) if path.exists() else {'events': []}
            value['events'].append(event)
            self._write(name, value)

    def submit(self, submitted, principal, allowed):
        value = request(submitted)
        if value['requester'] != principal: raise PermissionError('REQUESTER_MISMATCH')
        estate = value['estate_id']
        if estate not in allowed or estate not in self.estates: raise PermissionError('ESTATE_NOT_AUTHORIZED')
        if not self.estates[estate]['enabled']: raise RequestError('ESTATE_DISABLED')
        identity = uuid.uuid4().hex
        case = {'id': identity, 'estate_id': estate, 'requester': principal, 'status': 'RUNNING',
                'mode': 'REPLAY', 'request': value, 'events': []}
        with self.lock: self._write(identity, case)
        try: result = self.engine.submit(value, case_id=identity, requester=principal)
        except Exception:
            case.update(status='FAILED', error='REPLAY_NOT_AVAILABLE')
            with self.lock: self._write(identity, case)
            # No model/provider/native exception content crosses this boundary.
            raise RequestError('No exact saved replay for this request') from None
        case.update(status='COMPLETED', result=result)
        with self.lock: self._write(identity, case)
        return identity

    def get(self, identity, principal, allowed):
        if not re.fullmatch('[0-9a-f]{32}', identity): raise KeyError(identity)
        with self.lock:
            path = self.root / (identity + '.json')
            if not path.exists(): raise KeyError(identity)
            value = json.loads(path.read_bytes())
        if value['requester'] != principal or value['estate_id'] not in allowed: raise KeyError(identity)
        return value


def create_app(service, auth, *, port):
    hosts = {f'127.0.0.1:{port}', f'localhost:{port}'}
    def app(env, start):
        status, body, principal, identity = 500, {'error': 'INTERNAL_ERROR'}, None, None
        method, path = env.get('REQUEST_METHOD', ''), env.get('PATH_INFO', '')
        match = re.fullmatch(r'/v1/investigations/([0-9a-f]{32})(/result)?', path)
        route = '/v1/investigations/{id}' + ('/result' if match and match[2] else '') if match else path if path in ('/v1/health', '/v1/investigations') else 'UNKNOWN'
        try:
            if env.get('HTTP_HOST') not in hosts or env.get('HTTP_ORIGIN') not in (None, '', *('http://' + host for host in hosts)):
                raise PermissionError('LOOPBACK_SAME_ORIGIN_REQUIRED')
            principal = auth.check(env.get('HTTP_AUTHORIZATION', ''))
            if env.get('QUERY_STRING'): raise RequestError('Query parameters are not supported')
            if method == 'GET' and path == '/v1/health':
                status, body = 200, {'status': 'ok', 'mode': service.engine.mode, 'live_enabled': False}
            elif method == 'POST' and path == '/v1/investigations':
                if env.get('CONTENT_TYPE', '').split(';')[0] != 'application/json': raise RequestError('application/json required')
                try: length = int(env.get('CONTENT_LENGTH', ''))
                except ValueError: raise RequestError('Content-Length required') from None
                if not 0 < length <= MAX_BODY: raise RequestError('Request body too large or empty')
                from .provider_tape_contract import parse
                try: value = parse(env['wsgi.input'].read(length))
                except (ValueError, UnicodeError): raise RequestError('Invalid JSON') from None
                identity = service.submit(value, principal, auth.estates)
                status, body = 202, {'case_id': identity, 'status_url': '/v1/investigations/' + identity}
            elif method == 'GET' and match:
                identity = match[1]
                case = service.get(identity, principal, auth.estates)
                body = case.get('result', {'status': case['status']}) if match[2] else {
                    'case_id': identity, 'status': case['status'], 'mode': case['mode'],
                    'result_url': '/v1/investigations/' + identity + '/result'}
                status = 200
            else: status, body = 404, {'error': 'NOT_FOUND'}
        except PermissionError as error: status, body = 401 if principal is None else 403, {'error': str(error)}
        except RequestError as error: status, body = 400, {'error': str(error)}
        except KeyError: status, body = 404, {'error': 'NOT_FOUND'}
        except Exception: status, body = 500, {'error': 'INTERNAL_ERROR'}
        # Audit failure refuses the response; it never silently permits unaudited access.
        service.audit(method=method if method in ('GET', 'POST') else 'OTHER', route=route,
                      status=status, principal=principal, case_id=identity)
        raw = json.dumps(body, ensure_ascii=False, allow_nan=False).encode()
        labels = {200: 'OK', 202: 'Accepted', 400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found', 500: 'Internal Server Error'}
        start(str(status) + ' ' + labels[status], [('Content-Type', 'application/json; charset=utf-8'),
            ('Content-Length', str(len(raw))), ('Cache-Control', 'no-store'), ('X-Content-Type-Options', 'nosniff')])
        return [raw]
    return app

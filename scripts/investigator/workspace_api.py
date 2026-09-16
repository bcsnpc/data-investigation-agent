"""Authenticated loopback HTTP surface for the shared investigation workspace."""
import hmac
import json
from pathlib import Path
import sqlite3
from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIServer
from .onboarding import Conflict, fields

ASSETS = Path(__file__).resolve().parents[2] / 'apps/investigator-workspace'


class WorkspaceServer(ThreadingMixIn, WSGIServer):
    """Keep status/history responsive during a bounded intake provider call."""
    daemon_threads = True


def create_app(workspace, token, port=8776):
    if not isinstance(token, str) or len(token) < 32 or not token.isascii():
        raise ValueError('A separate local workspace key of at least 32 ASCII characters is required')
    hosts = {f'127.0.0.1:{port}', f'localhost:{port}'}

    def app(env, start):
        def respond(status, body, mime='application/json; charset=utf-8'):
            raw = body if isinstance(body, bytes) else json.dumps(body).encode()
            start(status, [('Content-Type', mime), ('Content-Length', str(len(raw))),
                          ('Cache-Control', 'no-store'), ('X-Content-Type-Options', 'nosniff'),
                          ('Referrer-Policy', 'no-referrer'),
                          ('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' blob:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")])
            return [raw]
        if env.get('HTTP_HOST') not in hosts:
            return respond('403 Forbidden', {'error': 'Loopback host required'})
        origin = env.get('HTTP_ORIGIN')
        if origin and origin not in {'http://' + h for h in hosts}:
            return respond('403 Forbidden', {'error': 'Same-origin requests required'})
        path, method = env.get('PATH_INFO', ''), env.get('REQUEST_METHOD', 'GET')
        assets = {'/': ('index.html', 'text/html; charset=utf-8'),
                  '/workspace.js': ('workspace.js', 'text/javascript'), '/screenshots.js': ('screenshots.js', 'text/javascript'), '/style.css': ('style.css', 'text/css')}
        if method == 'GET' and path in assets:
            filename, mime = assets[path]
            return respond('200 OK', (ASSETS / filename).read_bytes(), mime)
        auth = env.get('HTTP_AUTHORIZATION', '')
        if not auth.isascii() or not hmac.compare_digest(auth, 'Bearer ' + token):
            return respond('401 Unauthorized', {'error': 'Enter the local workspace access key'})
        if env.get('QUERY_STRING'):
            return respond('400 Bad Request', {'error': 'Unexpected query parameters'})
        try:
            if method not in ('GET', 'POST'):
                return respond('405 Method Not Allowed', {'error': 'Method not allowed'})
            body = None
            if method == 'POST':
                size = int(env.get('CONTENT_LENGTH', '0'))
                limit = 1_410_000 if path == '/api/workspace/attachments' else 16384
                if not 0 < size <= limit or env.get('CONTENT_TYPE', '').split(';')[0] != 'application/json':
                    raise ValueError('Expected bounded JSON')
                body = json.loads(env['wsgi.input'].read(size))
            if path == '/api/workspace/models' and method == 'GET':
                result = workspace.models()
            elif path == '/api/workspace/attachments':
                result = workspace.screenshots.upload(body) if method == 'POST' else workspace.screenshots.history()
            elif path.startswith('/api/workspace/attachments/'):
                parts = path[len('/api/workspace/attachments/'):].split('/')
                if len(parts) == 1 and method == 'GET': result = workspace.screenshots.image(parts[0])
                elif len(parts) == 2 and parts[1] == 'content' and method == 'GET':
                    metadata, raw = workspace.screenshots.image(parts[0], content=True)
                    return respond('200 OK', raw, metadata['mime'])
                elif len(parts) == 2 and parts[1] == 'reads' and method == 'GET': result = workspace.screenshots.reads(parts[0])
                elif len(parts) == 2 and parts[1] == 'remove' and method == 'POST':
                    fields(body, []); result = workspace.screenshots.remove(parts[0])
                else: return respond('404 Not Found', {'error': 'Not found'})
            elif path == '/api/workspace/screenshot-reads' and method == 'POST': result = workspace.screenshots.read(body)
            elif path.startswith('/api/workspace/screenshot-reads/'):
                parts = path[len('/api/workspace/screenshot-reads/'):].split('/')
                if len(parts) == 1 and method == 'GET': result = workspace.screenshots.saved('workspace_image_reads', parts[0])
                elif len(parts) == 2 and parts[1] == 'hold' and method == 'POST':
                    fields(body, []); result = workspace.screenshots.hold(parts[0])
                else: return respond('404 Not Found', {'error': 'Not found'})
            elif path == '/api/workspace/screenshot-reviews' and method == 'POST': result = workspace.screenshots.review(body)
            elif path == '/api/workspace/questions' and method == 'POST':
                result = workspace.intake.resolve(body)
            elif path == '/api/workspace/questions' and method == 'GET':
                result = workspace.intake.list()
            elif path.startswith('/api/workspace/questions/'):
                parts = path[len('/api/workspace/questions/'):].split('/')
                if len(parts) == 1 and method == 'GET':
                    result = workspace.intake.get(parts[0])
                elif len(parts) == 2 and parts[1] == 'hold' and method == 'POST':
                    fields(body, []); result = workspace.intake.hold(parts[0])
                else:
                    return respond('404 Not Found', {'error': 'Not found'})
            elif path == '/api/workspace/previews' and method == 'POST':
                result = workspace.preview(body)
            elif path == '/api/workspace/sessions' and method == 'GET':
                result = workspace.sessions()
            elif path == '/api/workspace/sessions' and method == 'POST':
                fields(body, ['preview_id'])
                result = workspace.start(body['preview_id'])
            elif path.startswith('/api/workspace/sessions/'):
                parts = path[len('/api/workspace/sessions/'):].split('/')
                if len(parts) == 1 and method == 'GET':
                    result = workspace.session(parts[0])
                elif len(parts) == 2 and parts[1] == 'cancel' and method == 'POST':
                    fields(body, [])
                    result = workspace.cancel(parts[0])
                else:
                    return respond('404 Not Found', {'error': 'Not found'})
            else:
                return respond('404 Not Found', {'error': 'Not found'})
            return respond('200 OK', result)
        except Conflict as exc:
            return respond('409 Conflict', {'error': str(exc)})
        except KeyError:
            return respond('404 Not Found', {'error': 'Investigation or catalog item not found'})
        except (ValueError, TypeError, OverflowError):
            return respond('400 Bad Request', {'error': 'Invalid scope or incomplete metadata. Review the selected metric and filters.'})
        except (sqlite3.Error, OSError, RuntimeError):
            return respond('503 Service Unavailable', {'error': 'Investigation storage is unavailable'})
    return app

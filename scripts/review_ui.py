"""Serve the fixed local review UI; API data still requires bearer authentication."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'apps/investigation-review'
ASSETS = {'/': ('index.html', 'text/html; charset=utf-8'),
          '/review.js': ('review.js', 'text/javascript; charset=utf-8'),
          '/review.css': ('review.css', 'text/css; charset=utf-8')}


def serve(environ, start_response):
    path = environ.get('PATH_INFO', '')
    if path not in ASSETS or environ.get('REQUEST_METHOD') != 'GET':
        return None
    name, mime = ASSETS[path]
    content = (ROOT / name).read_bytes()
    start_response('200 OK', [('Content-Type', mime), ('Content-Length', str(len(content))),
                             ('Cache-Control', 'no-store'), ('X-Content-Type-Options', 'nosniff'),
                             ('Referrer-Policy', 'no-referrer'),
                             ('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")])
    return [content]

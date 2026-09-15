"""Business-facing isolated demo. Attachments are retained, not OCR interpreted."""
import argparse
import base64
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import secrets
import sqlite3
import struct
from threading import Thread
from uuid import UUID, uuid4
from wsgiref.simple_server import make_server

import duckdb
from demo import require_demo
from defect_lab import evidence, fingerprints
from lab_filter_cause import verify
from lab_investigator import investigate
from serve_investigations import QuietHandler

ROOT = Path(__file__).resolve().parents[1]


def encoded(value):
    return json.dumps(value, default=str, sort_keys=True)


def now():
    return datetime.now(timezone.utc).isoformat()


def png(value):
    if not isinstance(value, str) or len(value) > 4_000_000:
        raise ValueError('Attach a PNG smaller than 3 MB')
    raw = base64.b64decode(value, validate=True)
    if len(raw) < 33 or raw[:8] != b'\x89PNG\r\n\x1a\n' or raw[12:16] != b'IHDR':
        raise ValueError('A PNG screenshot is required')
    width, height = struct.unpack('>II', raw[16:24])
    if not 1 <= width <= 8000 or not 1 <= height <= 8000:
        raise ValueError('Screenshot dimensions are unsupported')
    return raw


class BusinessDemo:
    def __init__(self, folder):
        self.folder = require_demo(folder)
        self.lab = self.folder / 'lab.duckdb'
        self.database = self.folder / 'business.sqlite'
        with self.connect() as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS snapshots(id TEXT PRIMARY KEY, body TEXT);
            CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY, request_key TEXT UNIQUE, body_hash TEXT,
              snapshot_id TEXT, question TEXT, screenshot BLOB, app_screenshot BLOB, status TEXT, result TEXT);
            CREATE TABLE IF NOT EXISTS steps(case_id TEXT, at TEXT, text TEXT);''')
            # A process interruption is visible and never silently retried.
            db.execute("UPDATE cases SET status='INTERRUPTED' WHERE status='RUNNING'")

    @contextmanager
    def connect(self):
        with closing(sqlite3.connect(self.database, timeout=10)) as db:
            with db:
                yield db

    def snapshot(self):
        with closing(duckdb.connect(str(self.lab), read_only=True)) as db:
            db.execute('BEGIN TRANSACTION')
            payload, context = evidence(self.lab, True, connection=db)
            fp = fingerprints(db)
        if any(r['currency'] != 'USD' for r in payload['rows']):
            raise ValueError('This demo supports USD only')
        identity = str(uuid4())
        data = {'id': identity, 'captured_at': now(), 'payload': payload, 'context': context, 'fingerprints': fp}
        with self.connect() as db:
            db.execute('INSERT INTO snapshots VALUES(?,?)', (identity, encoded(data)))
        return self.public_snapshot(data)

    @staticmethod
    def public_snapshot(data):
        rows = data['payload']['rows']
        orders = data['context']['records']
        return {'id': data['id'], 'captured_at': data['captured_at'], 'report': 'Net Cash',
                'currency': 'USD', 'scope': 'All demo orders', 'orders': orders,
                'reported': str(sum((Decimal(str(r['gold_net_cash'] or 0)) for r in rows), Decimal(0))),
                'payments': str(sum((Decimal(str(r['captured_amount'])) for r in orders), Decimal(0))),
                'refunds': str(sum((Decimal(str(r['refunded_amount'])) for r in orders), Decimal(0)))}

    def submit(self, body, launch=True):
        if set(body) != {'snapshot_id', 'question', 'screenshot', 'app_screenshot', 'request_key'}:
            raise ValueError('Invalid submission')
        key = str(UUID(body['request_key']))
        snapshot = str(UUID(body['snapshot_id']))
        question = body['question']
        if not isinstance(question, str) or not 5 <= len(question.strip()) <= 2000:
            raise ValueError('Describe the concern in 5 to 2000 characters')
        attachment = png(body['screenshot'])
        app_attachment = png(body['app_screenshot']) if body['app_screenshot'] else None
        digest = hashlib.sha256(encoded(body).encode()).hexdigest()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT id,body_hash FROM cases WHERE request_key=?', (key,)).fetchone()
            if old:
                if old[1] != digest:
                    raise ValueError('Submission changed; create a new request')
                return old[0]
            if not db.execute('SELECT 1 FROM snapshots WHERE id=?', (snapshot,)).fetchone():
                raise ValueError('Open the report before submitting')
            identity = str(uuid4())
            db.execute('INSERT INTO cases VALUES(?,?,?,?,?,?,?,?,?)',
                       (identity, key, digest, snapshot, question.strip(), attachment, app_attachment, 'RUNNING', None))
            db.execute('INSERT INTO steps VALUES(?,?,?)', (identity, now(), 'Question and screenshots received'))
        if launch:
            Thread(target=self.run, args=(identity,), daemon=False).start()
        return identity

    def step(self, identity, text):
        with self.connect() as db:
            db.execute('INSERT INTO steps VALUES(?,?,?)', (identity, now(), text))

    def run(self, identity):
        try:
            self.step(identity, 'Checking the selected report and its saved numbers')
            with self.connect() as db:
                row = db.execute('SELECT snapshots.body FROM cases JOIN snapshots ON snapshots.id=cases.snapshot_id WHERE cases.id=?', (identity,)).fetchone()
            saved = json.loads(row[0])
            with closing(duckdb.connect(str(self.lab), read_only=True)) as db:
                db.execute('BEGIN TRANSACTION')
                if fingerprints(db) != saved['fingerprints']:
                    raise ValueError('Report data changed; open the report and submit again')
                payload, context = evidence(self.lab, True, connection=db)
            self.step(identity, 'Payment and refund records checked against the report')
            self.step(identity, 'Checking how the reported amount was calculated')
            finding = investigate(payload, self.folder / 'evidence.sqlite', context,
                                  lambda p, r: verify(self.lab, p, r))
            # A changed source invalidates conclusions about the submitted snapshot.
            with closing(duckdb.connect(str(self.lab), read_only=True)) as db:
                if fingerprints(db) != saved['fingerprints']:
                    raise ValueError('Data changed during investigation; submit a fresh report')
            impact = finding['impact_by_currency']['USD']
            is_double = finding.get('root_cause_verified') and finding.get('root_cause') == 'Gold build subtracts refund amount twice'
            result = {'headline': 'A refund was deducted twice' if is_double else 'Checks completed; review the evidence',
                      'explanation': 'The report deducted the same refund twice for one order. This made Net Cash $99 lower than it should be.' if is_double and impact['downstream_minus_upstream'] == '-99.0000' else 'The saved comparison is available. No supported business explanation has been verified for this case.',
                      'reported': impact['gold_total'], 'expected': impact['silver_total'],
                      'difference': impact['downstream_minus_upstream'],
                      'affected_orders': finding['affected_records'], 'verified': bool(is_double),
                      'investigation_id': finding['id'], 'technical': finding,
                      'next_action': 'Ask the reporting team to correct the refund calculation and recheck this report.' if is_double else 'Ask a reviewer to investigate further.',
                      'limitation': 'Verified in this isolated demo. The screenshot is attached for reference; report context is supplied by the selected report, not image recognition.'}
            self.step(identity, 'Results saved with supporting order evidence')
            with self.connect() as db:
                db.execute("UPDATE cases SET status='COMPLETED',result=? WHERE id=?", (encoded(result), identity))
        except Exception as exc:
            message = str(exc) if isinstance(exc, ValueError) else 'The check could not complete. Please ask a reviewer to inspect this case.'
            with self.connect() as db:
                db.execute("UPDATE cases SET status='NEEDS_REVIEW',result=? WHERE id=?", (encoded({'message': message}), identity))

    def detail(self, identity):
        with self.connect() as db:
            row = db.execute('SELECT question,status,result,screenshot,app_screenshot,snapshot_id FROM cases WHERE id=?', (str(UUID(identity)),)).fetchone()
            if row is None:
                raise KeyError(identity)
            steps = db.execute('SELECT at,text FROM steps WHERE case_id=? ORDER BY rowid', (identity,)).fetchall()
        return {'id': identity, 'question': row[0], 'status': row[1], 'result': json.loads(row[2]) if row[2] else None,
                'screenshot_sha256': hashlib.sha256(row[3]).hexdigest(), 'application_screenshot_attached': row[4] is not None,
                'snapshot_id': row[5], 'steps': [{'at': at, 'text': text} for at, text in steps]}


def create_app(service, token):
    if len(token) < 32 or not token.isascii():
        raise ValueError('Set a local access token of at least 32 ASCII characters')
    assets = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'), '/style.css': ('style.css', 'text/css')}

    def app(env, start):
        def respond(status, data, mime='application/json'):
            raw = data if isinstance(data, bytes) else encoded(data).encode()
            start(status, [('Content-Type', mime), ('Content-Length', str(len(raw))), ('Cache-Control', 'no-store'),
                           ('X-Content-Type-Options', 'nosniff'), ('Content-Security-Policy', "default-src 'self'; img-src 'self' blob:; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'")])
            return [raw]
        path, method = env.get('PATH_INFO', ''), env.get('REQUEST_METHOD')
        if method == 'GET' and path in assets:
            file, mime = assets[path]
            return respond('200 OK', (ROOT / 'apps/business-demo' / file).read_bytes(), mime)
        if not secrets.compare_digest(env.get('HTTP_AUTHORIZATION', ''), 'Bearer ' + token):
            return respond('401 Unauthorized', {'error': 'Sign in to the demo'})
        try:
            if method == 'GET' and path == '/api/report':
                return respond('200 OK', service.snapshot())
            if method == 'GET' and path.startswith('/api/cases/'):
                return respond('200 OK', service.detail(path.split('/')[-1]))
            if method == 'POST' and path == '/api/cases':
                size = int(env.get('CONTENT_LENGTH', '0'))
                if not 0 < size <= 8_100_000:
                    raise ValueError('Attachments are too large')
                if env.get('CONTENT_TYPE', '').split(';')[0] != 'application/json':
                    raise ValueError('JSON required')
                raw = env['wsgi.input'].read(size)
                if len(raw) != size:
                    raise ValueError('Incomplete request')
                return respond('201 Created', {'id': service.submit(json.loads(raw))})
            return respond('404 Not Found', {'error': 'Not found'})
        except (ValueError, TypeError):
            return respond('400 Bad Request', {'error': 'Check the report selection, question and PNG screenshots, then try again.'})
        except KeyError:
            return respond('404 Not Found', {'error': 'Case not found'})

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8773)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Invalid port')
    service = BusinessDemo(args.folder)
    app = create_app(service, os.environ.get('INVESTIGATOR_API_TOKEN', ''))
    with make_server('127.0.0.1', args.port, app, handler_class=QuietHandler) as server:
        print(f'Business demo: http://127.0.0.1:{args.port}', flush=True)
        server.serve_forever()

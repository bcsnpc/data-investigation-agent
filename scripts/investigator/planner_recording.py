"""Opt-in local planner fixtures. Never records HTTP headers or client credentials."""
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
ACTIVE = ContextVar('planner_recording', default=None)
FLAG = 'INVESTIGATOR_RECORD_PLANNER'


class RecordingError(ValueError):
    pass


def _bytes(value):
    return json.dumps(value, ensure_ascii=False, indent=2).encode('utf-8')


def _safe(data):
    # Scan decoded JSON as well as raw bytes so escaping cannot hide a credential.
    value = data.decode('utf-8', errors='replace')
    try:
        parsed = json.loads(value)
        value += '\n' + str(parsed)
    except ValueError:
        pass
    for name, secret in os.environ.items():
        if len(secret) >= 12 and re.search(r'(?:^|_)(?:API_KEY|ACCESS_TOKEN|REFRESH_TOKEN|TOKEN|SECRET|PASSWORD|CONNECTION_STRING|KEY)$', name, re.I):
            if secret in value:
                raise RecordingError('RECORDING_SECRET_DETECTED')
    if re.search(r'(?i)(?:Bearer\s+[A-Za-z0-9_.~-]{8,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|'
                 r'(?:password|pwd|api[_-]?key|client[_-]?secret|access[_-]?token)'
                 r'[\s\"\x27]*[:=][\s\"\x27]*[A-Za-z0-9+/_.~-]{8,})', value):
        raise RecordingError('RECORDING_SECRET_DETECTED')


class CallRecord:
    def __init__(self, metadata):
        self.path = ROOT / '.local' / 'planner-recordings' / str(uuid4())
        self.path.mkdir(parents=True, exist_ok=False)
        self.bodies = {}
        self.exclusion = None
        self.safe_write('context.json', _bytes({'version': 1, 'created_utc': datetime.now(timezone.utc).isoformat(), **metadata}))

    def write(self, name, data):
        _safe(data)
        # Exclusive files: interrupted attempts and previous evidence are never overwritten.
        with (self.path / name).open('xb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        self.bodies[name] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}

    def safe_write(self, name, data):
        """Recording is observational: withholding a body cannot abort a call."""
        try:
            self.write(name, data)
            return True
        except RecordingError:
            self.exclusion = 'SECRET_DETECTED'
        except OSError:
            if self.exclusion is None:
                self.exclusion = 'RECORDING_IO_ERROR'
        return False

    def request(self, request):
        self.safe_write('request.body', request.read())

    def response(self, response):
        self.safe_write('response-status.json', _bytes({'status_code': response.status_code}))
        self.safe_write('response.body', response.read())

    def finish(self, error=None):
        cause = error
        exclusion = self.exclusion
        for _ in range(5):
            if cause is None:
                break
            if isinstance(cause, RecordingError):
                exclusion = 'SECRET_DETECTED'
                break
            cause = cause.__cause__
        self.safe_write('manifest.json', _bytes({'version': 1, 'files': dict(self.bodies),
            'error_type': type(error).__name__ if error else None,
            'exclusion': exclusion,
            'request_captured': 'request.body' in self.bodies,
            'response_captured': 'response.body' in self.bodies}))


@contextmanager
def recording(metadata):
    """The flag is operator process configuration, never a ticket/provider field."""
    if os.environ.get(FLAG) != '1' or ACTIVE.get() is not None:
        yield ACTIVE.get()
        return
    record = CallRecord(metadata() if callable(metadata) else metadata)
    token = ACTIVE.set(record)
    error = None
    try:
        yield record
    except BaseException as exc:
        error = exc
        raise
    finally:
        ACTIVE.reset(token)
        record.finish(error)


def http_options():
    record = ACTIVE.get()
    if record is None:
        return {}
    from openai import DefaultHttpxClient
    return {'http_client': DefaultHttpxClient(event_hooks={
        'request': [record.request], 'response': [record.response]})}


def load_session(session_id, directory=None):
    """Load byte-exact local fixtures without importing a provider or opening a network."""
    directory = Path(directory) if directory else ROOT / '.local' / 'planner-recordings'
    calls = []
    for path in directory.glob('*/context.json'):
        context = json.loads(path.read_bytes())
        if context.get('session_id') != session_id:
            continue
        manifest_path = path.parent / 'manifest.json'
        if not manifest_path.exists():
            raise RecordingError('RECORDING_INTERRUPTED')
        manifest = json.loads(manifest_path.read_bytes())
        bodies = {}
        for name, expected in manifest['files'].items():
            if name not in {'context.json', 'request.body', 'response.body', 'response-status.json', 'runtime-return.json'}:
                raise RecordingError('RECORDING_UNKNOWN_FILE')
            data = (path.parent / name).read_bytes()
            if len(data) != expected['bytes'] or hashlib.sha256(data).hexdigest() != expected['sha256']:
                raise RecordingError('RECORDING_INTEGRITY_MISMATCH')
            bodies[name] = data
        calls.append({'context': context, 'manifest': manifest, 'bodies': bodies})
    return sorted(calls, key=lambda call: (call['context'].get('planner_call', 0), call['context']['created_utc']))

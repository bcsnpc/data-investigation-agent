"""Azure SDK transport boundary: gate and journal every physical HTTP attempt.

Storage SDK does not install ``per_call_policies``. A transport wrapper is the
supported final send boundary, below SDK retry/redirect policies. No headers,
credentials, request bodies or provider exception messages enter this journal.
"""
import json
import hashlib
import os
from pathlib import Path
import threading
import time
import uuid
from urllib.parse import urlsplit, urlunsplit

from azure.core.pipeline.transport import HttpTransport, RequestsTransport

_LOCK = threading.Lock()


class GuardedTransport(HttpTransport):
    def __init__(self, gateway, identity, *, receipts=None, inner=None):
        self.gateway = gateway
        self.identity = identity
        self.receipts = Path(receipts or os.environ.get(
            'DIA_PLATFORM_CONTROL_RECEIPTS', '.local/platform-control-requests.jsonl'))
        self.inner = inner if inner is not None else RequestsTransport()

    def open(self):
        self.inner.open()

    def close(self):
        self.inner.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    def _record(self, record):
        # A journal failure before send prevents dispatch. An unresolved DISPATCHED
        # entry is conservatively counted after a process crash, never refunded.
        with _LOCK:
            self.receipts.parent.mkdir(parents=True, exist_ok=True)
            with self.receipts.open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(record, sort_keys=True) + '\n')
                stream.flush()
                os.fsync(stream.fileno())

    def send(self, request, **kwargs):
        # Exact original URL goes to the gate; only the query-free route is logged.
        # The RequestsTransport itself disables automatic requests redirects.
        self.gateway.http(self.identity, request.method, request.url,
                          body=request.body,headers=dict(request.headers))
        url = urlsplit(request.url)
        base = {'id': str(uuid.uuid4()), 'at': time.time(), 'identity': self.identity,
                'method': request.method, 'url': urlunsplit((url.scheme, url.netloc, url.path, '', '')),
                'request_url_sha256': hashlib.sha256(request.url.encode()).hexdigest(),
                'class': 'PLATFORM_CONTROL', 'physical_requests': 1}
        self._record({**base, 'phase': 'DISPATCHED'})
        try:
            response = self.inner.send(request, **kwargs)
        except Exception as error:
            self._record({**base, 'phase': 'ERROR', 'error_type': type(error).__name__})
            raise
        self._record({**base, 'phase': 'RESPONSE', 'status': response.status_code})
        return response

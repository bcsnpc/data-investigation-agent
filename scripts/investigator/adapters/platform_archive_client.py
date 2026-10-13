"""Identity-authenticated platform archive transport; no credential fallback."""
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import xml.etree.ElementTree as ET
from ..artifact_store import ArtifactError
from .platform_archive import BLOCK_BYTES, bind


class IdentityArchiveClient:
    """Azure token credential only. Fixed REST operations, finite controls/retries."""
    def __init__(self, account_url, credential, gateway, channel, *, max_requests, receipts, transport=None, sleep=time.sleep):
        from .guarded_transport import GuardedTransport
        if not callable(getattr(credential, 'get_token', None)):
            raise ArtifactError('ARCHIVE_TOKEN_CREDENTIAL_REQUIRED')
        if type(max_requests) is not int or max_requests < 1:
            raise ArtifactError('ARCHIVE_CONTROL_CAP_REQUIRED')
        self.account_url, self.credential, self.gateway, self.channel = account_url, credential, gateway, channel
        # One cap spans restarts; interrupted sends remain charged.
        previous = []
        if Path(receipts).exists():
            previous = [json.loads(line) for line in Path(receipts).read_text().splitlines()]
        charged = sum(row.get('phase') == 'DISPATCHED' for row in previous)
        self.remaining, self.sleep = max_requests - charged, sleep
        self.transport = transport or GuardedTransport(gateway, channel, receipts=receipts)

    @staticmethod
    def close(response):
        # azure.core's transport response wraps requests.Response; unlike the
        # higher-level REST response, the transport response has no close().
        target = getattr(response, 'internal_response', response)
        target.close()

    def request(self, key, operation, *, body=b'', block_id=None, etag=None, absent=False):
        from azure.core.pipeline.transport import HttpRequest
        from azure.core.exceptions import ServiceRequestError, ServiceResponseError
        with bind(self.gateway, self.channel, self.account_url, key, operation, body=body, block_id=block_id, etag=etag) as (method, url, required):
            for attempt in range(3):
                if self.remaining <= 0:
                    raise ArtifactError('ARCHIVE_CONTROL_CAP_REACHED')
                token = self.credential.get_token('https://storage.azure.com/.default')
                headers = {**required, 'Authorization': 'Bearer ' + token.token, 'x-ms-version': '2023-11-03',
                           'x-ms-date': datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')}
                self.remaining -= 1
                try:
                    response = self.transport.send(HttpRequest(method, url, headers=headers, data=body), stream=True,
                                                   connection_timeout=30, read_timeout=60)
                except (ServiceRequestError, ServiceResponseError):
                    if attempt == 2:
                        raise
                    self.sleep(2 ** attempt)
                    continue
                if response.status_code in (408, 429, 500, 502, 503, 504) and attempt < 2:
                    self.close(response)
                    self.sleep(2 ** attempt)
                    continue
                if absent and response.status_code == 404:
                    self.close(response)
                    return None
                if operation == 'COMMIT' and response.status_code in (409, 412):
                    self.close(response)
                    return None  # another attempt committed; whole download still required
                if not 200 <= response.status_code < 300:
                    status = response.status_code
                    self.close(response)
                    raise ArtifactError('ARCHIVE_HTTP_' + str(status))
                return response

    def properties(self, key):
        response = self.request(key, 'HEAD', absent=True)
        if response is None:
            return None
        try:
            headers = {k.lower(): v for k, v in response.headers.items()}
            return {'tier': headers.get('x-ms-access-tier'), 'etag': headers.get('etag')}
        finally:
            self.close(response)

    def blocks(self, key):
        response = self.request(key, 'BLOCKS', absent=True)
        if response is None:
            return {}
        try:
            data = bytearray()
            for chunk in response.stream_download(None):
                data.extend(chunk)
                if len(data) > BLOCK_BYTES:
                    raise ArtifactError('ARCHIVE_BLOCK_LIST_BOUND')
            root = ET.fromstring(bytes(data))
            return {row.findtext('Name'): int(row.findtext('Size')) for row in root.findall('./UncommittedBlocks/Block')}
        finally:
            self.close(response)

    def stage(self, key, identity, data):
        self.close(self.request(key, 'STAGE', body=data, block_id=identity))

    def commit(self, key, identities):
        root = ET.Element('BlockList')
        for identity in identities:
            ET.SubElement(root, 'Latest').text = identity
        response = self.request(key, 'COMMIT', body=ET.tostring(root, encoding='utf-8'))
        if response is not None:
            self.close(response)

    def download_chunks(self, key):
        response = self.request(key, 'DOWNLOAD')
        try:
            yield from response.stream_download(None)
        finally:
            self.close(response)

    def archive(self, key, etag):
        self.close(self.request(key, 'ARCHIVE', etag=etag))

"""One-request, content-bound authority for the private archive container."""
from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
import base64
import re
from urllib.parse import urlencode
from ..artifact_store import ArtifactError

ACTIVE = ContextVar('platform_archive_binding', default=None)
BLOCK_BYTES = 4 * 1024 * 1024


def declaration(value):
    from .blob_artifacts import validate_account_url
    if not isinstance(value, dict) or set(value) != {'account_url', 'container'} or value['container'] != 'archive':
        raise ArtifactError('PLATFORM_ARCHIVE_DECLARATION_REQUIRED')
    validate_account_url(value['account_url'])
    return value


@contextmanager
def bind(gateway, identity, account_url, key, operation, *, body=b'', block_id=None, etag=None, blob_md5=None):
    requested = declaration({'account_url': account_url, 'container': 'archive'})
    permissions = gateway.identity(identity)
    if permissions.get('role') != 'platform' or requested not in permissions.get('platform_archive', []):
        raise ArtifactError('PLATFORM_ARCHIVE_NOT_ALLOWED')
    if not re.fullmatch(r'originals/[0-9a-f]{64}/[0-9a-f]{64}(?:\.gz)?', key):
        raise ArtifactError('ARCHIVE_OBJECT_KEY')
    if not isinstance(body, bytes) or len(body) > BLOCK_BYTES:
        raise ArtifactError('ARCHIVE_REQUEST_BOUND')
    method, query, headers = {
        'HEAD': ('HEAD', {}, {}), 'DOWNLOAD': ('GET', {}, {}),
        'BLOCKS': ('GET', {'comp': 'blocklist', 'blocklisttype': 'all'}, {}),
        'STAGE': ('PUT', {'comp': 'block', 'blockid': block_id}, {}),
        'COMMIT': ('PUT', {'comp': 'blocklist'}, {'if-none-match': '*', 'x-ms-access-tier': 'Hot'}),
        'STAGE_CHECKED': ('PUT', {'comp': 'block', 'blockid': block_id},
                          {'content-md5': base64.b64encode(hashlib.md5(body).digest()).decode()}),
        'COMMIT_COOL': ('PUT', {'comp': 'blocklist'}, {'if-none-match': '*', 'x-ms-access-tier': 'Cool',
                        'content-md5': base64.b64encode(hashlib.md5(body).digest()).decode(),
                        'x-ms-blob-content-md5': blob_md5}),
        'ARCHIVE': ('PUT', {'comp': 'tier'}, {'if-match': etag, 'x-ms-access-tier': 'Archive'}),
    }.get(operation, (None, None, None))
    if method is None or (operation in ('STAGE','STAGE_CHECKED') and not re.fullmatch(r'[A-Za-z0-9+/]{86}==', block_id or '')):
        raise ArtifactError('ARCHIVE_OPERATION')
    if operation=='COMMIT_COOL':
        try: valid=isinstance(blob_md5,str) and len(base64.b64decode(blob_md5,validate=True))==16
        except ValueError: valid=False
        if not valid:raise ArtifactError('ARCHIVE_BLOB_MD5_REQUIRED')
    if operation == 'ARCHIVE' and not etag:
        raise ArtifactError('ARCHIVE_ETAG_REQUIRED')
    if operation not in ('STAGE', 'COMMIT','STAGE_CHECKED','COMMIT_COOL') and body:
        raise ArtifactError('ARCHIVE_BODY_FORBIDDEN')
    url = account_url + '/archive/' + key + ('?' + urlencode(query) if query else '')
    selected = ACTIVE.set({'gateway': gateway, 'identity': identity, 'url': url, 'method': method,
                          'sha': hashlib.sha256(body).hexdigest(), 'headers': headers})
    try:
        yield method, url, headers
    finally:
        ACTIVE.reset(selected)


def permits(gateway, identity, method, url, body, headers):
    selected = ACTIVE.get()
    headers = {k.lower(): v for k, v in (headers or {}).items()}
    return bool(selected and selected['gateway'] is gateway and selected['identity'] == identity
                and method == selected['method'] and url == selected['url']
                and isinstance(body or b'', bytes) and hashlib.sha256(body or b'').hexdigest() == selected['sha']
                and all(headers.get(k) == v for k, v in selected['headers'].items()))

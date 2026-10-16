"""Trusted recorder-only, one-object authority for private CAS transport."""
from contextlib import contextmanager
from contextvars import ContextVar
import gzip
import hashlib
import io
import re
from types import SimpleNamespace

from ..artifact_store import ArtifactError, CHUNK_SIZE, Files

ACTIVE = ContextVar('platform_cas_request_binding',default=None)
CONTAINERS=frozenset({'snapshots','tapes','captures','screenshots'})
MAX_OBJECT_BYTES=4*1024*1024


def declaration(value):
    from .blob_artifacts import validate_account_url
    if not isinstance(value,dict) or set(value)!={'account_url','container'}:
        raise ArtifactError('PLATFORM_CAS_DECLARATION_REQUIRED')
    validate_account_url(value['account_url'])
    if value['container'] not in CONTAINERS:raise ArtifactError('ARTIFACT_CONTAINER_NOT_ALLOWED')
    return value


def validate_key(key):
    if not isinstance(key,str) or not re.fullmatch(r'(chunks|files)/[0-9a-f]{64}',key):
        raise ArtifactError('INVALID_OBJECT_KEY')
    return key


def payload(key,data):
    validate_key(key)
    if not isinstance(data,bytes) or len(data)>MAX_OBJECT_BYTES:
        raise ArtifactError('PLATFORM_CAS_PAYLOAD_BOUND')
    expected=key.split('/')[1]
    if key.startswith('chunks/'):
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:raw=stream.read(CHUNK_SIZE+1)
        if len(raw)>CHUNK_SIZE or hashlib.sha256(raw).hexdigest()!=expected:
            raise ArtifactError('CHUNK_INTEGRITY')
    else:
        Files(SimpleNamespace(get=lambda _:data)).describe(expected)
    return hashlib.sha256(data).hexdigest()


@contextmanager
def bind(gateway,identity,account_url,container,key,data=None):
    requested=declaration({'account_url':account_url,'container':container})
    validate_key(key)
    permissions=gateway.identity(identity)
    if permissions.get('role')!='platform' or requested not in permissions.get('platform_cas',[]):
        from ..live_gateway import _deny
        _deny('PLATFORM_CAS_NOT_ALLOWED',identity=identity)
    fingerprint=payload(key,data) if data is not None else None
    binding={'gateway':gateway,'identity':identity,'url':account_url+'/'+container+'/'+key,
             'body_sha256':fingerprint}
    selected=ACTIVE.set(binding)
    try:yield
    finally:ACTIVE.reset(selected)


def permits(gateway,identity,method,url,body,headers):
    binding=ACTIVE.get()
    if (not binding or binding['gateway'] is not gateway or binding['identity']!=identity
            or url!=binding['url']):return False
    if method=='GET':return body in (None,b'')
    if method!='PUT' or binding['body_sha256'] is None:return False
    if not isinstance(body,bytes) or hashlib.sha256(body).hexdigest()!=binding['body_sha256']:return False
    headers={k.lower():v for k,v in (headers or {}).items()}
    return headers.get('if-none-match')=='*' and headers.get('x-ms-blob-type')=='BlockBlob'

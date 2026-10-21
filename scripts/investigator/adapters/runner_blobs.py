"""Run-specific immutable JSON capture authority on existing platform storage."""
import re
from urllib.parse import urlsplit
from ..artifact_store import ArtifactError

MAX_BYTES=32*1024*1024

def declaration(value):
    from .blob_artifacts import validate_account_url
    if not isinstance(value,dict) or set(value)!={'account_url','prefix','run_id','max_bytes'}:raise ArtifactError('RUNNER_BLOB_DECLARATION')
    validate_account_url(value['account_url'])
    if not re.fullmatch(r'[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*',value['prefix']) or any(part in ('.','..') for part in value['prefix'].split('/')):raise ArtifactError('RUNNER_BLOB_PREFIX')
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',value['run_id']):raise ArtifactError('RUNNER_BLOB_RUN_ID')
    if type(value['max_bytes'])is not int or not 1<=value['max_bytes']<=MAX_BYTES:raise ArtifactError('RUNNER_BLOB_BOUND')
    return value

def permits(gateway,identity,method,url,body,headers):
    parts=urlsplit(url)
    if parts.query or parts.fragment:return False
    for scope in gateway.identity(identity).get('runner_captures',[]):
        declaration(scope)
        prefix=scope['account_url']+'/captures/'+scope['prefix']+'/'+scope['run_id']+'/'
        if not url.startswith(prefix):continue
        leaf=url[len(prefix):]
        if not re.fullmatch(r'(?:[0-9]{8}-[a-z-]+|run-record)\.json',leaf):return False
        if method in ('GET','HEAD'):return body in (None,b'')
        if method!='PUT' or not isinstance(body,bytes) or len(body)>scope['max_bytes']:return False
        headers={k.lower():v for k,v in (headers or {}).items()}
        if headers.get('if-none-match')!='*' or headers.get('x-ms-blob-type')!='BlockBlob':return False
        from ..planner_recording import _safe
        _safe(body)
        return True
    return False

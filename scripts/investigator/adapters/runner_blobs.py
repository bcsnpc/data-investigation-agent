"""Run-specific immutable JSON capture authority on existing platform storage."""
import re,os
from pathlib import Path
from ..process_tape import bytes_of
from urllib.parse import urlsplit
from ..artifact_store import ArtifactError

MAX_BYTES=32*1024*1024


def immutable_upload(put,read,key,raw,*,sleep=None):
    """Retry only this immutable publication, never the investigation step.

    A lost PUT response may mean Azure already committed it. In that case a
    conditional retry returns 412; accepting it requires identical stored bytes.
    """
    import time
    from urllib.error import HTTPError,URLError
    sleep=sleep or time.sleep
    for attempt in range(3):
        try:return put(key,raw)
        except HTTPError as error:
            if error.code==412:
                if read(key)!=raw:raise ArtifactError('RUN_CAPTURE_IMMUTABLE_BYTES_DIFFER') from None
                return
            if error.code not in (408,429,500,502,503,504) or attempt==2:raise
        except (URLError,TimeoutError,ConnectionError):
            if attempt==2:raise
        sleep(2**attempt)

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
        if not re.fullmatch(r'(?:[0-9]{8}-[a-z-]+|run-record|timing-summary)\.json',leaf):return False
        if method in ('GET','HEAD'):return body in (None,b'')
        if method!='PUT' or not isinstance(body,bytes) or len(body)>scope['max_bytes']:return False
        headers={k.lower():v for k,v in (headers or {}).items()}
        if headers.get('if-none-match')!='*' or headers.get('x-ms-blob-type')!='BlockBlob':return False
        from ..planner_recording import _safe
        _safe(body)
        return True
    return False


def sink(config):
    """Use existing platform transport, managed identity and gateway allowlist."""
    from urllib.request import Request,build_opener
    from metadata_auth import NoRedirect
    from .managed_identity import Tokens
    from ..live_gateway import current,open_http
    from .blob_artifacts import validate_account_url
    validate_account_url(config['account_url'])
    prefix=config['prefix'].strip('/')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*',prefix):raise ValueError('RUN_CAPTURE_PREFIX_INVALID')
    tokens=Tokens(config['identity']);opener=build_opener(NoRedirect())
    def upload(key,raw):
        url=config['account_url']+'/captures/'+prefix+'/'+key
        headers={'x-ms-version':'2023-11-03','x-ms-blob-type':'BlockBlob','If-None-Match':'*','Content-Type':'application/json'}
        status=None
        try:
            current().http(config['channel'],'PUT',url,raw,headers)
            headers['Authorization']='Bearer '+tokens.get_token('https://storage.azure.com/.default')
            with open_http(opener,Request(url,data=raw,headers=headers,method='PUT'),timeout=120,identity=config['channel']) as response:
                status=response.status
                if status!=201:raise ValueError('RUN_CAPTURE_BLOB_PUT_FAILED')
        finally:
            log=Path(os.environ['DIA_PLATFORM_CONTROL_RECEIPTS']);log.parent.mkdir(parents=True,exist_ok=True)
            with log.open('ab') as stream:
                stream.write(bytes_of({'kind':'PLATFORM_ARTIFACT_CONTROL','method':'PUT','url':url,'http_status':status,'principal_id':config['identity']['principal_id'],'body_bytes':len(raw)})+b'\n')
                stream.flush();os.fsync(stream.fileno())
    def download(key):
        url=config['account_url']+'/captures/'+prefix+'/'+key
        headers={'x-ms-version':'2023-11-03'};status=None;count=0
        try:
            current().http(config['channel'],'GET',url,None,headers)
            headers['Authorization']='Bearer '+tokens.get_token('https://storage.azure.com/.default')
            with open_http(opener,Request(url,headers=headers,method='GET'),timeout=120,identity=config['channel']) as response:
                status=response.status
                if status!=200:raise ValueError('RUN_CAPTURE_BLOB_GET_FAILED')
                raw=response.read(MAX_BYTES+1);count=len(raw)
                if count>MAX_BYTES:raise ValueError('RUN_CAPTURE_BLOB_READ_BOUND')
                return raw
        finally:
            log=Path(os.environ['DIA_PLATFORM_CONTROL_RECEIPTS']);log.parent.mkdir(parents=True,exist_ok=True)
            with log.open('ab') as stream:
                stream.write(bytes_of({'kind':'PLATFORM_ARTIFACT_CONTROL','method':'GET','url':url,'http_status':status,'principal_id':config['identity']['principal_id'],'body_bytes':count})+b'\n')
                stream.flush();os.fsync(stream.fileno())
    def publish(key,raw):return immutable_upload(upload,download,key,raw)
    publish.read=download
    return publish

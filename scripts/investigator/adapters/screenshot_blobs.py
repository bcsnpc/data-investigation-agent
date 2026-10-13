"""Private screenshot pixels, with exact one-object platform authorization."""
from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
import re
from uuid import UUID

from ..artifact_store import ArtifactError
from .blob_artifacts import validate_account_url

ACTIVE = ContextVar('screenshot_blob_binding', default=None)


def declaration(value):
    if not isinstance(value, dict) or set(value) != {'account_url', 'container'} or value['container'] != 'screenshots':
        raise ArtifactError('SCREENSHOT_STORAGE_DECLARATION')
    validate_account_url(value['account_url'])
    return value


def object_key(environment, identity, sha256):
    if str(UUID(identity)) != identity or not re.fullmatch('[0-9a-f]{64}', sha256):
        raise ArtifactError('SCREENSHOT_OBJECT_IDENTITY')
    return 'images/'+hashlib.sha256(environment.encode()).hexdigest()+'/'+identity+'/'+sha256


def validate_key(key):
    if not isinstance(key, str) or not re.fullmatch(r'images/[0-9a-f]{64}/[0-9a-f-]{36}/[0-9a-f]{64}', key):
        raise ArtifactError('SCREENSHOT_OBJECT_KEY')
    UUID(key.split('/')[2])
    return key


@contextmanager
def bind(gateway, channel, account_url, key, method, data=None):
    allowed=declaration({'account_url':account_url,'container':'screenshots'})
    permissions=gateway.identity(channel)
    if permissions.get('role')!='platform' or allowed not in permissions.get('platform_screenshots',[]):
        raise ArtifactError('SCREENSHOT_PLATFORM_CHANNEL_NOT_ALLOWED')
    validate_key(key)
    if method not in ('GET','PUT','DELETE'):raise ArtifactError('SCREENSHOT_METHOD_NOT_ALLOWED')
    if method=='PUT' and (not isinstance(data, bytes) or not 1<=len(data)<=1024*1024
                          or hashlib.sha256(data).hexdigest()!=key.split('/')[-1]):
        raise ArtifactError('SCREENSHOT_PAYLOAD_IDENTITY')
    token=ACTIVE.set({'gateway':gateway,'channel':channel,'method':method,
                     'url':account_url+'/screenshots/'+key,'data':data})
    try:yield
    finally:ACTIVE.reset(token)


def permits(gateway, channel, method, url, body, headers):
    b=ACTIVE.get()
    if not b or b['gateway'] is not gateway or b['channel']!=channel or b['method']!=method or b['url']!=url:return False
    if method=='PUT':
        h={k.lower():v for k,v in (headers or {}).items()}
        return body==b['data'] and h.get('if-none-match')=='*' and h.get('x-ms-blob-type')=='BlockBlob'
    return body in (None,b'')


class Objects:
    def __init__(self, config):
        from azure.storage.blob import ContainerClient
        from .guarded_transport import GuardedTransport
        from .blob_artifacts import bound_credential
        from ..live_gateway import current
        self.account_url=validate_account_url(config['account_url']);self.channel=config['channel'];self.gateway=current()
        self.client=ContainerClient(self.account_url,'screenshots',credential=bound_credential(config['identity']),
            transport=GuardedTransport(self.gateway,self.channel),retry_total=0)

    def put(self,key,data):
        from azure.core.exceptions import ResourceExistsError
        with bind(self.gateway,self.channel,self.account_url,key,'PUT',data):
            try:self.client.get_blob_client(key).upload_blob(data,overwrite=False,validate_content=True)
            except ResourceExistsError:
                # A retry is safe only after byte verification, via its own gate.
                if self.get(key)!=data:raise ArtifactError('SCREENSHOT_IMMUTABLE_CONFLICT')

    def get(self,key):
        with bind(self.gateway,self.channel,self.account_url,key,'GET'):
            return self.client.get_blob_client(key).download_blob().readall()

    def delete(self,key):
        from azure.core.exceptions import ResourceNotFoundError
        with bind(self.gateway,self.channel,self.account_url,key,'DELETE'):
            try:self.client.get_blob_client(key).delete_blob()
            except ResourceNotFoundError:pass

"""Bounded privileged metadata transport: only the scanner gateway grants I/O."""
import json
from urllib.request import Request,build_opener
from urllib.parse import urlsplit
from urllib.error import HTTPError
from metadata_auth import NoRedirect
from . import scanner_identity as auth
from . import scanner_policy
from ..live_gateway import current,open_http


def channel(declaration):
    d=auth.validate(declaration);return 'scanner:'+d['tenant_id']+':'+d['client_id']


class ScannerHttp:
    SERVICES={'fabric':('https://api.fabric.microsoft.com/v1/','https://api.fabric.microsoft.com/.default'),
              'powerbi':('https://api.powerbi.com/v1.0/myorg/','https://analysis.windows.net/powerbi/api/.default')}
    def __init__(self,tokens,*,meter,opener=None,max_bytes=16*1024*1024):
        if not isinstance(tokens,auth.Tokens)or not callable(meter):raise ValueError('SCANNER_TOKENS_AND_METER_REQUIRED')
        auth.require_job(tokens.declaration)
        if type(max_bytes)is not int or not 1<=max_bytes<=16*1024*1024:raise ValueError('SCANNER_RESPONSE_BOUND')
        self.tokens,self.meter,self.opener,self.max_bytes=tokens,meter,opener or build_opener(NoRedirect()),max_bytes
    def __call__(self,endpoint,method='get',audience='fabric',body=None):
        if audience not in self.SERVICES:raise ValueError('SCANNER_AUDIENCE_FORBIDDEN')
        parsed=urlsplit(endpoint)
        if parsed.scheme or parsed.netloc or endpoint.startswith('/')or '..'in parsed.path.split('/'):
            raise ValueError('SCANNER_RELATIVE_ENDPOINT_REQUIRED')
        base,scope=self.SERVICES[audience];url=base+endpoint;method=method.upper()
        raw=None if body is None else json.dumps(body,sort_keys=True,separators=(',',':')).encode()
        if raw is not None and len(raw)>65536:raise ValueError('SCANNER_REQUEST_BOUND')
        who=channel(self.tokens.declaration);gateway=current()
        grant=gateway.http(who,method,url,raw)  # before any credential is acquired
        def send():
            request=Request(url,data=raw,method=method,headers={'Content-Type':'application/json',
                'Authorization':'Bearer '+self.tokens.get_token(scope)})
            try:
                with open_http(self.opener,request,timeout=90,identity=who)as response:
                    content=response.read(self.max_bytes+1)
                    if len(content)>self.max_bytes:raise ValueError('SCANNER_RESPONSE_BOUND')
                    value={'status_code':response.status,'headers':dict(response.headers),
                           'text':json.loads(content)if content else {}}
            except HTTPError as exc:
                from .metadata_error import MetadataUnavailable
                try:
                    content=exc.read(32769);error=json.loads(content)if len(content)<=32768 else None
                except Exception:error=None
                raise MetadataUnavailable(exc.code,error)from None
            scanner_policy.bind_response(gateway.identity(who),who,grant,method,url,raw,value)
            return value
        return self.meter(send)

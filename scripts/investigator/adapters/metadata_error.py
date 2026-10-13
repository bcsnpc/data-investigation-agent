"""Bounded provider diagnostics; response messages, URLs and headers never escape."""
import re
from ..process_failure import capture

CODES = frozenset({'Forbidden','Unauthorized','InsufficientPrivileges','InsufficientPermissions',
    'ItemNotFound','EntityNotFound','NotFound','OperationNotSupported','InvalidRequest',
    'TooManyRequests','CapacityNotActive','ServiceUnavailable','AccessDenied',
    'PowerBINotAuthorizedException','AuthorizationFailed','UnsupportedOperation'})

def provider_code(value):
    return value if isinstance(value,str) and (value in CODES or re.fullmatch(r'AADSTS[0-9]{4,12}',value)) else None

class MetadataUnavailable(RuntimeError):
    def __init__(self,status,body=None):
        self.http_status=status if type(status)is int and 100<=status<=599 else None
        super().__init__('Metadata HTTP status '+str(self.http_status) if self.http_status is not None else 'Metadata provider request unavailable')
        body=body if isinstance(body,dict) else {}
        error=body.get('error') if isinstance(body.get('error'),dict) else {}
        self.provider_code=provider_code(body.get('errorCode') or error.get('code') or body.get('code'))

def safe_failure(error):
    result=capture(error)
    if isinstance(error,MetadataUnavailable):
        result.update(message='Metadata provider request unavailable',message_redacted=False)
    status=getattr(error,'http_status',None)
    if type(status)is int and 100<=status<=599:result['http_status']=status
    code=provider_code(getattr(error,'provider_code',None))
    if code is not None:result['provider_code']=code
    return result

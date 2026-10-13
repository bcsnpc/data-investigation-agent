"""Privileged metadata identity, loadable only inside a trusted scanner job.

No model tool or investigation config selects this adapter. Its platform roles
do not authorize writes: every token exchange and estate operation still passes
the scanner-specific gateway policy.
"""
from contextlib import contextmanager
from contextvars import ContextVar
import copy
from uuid import UUID

from . import federated_reader as federation

MODE='federated_scanner'
SCOPES=federation.SCOPES-{'https://database.windows.net/.default'}
_JOB=ContextVar('privileged_metadata_scanner_job',default=None)


def validate(value):
    if not isinstance(value,dict) or value.get('mode')!=MODE:
        raise ValueError('SCANNER_CONFIGURATION_REQUIRED')
    plain=copy.deepcopy(value);plain['mode']=federation.MODE
    federation.validate(plain)
    return copy.deepcopy(value)


def principal(value):
    d=validate(value);return tuple(d[k]for k in ('tenant_id','client_id','principal_id'))


@contextmanager
def job(declaration,workspaces,*,kind):
    if kind not in ('SCAN','CHANGE_DETECTION') or not isinstance(workspaces,(list,tuple)) or not 1<=len(workspaces)<=3:
        raise ValueError('SCANNER_JOB_SCOPE_REQUIRED')
    workspaces=tuple(str(UUID(w)) for w in workspaces)
    if len(set(workspaces))!=len(workspaces):raise ValueError('SCANNER_WORKSPACE_SCOPE_DUPLICATE')
    if _JOB.get() is not None:raise ValueError('SCANNER_JOB_NESTING_REFUSED')
    token=_JOB.set((principal(declaration),frozenset(workspaces),kind))
    try:yield
    finally:_JOB.reset(token)


def require_job(declaration,workspaces=()):
    active=_JOB.get()
    if active is None or active[0]!=principal(declaration) or not set(workspaces)<=active[1]:
        raise PermissionError('SCANNER_CREDENTIAL_UNAVAILABLE_TO_INVESTIGATION')


def channel(value,scope):
    d=validate(value)
    if scope not in SCOPES:raise ValueError('SCANNER_AUDIENCE_FORBIDDEN')
    return 'scanner:'+d['tenant_id']+':'+d['client_id']+(':'+('fabric' if 'api.fabric.' in scope else 'powerbi'))


def validate_exchange(method,url,body,grant):
    try:
        d=validate(grant['authentication']);require_job(d)
        if grant['scope']not in SCOPES:return False
        converted=copy.deepcopy(grant);converted['authentication']['mode']=federation.MODE
        return federation.validate_request(method,url,body,converted)
    except Exception:return False


class Tokens:
    def __init__(self,declaration,*,managed=None,opener=None):
        self.declaration=validate(declaration);require_job(self.declaration)
        self.managed,self.opener=managed,opener

    def get_token(self,scope):
        require_job(self.declaration)
        identity=channel(self.declaration,scope)
        value=copy.deepcopy(self.declaration);value['mode']=federation.MODE
        # Share only the existing exchange implementation/claim checks; this is
        # still a scanner-only logical channel with a scanner auth grant.
        return federation.Tokens(value,managed=self.managed,opener=self.opener,
                                 gateway_identity=identity).get_token(scope)

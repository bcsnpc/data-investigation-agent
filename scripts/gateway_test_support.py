"""Explicit synthetic policies for transport tests; never imported by runtime."""
from contextlib import contextmanager
import copy
import os
from unittest.mock import patch
from investigator.live_gateway import ACTIVE, configured

@contextmanager
def allow_http(*entries):
    base=copy.deepcopy(ACTIVE.get().policy) if ACTIVE.get() else {'version':1,'live_enabled':True,'identities':{}}
    grants=base['identities'].setdefault('offline-test',{}).setdefault('http',[])
    for entry in entries:
        if entry not in grants:grants.append(entry)
    with patch.dict(os.environ,{'DIA_GATEWAY_HTTP_IDENTITY':'offline-test','DIA_GATEWAY_MODEL_IDENTITY':'offline-test'}),configured(base):
        yield

@contextmanager
def allow_models():
    with allow_http(*[{'method':'POST','url':'https://'+host+'.openai.azure.com/openai/v1/responses','purpose':'model'}
                      for host in ('test','offline','synthetic')]):yield

@contextmanager
def allow_sql(server,database,objects,controls=()):
    base=copy.deepcopy(ACTIVE.get().policy) if ACTIVE.get() else {'version':1,'live_enabled':True,'identities':{}}
    base['identities'].setdefault('offline-test',{}).setdefault('sql',[]).append({
        'server':server,'database':database,'objects':objects,'read_only':True,'row_cap':1000,
        'timeout_seconds':30,'controls':list(controls)})
    with patch.dict(os.environ,{'DIA_GATEWAY_SQL_IDENTITY':'offline-test'}),configured(base):yield

@contextmanager
def allow_native(operation,**target):
    base=copy.deepcopy(ACTIVE.get().policy) if ACTIVE.get() else {'version':1,'live_enabled':True,'identities':{}}
    base['identities'].setdefault('offline-test',{}).setdefault('native_controls',[]).append({'operation':operation,**target})
    with patch.dict(os.environ,{'DIA_GATEWAY_HTTP_IDENTITY':'offline-test'}),configured(base):yield

"""Pinned OpenRouter Chat Completions. No model/provider failover or paid fallback."""
import json
from dataclasses import replace
from copy import deepcopy
from . import reasoning_nvidia as wire
from ..openrouter_budget import FreeBudget, PaidBudget

BASE='https://openrouter.ai/api/v1'
READ_TOOLS=wire.READ_TOOLS


def request_for(**kwargs):
    # Reuse the tested wire codec, preserving opaque provider state on tool continuations.
    kwargs=deepcopy(kwargs)
    for message in kwargs['messages']:
        if isinstance(message['content'],list):
            for block in message['content']:
                if block.get('type')=='provider_state' and block.get('provider')=='openrouter':block['provider']='nvidia'
    value=wire.request_for(**kwargs)
    value.update(stream=True,stream_options={'include_usage':True},
                 provider={'allow_fallbacks':False,'require_parameters':True},usage={'include':True})
    if kwargs['model'].endswith(':free'):value['provider']['max_price']={'prompt':0,'completion':0}
    return value


def response_for(body,model,tools):
    reply=wire.response_for(body,model,tools)
    for block in reply.content:
        if block.get('type')=='provider_state':block['provider']='openrouter'
    return replace(reply,provider='openrouter')


def authorize_body(permissions,method,url,raw):
    spec=permissions.get('ai_providers',{}).get('openrouter')
    if not isinstance(spec,dict) or spec.get('endpoint')!=BASE or spec.get('synthetic_only')is not True or spec.get('quality_scope')!='DEV_ONLY':
        raise ValueError('OPENROUTER_SYNTHETIC_DEV_CONFIGURATION_REQUIRED')
    if method=='GET' and url in (BASE+'/key',BASE+'/models') and raw is None:return
    if method!='POST' or url!=BASE+'/chat/completions':raise ValueError('OPENROUTER_ENDPOINT_REFUSED')
    body=json.loads(raw) if isinstance(raw,(str,bytes)) else deepcopy(raw)
    extra={'allow_fallbacks':False,'require_parameters':True}
    if body.get('model','').endswith(':free'):extra['max_price']={'prompt':0,'completion':0}
    elif spec.get('paid_qualified')is not True:raise ValueError('OPENROUTER_PAID_NOT_QUALIFIED')
    if body.pop('provider',None)!=extra or body.pop('usage',None)!={'include':True}:raise ValueError('OPENROUTER_NO_FAILOVER_REQUIRED')
    if body.get('stream')is not True:raise ValueError('OPENROUTER_STREAM_USAGE_REQUIRED')
    # Exact same read-only function set and payload boundaries; no generic OpenAI escape path.
    return wire.authorize_body({'ai_providers':{'nvidia':{**spec,'endpoint':wire.BASE}}},method,wire.BASE+'/chat/completions',body)


class Client(wire.Client):
    provider='openrouter'
    base=BASE
    budget_type=(FreeBudget,PaidBudget)
    request_for=staticmethod(request_for)
    response_for=staticmethod(response_for)

    def validate_usage(self,value):
        from decimal import Decimal
        from ..model_spend import SpendHold
        cost=value.get('usage',{}).get('cost')
        self.record({'event':'PROVIDER_REPORTED_COST','provider':'openrouter','model':self.model,'cost_usd':cost})
        if self.model.endswith(':free') and cost is not None and Decimal(str(cost))!=0:
            raise SpendHold('OPENROUTER_FREE_MODEL_REPORTED_NONZERO_COST')

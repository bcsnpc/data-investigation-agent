"""Smoke configuration starts from the installed investigation environment."""
from copy import deepcopy
import json

def guided_environment(smoke,guided,*,input_url):
    if not any(c['kind']=='guided-investigation'for c in guided['checks'].values()):raise ValueError('EXISTING_GUIDED_INSTALLATION_REQUIRED')
    result=deepcopy(guided)
    # Run ID and capture grant are one contract: copy them together, never
    # graft a guided policy onto the legacy capture prefix.
    for key in ('checks','image','input','manifest','deployment','platform_cost_observation','access_check'):
        if key in smoke:result[key]=deepcopy(smoke[key])
    result.pop('schedule',None)
    policy=json.loads(result['environment']['DIA_PLATFORM_GATEWAY_POLICY'])
    previous=guided['input']['url'];found=False
    for entry in policy['identities']['worker:state']['http']:
        if entry['url']==previous:entry['url']=input_url;found=True
    if not found:raise ValueError('GUIDED_INPUT_READ_NOT_DECLARED')
    result['environment']['DIA_PLATFORM_GATEWAY_POLICY']=json.dumps(policy,sort_keys=True)
    return result

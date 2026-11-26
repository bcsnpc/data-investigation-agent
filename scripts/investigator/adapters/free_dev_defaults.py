"""The only active free dev defaults. History and gate providers are separate."""
from copy import deepcopy
MODELS={'primary':{'provider':'openrouter','model':'nvidia/nemotron-3.5-super-vl:free','endpoint':'https://openrouter.ai/api/v1'},
        'backup':{'provider':'nvidia','model':'moonshotai/kimi-k3.1-pro','endpoint':'https://integrate.api.nvidia.com/v1'}}
def pin(config,*,role='primary'):
    if role not in MODELS:raise ValueError('FREE_DEV_ROLE_REQUIRED')
    value=deepcopy(config);value.update(MODELS[role],synthetic_only=True,quality_scope='DEV_ONLY')
    return value

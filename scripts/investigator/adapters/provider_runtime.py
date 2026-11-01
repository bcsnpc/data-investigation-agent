"""Trusted installation routing, shared by all AI steps; never ticket-selected."""
from copy import deepcopy

STEPS = frozenset(('INVESTIGATOR', 'SCREENSHOT', 'SUMMARY', 'ENRICHMENT', 'WRITER', 'GRADING', 'REVIEWER', 'SMOKE'))


def select(configuration, *, tenant, step):
    if step not in STEPS:
        raise ValueError('CONFIGURED_AI_STEP_REQUIRED')
    tenant_config = configuration.get('tenants', {}).get(tenant, {})
    selected = tenant_config.get('steps', {}).get(step,
               tenant_config.get('default', configuration.get('steps', {}).get(step, configuration.get('default'))))
    if not isinstance(selected, dict):
        raise ValueError('PROVIDER_CONFIGURATION_REQUIRED')
    validate(selected)
    return deepcopy(selected)


def validate(config):
    required = {'model', 'rate_card', 'secret_reference', 'gateway_identity', 'worker_identity'}
    if not isinstance(config, dict) or not required <= config.keys() <= required | {'provider', 'endpoint', 'explicit_cache'}:
        raise ValueError('PROVIDER_CONFIGURATION_SHAPE')
    provider = config.get('provider', 'anthropic')
    if provider not in ('anthropic', 'openai', 'azure_openai'):
        raise ValueError('PROVIDER_NOT_INSTALLED')
    if provider != 'anthropic':
        from .reasoning_openai import endpoint
        base = endpoint(config.get('endpoint', 'https://api.openai.com/v1'))
        if (provider == 'openai') != (base == 'https://api.openai.com/v1'):
            raise ValueError('PROVIDER_ENDPOINT_MISMATCH')
    if 'explicit_cache' in config and type(config['explicit_cache']) is not bool:
        raise ValueError('CACHE_CONFIGURATION_BOOLEAN_REQUIRED')
    return provider


def client(config, *, budget, record, diagnostic_prompt_cache=None, **ports):
    provider = validate(config)
    arguments = {'model': config['model'], 'budget': budget, 'record': record,
                 'identity': config['gateway_identity'], 'secret_reference': config['secret_reference'], **ports}
    if provider == 'anthropic':
        from .reasoning_anthropic import Client
        if diagnostic_prompt_cache is not None:
            arguments['diagnostic_prompt_cache'] = diagnostic_prompt_cache
    else:
        from .reasoning_openai import Client
        arguments['base'] = config.get('endpoint', 'https://api.openai.com/v1')
        arguments['explicit_cache'] = config.get('explicit_cache', False)
    return Client(**arguments)


def validate_graders(investigator, primary, secondary, reviewer):
    providers = [validate(c) for c in (investigator, primary, secondary, reviewer)]
    if providers[0] == providers[1]:
        raise ValueError('PRIMARY_GRADER_MUST_USE_DIFFERENT_PROVIDER')
    for config in (secondary, reviewer):
        if (config.get('provider', 'anthropic'), config['model']) == (providers[0], investigator['model']):
            raise ValueError('SECONDARY_AND_REVIEWER_MUST_USE_DIFFERENT_MODEL')

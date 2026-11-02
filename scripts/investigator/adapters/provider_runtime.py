"""Trusted installation routing, shared by all AI steps; never ticket-selected."""
from copy import deepcopy

STEPS = frozenset(('INTAKE', 'INTAKE_FALLBACK', 'INVESTIGATOR', 'INVESTIGATOR_FALLBACK', 'SCREENSHOT', 'SUMMARY', 'ENRICHMENT', 'WRITER', 'GRADING', 'SECONDARY_GRADING', 'REVIEWER', 'SMOKE'))


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
    if not isinstance(config, dict) or not required <= config.keys() <= required | {'provider', 'endpoint', 'explicit_cache', 'region'}:
        raise ValueError('PROVIDER_CONFIGURATION_SHAPE')
    provider = config.get('provider', 'anthropic')
    if provider not in ('anthropic', 'openai', 'azure_openai', 'bedrock'):
        raise ValueError('PROVIDER_NOT_INSTALLED')
    if provider == 'bedrock':
        from .reasoning_bedrock import endpoint, model_guard
        model_guard(config['model'])
        base = endpoint(config.get('region', 'us-east-1'))
        if config.get('endpoint', base) != base:
            raise ValueError('PROVIDER_ENDPOINT_MISMATCH')
    elif provider != 'anthropic':
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
        if diagnostic_prompt_cache is None and 'explicit_cache' in config:
            diagnostic_prompt_cache = config['explicit_cache']
        if diagnostic_prompt_cache is not None:
            arguments['diagnostic_prompt_cache'] = diagnostic_prompt_cache
    elif provider == 'bedrock':
        from .reasoning_bedrock import Client
        arguments['region'] = config.get('region', 'us-east-1')
        arguments['explicit_cache'] = config.get('explicit_cache', False)
    else:
        from .reasoning_openai import Client
        arguments['base'] = config.get('endpoint', 'https://api.openai.com/v1')
        arguments['explicit_cache'] = config.get('explicit_cache', False)
    return UnifiedClient(Client(**arguments), provider=provider, record=record)


class UnifiedClient:
    """The application sees normalized usage/cost; native bodies stay recorded."""
    def __init__(self, transport, *, provider, record):
        self.transport, self.provider, self.record = transport, provider, record

    def __getattr__(self, name):
        return getattr(self.transport, name)

    def complete(self, **request):
        from .provider_contract import anthropic_reply, Usage
        native = self.transport.complete(**request)
        if self.provider == 'anthropic':
            usage = anthropic_reply(native).usage
        else:
            parts = native['usage']
            cached = parts.get('cache_read_input_tokens', 0)
            writes = parts.get('cache_creation_input_tokens', 0)
            usage = Usage(parts['input_tokens'] + cached + writes, cached, writes, parts['output_tokens'])
        cost = self.transport.budget.rate.usage_price(usage.budget_usage())
        purpose = getattr(self.transport.budget, 'purpose', 'INVESTIGATOR')
        normalized = {'provider': self.provider, 'model': self.model,
                      'step': purpose if isinstance(purpose, str) else 'INVESTIGATOR',
                      'normalized_usage': deepcopy(usage.__dict__), 'cost_microdollars': cost,
                      'cache_read_ratio': usage.cache_read_ratio}
        self.record({'event': 'AI_NORMALIZED_USAGE', **normalized})
        return {**native, **normalized}


def validate_graders(investigator, primary, secondary, reviewer):
    providers = [validate(c) for c in (investigator, primary, secondary, reviewer)]
    if providers[0] == providers[1]:
        raise ValueError('PRIMARY_GRADER_MUST_USE_DIFFERENT_PROVIDER')
    for config in (secondary, reviewer):
        if (config.get('provider', 'anthropic'), config['model']) == (providers[0], investigator['model']):
            raise ValueError('SECONDARY_AND_REVIEWER_MUST_USE_DIFFERENT_MODEL')

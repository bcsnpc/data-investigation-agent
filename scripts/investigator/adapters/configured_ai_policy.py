"""Select the configured vendor's body checker without widening its allowlist."""


def authorize_body(permissions, method, url, raw):
    if url.startswith('https://api.anthropic.com/'):
        spec = permissions.get('ai_providers', {}).get('anthropic')
        if not isinstance(spec, dict) or spec.get('endpoint', '').rstrip('/') not in (
                'https://api.anthropic.com', 'https://api.anthropic.com/v1'):
            raise ValueError('PROVIDER_NOT_CONFIGURED')
        from .reasoning_anthropic import authorize_body as anthropic
        body = anthropic({'reasoning_models': spec.get('models', [])}, method, url, raw)
        if any(tool['name'] not in spec.get('tools', []) for tool in body['tools']):
            raise ValueError('TOOL_NOT_CONFIGURED')
        return body
    from .reasoning_openai import authorize_body as openai
    return openai(permissions, method, url, raw)

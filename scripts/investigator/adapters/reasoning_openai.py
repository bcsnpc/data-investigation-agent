"""Budgeted Responses transport; configured endpoints only, no SDK fallback."""
from copy import deepcopy
import json
import re
import time
from urllib.request import Request, build_opener
from urllib.error import HTTPError
from ..estate_graph_contract import canonical
from .provider_contract import openai_request, openai_reply


class ProviderHTTPError(RuntimeError):
    def __init__(self, status):
        self.http_status = status
        super().__init__('OPENAI_HTTP_' + str(status))


def endpoint(value):
    if value == 'https://api.openai.com/v1':
        return value
    if isinstance(value, str) and re.fullmatch(r'https://[a-zA-Z0-9-]+\.openai\.azure\.com/openai/v1', value):
        return value
    raise ValueError('CONFIGURED_PROVIDER_ENDPOINT_REQUIRED')


def authorize_body(permissions, method, url, raw):
    configured = permissions.get('ai_providers', {})
    matches = [(name, spec) for name, spec in configured.items()
               if name in ('openai', 'azure_openai') and url.startswith(endpoint(spec['endpoint']) + '/')]
    if len(matches) != 1:
        raise ValueError('PROVIDER_NOT_CONFIGURED')
    name, spec = matches[0]
    if method == 'GET' and url == spec['endpoint'] + '/models' and raw is None:
        return
    if method != 'POST' or url != spec['endpoint'] + '/responses':
        raise ValueError('PROVIDER_ENDPOINT_REFUSED')
    body = json.loads(raw) if isinstance(raw, (str, bytes)) else raw
    required = {'model', 'input', 'tools', 'max_output_tokens', 'store'}
    if not isinstance(body, dict) or not required <= body.keys() <= required | {'prompt_cache_options'}:
        raise ValueError('PROVIDER_BODY_SHAPE')
    if body['model'] not in spec.get('models', []) or body['store'] is not False:
        raise ValueError('MODEL_NOT_CONFIGURED_OR_STORAGE_ENABLED')
    if type(body['max_output_tokens']) is not int or not 1 <= body['max_output_tokens'] <= 16000:
        raise ValueError('PROVIDER_OUTPUT_BOUND')
    if not isinstance(body['input'], list) or not isinstance(body['tools'], list) or not body['tools']:
        raise ValueError('CLIENT_INPUT_AND_TOOLS_REQUIRED')
    for tool in body['tools']:
        if set(tool) != {'type', 'name', 'description', 'parameters', 'strict'} or tool['type'] != 'function':
            raise ValueError('SERVER_TOOL_REFUSED')
        if tool['name'] not in spec.get('tools', []):
            raise ValueError('TOOL_NOT_CONFIGURED')
    if 'prompt_cache_options' in body and body['prompt_cache_options'] != {'mode': 'explicit', 'ttl': '30m'}:
        raise ValueError('CACHE_POLICY_NOT_CONFIGURED')


class Client:
    def __init__(self, *, model, budget, identity, secret_reference, record,
                 base='https://api.openai.com/v1', send=None, key_reader=None,
                 sleep=time.sleep, explicit_cache=False):
        from .managed_identity import validate_secret_reference
        validate_secret_reference(secret_reference)
        if budget.rate.model != model:
            raise ValueError('MODEL_RATE_MISMATCH')
        self.base = endpoint(base)
        self.provider = 'openai' if self.base == 'https://api.openai.com/v1' else 'azure_openai'
        self.model, self.budget, self.identity = model, budget, identity
        self.reference, self.record = deepcopy(secret_reference), record
        self.send, self.key_reader, self.sleep = send, key_reader, sleep
        self.explicit_cache = explicit_cache
        self.successful_calls = 0

    def _http(self, method, url, body=None):
        from ..live_gateway import current, open_http
        from .managed_identity import secret
        from metadata_auth import NoRedirect
        from ..round23_calendar import require_live_window
        require_live_window()
        raw = None if body is None else canonical(body).encode()
        current().http(self.identity, method, url, raw)
        key = (self.key_reader or secret)(self.reference, gateway_identity=self.identity)
        request = Request(url, data=raw, method=method,
                          headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
        try:
            with open_http(build_opener(NoRedirect()), request, timeout=90, identity=self.identity) as response:
                data = response.read(4 * 1024 * 1024 + 1)
            if len(data) > 4 * 1024 * 1024:
                raise ValueError('MODEL_RESPONSE_BOUND')
            if key in data.decode('utf8', errors='replace'):
                raise ValueError('MODEL_SECRET_ECHO')
            return json.loads(data)
        except HTTPError as error:
            # Provider bodies can contain echoed headers; never put them in errors.
            raise ProviderHTTPError(error.code) from None
        finally:
            key = request = None

    def discover(self):
        listing = (self.send or self._http)('GET', self.base + '/models')
        self.record({'event': 'REASONING_MODEL_DISCOVERY', 'provider': self.provider, 'listing': listing})
        return listing

    def complete(self, *, system, messages, tools, max_tokens=4000, private_summary=False):
        from ..planner_recording import _safe
        body = openai_request(model=self.model, system=system, messages=messages, tools=tools,
                              max_tokens=max_tokens, explicit_cache=self.explicit_cache)
        _safe(canonical(body).encode())
        reserve_body = {**body, 'max_tokens': max_tokens}
        for attempt in range(3):
            reservation = self.budget.reserve(reserve_body)
            try:
                self.record({'event': 'REASONING_REQUEST', 'provider': self.provider, 'reservation': reservation,
                             **self._capture(body, private_summary)})
                response = (self.send or self._http)('POST', self.base + '/responses', body)
                reply = openai_reply(response, provider=self.provider)
                self.budget.settle(reservation, reply.usage.budget_usage())
                _safe(canonical(response).encode())
                self.record({'event': 'REASONING_RESPONSE', 'provider': self.provider, 'reservation': reservation,
                             **self._capture(response, private_summary)})
                self.successful_calls += 1
                self.record({'event': 'REASONING_CACHE_USAGE', 'provider': self.provider,
                             'successful_call': self.successful_calls,
                             'total_input_tokens': reply.usage.input_tokens,
                             'cache_read_input_tokens': reply.usage.cached_input_tokens,
                             'cache_creation_input_tokens': reply.usage.cache_write_tokens,
                             'cache_read_ratio': reply.usage.cache_read_ratio})
                return reply.compatible()
            except ProviderHTTPError as error:
                if attempt == 2 or error.http_status not in (408, 429, 500, 502, 503, 504):
                    raise
                self.record({'event': 'REASONING_TRANSIENT', 'provider': self.provider,
                             'status': error.http_status, 'attempt': attempt + 1, 'wait_seconds': 30 * (attempt + 1)})
            finally:
                self.budget.settle(reservation)
            self.sleep(30 * (attempt + 1))

    @staticmethod
    def _capture(body, private):
        if not private:
            return {'body': body}
        from hashlib import sha256
        return {'private_case_content_omitted': True, 'sha256': sha256(canonical(body).encode()).hexdigest()}

"""Pinned NVIDIA Build Chat Completions, synthetic dev only, no failover."""
import json
import random
import time
from copy import deepcopy
from urllib.request import Request, build_opener
from urllib.error import HTTPError, URLError
from http.client import IncompleteRead
from .provider_contract import Reply, Usage, count
from ..estate_graph_contract import canonical
from ..nvidia_free_budget import FreeBudget

BASE = 'https://integrate.api.nvidia.com/v1'
READ_TOOLS = frozenset(('run_sql','run_dax','get_definition','get_lineage','get_job_runs',
    'get_refresh_history','get_security_definitions','record_trace','list_candidates','get_evidence',
    'ask_user_choice','submit_finding','lookup_intake_catalog','resolve_intake','describe_screenshot',
    'plan_screenshot_lookup','lookup_screenshot','get_target_candidates','check_target_candidates',
    'contribution_analysis','row_layer_diff','evaluate_delivery','repair_delivery',
    'grade_investigation','review_disagreement'))


class ProviderError(RuntimeError):
    def __init__(self, status, retry_after=None):
        self.http_status, self.retry_after = status, retry_after
        super().__init__('NVIDIA_HTTP_' + str(status))


def request_for(*, model, system, messages, tools, max_tokens):
    native = [{'role': 'system', 'content': system}]
    for message in messages:
        if isinstance(message['content'], str):
            native.append(deepcopy(message)); continue
        parts, calls, state = [], [], {}
        for block in message['content']:
            if block['type'] == 'text': parts.append({'type': 'text', 'text': block['text']})
            elif block['type'] == 'image':
                source = block['source']
                if source['type'] != 'base64': raise ValueError('INLINE_IMAGE_REQUIRED')
                parts.append({'type': 'image_url', 'image_url': {'url': 'data:' + source['media_type'] + ';base64,' + source['data']}})
            elif block['type'] == 'tool_use':
                calls.append({'id': block['id'], 'type': 'function', 'function': {'name': block['name'], 'arguments': canonical(block['input'])}})
            elif block['type'] == 'tool_result':
                native.append({'role': 'tool', 'tool_call_id': block['tool_use_id'], 'content': block['content'] if isinstance(block['content'], str) else canonical(block['content'])})
            elif block['type'] == 'provider_state' and block.get('provider') == 'nvidia':
                state = deepcopy(block['item'])
                if set(state) != {'reasoning_content'}: raise ValueError('UNSUPPORTED_PROVIDER_STATE')
            else: raise ValueError('UNSUPPORTED_NVIDIA_CONTENT')
        if parts or calls:
            row = {'role': message['role'], 'content': parts or None, **state}
            if calls: row['tool_calls'] = calls
            native.append(row)
    return {'model': model, 'messages': native, 'tools': [{'type': 'function', 'function':
            {'name': t['name'], 'description': t['description'], 'parameters': deepcopy(t['input_schema'])}} for t in tools],
            'max_tokens': max_tokens, 'temperature': .2, 'stream': False, 'tool_choice': 'auto'}


def response_for(body, model, tools):
    if body.get('model') != model: raise ValueError('NVIDIA_RESPONSE_MODEL_DIFFERS_FROM_PIN')
    choices = body.get('choices', [])
    if len(choices) != 1: raise ValueError('ONE_NVIDIA_CHOICE_REQUIRED')
    choice = choices[0]; message = choice['message']; content = []
    if message.get('reasoning_content'):
        content.append({'type': 'provider_state', 'provider': 'nvidia', 'item': {'reasoning_content': message['reasoning_content']}})
    if message.get('content'): content.append({'type': 'text', 'text': message['content']})
    ids = set(); allowed = {t['name'] for t in tools}
    for call in message.get('tool_calls', []):
        if call.get('type') != 'function' or not call.get('id') or call['id'] in ids or call['function']['name'] not in allowed:
            raise ValueError('NVIDIA_UNDECLARED_OR_INVALID_TOOL_CALL')
        ids.add(call['id'])
        try:value = json.loads(call['function']['arguments'])
        except (ValueError,TypeError,KeyError):
            if choice['finish_reason']=='length':continue
            raise ValueError('NVIDIA_TOOL_JSON_REQUIRED') from None
        if not isinstance(value, dict):
            if choice['finish_reason']=='length':continue
            raise ValueError('NVIDIA_TOOL_OBJECT_REQUIRED')
        content.append({'type': 'tool_use', 'id': call['id'], 'name': call['function']['name'], 'input': value})
    usage = body['usage']; cached = (usage.get('prompt_tokens_details') or {}).get('cached_tokens', 0)
    return Reply('nvidia', model, body['id'], content,
                 'max_tokens' if choice['finish_reason'] == 'length' else 'tool_use' if message.get('tool_calls') else 'end_turn',
                 Usage(count(usage['prompt_tokens']), count(cached), 0, count(usage['completion_tokens'])))


def authorize_body(permissions, method, url, raw):
    spec = permissions.get('ai_providers', {}).get('nvidia')
    if not isinstance(spec, dict) or spec.get('endpoint') != BASE or spec.get('synthetic_only') is not True or spec.get('quality_scope') != 'DEV_ONLY':
        raise ValueError('NVIDIA_SYNTHETIC_DEV_CONFIGURATION_REQUIRED')
    if method == 'GET' and url == BASE + '/models' and raw is None: return
    if method != 'POST' or url != BASE + '/chat/completions': raise ValueError('NVIDIA_ENDPOINT_REFUSED')
    body = json.loads(raw) if isinstance(raw, (str, bytes)) else raw
    required = {'model', 'messages', 'tools', 'max_tokens', 'temperature', 'stream', 'tool_choice'}
    if not isinstance(body, dict) or set(body) != required: raise ValueError('NVIDIA_BODY_SHAPE')
    if body['model'] not in spec.get('models', []) or body['stream'] is not False or body['tool_choice'] != 'auto': raise ValueError('NVIDIA_MODEL_OR_TOOL_POLICY')
    if type(body['max_tokens']) is not int or not 1 <= body['max_tokens'] <= 16000 or body['temperature'] != .2: raise ValueError('NVIDIA_OUTPUT_BOUND')
    if not isinstance(body['messages'], list) or not body['messages'] or not isinstance(body['tools'], list) or not body['tools']: raise ValueError('NVIDIA_MESSAGES_AND_TOOLS_REQUIRED')
    for tool in body['tools']:
        if set(tool) != {'type', 'function'} or tool['type'] != 'function' or set(tool['function']) != {'name', 'description', 'parameters'} or tool['function']['name'] not in spec.get('tools', []) or tool['function']['name'] not in READ_TOOLS:
            raise ValueError('NVIDIA_SERVER_OR_UNDECLARED_TOOL_REFUSED')


class Client:
    def __init__(self, *, model, budget, identity, secret_reference, record, send=None,
                 key_reader=None, sleep=time.sleep, clock=time.monotonic, jitter=random.random):
        from .managed_identity import validate_secret_reference
        validate_secret_reference(secret_reference)
        if not isinstance(budget, FreeBudget) or budget.rate.model != model: raise ValueError('NVIDIA_FREE_PINNED_BUDGET_REQUIRED')
        self.model, self.budget, self.identity = model, budget, identity
        self.reference, self.record = deepcopy(secret_reference), record
        self.send, self.key_reader, self.sleep, self.clock, self.jitter = send, key_reader, sleep, clock, jitter

    def _http(self, method, url, body=None):
        from ..round23_calendar import require_live_window
        require_live_window()
        from ..live_gateway import current, open_http
        from .managed_identity import secret
        from metadata_auth import NoRedirect
        raw = canonical(body).encode() if body is not None else None
        current().http(self.identity, method, url, raw)
        key = (self.key_reader or secret)(self.reference, gateway_identity=self.identity)
        request = Request(url, data=raw, method=method, headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
        try:
            with open_http(build_opener(NoRedirect()), request, timeout=120, identity=self.identity) as response:
                data = response.read(4 * 1024 * 1024 + 1)
            if len(data) > 4 * 1024 * 1024 or key.encode() in data: raise ValueError('NVIDIA_RESPONSE_BOUND_OR_SECRET_ECHO')
            return json.loads(data)
        except HTTPError as error:
            try: retry = min(300, max(0, float(error.headers.get('Retry-After', 0))))
            except (AttributeError, TypeError, ValueError): retry = None
            raise ProviderError(error.code, retry) from None
        finally: key = request = None

    def discover(self):
        value = (self.send or self._http)('GET', BASE + '/models')
        self.record({'event': 'REASONING_MODEL_DISCOVERY', 'provider': 'nvidia', 'listing': value})
        return value

    def complete(self, *, system, messages, tools, max_tokens=4000, private_summary=False):
        from ..planner_recording import _safe
        body = request_for(model=self.model, system=system, messages=messages, tools=tools, max_tokens=max_tokens)
        _safe(canonical(body).encode()); attempt = 0; started = self.clock()
        while True:
            reservation = self.budget.reserve(body)
            try:
                self.record({'event': 'REASONING_REQUEST', 'provider': 'nvidia', 'reservation': reservation, 'body': body})
                value = (self.send or self._http)('POST', BASE + '/chat/completions', body)
                _safe(canonical(value).encode())
                self.record({'event': 'REASONING_RESPONSE', 'provider': 'nvidia', 'reservation': reservation, 'body': value})
                # Account native usage even when a malformed tool result is rejected below.
                native = value['usage']; usage = {'input_tokens': count(native['prompt_tokens']), 'output_tokens': count(native['completion_tokens'])}
                self.budget.settle(reservation, usage)
                reply = response_for(value, self.model, tools)
                return reply.compatible()
            except (ProviderError, ConnectionError, TimeoutError, URLError, IncompleteRead) as error:
                from .provider_failures import retryable
                if not retryable(error): raise
                if self.clock() - started >= 1800: raise RuntimeError('NVIDIA_RATE_QUEUE_DEADLINE_ENVIRONMENT_AFFECTED') from None
                if getattr(error, 'http_status', None) != 429 and attempt >= 2: raise
                wait = max(getattr(error, 'retry_after', None) or 0, min(60, 1.5 * 2 ** min(attempt, 6)) + self.jitter())
                self.record({'event': 'REASONING_TRANSIENT', 'provider': 'nvidia', 'model': self.model,
                             'status': getattr(error, 'http_status', None), 'wait_seconds': wait,
                             'unknown_call_stays_charged': True, 'is_quality_result': False})
                attempt += 1
            finally: self.budget.settle(reservation)
            self.sleep(wait)

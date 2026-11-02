"""Configured Nova Converse transport; secrets remain in memory, no SDK fallback."""
import base64
from copy import deepcopy
import json
import os
import re
import time
from urllib.parse import quote
from .provider_contract import Reply, Usage, count
from ..estate_graph_contract import canonical


def model_guard(model):
    if not isinstance(model, str):
        raise ValueError('BEDROCK_MODEL_REQUIRED')
    # Check the vendor even inside regional/global inference profile IDs/ARNs.
    if 'anthropic.' in model.lower():
        if os.environ.get('BEDROCK_ALLOW_CLAUDE', 'false').lower() != 'true':
            raise ValueError('BEDROCK_CLAUDE_DISABLED_OWNER_DECISION_REQUIRED')
        # Still requires the separately configured model, rate and exact gateway route.
        return model
    if not re.fullmatch(r'amazon\.nova-(?:micro|lite|pro)-v[0-9]+:[0-9]+', model):
        raise ValueError('BEDROCK_AMAZON_NOVA_ONLY')
    return model


def endpoint(region):
    if not isinstance(region, str) or not re.fullmatch(r'us-east-1', region):
        raise ValueError('BEDROCK_APPROVED_REGION_REQUIRED')
    return 'https://bedrock-runtime.' + region + '.amazonaws.com'


def request_for(*, model, system, messages, tools, max_tokens, explicit_cache=False):
    model_guard(model)
    if type(max_tokens) is not int or not 1 <= max_tokens <= 16000:
        raise ValueError('PROVIDER_OUTPUT_BOUND')
    converted = []
    for message in messages:
        if message['role'] not in ('user', 'assistant'):
            raise ValueError('BEDROCK_MESSAGE_ROLE')
        blocks = message['content']
        if isinstance(blocks, str):
            content = [{'text': blocks}]
        else:
            content = []
            for block in blocks:
                kind = block['type']
                if kind == 'text':
                    content.append({'text': block['text']})
                elif kind == 'tool_use':
                    content.append({'toolUse': {'toolUseId': block['id'], 'name': block['name'], 'input': deepcopy(block['input'])}})
                elif kind == 'tool_result':
                    value = block['content']
                    result = [{'text': value}] if isinstance(value, str) else [{'json': deepcopy(value)}]
                    content.append({'toolResult': {'toolUseId': block['tool_use_id'], 'content': result,
                                                  'status': 'error' if block.get('is_error') else 'success'}})
                elif kind == 'image':
                    source = block['source']
                    if source['type'] != 'base64' or source['media_type'] not in ('image/png', 'image/jpeg', 'image/webp', 'image/gif'):
                        raise ValueError('INLINE_IMAGE_REQUIRED')
                    content.append({'image': {'format': source['media_type'].split('/')[1],
                                              'source': {'bytes': base64.b64decode(source['data'], validate=True)}}})
                else:
                    raise ValueError('BEDROCK_CONTENT_BLOCK_UNSUPPORTED')
        converted.append({'role': message['role'], 'content': content})
    result = {'modelId': model, 'system': [{'text': system}], 'messages': converted,
              'inferenceConfig': {'maxTokens': max_tokens},
              'toolConfig': {'tools': [{'toolSpec': {'name': t['name'], 'description': t.get('description', ''),
                                                     'inputSchema': {'json': deepcopy(t['input_schema'])}}} for t in tools]}}
    if explicit_cache:
        # Nova supports system/messages cachePoints, not tool cachePoints.
        result['system'].append({'cachePoint': {'type': 'default'}})
    return result


def response_for(response, model):
    usage = response['usage']
    fresh = count(usage['inputTokens'])
    cached = count(usage.get('cacheReadInputTokens', 0))
    writes = count(usage.get('cacheWriteInputTokens', 0))
    content = []
    for block in response['output']['message']['content']:
        if 'text' in block:
            content.append({'type': 'text', 'text': block['text']})
        elif 'toolUse' in block:
            use = block['toolUse']
            content.append({'type': 'tool_use', 'id': use['toolUseId'], 'name': use['name'], 'input': deepcopy(use['input'])})
        else:
            raise ValueError('BEDROCK_REPLY_BLOCK_UNSUPPORTED')
    reasons = {'tool_use': 'tool_use', 'end_turn': 'end_turn', 'max_tokens': 'max_tokens', 'stop_sequence': 'stop_sequence'}
    if response['stopReason'] not in reasons:
        raise ValueError('BEDROCK_STOP_REASON_UNSUPPORTED')
    return Reply('bedrock', model, response.get('ResponseMetadata', {}).get('RequestId', ''), content,
                 reasons[response['stopReason']], Usage(fresh + cached + writes, cached, writes, count(usage['outputTokens'])))


def authorize_body(permissions, method, url, raw):
    spec = permissions.get('ai_providers', {}).get('bedrock')
    if not isinstance(spec, dict):
        raise ValueError('PROVIDER_NOT_CONFIGURED')
    body = json.loads(raw) if isinstance(raw, (bytes, str)) else raw
    base = endpoint(spec.get('region'))
    model = next((m for m in spec.get('models', []) if url == base + '/model/' + quote(model_guard(m), safe='') + '/converse'), None)
    if method != 'POST' or model is None:
        raise ValueError('BEDROCK_ENDPOINT_REFUSED')
    # modelId is a URI field in the native SDK request, not in its JSON body.
    if not isinstance(body, dict) or set(body) != {'system', 'messages', 'inferenceConfig', 'toolConfig'}:
        raise ValueError('BEDROCK_BODY_SHAPE')
    if set(body['inferenceConfig']) != {'maxTokens'} or type(body['inferenceConfig']['maxTokens']) is not int or not 1 <= body['inferenceConfig']['maxTokens'] <= 16000:
        raise ValueError('PROVIDER_OUTPUT_BOUND')
    if set(body['toolConfig']) != {'tools'} or not body['toolConfig']['tools']:
        raise ValueError('CLIENT_TOOLS_REQUIRED')
    for tool in body['toolConfig']['tools']:
        if set(tool) != {'toolSpec'} or set(tool['toolSpec']) != {'name', 'description', 'inputSchema'} or tool['toolSpec']['name'] not in spec.get('tools', []):
            raise ValueError('TOOL_NOT_CONFIGURED')


class BedrockProvider:
    def __init__(self, *, model, budget, identity, secret_reference, record, region='us-east-1',
                 explicit_cache=False, sdk_factory=None, key_reader=None, sleep=time.sleep):
        from .managed_identity import validate_secret_reference
        if set(secret_reference) != {'access_key_id', 'secret_access_key', 'region'}:
            raise ValueError('BEDROCK_VAULT_REFERENCES_REQUIRED')
        for reference in secret_reference.values():
            validate_secret_reference(reference)
        model_guard(model)
        if budget.rate.model != model:
            raise ValueError('MODEL_RATE_MISMATCH')
        self.model, self.budget, self.identity, self.record = model, budget, identity, record
        self.references, self.region = deepcopy(secret_reference), region
        self.base, self.explicit_cache = endpoint(region), explicit_cache
        self.sdk_factory, self.key_reader, self.sleep = sdk_factory, key_reader, sleep
        from .anthropic_prompt_cache import StablePrefix
        self.stable = StablePrefix()
        self.successful_calls = 0

    def _invoke(self, body):
        from ..live_gateway import current
        from .managed_identity import secret
        from ..round23_calendar import require_live_window
        from ..planner_recording import _safe
        require_live_window()
        # SDK credentials are explicit. Never use environment/profile/instance fallback.
        reader = self.key_reader or secret
        values = {k: reader(v, gateway_identity=self.identity) for k, v in self.references.items()}
        if values['region'] != self.region:
            raise ValueError('BEDROCK_REGION_SECRET_DIFFERS')
        try:
            from botocore.config import Config
            factory = self.sdk_factory
            if factory is None:
                import boto3
                factory = boto3.client
            sdk = factory('bedrock-runtime', region_name=self.region, endpoint_url=self.base,
                          aws_access_key_id=values['access_key_id'], aws_secret_access_key=values['secret_access_key'],
                          config=Config(connect_timeout=15, read_timeout=90, retries={'total_max_attempts': 1}))
            def check(request, **kwargs):
                current().http(self.identity, 'POST', request.url, request.body)
                # Preserve exact unsigned payload bytes, never signed headers.
                raw = request.body.encode() if isinstance(request.body, str) else request.body
                from hashlib import sha256
                self.record({'event': 'BEDROCK_NATIVE_REQUEST', 'body_base64': base64.b64encode(raw).decode('ascii'),
                             'sha256': sha256(raw).hexdigest(), 'signed_headers_omitted': True})
            sdk.meta.events.register('before-send.bedrock-runtime.Converse', check)
            # Also admit before entering any SDK transport, including test factories.
            url = self.base + '/model/' + quote(self.model, safe='') + '/converse'
            current().http(self.identity, 'POST', url, capture({k: v for k, v in body.items() if k != 'modelId'}))
            try:
                result = sdk.converse(**body)
                _safe(canonical(result).encode())
                if any(value and value in canonical(result) for key, value in values.items() if key != 'region'):
                    raise ValueError('MODEL_SECRET_ECHO')
                return result
            finally:
                sdk.close()
        except Exception as error:
            from botocore.exceptions import ClientError
            from ..live_gateway import GatewayDenied
            if isinstance(error, GatewayDenied):
                raise
            if isinstance(error, ClientError):
                # AWS error strings may include headers/credential IDs. Keep only code/status.
                raise BedrockError(error.response.get('Error', {}).get('Code', 'Unknown'),
                                   error.response.get('ResponseMetadata', {}).get('HTTPStatusCode')) from None
            raise RuntimeError('BEDROCK_TRANSPORT_FAILED_' + type(error).__name__) from None
        finally:
            values = sdk = None

    def complete(self, *, system, messages, tools, max_tokens=4000, private_summary=False):
        from ..planner_recording import _safe
        from .provider_failures import retryable
        investigation = any(t['name'] == 'submit_finding' for t in tools)
        if investigation:
            # Nova isn't approved as an investigator in this round.
            raise ValueError('BEDROCK_INVESTIGATOR_NOT_APPROVED')
        body = request_for(model=self.model, system=system, messages=messages, tools=tools,
                           max_tokens=max_tokens, explicit_cache=self.explicit_cache)
        raw = capture(body)
        _safe(canonical(raw).encode())
        for attempt in range(3):
            reservation = self.budget.reserve({'model': self.model, 'max_tokens': max_tokens, 'request': raw})
            try:
                self.record({'event': 'REASONING_REQUEST', 'provider': 'bedrock', 'reservation': reservation,
                             **record_body(raw, private_summary)})
                native = self._invoke(body)
                reply = response_for(native, self.model)
                self.record({'event': 'REASONING_RESPONSE', 'provider': 'bedrock', 'reservation': reservation,
                             **record_body(native, private_summary)})
                self.budget.settle(reservation, reply.usage.budget_usage())
                self.successful_calls += 1
                self.record({'event': 'REASONING_CACHE_USAGE', 'provider': 'bedrock',
                             'successful_call': self.successful_calls, 'total_input_tokens': reply.usage.input_tokens,
                             'cache_read_input_tokens': reply.usage.cached_input_tokens,
                             'cache_creation_input_tokens': reply.usage.cache_write_tokens,
                             'cache_read_ratio': reply.usage.cache_read_ratio})
                return reply.compatible()
            except BedrockError as error:
                if attempt == 2 or not retryable(error):
                    raise
                self.record({'event': 'REASONING_TRANSIENT', 'provider': 'bedrock', 'status': error.http_status,
                             'attempt': attempt + 1, 'unknown_usage_retains_full_reservation': True})
            finally:
                self.budget.settle(reservation)
            self.sleep(30 * (attempt + 1))


class BedrockError(RuntimeError):
    def __init__(self, code, status):
        self.http_status = status
        self.code = code if re.fullmatch(r'[A-Za-z0-9]+', str(code)) else 'Unknown'
        super().__init__('BEDROCK_' + self.code)


def capture(value):
    """Reversible image bytes representation; never handles signed headers."""
    if isinstance(value, bytes):
        return {'base64': base64.b64encode(value).decode('ascii')}
    if isinstance(value, list):
        return [capture(v) for v in value]
    if isinstance(value, dict):
        return {k: capture(v) for k, v in value.items()}
    return value


def record_body(body, private):
    if private:
        from hashlib import sha256
        return {'private_case_content_omitted': True, 'sha256': sha256(canonical(body).encode()).hexdigest()}
    return {'body': body}


Client = BedrockProvider

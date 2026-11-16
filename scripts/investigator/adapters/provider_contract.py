"""Pure provider codecs. No network, credentials, budget or estate access here.

The internal content blocks are text, image, tool_use and tool_result. Tool
schemas and call IDs are retained across vendors; provider bytes stay on tapes.
"""
from copy import deepcopy
from dataclasses import dataclass
import json


def count(value):
    if type(value) is not int or value < 0:
        raise ValueError('EXACT_PROVIDER_TOKEN_COUNT_REQUIRED')
    return value


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    cached_input_tokens: int
    cache_write_tokens: int
    output_tokens: int

    def __post_init__(self):
        for value in self.__dict__.values():
            count(value)
        if self.cached_input_tokens + self.cache_write_tokens > self.input_tokens:
            raise ValueError('CACHE_COUNTS_EXCEED_INPUT')

    @property
    def cache_read_ratio(self):
        return self.cached_input_tokens / self.input_tokens if self.input_tokens else 0.0

    def budget_usage(self):
        return {'input_tokens': self.input_tokens - self.cached_input_tokens - self.cache_write_tokens,
                'cache_read_input_tokens': self.cached_input_tokens,
                'cache_creation_input_tokens': self.cache_write_tokens,
                'output_tokens': self.output_tokens}


@dataclass(frozen=True)
class Reply:
    provider: str
    model: str
    response_id: str
    content: list
    stop_reason: str
    usage: Usage

    def compatible(self):
        """Compatibility view while existing investigators consume content blocks."""
        return {'id': self.response_id, 'model': self.model, 'content': deepcopy(self.content),
                'stop_reason': self.stop_reason, 'usage': self.usage.budget_usage(),
                'provider': self.provider, 'cache_read_ratio': self.usage.cache_read_ratio}


def anthropic_reply(response):
    usage = response['usage']
    base = count(usage['input_tokens'])
    cached = count(usage.get('cache_read_input_tokens', 0))
    writes = count(usage.get('cache_creation_input_tokens', 0))
    return Reply('anthropic', response['model'], response['id'], deepcopy(response['content']),
                 response['stop_reason'], Usage(base + cached + writes, cached, writes, count(usage['output_tokens'])))


def openai_request(*, model, system, messages, tools, max_tokens, explicit_cache=False):
    instructions = {'type': 'input_text', 'text': system}
    if explicit_cache:
        instructions['prompt_cache_breakpoint'] = {'mode': 'explicit'}
    inputs = [{'role': 'developer', 'content': [instructions]}]
    for message in messages:
        content = message['content']
        if isinstance(content, str):
            inputs.append({'role': message['role'], 'content': content})
            continue
        pending = []
        def flush():
            if pending:
                inputs.append({'role': message['role'], 'content': deepcopy(pending)})
                pending.clear()
        for block in content:
            kind = block['type']
            if kind == 'text':
                pending.append({'type': 'output_text' if message['role'] == 'assistant' else 'input_text', 'text': block['text']})
            elif kind == 'image':
                source = block['source']
                if source['type'] != 'base64':
                    raise ValueError('INLINE_IMAGE_REQUIRED')
                pending.append({'type': 'input_image', 'image_url': 'data:' + source['media_type'] + ';base64,' + source['data']})
            elif kind == 'tool_use':
                flush()
                inputs.append({'type': 'function_call', 'call_id': block['id'], 'name': block['name'],
                               'arguments': json.dumps(block['input'], sort_keys=True, separators=(',', ':'))})
            elif kind == 'tool_result':
                flush()
                output = block['content']
                inputs.append({'type': 'function_call_output', 'call_id': block['tool_use_id'],
                               'output': output if isinstance(output, str) else json.dumps(output, sort_keys=True)})
            elif kind == 'provider_state':
                flush()
                if block.get('provider') not in ('openai', 'azure_openai') or block.get('item', {}).get('type') != 'reasoning':
                    raise ValueError('UNSUPPORTED_PROVIDER_STATE')
                inputs.append(deepcopy(block['item']))
            else:
                raise ValueError('UNSUPPORTED_INTERNAL_CONTENT:' + kind)
        flush()
    body = {'model': model, 'input': inputs, 'tools': [
        {'type': 'function', 'name': t['name'], 'description': t['description'],
         'parameters': deepcopy(t['input_schema']), 'strict': False} for t in tools],
        'max_output_tokens': max_tokens, 'store': False, 'include': ['reasoning.encrypted_content']}
    if explicit_cache:
        body['prompt_cache_options'] = {'mode': 'explicit', 'ttl': '30m'}
    return body


def openai_reply(response, *, provider='openai'):
    usage = response['usage']
    details = usage.get('input_tokens_details') or {}
    content = []
    for item in response.get('output', []):
        if item['type'] == 'function_call':
            arguments = json.loads(item['arguments'])
            if not isinstance(arguments, dict):
                raise ValueError('TOOL_ARGUMENT_OBJECT_REQUIRED')
            content.append({'type': 'tool_use', 'id': item['call_id'], 'name': item['name'], 'input': arguments})
        elif item['type'] == 'message':
            for block in item['content']:
                if block['type'] == 'output_text':
                    content.append({'type': 'text', 'text': block['text']})
                elif block['type'] == 'refusal':
                    content.append({'type': 'text', 'text': block['refusal']})
        elif item['type'] == 'reasoning':
            content.append({'type': 'provider_state', 'provider': provider, 'item': deepcopy(item)})
        else:
            raise ValueError('UNSUPPORTED_PROVIDER_OUTPUT:' + item['type'])
    status = response.get('status')
    reason = ((response.get('incomplete_details') or {}).get('reason'))
    stop = ('max_tokens' if reason == 'max_output_tokens' else
            'tool_use' if any(c['type'] == 'tool_use' for c in content) else 'end_turn')
    if status not in ('completed', 'incomplete'):
        raise ValueError('PROVIDER_RESULT_NOT_COMPLETED')
    return Reply(provider, response['model'], response['id'], content, stop,
                 Usage(count(usage['input_tokens']), count(details.get('cached_tokens', 0)),
                       count(details.get('cache_write_tokens', 0)), count(usage['output_tokens'])))

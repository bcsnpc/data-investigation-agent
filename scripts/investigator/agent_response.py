"""Read a single completed decision from provider phase metadata, not prose."""
from .generation_policy import ProviderResponseError


def final_text(response, usage=None):
    if any(item.type not in ('message', 'reasoning') for item in response.output):
        raise ProviderResponseError('DECISION_CALL_SHAPE', usage)
    messages = [item for item in response.output if item.type == 'message']
    phased = any(getattr(item, 'phase', None) is not None for item in messages)
    if phased:
        selected = [item for item in messages
                    if getattr(item, 'phase', None) == 'final_answer']
        if (len(selected) != 1 or any(getattr(item, 'phase', None)
                not in ('commentary', 'final_answer') for item in messages)):
            raise ProviderResponseError('DECISION_CALL_SHAPE', usage)
    else:
        # Older providers may omit phase entirely. Only one message is a
        # decision; multiple messages must not be selected by their contents.
        selected = messages
        if len(selected) != 1:
            raise ProviderResponseError('DECISION_CALL_SHAPE', usage)
    message = selected[0]
    if message.status != 'completed' or getattr(message, 'role', None) != 'assistant':
        raise ProviderResponseError('RESPONSE_NOT_COMPLETED', usage)
    if not message.content or any(item.type != 'output_text' for item in message.content):
        raise ProviderResponseError('DECISION_CALL_SHAPE', usage)
    return ''.join(item.text for item in message.content)

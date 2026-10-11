"""Provider subset derived from the unchanged agent consumer contract.

Unsupported constraints are stated at their exact field, then validated by
the loop before dispatch. No constraint is removed from the consumer schema.
"""
import json
from jsonschema import Draft202012Validator
from .adapters.structured_output_contract import KEYS, TYPES


def schema(consumer):
    count = 0

    def walk(node, depth=1):
        nonlocal count
        result = {}
        for key, value in node.items():
            if key == 'properties':
                count += len(value)
                result[key] = {name: walk(child, depth + 1) for name, child in value.items()}
            elif key == 'items':
                result[key] = walk(value, depth + 1)
            elif key == 'anyOf':
                result[key] = [walk(child, depth) for child in value]
            elif key in KEYS:
                result[key] = value
        omitted = {key: value for key, value in node.items() if key not in KEYS}
        if omitted:
            result['description'] = (result.get('description', '') +
                ' Consumer constraints (validated before use): ' +
                json.dumps(omitted, sort_keys=True, separators=(',', ':'))).strip()
        kinds = result.get('type', [])
        kinds = [kinds] if isinstance(kinds, str) else kinds
        if any(kind not in TYPES for kind in kinds):
            raise ValueError('AGENT_WIRE_TYPE')
        if 'object' in kinds:
            if depth > 10 or count > 5000:
                raise ValueError('AGENT_WIRE_SIZE')
            if result.get('additionalProperties') is not False or set(result.get('required', [])) != set(result.get('properties', {})):
                raise ValueError('AGENT_WIRE_CLOSED_OBJECT')
        return result

    wire = walk(consumer)
    Draft202012Validator.check_schema(wire)
    if wire.get('type') != 'object' or 'anyOf' in wire:
        raise ValueError('AGENT_WIRE_ROOT')
    return wire

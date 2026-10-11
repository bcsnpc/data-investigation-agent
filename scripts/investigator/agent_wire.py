"""Provider subset derived from the unchanged agent consumer contract.

Unsupported constraints are stated at their exact field, then validated by
the loop before dispatch. No constraint is removed from the consumer schema.
"""
import json
from collections import Counter
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
    # JSON Schema references share identical subcontracts rather than repeating
    # their fields in every tool branch. This is supported structured-output
    # syntax, not a weaker consumer contract.
    nodes, counts = {}, Counter()
    def text(node): return json.dumps(node, sort_keys=True, separators=(',', ':'))
    def children(node):
        yield from node.get('properties', {}).values()
        yield from node.get('anyOf', [])
        if 'items' in node: yield node['items']
    def collect(node):
        encoded = text(node)
        if len(encoded) >= 100:
            nodes[encoded] = node; counts[encoded] += 1
        for child in children(node): collect(child)
    collect(wire)
    names = {key: 'd'+str(i) for i, key in enumerate(sorted(k for k, n in counts.items() if n > 1))}
    def share(node, defining=None):
        key = text(node)
        if key in names and key != defining: return {'$ref': '#/$defs/'+names[key]}
        out = dict(node)
        if 'properties' in out: out['properties'] = {k: share(v) for k, v in out['properties'].items()}
        if 'items' in out: out['items'] = share(out['items'])
        if 'anyOf' in out: out['anyOf'] = [share(v) for v in out['anyOf']]
        return out
    compact = share(wire)
    if names: compact['$defs'] = {names[key]: share(nodes[key], key) for key in names}
    Draft202012Validator.check_schema(compact)
    return compact

"""Lossless repeated-value references; never truncate evidence or prose."""
import copy
import json
from collections import Counter

REF = '$agent_shared_ref'
VERSION = 'agent-shared-input-v1'


def encode(value):
    counts, objects = Counter(), {}

    def key(node):
        return json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

    def visit(node):
        if isinstance(node, dict):
            if REF in node:
                raise ValueError('AGENT_SHARED_INPUT_RESERVED_KEY')
            text = key(node)
            if len(text) >= 256:
                counts[text] += 1; objects[text] = node
            for child in node.values(): visit(child)
        elif isinstance(node, list):
            for child in node: visit(child)

    visit(value)
    names = {text: 's'+str(i) for i, text in enumerate(sorted(k for k, n in counts.items() if n > 1))}

    def transform(node, defining=None):
        if isinstance(node, dict):
            text = key(node)
            if text in names and text != defining:
                return {REF: names[text]}
            return {k: transform(v) for k, v in node.items()}
        if isinstance(node, list): return [transform(v) for v in node]
        return copy.deepcopy(node)

    return {'format': VERSION, 'payload': transform(value),
            'shared_values': {names[k]: transform(objects[k], k) for k in names}}


def decode(packet):
    if set(packet) != {'format', 'payload', 'shared_values'} or packet['format'] != VERSION:
        raise ValueError('AGENT_SHARED_INPUT_FORMAT')

    def expand(node, seen=()):
        if isinstance(node, dict):
            if REF in node:
                if set(node) != {REF} or node[REF] in seen or node[REF] not in packet['shared_values']:
                    raise ValueError('AGENT_SHARED_INPUT_REFERENCE')
                return expand(packet['shared_values'][node[REF]], seen+(node[REF],))
            return {k: expand(v, seen) for k, v in node.items()}
        if isinstance(node, list): return [expand(v, seen) for v in node]
        return copy.deepcopy(node)

    return expand(packet['payload'])

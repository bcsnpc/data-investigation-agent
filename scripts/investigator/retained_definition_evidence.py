"""Citable references to definitions already present in the pinned case context.

No fetch, model output or freshness inference participates. Native content stays
in the existing context instead of being duplicated into every case reference.
"""
from copy import deepcopy
from .estate_graph_contract import canonical

KIND = 'RETAINED_DEFINITION_REFERENCE'
FIELDS = ('expression', 'definitions', 'content', 'computed_definition')
QUALIFICATION = 'Retained native definition; current deployment freshness and numerical effect are not established by this reference.'


def references(context):
    result = []
    for item in context.get('retained_native_definitions', []):
        fields = {key: value for key, value in item.get('metadata', {}).items()
                  if key in FIELDS and value}
        if not (fields and item.get('id') and item.get('content_hash') and item.get('provenance')):
            continue
        result.append({'kind': KIND, 'asset_id': item['id'], 'name': item.get('name', item['id']),
                       'content_hash': item['content_hash'], 'qualification': QUALIFICATION})
    return result


def resolve(reference, context):
    if reference not in references(context):
        raise ValueError('RETAINED_DEFINITION_REFERENCE_NOT_IN_PINNED_CONTEXT')
    matches = [item for item in context.get('retained_native_definitions', [])
               if item.get('id') == reference['asset_id']
               and item.get('content_hash') == reference['content_hash']]
    if len(matches) != 1:
        raise ValueError('RETAINED_DEFINITION_REFERENCE_NOT_UNIQUE')
    item = matches[0]
    fields = {key: deepcopy(item['metadata'][key]) for key in FIELDS if item['metadata'].get(key)}
    single = next(iter(fields.values()))
    return {**deepcopy(reference), 'content': single if len(fields) == 1 and isinstance(single, str) else canonical(fields),
            'retained_native_definition': fields, 'provenance': deepcopy(item['provenance']),
            'projection': deepcopy(item.get('projection')), 'current_native_fetch_performed': False}

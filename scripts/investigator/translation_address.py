"""Consumer-owned addresses for translation probes and key-binding witnesses."""
from datetime import datetime
from jsonschema import Draft202012Validator
from .code_sources import obj

HASH = {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}
SCHEMA = {'oneOf': [obj({'kind': {'const': 'KEY_BINDING'}, 'declaration_hash': HASH}),
    obj({'kind': {'const': 'TRANSLATION'}, 'proposal_hash': HASH,
         'cell': {'type': ['object', 'null']},
         'evaluation_timestamp': {'type': ['string', 'null'], 'maxLength': 64}})]}


def validate(address):
    Draft202012Validator(SCHEMA).validate(address)
    if address['kind'] == 'TRANSLATION':
        if address['cell'] is not None:
            from .report_cell import validate as validate_cell
            validate_cell(address['cell'], address['cell'].get('measure_id'))
        value = address['evaluation_timestamp']
        if value is not None and datetime.fromisoformat(value.replace('Z', '+00:00')).tzinfo is None:
            raise ValueError('Translation timestamp requires a timezone')
    return address

"""Owner-declared string equality. Unknown declarations never imply defaults."""
import copy
from jsonschema import Draft202012Validator

SCHEMA = {'type': 'object', 'additionalProperties': False,
          'properties': {'collation': {'type': 'string', 'minLength': 1, 'maxLength': 128},
                         'case_fold': {'type': 'boolean'}, 'trim': {'type': 'boolean'},
                         'accent_fold': {'type': 'boolean'}},
          'required': ['collation', 'case_fold', 'trim', 'accent_fold']}


def validate(value):
    Draft202012Validator(SCHEMA).validate(value)
    if value['collation'] == 'BINARY' and any(value[k] for k in ('case_fold', 'trim', 'accent_fold')):
        raise ValueError('BINARY declares exact strings, without folding or trimming')
    return copy.deepcopy(value)


def binary(value):
    """Adapter renderers must opt into a faithful supported declaration."""
    value = validate(value)
    if value != {'collation': 'BINARY', 'case_fold': False, 'trim': False, 'accent_fold': False}:
        raise NotImplementedError('STRING_SEMANTICS_RENDERING_UNSUPPORTED: ' + value['collation'])
    return value

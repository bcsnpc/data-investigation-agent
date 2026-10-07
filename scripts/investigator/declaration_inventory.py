"""Consumer-owned neutral declaration inventory contract; native provenance is opaque."""
import copy
import hashlib
import json

SCHEMA = {
    'disposition': {'type': 'string', 'enum': ['ACTIVE', 'CONDITIONAL', 'UNSUPPORTED']},
    'volatility': {'type': 'string', 'enum': ['FIXED', 'VIEWER_CHANGEABLE', 'UNKNOWN']},
    'assumption': {'type': 'string', 'enum': ['NONE', 'SAVED_DEFAULT', 'INVOCATION_UNKNOWN', 'APPLICABILITY_UNKNOWN']},
}


class MissingInventory(ValueError):
    """The producer supplied no inventory; no inventory content was validated."""


def identity(source):
    if (not isinstance(source, dict) or set(source) != {'location', 'content_hash'}
            or not isinstance(source['location'], str) or not 1 <= len(source['location']) <= 4000
            or not isinstance(source['content_hash'], str) or len(source['content_hash']) != 64
            or any(c not in '0123456789abcdef' for c in source['content_hash'])):
        raise ValueError('Declaration identity requires location and content hash')
    from .privacy_identities import digest
    return digest(source,lambda body:json.dumps(body,sort_keys=True,separators=(',',':')))


def neutral(entries):
    """Only consumer fields can reach model-visible evidence or rendered claims."""
    return [{k: copy.deepcopy(entry[k]) for k in ('id', 'disposition', 'volatility', 'assumption')}
            for entry in entries]


def qualifications(fields, label):
    from .declared_reproduction import BASELINE_LIMIT, ACTIVE_LIMIT, TIMING_LIMIT, OPEN_LIMIT
    result = [BASELINE_LIMIT, ACTIVE_LIMIT, TIMING_LIMIT, OPEN_LIMIT]
    if any(e['disposition'] == 'CONDITIONAL' for e in fields):
        result.append('An invoked bookmark or other stored alternative remains possible; invocation was not established.')
    if any(e['disposition'] == 'ACTIVE' and e['assumption'] == 'SAVED_DEFAULT' for e in fields):
        result.append('The check assumes saved default positions for viewer-changeable selections; their current positions were not established.'
                      if label == 'REPRODUCED' else
                      'A moved slicer or other saved-default selection remains an explicit possibility; its current position was not established.')
    return result

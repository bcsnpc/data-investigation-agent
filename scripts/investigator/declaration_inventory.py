"""Consumer-owned neutral declaration inventory contract; native provenance is opaque."""
import copy
import hashlib
import json
from collections import Counter

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
    return hashlib.sha256(json.dumps(source, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def validate(inventory, active):
    from .declared_reproduction import compose
    if inventory is None:
        raise MissingInventory('Required declaration inventory was not supplied')
    if not isinstance(inventory, dict) or set(inventory) != {'discovered', 'entries'}:
        raise ValueError('Declaration inventory is malformed')
    discovered, entries = inventory['discovered'], inventory['entries']
    if not isinstance(discovered, list) or not 0 <= len(discovered) <= 512 or not isinstance(entries, list):
        raise ValueError('Declaration inventory requires bounded discovered entries')
    if len(entries) != len(discovered):
        raise ValueError('Declaration conservation failed: entry count differs')
    if not isinstance(active, list):
        raise ValueError('Active restriction set requires a list')
    ids = [identity(source) for source in discovered]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate discovered declaration identity')
    accounted = []
    represented = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {'id', 'source', 'disposition', 'volatility', 'assumption', 'opaque_provenance', 'restrictions'}:
            raise ValueError('Declaration entry requires exactly one disposition and all contract fields')
        if entry['id'] != identity(entry['source']):
            raise ValueError('Declaration identity differs from location/content')
        for field, vocabulary in SCHEMA.items():
            if entry[field] not in vocabulary['enum']:
                raise ValueError('Invalid declaration ' + field)
        if not isinstance(entry['opaque_provenance'], str) or len(entry['opaque_provenance']) > 4000:
            raise ValueError('Opaque declaration provenance exceeds bound')
        if not isinstance(entry['restrictions'], list):
            raise ValueError('Declaration restrictions require a list')
        accounted.append(entry['id'])
        if entry['disposition'] == 'ACTIVE':
            if not entry['restrictions']: raise ValueError('Active declaration requires nonempty restrictions')
            compose(entry['restrictions'])
            if entry['assumption'] not in ('NONE', 'SAVED_DEFAULT') or entry['volatility'] == 'UNKNOWN':
                raise ValueError('Active declaration applicability must be established')
            if entry['assumption'] == 'SAVED_DEFAULT' and entry['volatility'] != 'VIEWER_CHANGEABLE':
                raise ValueError('Saved default requires viewer-changeable volatility')
            represented.extend(entry['restrictions'])
        elif entry['restrictions']:
            raise ValueError('Excluded declaration cannot carry active restrictions')
    if Counter(accounted) != Counter(ids):
        raise ValueError('Declaration conservation failed: missing or duplicate dispositions')
    canonical = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)
    if Counter(map(canonical, represented)) != Counter(map(canonical, active)):
        raise ValueError('Active restrictions and inventory do not conserve declaration coverage')
    if active:
        compose(active)
    return sorted(copy.deepcopy(entries), key=lambda entry: entry['id'])


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

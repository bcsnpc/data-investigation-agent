"""Exact installed database selection, never inferred from SQL text or names."""
from copy import deepcopy
import re


def entries(config):
    if 'sql_connections' in config:
        if 'sql' in config: raise ValueError('Ambiguous default and named SQL connections')
        return config['sql_connections']
    return {'default': config['sql']} if 'sql' in config else {}


def root(connection):
    return 'sql://' + connection['server'] + '/' + connection['database']


def validate_connections(config):
    from metadata_config import validate_config
    connections = entries(config)
    if not isinstance(connections, dict) or not 1 <= len(connections) <= 32:
        raise ValueError('Named SQL connections require 1 to 32 entries')
    roots = set()
    for name, connection in connections.items():
        if not isinstance(name, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,79}', name):
            raise ValueError('Invalid SQL connection name')
        projected = {k: deepcopy(v) for k,v in config.items() if k != 'sql_connections'}
        projected['sql'] = connection
        validate_config(projected)
        address = root(connection).casefold()
        if address in roots: raise ValueError('Duplicate SQL database binding')
        roots.add(address)


def for_asset(config, asset, name=None):
    """Project one exact declared connection; legacy configs remain byte-identical."""
    if 'sql_connections' not in config:
        if name is not None and name != 'default': raise ValueError('Unknown SQL connection')
        return config
    matches = [(key, c) for key,c in entries(config).items()
               if asset == root(c) or asset.startswith(root(c) + '/')]
    if len(matches) != 1 or name is not None and matches[0][0] != name:
        raise ValueError('SQL asset outside declared connection')
    result = {k:deepcopy(v) for k,v in config.items() if k != 'sql_connections'}
    result['sql'] = deepcopy(matches[0][1])
    return result


def for_request(config, request):
    if 'sql_connections' not in config: return config
    ids = request.get('asset_ids') or ([request['object_id']] if 'object_id' in request else [])
    if not ids: raise ValueError('Named SQL request requires exact asset IDs')
    projected = [for_asset(config, asset) for asset in ids]
    if any(row['sql'] != projected[0]['sql'] for row in projected):
        raise ValueError('Cross-connection SQL request refused')
    return projected[0]

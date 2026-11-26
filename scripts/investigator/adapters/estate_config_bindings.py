"""Cross-check connector references against the existing native installation."""


def validate_bindings(value):
    manifest = value['installation']
    adapters = {row['id']: row for row in manifest['adapters']}
    addresses = {row['asset_id'] for row in manifest['layers'] + manifest['resources']}
    for row in value['connectors']:
        if not set(row['objects']) <= addresses:
            raise ValueError('estate.connectors.' + row['id'] + ': object is not installed')
        options = adapters[row['adapter']]['options']
        required = 'sql' if row['kind'] == 'azure-sql' else 'fabric'
        if row['enabled'] and required not in options and not (required == 'sql' and 'sql_connections' in options):
            raise ValueError('estate.connectors.' + row['id'] + ': installed platform is absent')
    from .sql_connections import entries, for_asset
    for name, connection in value.get('connections', {}).items():
        installed = [entry for adapter in adapters.values() for key, entry in entries(adapter['options']).items()
                     if key == name or key == 'default' and len(value['connections']) == 1]
        if len(installed) != 1 or any(installed[0][k] != connection[k] for k in ('server', 'database')):
            raise ValueError('estate.connections.' + name + ': installed database differs')
        identity = value['identities'][connection['identity']]['reference']
        reader = next((row for row in manifest['identities'] if row['id'] == identity), None)
        if reader is None: raise ValueError('estate.connections.' + name + ': reader is not installed')
        if installed[0]['auth'].get('account') != reader['principal']:
            raise ValueError('estate.connections.' + name + ': installed reader differs')
        def secret_names(item):
            if isinstance(item, dict):
                return ({item['secret_name']} if 'secret_name' in item else set()) | set().union(*(secret_names(v) for v in item.values()))
            if isinstance(item, list): return set().union(*(secret_names(v) for v in item))
            return set()
        if secret_names(installed[0]['auth']) != set(connection['secret_refs']):
            raise ValueError('estate.connections.' + name + ': installed secret names differ')
    for row in value['connectors']:
        if 'connection' not in row: continue
        options = adapters[row['adapter']]['options']
        connection = value['connections'][row['connection']]
        for asset in row['objects']:
            selected = for_asset(options, asset, row['connection'] if 'sql_connections' in options else None)
            if any(selected['sql'][k] != connection[k] for k in ('server', 'database')):
                raise ValueError('estate.connectors.' + row['id'] + ': object leaves connection')
    identities = {row['id']: row for row in manifest['identities']}
    for name, row in value['identities'].items():
        if row['reference'] not in identities:
            raise ValueError('estate.identities.' + name + ': reader is not installed')
    for role, layer in value['layers'].items():
        if not set(layer['objects']) <= addresses:
            raise ValueError('estate.layers.' + role + ': object is not installed')
        allowed = {address for key in layer['connectors'] for address in
                   next(row for row in value['connectors'] if row['id'] == key)['objects']}
        if not set(layer['objects']) <= allowed:
            raise ValueError('estate.layers.' + role + ': object outside connector declaration')
    credential = manifest['model']['credential']
    if credential.get('mode') == 'key_vault':
        ref = credential['reference']
        if ref['secret_name'] != value['model']['secret_ref'] or ref['vault_url'] != 'https://' + value['secrets']['vault'] + '.vault.azure.net':
            raise ValueError('estate.secrets: installed model secret reference differs')

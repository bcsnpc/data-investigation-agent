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
        if row['enabled'] and required not in options:
            raise ValueError('estate.connectors.' + row['id'] + ': installed platform is absent')
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

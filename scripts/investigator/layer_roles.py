"""Estate-declared roles. Position and asset names never determine a role."""
ROLES = ('PRESENTATION', 'SEMANTIC', 'SERVING', 'REFINED', 'LANDING', 'APPLICATION')


def declarations(value):
    if not isinstance(value, list):
        raise ValueError('Layer roles must be a list')
    result = {}
    from .business_vocabulary import validate_identifier_form
    for row in value:
        if not isinstance(row, dict) or set(row) != {'asset_id', 'role', 'business_name'}:
            raise ValueError('Layer role requires identity, closed role and business name')
        identity, role, name = row['asset_id'], row['role'], row['business_name']
        if not isinstance(identity, str) or not identity or identity in result:
            raise ValueError('Layer role identity missing or duplicated')
        if role not in ROLES or not isinstance(name, str) or not name.strip() or len(name) > 80:
            raise ValueError('Unknown layer role or invalid display name')
        validate_identifier_form(name)
        result[identity] = {'role': role, 'business_name': name}
    names = {}
    for row in result.values():
        if row['role'] in names and names[row['role']] != row['business_name']:
            raise ValueError('A role must have one business display name')
        names[row['role']] = row['business_name']
    return result


def apply(labels, layers, configured):
    roles = declarations(configured)
    return {layer['id']: {**labels.get(layer['id'], {}), **roles.get(layer['id'], {})}
            for layer in layers}


def name(payload, identity):
    # Legacy estates without a declaration remain explicitly unnamed. They
    # must never acquire a role from their position or a naming convention.
    return payload.get('layer_labels', {}).get(identity, {}).get('business_name', 'declared layer')

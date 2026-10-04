"""Explicit estate audit sources; an unavailable declaration is not a fallback."""


def declarations(value):
    if not isinstance(value, list) or not 1 <= len(value) <= 32:
        raise ValueError('Load audit declarations require one to 32 entries')
    found = set()
    result = []
    for entry in value:
        if not isinstance(entry, dict) or set(entry) != {'delivery_asset_id', 'producer_asset_id', 'audit_asset_id'}:
            raise ValueError('Load audit requires delivery, producer and audit asset identities')
        if any(not isinstance(v, str) or not 1 <= len(v) <= 300 or v != v.strip() for v in entry.values()):
            raise ValueError('Load audit identities must be bounded stable asset identities')
        if entry['delivery_asset_id'] in found:
            raise ValueError('Multiple audit sources for the same delivery are ambiguous')
        found.add(entry['delivery_asset_id'])
        result.append(dict(entry))
    return result

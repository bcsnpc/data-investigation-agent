"""Installed adapters own native declared-route interpretation."""
def declared_route_validator(manifest):
    implementations={a['implementation'] for a in manifest['adapters']}
    from .microsoft_readiness import validate_declared_route
    # Installation validation separately owns adapter options and identities.
    # An unfamiliar implementation never obtains a permissive default.
    if implementations == {'microsoft'}:
        return validate_declared_route
    raise ValueError('DECLARED_ROUTE_ADAPTER_VALIDATOR_UNAVAILABLE')


def required_native_bindings(receipt,manifest,inventory):
    implementations={a['implementation']for a in manifest.get('adapters',[])}
    if implementations=={'microsoft'}:
        from .microsoft_readiness import required_copy_bindings
        return required_copy_bindings(receipt,manifest,inventory)
    if implementations:raise ValueError('DECLARED_ROUTE_ADAPTER_VALIDATOR_UNAVAILABLE')
    return []

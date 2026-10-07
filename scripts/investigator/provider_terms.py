"""Installation provenance, separate from credentials and planner input.

An endpoint hostname does not establish a deployment's region or residency.
Legacy installations remain readable with explicit missing-region evidence.
"""
import copy


def declaration(model):
    return {key: copy.deepcopy(model[key]) for key in ('provider', 'deployment', 'endpoint')} | {
        'region': copy.deepcopy(model.get('region', {
            'status': 'UNDECLARED',
            'reason': 'Installation has no explicit provider-region declaration; endpoint is not region evidence.'}))}


def from_bootstrap(bootstrap):
    """Historical tapes are not backfilled with a later installation claim."""
    terms = bootstrap.get('config', {}).get('_estate', {}).get('provider_terms')
    if terms is not None: return copy.deepcopy(terms)
    profile = bootstrap.get('profile', {})
    return {'provider': profile.get('adapter'), 'deployment': profile.get('deployment'),
            'endpoint': profile.get('endpoint'), 'region': {
                'status': 'UNRECORDED', 'reason': 'This tape predates explicit provider-region recording.'}}

"""Closed installation schema; platform vocabulary stays adapter-owned."""
def _object(properties, optional=()):
    return dict(type='object', additionalProperties=False, properties=properties,
                required=[key for key in properties if key not in optional])

TEXT = {'type': 'string', 'minLength': 1, 'maxLength': 1000}
FLAG = {'type': 'boolean'}
NAMES = {'type': 'array', 'items': TEXT, 'uniqueItems': True}
IDENTIFIER = {'type': 'string', 'pattern': '^[a-z][a-z0-9-]{0,79}$'}
CAP = {'type': 'integer', 'minimum': 1, 'maximum': 1000000000}
ROLES = ('source', 'bronze', 'silver', 'gold', 'model', 'report')
LIMITS = _object({name: CAP for name in ('requests_per_ticket', 'requests_per_day',
    'microdollars_per_ticket', 'microdollars_per_day', 'microdollars_per_month')})
SCHEMA = _object({
    'version': {'const': 'estate-config/1'}, 'id': IDENTIFIER, 'name': TEXT,
    'enabled': FLAG, 'status': {'enum': ['DRAFT', 'CONFIGURED', 'SMOKE_ONLY', 'READY_SEALED_TEST']},
    'references': _object({key: TEXT for key in ('tenant', 'subscription', 'resource_group')}),
    'connectors': {'type': 'array', 'minItems': 1, 'items': _object({
        'id': IDENTIFIER, 'kind': {'enum': ['fabric', 'powerbi', 'azure-sql', 'fabric-sql', 'databricks', 'snowflake']},
        'enabled': FLAG, 'identity': TEXT, 'adapter': TEXT,
        'objects': NAMES, 'discovery': NAMES, 'connection': IDENTIFIER}, optional=('connection',))},
    'connections': {'type': 'object', 'minProperties': 1, 'propertyNames': IDENTIFIER,
        'additionalProperties': _object({'server': TEXT, 'database': TEXT, 'identity': TEXT, 'secret_refs': NAMES})},
    'layers': _object({role: _object({'connectors': NAMES, 'objects': NAMES, 'discovery': NAMES,
        'connections': NAMES}, optional=('connections',)) for role in ROLES}),
    'source_of_truth': {'enum': list(ROLES)}, 'deepest_reachable': {'enum': list(ROLES) + [None]},
    'identities': {'type': 'object', 'minProperties': 1, 'additionalProperties': _object({
        'kind': {'enum': ['managed-identity', 'service-principal']}, 'reference': TEXT,
        'tenant': TEXT, 'secret_refs': NAMES})},
    'secrets': _object({'vault': TEXT, 'names': NAMES}),
    'model': _object({'provider': TEXT, 'model': TEXT, 'secret_ref': TEXT, 'limits': LIMITS}),
    'limits': LIMITS,
    'optional_sources': _object({name: _object({'enabled': {'const': False}, 'adapter': TEXT})
        for name in ('catalog', 'ontology', 'glossary')}),
    'deployment': _object({'jobs': _object({key: IDENTIFIER for key in ('worker', 'graph', 'collectors')})}),
    # Existing adapter-owned manifest is the sole native-address/credential binding.
    # The outer connector and layer lists reference it; they never override it.
    'installation': {'type': ['object', 'null']},
}, optional=('connections',))

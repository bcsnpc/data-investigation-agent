"""Versioned deployment-owned configuration. Loading never authenticates or reads data."""
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
from jsonschema import Draft202012Validator


from .adapters.estate_config_schema import SCHEMA, ROLES


def validate(value):
    _reject_values(value)
    errors = sorted(Draft202012Validator(SCHEMA).iter_errors(value), key=lambda e: str(list(e.path)))
    if errors:
        error = errors[0]
        detail = 'schema ' + error.validator + ' check failed'
        if error.validator == 'required':
            detail = 'missing fields: ' + ', '.join(key for key in error.validator_value if key not in error.instance)
        raise ValueError('estate.' + '.'.join(map(str, error.path)) + ': ' + detail)
    result = deepcopy(value)
    def fail(path, message):
        raise ValueError('estate.' + path + ': ' + message)
    if result['status'] in ('SMOKE_ONLY', 'READY_SEALED_TEST') and result['enabled']:
        fail('enabled', 'sealed estate permits connectivity only; ticket runs are disabled')
    if result['enabled'] and result['deepest_reachable'] is None:
        fail('deepest_reachable', 'enabled estate requires declared reachability')
    if result['enabled'] and result['status'] != 'CONFIGURED':
        fail('status', 'an enabled installation must be CONFIGURED')
    connectors = {row['id']: row for row in result['connectors']}
    if len(connectors) != len(result['connectors']): fail('connectors', 'duplicate ID')
    secrets = set(result['secrets']['names'])
    for name, identity in result['identities'].items():
        if not set(identity['secret_refs']) <= secrets: fail('identities.' + name, 'missing secret name')
    if result['model']['secret_ref'] not in secrets: fail('model.secret_ref', 'missing secret name')
    for key, caps in (('limits', result['limits']), ('model.limits', result['model']['limits'])):
        if caps['requests_per_ticket'] > caps['requests_per_day']: fail(key, 'ticket request cap exceeds day')
        if not caps['microdollars_per_ticket'] <= caps['microdollars_per_day'] <= caps['microdollars_per_month']:
            fail(key, 'ticket/day/month cash caps are out of order')
    connections = result.get('connections', {})
    for name, connection in connections.items():
        if connection['identity'] not in result['identities']: fail('connections.' + name, 'unknown identity')
        if not set(connection['secret_refs']) <= secrets: fail('connections.' + name, 'missing secret name')
    for row in connectors.values():
        if 'connection' in row:
            connection = connections.get(row['connection'])
            if connection is None: fail('connectors.' + row['id'], 'unknown connection')
            if row['identity'] != connection['identity']: fail('connectors.' + row['id'], 'connection identity differs')
        if row['identity'] not in result['identities']: fail('connectors.' + row['id'], 'unknown identity reference')
        if row['enabled'] and (not result['enabled'] or row['kind'] in ('databricks', 'snowflake')):
            fail('connectors.' + row['id'], 'disabled estate or unimplemented connector')
        if not row['objects'] and not row['discovery']: fail('connectors.' + row['id'], 'object or discovery rule required')
    for role, layer in result['layers'].items():
        if not set(layer.get('connections', [])) <= connections.keys(): fail('layers.' + role, 'unknown connection')
        declared = {connectors[key].get('connection') for key in layer['connectors'] if key in connectors}
        if not set(layer.get('connections', [])) <= declared: fail('layers.' + role, 'connection outside layer connectors')
        if not layer['connectors'] or not layer['objects'] and not layer['discovery']:
            fail('layers.' + role, 'layer gap: declare connectors and objects or discovery rules')
        if not set(layer['connectors']) <= connectors.keys(): fail('layers.' + role, 'unknown connector')
        if result['enabled'] and not any(connectors[key]['enabled'] for key in layer['connectors']):
            fail('layers.' + role, 'no enabled connector')
    if len(set(result['deployment']['jobs'].values())) != 3: fail('deployment.jobs', 'job names must differ')
    if result['enabled']:
        for key, reference in result['references'].items():
            if reference.startswith(('PLACEHOLDER', 'REPLACE')): fail('references.' + key, 'unresolved placeholder')
    manifest = result['installation']
    if result['enabled'] and manifest is None: fail('installation', 'enabled estate requires installed bindings')
    if manifest is not None:
        from .estate_manifest import validate as validate_manifest
        validate_manifest(manifest)
        adapters = {row['id'] for row in manifest['adapters']}
        if any(row['adapter'] not in adapters for row in connectors.values()): fail('connectors', 'unknown installed adapter')
        if result['model']['provider'] != manifest['model']['provider'] or result['model']['model'] != manifest['model']['deployment']:
            fail('model', 'does not match installed model binding')
        from .adapters.estate_config_bindings import validate_bindings
        validate_bindings(result)
    return result


def _reject_values(value):
    """Reject credential values, including nested adapter options. References are fine."""
    forbidden = {'password', 'client_secret', 'access_token', 'refresh_token', 'api_key', 'secret_value', 'connection_string'}
    if isinstance(value, dict):
        if forbidden & {key.casefold() for key in value}: raise ValueError('estate: secret values are forbidden; use named references')
        for child in value.values(): _reject_values(child)
    elif isinstance(value, list):
        for child in value: _reject_values(child)


def load(path):
    from .provider_tape_contract import parse
    return validate(parse(Path(path).read_bytes()))


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def dry_run(value):
    value = validate(value)
    return {'status': value['status'] if value['status'] in ('SMOKE_ONLY', 'READY_SEALED_TEST') else 'VALID' if value['enabled'] else 'DRAFT_DISABLED', 'estate_id': value['id'],
            'config_sha256': fingerprint(value), 'layers': list(value['layers']),
            'connectors': [row['id'] for row in value['connectors']], 'network_calls': 0,
            'secret_resolution': 'NOT_ATTEMPTED', 'execution_enabled': False}


def engine_manifest(value):
    value = validate(value)
    if not value['enabled']: raise ValueError('ESTATE_DISABLED: dry-run only')
    return deepcopy(value['installation'])


@lru_cache(maxsize=8)
def _configured(path, stamp):
    return load(path)


def configured():
    """Optional trusted process setting, never accepted from ticket/model fields."""
    path = os.environ.get('DIA_ESTATE_CONFIG')
    if not path: return None
    file = Path(path).resolve()
    return deepcopy(_configured(str(file), file.stat().st_mtime_ns))


def command(argv):
    import argparse
    parser = argparse.ArgumentParser(description='Validate estate configuration without network or secrets')
    parser.add_argument('action', choices=('validate',))
    parser.add_argument('file', type=Path)
    args = parser.parse_args(argv)
    try: result = dry_run(load(args.file))
    except (ValueError, OSError) as error:
        # Schema validation can include untrusted values; do not print them.
        print(json.dumps({'status': 'INVALID', 'reason': str(error) if isinstance(error,ValueError) else 'configuration file could not be read'}))
        return 2
    print(json.dumps(result, indent=2))
    return 0

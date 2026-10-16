"""Approved endpoint metadata reuse; never a fresh attestation or a fallback."""
import copy
import hashlib
import json
import re
from pathlib import Path
from uuid import UUID


def validate(value):
    from metadata_config import keys, text
    keys(value, ['version', 'receipt_path', 'receipt_sha256', 'source_context_version', 'bindings'])
    if value['version'] != 1: raise ValueError('Unsupported retained endpoint version')
    text(value['receipt_path']); text(value['source_context_version'])
    if not re.fullmatch('[0-9a-f]{64}', value['receipt_sha256']):
        raise ValueError('Retained endpoint receipt hash invalid')
    if not isinstance(value['bindings'], list) or not value['bindings']:
        raise ValueError('Retained endpoints require explicit bindings')
    seen = set()
    for row in value['bindings']:
        keys(row, ['request', 'container_asset_hash', 'endpoint_asset_hash'])
        keys(row['request'], ['workspace', 'lakehouse'])
        for raw in row['request'].values(): UUID(raw)
        key = tuple(sorted(row['request'].items()))
        if key in seen: raise ValueError('Duplicate retained endpoint binding')
        seen.add(key)
        for name in ('container_asset_hash', 'endpoint_asset_hash'):
            if not re.fullmatch('[0-9a-f]{64}', row[name]):
                raise ValueError('Retained endpoint asset hash invalid')
    return value


def read(config, context, request, *, receipt_path=None):
    """Return only the exact approved route; missing/stale declarations fail closed.

    This is a local metadata lookup, not a physical request. Query-bound surface
    reporting and read-only permission checks still execute on every value route.
    """
    pin = validate(config['fabric']['retained_endpoints'])
    bindings = [row for row in pin['bindings'] if row['request'] == request]
    if len(bindings) != 1: raise ValueError('Endpoint request has no retained binding')
    if request['workspace'] != config['fabric']['workspace_id']:
        raise ValueError('Retained endpoint leaves approved workspace')
    raw = Path(receipt_path if receipt_path is not None else pin['receipt_path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != pin['receipt_sha256']:
        raise ValueError('Retained endpoint receipt changed')
    receipt = json.loads(raw)
    rows = [row for row in receipt if row.get('request') == request]
    if len(rows) != 1: raise ValueError('Endpoint receipt lacks a unique request')
    response = rows[0]['response']
    props = response.get('properties', {}).get('sqlEndpointProperties', {})
    if (response.get('id') != request['lakehouse'] or
        response.get('workspaceId') != request['workspace'] or
        response.get('type') != 'Lakehouse' or
        props.get('connectionString') != config['fabric']['sql_reader']['server']):
        raise ValueError('Retained endpoint response route differs')
    prefix = 'fabric://' + request['workspace'] + '/'
    expected = ((prefix + request['lakehouse'], 'Lakehouse', 'container_asset_hash'),
                (prefix + str(props.get('id')), 'SQLEndpoint', 'endpoint_asset_hash'))
    for identity, kind, hash_name in expected:
        assets = [a for a in context.get('assets', []) if a.get('id') == identity]
        if (len(assets) != 1 or assets[0].get('availability') != 'CURRENT' or
            assets[0].get('kind') != kind or assets[0].get('provenance') != 'DISCOVERED' or
            assets[0].get('content_hash') != bindings[0][hash_name]):
            raise ValueError('Retained endpoint discovered binding is stale or absent')
    result = copy.deepcopy(response)
    result['endpoint_provenance'] = {
        'kind': 'RETAINED_METADATA', 'receipt_sha256': pin['receipt_sha256'],
        'source_context_version': pin['source_context_version'],
        'current_context_version': context.get('version'),
        'container_asset_hash': bindings[0]['container_asset_hash'],
        'endpoint_asset_hash': bindings[0]['endpoint_asset_hash'],
        'limitation': 'Retained endpoint declaration; current connection remains query-attested only where reportable.'}
    return result

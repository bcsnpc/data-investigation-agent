"""Trusted platform-only health control; never an investigation/model tool.

One read-only tool-state statement, an immutable health blob PUT/GET, and one
bounded Key Vault metadata page. No estate endpoint, model, secret value, role,
resource, schema or migration mutation is accepted by this command.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.error import HTTPError
from urllib.request import Request, build_opener

from investigator.adapters.managed_identity import Tokens, validate
from investigator.live_gateway import current, open_http, configured
from metadata_auth import NoRedirect

PG_QUERY = """SELECT current_database(), current_user,
 current_setting('transaction_read_only'),
 (SELECT count(*) FROM dia_state.state_schema_versions),
 (SELECT count(*) FROM dia_state.state_migrations),
 (SELECT count(*) FROM dia_state.state_accounts),
 (SELECT count(*) FROM dia_state.state_documents)"""


def plan(config):
    required = {'version', 'identity', 'state_channel', 'metadata_channel', 'postgres', 'blob', 'key_vault', 'nonce', 'receipt_key'}
    if set(config) != required or config['version'] != 1:
        raise ValueError('PLATFORM_HEALTH_CONFIGURATION')
    identity = validate(config['identity'])
    if any(not isinstance(config[name], str) or not re.fullmatch(r'[A-Za-z0-9:_-]{1,100}', config[name]) for name in ('state_channel', 'metadata_channel')):
        raise ValueError('PLATFORM_HEALTH_CHANNEL')
    pg = config['postgres']; blob = config['blob']; vault = config['key_vault']
    if set(pg) != {'host', 'database', 'user'} or not re.fullmatch(r'[a-z0-9-]+\.postgres\.database\.azure\.com', pg['host']):
        raise ValueError('PLATFORM_POSTGRES_CONFIGURATION')
    if any(not isinstance(pg[name], str) or not 1 <= len(pg[name]) <= 128 for name in ('database', 'user')):
        raise ValueError('PLATFORM_POSTGRES_CONFIGURATION')
    if set(blob) != {'account_url', 'container'} or not re.fullmatch(r'https://[a-z0-9]{3,24}\.blob\.core\.windows\.net', blob['account_url']) or blob['container'] != 'captures':
        raise ValueError('PLATFORM_HEALTH_BLOB_CONFIGURATION')
    if set(vault) != {'vault_url'} or not re.fullmatch(r'https://[a-zA-Z0-9-]{3,24}\.vault\.azure\.net', vault['vault_url']):
        raise ValueError('PLATFORM_HEALTH_VAULT_CONFIGURATION')
    if not isinstance(config['nonce'], str) or not re.fullmatch('[a-f0-9]{16,64}', config['nonce']):
        raise ValueError('PLATFORM_HEALTH_NONCE')
    if not isinstance(config['receipt_key'], str) or not re.fullmatch('[a-f0-9]{64}', config['receipt_key']):
        raise ValueError('PLATFORM_HEALTH_RECEIPT_KEY')
    body = json.dumps({'kind': 'PLATFORM_HEALTH', 'version': 1,
                       'principal_id': identity['principal_id'], 'nonce': config['nonce']}, sort_keys=True, separators=(',', ':')).encode()
    digest = hashlib.sha256(body).hexdigest()
    return {'body': body, 'sha256': digest,
            'blob_url': blob['account_url'] + '/captures/files/' + digest,
            'receipt_url': blob['account_url'] + '/captures/health/' + config['receipt_key'] + '.json',
            'vault_url': vault['vault_url'] + '/secrets?api-version=7.4&maxresults=1'}


def permissions(config):
    """Plan only: print exact grants for operator review; never install a policy."""
    planned = plan(config)
    return {'platform_database': config['postgres'], 'http': [
        {'identity': config['state_channel'], 'method': method, 'url': planned['blob_url'], 'purpose': 'platform_blob'}
        for method in ('PUT', 'GET')] + [
        {'identity': config['state_channel'], 'method': method, 'url': planned['receipt_url'], 'purpose': 'platform_blob'}
        for method in ('PUT', 'GET')] + [
        {'identity': config['metadata_channel'], 'method': 'GET', 'url': planned['vault_url'], 'purpose': 'metadata'}],
        'health_blob_sha256': planned['sha256'], 'postgres_statement': PG_QUERY,
        'writes': 'Only immutable own-health challenge and result receipt blobs; no database write.',
        'secret_values_requested': False}


def postgres_read(config, tokens):
    from investigator.postgres_connection import connect as postgres_connect
    from investigator.adapters.platform_credentials import trust_roots
    pg = config['postgres']
    password = tokens.get_token('https://ossrdbms-aad.database.windows.net/.default')
    with postgres_connect(host=pg['host'], dbname=pg['database'], user=pg['user'], password=password,
                        sslmode='verify-full', sslrootcert=trust_roots(), connect_timeout=15, autocommit=True,
                        options='-c default_transaction_read_only=on -c statement_timeout=15000') as db:
        return list(db.execute(PG_QUERY).fetchone())


def run(config, *, tokens=None, opener=None, pg_read=None):
    planned = plan(config)
    gateway = current()
    # All exact authorities are checked before authentication or transport.
    gateway.platform_database(config['state_channel'], config['postgres']['host'], config['postgres']['database'])
    for grant in permissions(config)['http']:
        gateway.http(grant['identity'], grant['method'], grant['url'], planned['body'] if grant['method'] == 'PUT' else None)
    tokens = tokens or Tokens(config['identity'])
    opener = opener or build_opener(NoRedirect())
    rows = []
    checks = {}

    def request(name, method, url, scope, channel, body=None):
        headers = {'Authorization': 'Bearer ' + tokens.get_token(scope)}
        if scope == 'https://storage.azure.com/.default': headers['x-ms-version'] = '2023-11-03'
        if method == 'PUT': headers.update({'x-ms-blob-type': 'BlockBlob', 'If-None-Match': '*', 'Content-Type': 'application/json'})
        receipt = {'kind': name, 'method': method, 'endpoint_sha256': hashlib.sha256(url.encode()).hexdigest(), 'identity': config['identity']['principal_id']}
        try:
            with open_http(opener, Request(url, data=body, headers=headers, method=method), timeout=30, identity=channel) as response:
                content = response.read(65537)
                receipt['status'] = response.status
                receipt['request_id'] = response.headers.get('x-ms-request-id')
            if len(content) > 65536: raise ValueError('PLATFORM_HEALTH_RESPONSE_BOUND')
            receipt['response_bytes'] = len(content)
            return receipt['status'], content
        except HTTPError as exc:
            receipt['status'] = exc.code
            receipt['request_id'] = exc.headers.get('x-ms-request-id') if exc.headers else None
            return exc.code, b''
        finally:
            rows.append(receipt)

    try:
        value = (pg_read or postgres_read)(config, tokens)
        if len(value) != 7 or value[0] != config['postgres']['database'] or value[1] != config['postgres']['user'] or value[2] != 'on':
            raise ValueError('PLATFORM_POSTGRES_IDENTITY_OR_READ_ONLY_MISMATCH')
        checks['postgres'] = {'status': 'PASS', 'database': value[0], 'identity': value[1], 'transaction_read_only': value[2],
                              'schema_versions': value[3], 'migrations': value[4], 'accounts': value[5], 'documents': value[6],
                              'limitation': 'Counts establish reachability, not exact migration equivalence.'}
        rows.append({'kind': 'PLATFORM_POSTGRES_READ', 'identity': config['identity']['principal_id'], 'statement': PG_QUERY, 'status': 'AVAILABLE'})
    except Exception as exc:
        checks['postgres'] = {'status': 'FAIL', 'error_type': type(exc).__name__, 'sqlstate': getattr(exc, 'sqlstate', None)}
        rows.append({'kind': 'PLATFORM_POSTGRES_READ', 'identity': config['identity']['principal_id'], 'statement': PG_QUERY, 'status': 'FAILED', 'error_type': type(exc).__name__})
    try:
        status, _ = request('PLATFORM_HEALTH_BLOB_PUT', 'PUT', planned['blob_url'], 'https://storage.azure.com/.default', config['state_channel'], planned['body'])
        if status not in (201, 409, 412): raise ValueError('PLATFORM_HEALTH_BLOB_PUT_REFUSED')
        status, raw = request('PLATFORM_HEALTH_BLOB_GET', 'GET', planned['blob_url'], 'https://storage.azure.com/.default', config['state_channel'])
        if status != 200 or raw != planned['body']: raise ValueError('PLATFORM_HEALTH_BLOB_READBACK_DIFFERS')
        checks['blob'] = {'status': 'PASS', 'sha256': planned['sha256'], 'immutable': True}
    except Exception as exc:
        checks['blob'] = {'status': 'FAIL', 'error_type': type(exc).__name__}
    try:
        status, raw = request('PLATFORM_VAULT_METADATA', 'GET', planned['vault_url'], 'https://vault.azure.net/.default', config['metadata_channel'])
        if status != 200: raise ValueError('PLATFORM_VAULT_METADATA_REFUSED')
        value = json.loads(raw)
        items = value.get('value')
        if not isinstance(items, list) or len(items) > 1: raise ValueError('PLATFORM_VAULT_METADATA_BOUND')
        checks['key_vault'] = {'status': 'PASS', 'metadata_items': len(items), 'more_pages_not_followed': bool(value.get('nextLink')),
            'item_id_sha256': [hashlib.sha256(str(item.get('id', '')).encode()).hexdigest() for item in items],
            'secret_read_verified': False, 'limitation': 'One metadata page only; no secret value was requested or established.'}
    except Exception as exc:
        checks['key_vault'] = {'status': 'FAIL', 'error_type': type(exc).__name__, 'secret_read_verified': False}
        from investigator.adapters.managed_identity import TokenBindingError
        if isinstance(exc, TokenBindingError):
            checks['key_vault']['authentication_reason'] = exc.reason
    result = {'version': 1, 'kind': 'PLATFORM_HEALTH', 'principal_id': config['identity']['principal_id'],
            'recorded_at': datetime.now(timezone.utc).isoformat(),
            'status': 'PASS' if all(value['status'] == 'PASS' for value in checks.values()) else 'FAIL',
            'checks': checks, 'receipts': list(rows), 'estate_reads': 0, 'model_calls': 0,
            'control_operations': len(rows), 'limitation': 'Platform-only health; not estate readiness or successful migration attestation.'}
    # Failures are publishable too. The endpoint was explicitly approved before
    # probes, and is separate from CAS because its immutable key predates results.
    raw = json.dumps(result, sort_keys=True, separators=(',', ':')).encode()
    start = len(rows)
    try:
        if len(raw) > 32768: raise ValueError('PLATFORM_HEALTH_RECEIPT_BOUND')
        status, _ = request('PLATFORM_HEALTH_RECEIPT_PUT', 'PUT', planned['receipt_url'], 'https://storage.azure.com/.default', config['state_channel'], raw)
        if status not in (201, 409, 412): raise ValueError('PLATFORM_HEALTH_RECEIPT_PUT_REFUSED')
        status, saved = request('PLATFORM_HEALTH_RECEIPT_GET', 'GET', planned['receipt_url'], 'https://storage.azure.com/.default', config['state_channel'])
        if status != 200 or saved != raw: raise ValueError('PLATFORM_HEALTH_RECEIPT_READBACK_DIFFERS')
        result['receipt_publication'] = {'status': 'PASS', 'url': planned['receipt_url'], 'sha256': hashlib.sha256(raw).hexdigest(), 'byte_verified': True}
    except Exception as exc:
        result['status'] = 'FAIL'
        result['receipt_publication'] = {'status': 'FAIL', 'error_type': type(exc).__name__}
    result['publication_receipts'] = rows[start:]
    result['control_operations'] = len(rows)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--config', type=Path)
    source.add_argument('--environment-config', action='store_true')
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    config = json.loads(os.environ['DIA_PLATFORM_HEALTH_CONFIG']) if args.environment_config else json.loads(args.config.read_text(encoding='utf-8-sig'))
    if args.plan:
        result = permissions(config)
    elif args.environment_config:
        # Both values are deployment-owned configuration, never model arguments.
        # No file or credential is created; the kill switch still applies.
        with configured(json.loads(os.environ['DIA_PLATFORM_GATEWAY_POLICY'])):
            result = run(config)
    else:
        result = run(config)
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding='utf-8')
    print(text)
    raise SystemExit(0 if args.plan or result['status'] == 'PASS' else 1)

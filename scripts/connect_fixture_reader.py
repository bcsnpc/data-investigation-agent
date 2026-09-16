"""Sign in an isolated fixture reader; keep its MSAL cache Windows-protected.

This never replaces the publisher's Fabric CLI credentials. Run with the
repository's Fabric virtualenv, which contains MSAL and msal-extensions.
"""
import argparse
import base64
import json
from pathlib import Path
from uuid import UUID
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def application(tenant):
    import msal
    from msal_extensions import FilePersistenceWithDataProtection, PersistedTokenCache
    from fabric_cli.core.fab_constant import AUTH_DEFAULT_CLIENT_ID
    folder = Path(__file__).resolve().parents[1] / '.local/fixture-reader-auth'
    folder.mkdir(parents=True, exist_ok=True)
    cache = PersistedTokenCache(FilePersistenceWithDataProtection(str(folder / 'msal.cache')))
    return msal.PublicClientApplication(AUTH_DEFAULT_CLIENT_ID,
        authority='https://login.microsoftonline.com/' + str(UUID(tenant)), token_cache=cache)


def token(app, account, tenant, scope, interactive=False):
    accounts = [a for a in app.get_accounts(username=account) if a.get('realm', '').lower() == tenant.lower()]
    result = app.acquire_token_silent([scope], account=accounts[0]) if len(accounts) == 1 else None
    if not result and interactive:
        result = app.acquire_token_interactive(scopes=[scope], login_hint=account, prompt='select_account', timeout=300)
    if not result or 'access_token' not in result:
        raise RuntimeError('Reader sign-in unavailable')
    # Token is issued through MSAL, not supplied by an HTTP caller. Check the
    # actual access-token identity: silent results need not include an ID token.
    part = result['access_token'].split('.')[1]
    claims = json.loads(base64.urlsafe_b64decode(part + '=' * (-len(part) % 4)))
    username = claims.get('preferred_username') or claims.get('upn') or ''
    if (username.casefold() != account.casefold() or claims.get('tid', '').lower() != tenant.lower()
            or claims.get('aud', '').rstrip('/') != scope.removesuffix('/.default').rstrip('/')):
        raise RuntimeError('Reader account or tenant mismatch')
    return result['access_token']


def verify(app, account, tenant, workspace, model, bundle=None):
    access = token(app, account, tenant, 'https://analysis.windows.net/powerbi/api/.default')
    base = 'https://api.powerbi.com/v1.0/myorg/groups/' + str(UUID(workspace))
    path = base + '/datasets/' + str(UUID(model))
    results = {'account': account, 'tenant': tenant, 'workspace_id': workspace, 'model_id': model,
               'generation_proven': False, 'live_acceptance_ready': False}
    for name, url, body in [('native_identity', path + '/executeQueries',
                             {'queries': [{'query': 'EVALUATE ROW("reader", USERPRINCIPALNAME())'}]}),
                            ('write_required_refresh_history', path + '/refreshes?$top=1', None)]:
        request = Request(url, data=json.dumps(body).encode() if body else None,
                          headers={'Authorization': 'Bearer ' + access, 'Content-Type': 'application/json'})
        try:
            with urlopen(request, timeout=60) as response:
                raw = response.read(1_000_001)
                if len(raw) > 1_000_000:
                    raise ValueError('Reader response too large')
                value = json.loads(raw)
                results[name] = {'http_status': response.status}
                if name == 'native_identity':
                    rows = value.get('results', [{}])[0].get('tables', [{}])[0].get('rows', [])
                    results[name]['identity_matches'] = len(rows) == 1 and rows[0].get('[reader]', '').casefold() == account.casefold()
        except HTTPError as exc:
            results[name] = {'http_status': exc.code}
    if bundle is not None:
        from import_fixture import validate, query, verify_table
        bundle = validate(bundle)
        observations = []
        for table in bundle['inputs']:
            body = {'queries': [{'query': query(table)}], 'serializerSettings': {'includeNulls': True}}
            request = Request(path + '/executeQueries', data=json.dumps(body).encode(),
                              headers={'Authorization': 'Bearer ' + access, 'Content-Type': 'application/json'})
            with urlopen(request, timeout=60) as response:
                raw = response.read(4_000_001)
                if len(raw) > 4_000_000:
                    raise ValueError('Reader content response too large')
                observations.append(verify_table(table, json.loads(raw)))
        results.update(bundle_hash=bundle['bundle_hash'], tables=observations,
                       contents_match=all(x['matches'] for x in observations))
    results['fixture_reader_checks_passed'] = (results.get('native_identity', {}).get('identity_matches') is True
        and results.get('write_required_refresh_history', {}).get('http_status') == 403
        and (bundle is None or results.get('contents_match') is True))
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tenant', required=True)
    parser.add_argument('--account', required=True)
    parser.add_argument('--workspace', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--sign-in', action='store_true')
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        app = application(args.tenant)
        if args.sign_in:
            token(app, args.account, args.tenant, 'https://analysis.windows.net/powerbi/api/.default', interactive=True)
        bundle = json.loads(args.bundle.read_text(encoding='utf-8')) if args.bundle else None
        result = verify(app, args.account, args.tenant, args.workspace, args.model, bundle)
        args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result))
        if not result['fixture_reader_checks_passed']:
            raise SystemExit(2)
    except Exception as exc:
        print(json.dumps({'status': 'UNAVAILABLE', 'error_type': type(exc).__name__}))
        raise SystemExit(1)

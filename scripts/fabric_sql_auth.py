"""Browser-based SQL authentication using the CLI's existing encrypted cache."""
import base64
import json

SQL_SCOPE = 'https://database.windows.net/.default'
ACCOUNT = 'admin@skynwhy.com'  # Current OrderOps development operator.


def client(tenant):
    import msal
    from msal_extensions import PersistedTokenCache
    from fabric_cli.core.fab_auth import FabAuth
    from fabric_cli.core import fab_constant
    auth = FabAuth()
    return msal.PublicClientApplication(
        fab_constant.AUTH_DEFAULT_CLIENT_ID,
        authority='https://login.microsoftonline.com/'+tenant,
        token_cache=PersistedTokenCache(auth._get_persistence()),
        enable_broker_on_windows=False, enable_broker_on_mac=False)


def verify(result, tenant):
    if not result or not result.get('access_token'):
        raise RuntimeError('SQL sign-in unavailable; run connect_fabric_sql.py')
    token = result['access_token']
    part = token.split('.')[1]
    claims = json.loads(base64.urlsafe_b64decode(part+'='*(-len(part)%4)))
    if claims.get('tid', '').lower() != tenant.lower():
        raise RuntimeError('SQL token tenant differs from configuration')
    return token


def get_sql_token(tenant):
    app = client(tenant)
    accounts = app.get_accounts(username=ACCOUNT)
    if len(accounts) != 1:
        raise RuntimeError('Expected enterprise SQL account unavailable or ambiguous')
    return verify(app.acquire_token_silent([SQL_SCOPE], account=accounts[0]), tenant)


def sign_in(tenant):
    app = client(tenant)
    result = app.acquire_token_interactive([SQL_SCOPE], login_hint=ACCOUNT,
                                           prompt='select_account', timeout=300)
    verify(result, tenant)
    claims = result.get('id_token_claims', {})
    if claims.get('preferred_username', '').casefold() != ACCOUNT.casefold():
        raise RuntimeError('Select '+ACCOUNT+' when signing in')
    get_sql_token(tenant)

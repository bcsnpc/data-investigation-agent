"""Existing delegated reader cache, fetched by MI and used only in memory.

This is credential relocation, not consent or sign-in. No interactive, CLI,
administrator, disk-cache, or credential-chain fallback exists.
"""
import base64
import json
from urllib.parse import urlencode, parse_qs
from urllib.request import Request, build_opener
from urllib.error import HTTPError
from uuid import UUID

from .managed_identity import secret, validate_secret_reference

MODE = 'key_vault_user_cache'
PBI = 'https://analysis.windows.net/powerbi/api/.default'
SQL = 'https://database.windows.net/.default'
FIELDS = {'mode', 'tenant_id', 'client_id', 'principal_id', 'account', 'scope', 'reference'}


def validate_refresh_request(method, url, body, grant):
    try:
        expected = 'https://login.microsoftonline.com/' + str(UUID(grant['tenant_id'])) + '/oauth2/v2.0/token'
        data = parse_qs(body.decode() if isinstance(body, bytes) else body, strict_parsing=True)
        return (method == 'POST' and url == expected and data.get('grant_type') == ['refresh_token']
                and data.get('client_id') == [grant['client_id']] and grant['scope'] in (PBI, SQL)
                and len(data.get('scope', [])) == 1 and grant['scope'] in data['scope'][0].split()
                and not set(data['scope'][0].split()) - {grant['scope'], 'openid', 'profile', 'offline_access'}
                and len(data.get('refresh_token', [])) == 1
                and not set(data) - {'grant_type','client_id','scope','refresh_token','client_info','claims'})
    except Exception:
        return False


def validate(value):
    if not isinstance(value, dict) or set(value) != FIELDS or value['mode'] != MODE:
        raise ValueError('USER_CACHE_CONFIGURATION_REQUIRED')
    for key in ('tenant_id', 'client_id', 'principal_id'):
        if not isinstance(value[key], str) or str(UUID(value[key])) != value[key]:
            raise ValueError('USER_CACHE_IDENTIFIER_INVALID')
    if (not isinstance(value['account'], str) or value['account'].count('@') != 1
            or len(value['account']) > 254 or any(c.isspace() for c in value['account'])):
        raise ValueError('USER_CACHE_ACCOUNT_INVALID')
    if value['scope'] not in (PBI, SQL):
        raise ValueError('USER_CACHE_AUDIENCE_UNDECLARED')
    validate_secret_reference(value['reference'])
    return dict(value)


def reference(value):
    value = validate(value)['reference']
    return value['vault_url'] + '/secrets/' + value['secret_name'] + '/' + value['secret_version']


def channel(value):
    value=validate(value)
    return 'user-cache:' + value['client_id'] + (':powerbi' if value['scope']==PBI else ':sql')


def cache_payload(raw, declaration):
    """Validate minimal migration envelope before handing anything to MSAL."""
    d = validate(declaration)
    if not isinstance(raw, str) or len(raw.encode()) > 32768:
        raise ValueError('USER_CACHE_PAYLOAD_INVALID')
    envelope = json.loads(raw)
    if set(envelope) != {'version', 'cache'} or envelope['version'] != 1:
        raise ValueError('USER_CACHE_PAYLOAD_INVALID')
    cache = envelope['cache']
    if not isinstance(cache, dict) or set(cache) != {'Account', 'RefreshToken', 'AppMetadata'}:
        raise ValueError('USER_CACHE_MINIMAL_PAYLOAD_REQUIRED')
    if any(not isinstance(cache[k], dict) for k in cache):
        raise ValueError('USER_CACHE_PAYLOAD_INVALID')
    accounts = list(cache['Account'].values())
    if len(accounts) != 1:
        raise ValueError('USER_CACHE_SINGLE_ACCOUNT_REQUIRED')
    a = accounts[0]
    if (a.get('realm') != d['tenant_id'] or a.get('local_account_id') != d['principal_id']
            or a.get('username', '').casefold() != d['account'].casefold()
            or a.get('environment') != 'login.microsoftonline.com' or not a.get('home_account_id')):
        raise ValueError('USER_CACHE_ACCOUNT_BINDING_MISMATCH')
    refresh = list(cache['RefreshToken'].values())
    if not refresh or len(refresh) > 4:
        raise ValueError('USER_CACHE_REFRESH_REQUIRED')
    for row in refresh:
        if (row.get('client_id') != d['client_id'] or row.get('home_account_id') != a['home_account_id']
                or row.get('environment') != a['environment'] or not isinstance(row.get('secret'), str)
                or not row['secret'] or row.get('credential_type') != 'RefreshToken'):
            raise ValueError('USER_CACHE_REFRESH_BINDING_MISMATCH')
    for row in cache['AppMetadata'].values():
        if row.get('client_id') != d['client_id'] or row.get('environment') != a['environment']:
            raise ValueError('USER_CACHE_APP_BINDING_MISMATCH')
    return cache


class Http:
    """MSAL transport: exact declared tenant endpoints and gateway, no redirects."""
    def __init__(self, declaration, gateway_identity=None):
        self.d = declaration
        self.gateway_identity = gateway_identity or channel(declaration)

    def get(self, url, **kwargs):
        expected = 'https://login.microsoftonline.com/' + self.d['tenant_id'] + '/v2.0/.well-known/openid-configuration'
        if url != expected or kwargs.get('params'):
            raise ValueError('USER_CACHE_DISCOVERY_ENDPOINT_REFUSED')
        return self._request(Request(url, method='GET'))

    def post(self, url, data=None, **kwargs):
        expected = 'https://login.microsoftonline.com/' + self.d['tenant_id'] + '/oauth2/v2.0/token'
        if (url != expected or not isinstance(data, dict) or data.get('grant_type') != 'refresh_token'
                or data.get('client_id') != self.d['client_id']
                or set(str(data.get('scope', '')).split()) - {self.d['scope'], 'openid', 'profile', 'offline_access'}
                or self.d['scope'] not in str(data.get('scope', '')).split()):
            raise ValueError('USER_CACHE_REFRESH_REQUEST_REFUSED')
        return self._request(Request(url, data=urlencode(data).encode(), method='POST',
            headers={'Content-Type':'application/x-www-form-urlencoded'}))

    def _request(self, request):
        from metadata_auth import NoRedirect
        from ..live_gateway import open_http
        try:
            response = open_http(build_opener(NoRedirect()), request, timeout=30, identity=self.gateway_identity)
        except HTTPError as error:
            response = error
        with response:
            body = response.read(65537)
            if len(body) > 65536:
                raise ValueError('USER_CACHE_RESPONSE_TOO_LARGE')
            class Result:
                status_code = response.code
                text = body.decode('utf-8')
                headers = dict(response.headers)
                def json(self):
                    return json.loads(self.text)
            return Result()


class Tokens:
    def __init__(self, declaration, *, loader=None, application=None, gateway_identity=None):
        self.d = validate(declaration)
        self.loader = loader or secret
        self.application = application
        self.gateway_identity = gateway_identity or channel(declaration)

    def get_token(self, scope):
        if scope != self.d['scope']:
            raise ValueError('USER_CACHE_AUDIENCE_UNDECLARED')
        try:
            import msal
            cache = msal.SerializableTokenCache()
            options = {'gateway_identity': self.gateway_identity} if self.gateway_identity is not None else {}
            cache.deserialize(json.dumps(cache_payload(self.loader(self.d['reference'], **options), self.d)))
            factory = self.application or msal.PublicClientApplication
            app = factory(self.d['client_id'], authority='https://login.microsoftonline.com/' + self.d['tenant_id'],
                token_cache=cache, http_client=Http(self.d, self.gateway_identity), instance_discovery=False, enable_pii_log=False)
            accounts = app.get_accounts(username=self.d['account'])
            if len(accounts) != 1 or accounts[0].get('local_account_id') != self.d['principal_id']:
                raise ValueError('account')
            result = app.acquire_token_silent([scope], account=accounts[0])
            token = result['access_token']
            part = token.split('.')[1]
            claims = json.loads(base64.urlsafe_b64decode(part + '=' * (-len(part) % 4)))
            if (claims.get('tid') != self.d['tenant_id'] or claims.get('oid') != self.d['principal_id']
                    or str(claims.get('aud', '')).rstrip('/') != scope.removesuffix('/.default').rstrip('/')
                    or (claims.get('preferred_username') or claims.get('upn') or self.d['account']).casefold() != self.d['account'].casefold()):
                raise ValueError('binding')
            return token
        except Exception:
            raise RuntimeError('USER_CACHE_TOKEN_UNAVAILABLE_OR_BINDING_MISMATCH') from None


def credential(reader):
    if reader.get('mode') == MODE:
        return validate({k: reader[k] for k in FIELDS})
    from .managed_identity import FIELDS as MI_FIELDS, validate as mi_validate
    return mi_validate({k: reader[k] for k in MI_FIELDS})


def provider(declaration):
    if declaration.get('mode') == MODE:
        return Tokens(declaration)
    from .managed_identity import Tokens as MI_Tokens
    return MI_Tokens(declaration)

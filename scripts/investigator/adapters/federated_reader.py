"""Secretless, explicitly bound reader application; no interactive fallback."""
import base64
import json
import re
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode
from urllib.request import Request, build_opener
from uuid import UUID

MODE = 'federated_reader'
FIELDS = {'mode', 'tenant_id', 'client_id', 'principal_id', 'managed_identity'}
SCOPES = frozenset({'https://database.windows.net/.default',
                    'https://api.fabric.microsoft.com/.default',
                    'https://analysis.windows.net/powerbi/api/.default'})
EXCHANGE = 'api://AzureADTokenExchange/.default'
ASSERTION_TYPE = 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer'


class FederationUnavailable(RuntimeError):
    def __init__(self, stage, *, http_status=None, provider_code=None):
        super().__init__('FEDERATED_READER_TOKEN_UNAVAILABLE_OR_BINDING_MISMATCH')
        self.stage=stage
        self.http_status=http_status
        self.provider_code=provider_code


def validate(value):
    from .managed_identity import validate as managed
    if not isinstance(value, dict) or set(value) != FIELDS or value['mode'] != MODE:
        raise ValueError('FEDERATED_READER_CONFIGURATION_REQUIRED')
    for key in ('tenant_id', 'client_id', 'principal_id'):
        if not isinstance(value[key], str) or str(UUID(value[key])) != value[key]:
            raise ValueError('FEDERATED_READER_IDENTIFIER_INVALID')
    managed(value['managed_identity'])
    return json.loads(json.dumps(value))


def reference(value):
    d = validate(value)
    return 'federated-reader://' + d['tenant_id'] + '/' + d['client_id']


def channel(value, scope=None):
    d = validate(value)
    suffix = '' if scope is None else ':' + {'https://database.windows.net/.default': 'sql',
        'https://api.fabric.microsoft.com/.default': 'fabric',
        'https://analysis.windows.net/powerbi/api/.default': 'powerbi'}[scope]
    return 'federated:' + d['tenant_id'] + ':' + d['client_id'] + suffix


def claims(token):
    part = token.split('.')[1]
    return json.loads(base64.urlsafe_b64decode(part + '=' * (-len(part) % 4)))


def validate_request(method, url, body, grant):
    try:
        d = validate(grant['authentication'])
        data = parse_qs(body.decode() if isinstance(body, bytes) else body, strict_parsing=True)
        return (method == 'POST' and url == 'https://login.microsoftonline.com/' + d['tenant_id'] + '/oauth2/v2.0/token'
                and set(data) == {'client_id', 'scope', 'grant_type', 'client_assertion_type', 'client_assertion'}
                and data['client_id'] == [d['client_id']]
                and data['scope'] == [grant['scope']] and grant['scope'] in SCOPES
                and data['grant_type'] == ['client_credentials']
                and data['client_assertion_type'] == [ASSERTION_TYPE]
                and len(data['client_assertion']) == 1
                and claims(data['client_assertion'][0]).get('tid') == d['managed_identity']['tenant_id']
                and claims(data['client_assertion'][0]).get('oid') == d['managed_identity']['principal_id']
                and claims(data['client_assertion'][0]).get('aud') == 'api://AzureADTokenExchange')
    except Exception:
        return False


class Tokens:
    def __init__(self, declaration, *, managed=None, opener=None, gateway_identity=None):
        self.d = validate(declaration)
        if managed is None:
            from azure.identity import ManagedIdentityCredential
            managed = ManagedIdentityCredential(client_id=self.d['managed_identity']['client_id'])
        self.managed = managed
        self.opener = opener
        self.gateway_identity = gateway_identity

    def get_token(self, scope):
        if scope not in SCOPES:
            raise ValueError('FEDERATED_READER_AUDIENCE_UNDECLARED')
        from metadata_auth import NoRedirect
        from ..live_gateway import open_http
        stage='MANAGED_ASSERTION'
        try:
            assertion = self.managed.get_token(EXCHANGE).token
            stage='MANAGED_ASSERTION_BINDING'
            observed = claims(assertion)
            mi = self.d['managed_identity']
            if (observed.get('tid') != mi['tenant_id'] or observed.get('oid') != mi['principal_id']
                    or observed.get('aud') != 'api://AzureADTokenExchange'):
                raise ValueError('Managed assertion binding differs')
            url = 'https://login.microsoftonline.com/' + self.d['tenant_id'] + '/oauth2/v2.0/token'
            body = urlencode({'client_id': self.d['client_id'], 'scope': scope,
                              'grant_type': 'client_credentials', 'client_assertion_type': ASSERTION_TYPE,
                              'client_assertion': assertion}).encode()
            request = Request(url, data=body, method='POST', headers={'Content-Type': 'application/x-www-form-urlencoded'})
            stage='TOKEN_EXCHANGE'
            with open_http(self.opener or build_opener(NoRedirect()), request, timeout=30,
                           identity=self.gateway_identity or channel(self.d, scope)) as response:
                raw = response.read(32769)
            if len(raw) > 32768:
                raise ValueError('Token response too large')
            token = json.loads(raw)['access_token']
            stage='APPLICATION_TOKEN_BINDING'
            observed = claims(token)
            if (observed.get('tid') != self.d['tenant_id'] or observed.get('oid') != self.d['principal_id']
                    or (observed.get('appid') or observed.get('azp')) != self.d['client_id']
                    or str(observed.get('aud', '')).rstrip('/') != scope.removesuffix('/.default').rstrip('/')):
                raise ValueError('Application token binding differs')
            return token
        except HTTPError as error:
            code=None
            try:
                parsed=json.loads(error.read(32769))
                if isinstance(parsed.get('error_codes'),list) and parsed['error_codes'] and type(parsed['error_codes'][0]) is int:
                    code='AADSTS'+str(parsed['error_codes'][0])
                elif isinstance(parsed.get('error'),str) and re.fullmatch('[A-Za-z0-9_]{1,80}',parsed['error']):
                    code=parsed['error']
            except Exception:pass
            raise FederationUnavailable(stage,http_status=error.code,provider_code=code) from None
        except Exception as error:
            # Only the numeric Entra identifier may escape an SDK exception.
            found=re.search(r'\bAADSTS[0-9]{4,12}\b',str(error))
            raise FederationUnavailable(stage,provider_code=found[0] if found else None) from None

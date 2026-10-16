"""Explicit Azure managed identity; no developer/CLI credential fallback.

Authentication is an auth-plane operation. Tokens and secret values stay in
memory and never become capture events, evidence, configuration or errors.
"""
import base64
from contextlib import contextmanager
from contextvars import ContextVar
import json
import re
from urllib.request import Request, build_opener
from uuid import UUID

FIELDS = {'mode', 'client_id', 'tenant_id', 'principal_id'}
MODEL_SESSION = ContextVar('azure_managed_model_session', default=None)
SCOPES = frozenset({
    'https://database.windows.net/.default',
    'https://api.fabric.microsoft.com/.default',
    'https://analysis.windows.net/powerbi/api/.default',
    'https://storage.azure.com/.default',
    'https://vault.azure.net/.default',
    'https://cognitiveservices.azure.com/.default',
    'https://ossrdbms-aad.database.windows.net/.default',
})

TOKEN_FAILURE_REASONS = frozenset({'TOKEN_ACQUISITION_FAILED', 'TOKEN_NOT_JWT',
    'TENANT_MISMATCH', 'PRINCIPAL_MISMATCH', 'AUDIENCE_MISMATCH'})

# Key Vault's documented service application ID is an alternate audience for
# that resource only. It is not permission to accept arbitrary GUID audiences.
# https://learn.microsoft.com/en-us/azure/key-vault/secrets/overview-storage-keys
AUDIENCE_ALIASES = {'https://vault.azure.net/.default': frozenset({
    'cfa8b339-82a2-471a-a3c9-0fc0be7a4093'})}


class TokenBindingError(RuntimeError):
    def __init__(self, reason):
        if reason not in TOKEN_FAILURE_REASONS:
            raise ValueError('UNKNOWN_TOKEN_FAILURE_REASON')
        self.reason = reason
        super().__init__('MANAGED_IDENTITY_TOKEN_UNAVAILABLE_OR_BINDING_MISMATCH: ' + reason)


def validate(value):
    if not isinstance(value, dict) or set(value) != FIELDS or value['mode'] != 'managed_identity':
        raise ValueError('MANAGED_IDENTITY_CONFIGURATION_REQUIRED')
    for name in FIELDS - {'mode'}:
        if not isinstance(value[name], str) or str(UUID(value[name])) != value[name]:
            raise ValueError('MANAGED_IDENTITY_CANONICAL_IDENTIFIERS_REQUIRED')
    return dict(value)


def reference(value):
    return 'managed-identity://' + validate(value)['client_id']


class Tokens:
    def __init__(self, declaration, *, credential=None):
        self.declaration = validate(declaration)
        if credential is None:
            from azure.identity import ManagedIdentityCredential
            credential = ManagedIdentityCredential(client_id=self.declaration['client_id'])
        self.credential = credential

    def get_token(self, scope):
        if scope not in SCOPES:
            raise ValueError('MANAGED_IDENTITY_AUDIENCE_UNDECLARED')
        try:
            token = self.credential.get_token(scope).token
        except Exception:
            raise TokenBindingError('TOKEN_ACQUISITION_FAILED') from None
        try:
            part = token.split('.')[1]
            claims = json.loads(base64.urlsafe_b64decode(part + '=' * (-len(part) % 4)))
            if not isinstance(claims, dict):raise ValueError('claims')
        except Exception:
            raise TokenBindingError('TOKEN_NOT_JWT') from None
        # SDK obtained the token from the selected identity endpoint. These are
        # binding checks; the destination server still verifies its signature.
        if claims.get('tid') != self.declaration['tenant_id']:
            raise TokenBindingError('TENANT_MISMATCH')
        if claims.get('oid') != self.declaration['principal_id']:
            raise TokenBindingError('PRINCIPAL_MISMATCH')
        audience = str(claims.get('aud', '')).rstrip('/')
        if (audience != scope.removesuffix('/.default').rstrip('/')
                and audience not in AUDIENCE_ALIASES.get(scope, ())):
            raise TokenBindingError('AUDIENCE_MISMATCH')
        return token


def validate_secret_reference(value):
    if (not isinstance(value, dict)
            or set(value) != {'vault_url', 'secret_name', 'secret_version', 'identity'}):
        raise ValueError('KEY_VAULT_VERSIONED_REFERENCE_REQUIRED')
    if not isinstance(value['vault_url'],str) or not re.fullmatch(r'https://[a-zA-Z0-9-]{3,24}\.vault\.azure\.net', value['vault_url']):
        raise ValueError('KEY_VAULT_HTTPS_ENDPOINT_REQUIRED')
    if not isinstance(value['secret_name'],str) or not re.fullmatch(r'[a-zA-Z0-9-]{1,127}', value['secret_name']):
        raise ValueError('KEY_VAULT_SECRET_NAME_INVALID')
    if not isinstance(value['secret_version'],str) or not re.fullmatch(r'[a-f0-9]{32}', value['secret_version']):
        raise ValueError('KEY_VAULT_SECRET_VERSION_REQUIRED')
    validate(value['identity'])
    return value


def secret(value, *, tokens=None, opener=None, gateway_identity=None):
    """Read exactly one versioned secret through the external-call gateway.

    The response is deliberately not an evidence read/tape event. Callers may
    record the reference and availability, never the returned secret.
    """
    validate_secret_reference(value)
    from metadata_auth import NoRedirect
    from ..live_gateway import open_http
    provider = tokens or Tokens(value['identity'])
    url = (value['vault_url'] + '/secrets/' + value['secret_name'] + '/'
           + value['secret_version'] + '?api-version=7.4')
    request = Request(url, method='GET', headers={
        'Authorization': 'Bearer ' + provider.get_token('https://vault.azure.net/.default')})
    try:
        with open_http(opener or build_opener(NoRedirect()), request,
                       timeout=30, identity=gateway_identity) as response:
            raw = response.read(32769)
        if len(raw) > 32768:
            raise ValueError('oversize')
        result = json.loads(raw)
        expected = url.split('?', 1)[0]
        if result.get('id') != expected or not isinstance(result.get('value'), str) or not result['value']:
            raise ValueError('binding')
        return result['value']
    except Exception:
        raise RuntimeError('KEY_VAULT_SECRET_UNAVAILABLE_OR_BINDING_MISMATCH') from None


@contextmanager
def model_session(settings):
    """Select one model credential for this task, without process-global secrets."""
    mode = settings.get('mode')
    if mode == 'managed_identity':
        credential = {k: settings[k] for k in FIELDS}
        validate(credential)
    elif mode == 'key_vault':
        credential = {'mode': mode, 'reference': settings['reference']}
        validate_secret_reference(credential['reference'])
    else:
        raise ValueError('CLOUD_MODEL_AUTHENTICATION_MODE_REQUIRED')
    endpoint = settings['endpoint']
    if not re.fullmatch(r'https://[a-zA-Z0-9-]+\.openai\.azure\.com/?', endpoint):
        raise ValueError('MODEL_ENDPOINT_INVALID')
    from investigator.provider_selection import DEPLOYMENT
    selection = MODEL_SESSION.set({'endpoint': endpoint, 'credential': credential})
    deployment = DEPLOYMENT.set(settings['deployment'])
    try:
        yield
    finally:
        DEPLOYMENT.reset(deployment)
        MODEL_SESSION.reset(selection)


def model_key(session):
    """OpenAI's Azure v1 client accepts a bearer token in its api_key argument."""
    credential = session['credential']
    if credential['mode'] == 'managed_identity':
        return Tokens(credential).get_token('https://cognitiveservices.azure.com/.default')
    import os
    return secret(credential['reference'],gateway_identity=os.environ.get('DIA_GATEWAY_MODEL_IDENTITY',''))

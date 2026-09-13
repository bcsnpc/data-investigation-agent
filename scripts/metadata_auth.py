"""Authentication and HTTP transport seams for metadata connectors.

Hosted callers can inject TokenProvider (for example an Azure Identity adapter).
The CLI factory currently uses the explicitly configured local Fabric CLI login.
"""
import base64
import contextlib
import io
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Protocol
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError


class TokenProvider(Protocol):
    def get_token(self, scope: str) -> str: ...


class AzureCredentialTokens:
    """Adapter for an injected Azure Identity credential; never constructs one implicitly."""
    def __init__(self, credential):
        self.credential = credential

    def get_token(self, scope):
        return self.credential.get_token(scope).token


class FabricCliTokens:
    def __init__(self, tenant):
        self.tenant = tenant.lower()
        self.cache = {}

    def get_token(self, scope):
        if scope not in self.cache:
            from fabric_cli.core.fab_auth import FabAuth
            with contextlib.redirect_stdout(io.StringIO()):
                token = FabAuth().get_access_token([scope], interactive_renew=False)
            if not token:
                raise RuntimeError('Authentication unavailable')
            # Token comes from MSAL, not user input; check the chosen tenant before use.
            payload = token.split('.')[1]
            claims = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))
            if claims.get('tid', '').lower() != self.tenant:
                raise RuntimeError('Authenticated tenant differs from configuration')
            self.cache[scope] = token
        return self.cache[scope]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class MetadataHttp:
    """Only metadata GET and getDefinition POST against fixed Microsoft endpoints."""
    SERVICES = {
        'fabric': ('https://api.fabric.microsoft.com/v1/', 'https://api.fabric.microsoft.com/.default'),
        'powerbi': ('https://api.powerbi.com/v1.0/myorg/', 'https://analysis.windows.net/powerbi/api/.default'),
        'onelake': ('https://onelake.table.fabric.microsoft.com/', 'https://storage.azure.com/.default'),
    }

    def __init__(self, tokens: TokenProvider, opener=None):
        self.tokens = tokens
        self.opener = opener or build_opener(NoRedirect())

    def __call__(self, endpoint, method='get', audience='fabric'):
        base, scope = self.SERVICES[audience]
        url = urlsplit(endpoint)
        if url.scheme or url.netloc or endpoint.startswith('/') or '..' in url.path.split('/'):
            raise ValueError('Expected a relative service endpoint')
        if method.lower() != 'get' and not (audience == 'fabric' and method.lower() == 'post' and url.path.endswith('/getDefinition')):
            raise ValueError('Metadata transport rejects mutations')
        request = Request(base + endpoint, method=method.upper(),
                          headers={'Authorization': 'Bearer ' + self.tokens.get_token(scope)})
        try:
            with self.opener.open(request, timeout=90) as response:
                body = response.read()
                return {'status_code': response.status, 'headers': dict(response.headers),
                        'text': json.loads(body) if body else {}}
        except HTTPError as exc:
            raise RuntimeError('Metadata HTTP status ' + str(exc.code)) from None


class WorkerTransport:
    """Development bridge: isolated CLI virtualenv, structured input, no tokens in output."""
    def __init__(self, python, tenant, worker):
        self.python, self.tenant, self.worker = python, tenant, str(worker)

    def invoke(self, request):
        request = dict(request, tenant=self.tenant)
        result = subprocess.run([self.python, self.worker], input=json.dumps(request),
                                capture_output=True, text=True, encoding='utf-8', timeout=360)
        if result.returncode:
            raise RuntimeError('Metadata authentication/transport worker failed')
        return json.loads(result.stdout)

    def __call__(self, endpoint, method='get', audience='fabric'):
        return self.invoke({'operation': 'request', 'endpoint': endpoint, 'method': method, 'audience': audience})

    def tables(self, workspace, item):
        return self.invoke({'operation': 'tables', 'workspace': workspace, 'item': item})


class PowerShellSqlCatalog:
    """Local DPAPI authentication adapter; the SQL connector only receives catalog data."""
    def __init__(self, script, credential_file, runner=subprocess.run):
        self.script, self.credential_file, self.runner = str(script), credential_file, runner

    def __call__(self, server, database, visibility_schema):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'catalog.json'
            result = self.runner(['powershell', '-NoProfile', '-File', self.script,
                '-Server', server, '-Database', database, '-VisibilitySchema', visibility_schema,
                '-CredentialPath', self.credential_file, '-OutputPath', str(output)],
                capture_output=True, timeout=240)
            if result.returncode:
                raise RuntimeError('SQL metadata connection failed')
            return json.loads(output.read_text(encoding='utf-8-sig'))

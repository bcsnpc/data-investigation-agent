"""Explicit platform credential implementation; no ambient chain."""
def credential_type():
    from azure.identity import ManagedIdentityCredential
    return ManagedIdentityCredential


def trust_roots():
    import certifi
    return certifi.where()

CREDENTIAL_PATH_WORDS = r"secret|secrets|credentials?|tokens?|azure|ssh|env"
FORBIDDEN_HTTP_SEGMENTS = {"permissions", "users", "share", "shares", "roleassignments", "xmla"}


class OwnerCliCredential:
    """Explicit existing CLI installation/profile. Token stays only in memory."""
    def __init__(self, python, tenant, subscription):
        from pathlib import Path
        if not Path(python).is_file() or not tenant or not subscription:
            raise ValueError('OWNER_CLI_IDENTITY_ARGUMENTS')
        self.python, self.tenant, self.subscription = str(python), tenant, subscription
        self.cached = None

    def get_token(self, *scopes, **kwargs):
        import json
        import subprocess
        import time
        from azure.core.credentials import AccessToken
        if scopes != ('https://storage.azure.com/.default',):
            raise ValueError('OWNER_CLI_STORAGE_SCOPE_ONLY')
        if self.cached is not None and self.cached.expires_on > time.time() + 120:
            return self.cached
        # Azure CLI rejects --tenant together with --subscription. Pin the
        # subscription in the request and verify BOTH returned identity fields.
        result = subprocess.run([self.python, '-m', 'azure.cli', 'account', 'get-access-token',
                   '--subscription', self.subscription, '--scope', scopes[0],
                   '--output', 'json', '--only-show-errors'], capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise RuntimeError('OWNER_CLI_TOKEN_REFUSED_EXIT_' + str(result.returncode))
        value = json.loads(result.stdout)
        if value.get('tenant') != self.tenant or value.get('subscription') != self.subscription:
            raise ValueError('OWNER_CLI_TOKEN_IDENTITY_DIFFERS')
        self.cached = AccessToken(value['accessToken'], int(value['expires_on']))
        return self.cached

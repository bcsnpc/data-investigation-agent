"""Azure CLI SQL tokens from an isolated, configured profile; no token exports.

The account and profile directory come from configuration. A profile is bound to
exactly one account: a session held by any other account is refused, and one
profile never falls back to another.
"""
import base64
import json
import os
from pathlib import Path
import subprocess
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
SQL_RESOURCE = 'https://database.windows.net/'


class SignInRequired(RuntimeError):
    """No usable session for the configured account in the configured profile."""
    def __init__(self, account, profile):
        super().__init__(f'Azure CLI sign-in required for {account} in profile {profile}')
        self.account, self.profile = account, profile


def profile_path(profile):
    """Profiles are local run artifacts: relative, and under `.local/` only."""
    if not isinstance(profile, str) or not profile or Path(profile).is_absolute():
        raise ValueError('SQL session profile must be a relative path')
    local = (ROOT/'.local').resolve()
    path = (ROOT/profile).resolve()
    if local not in path.parents:
        raise ValueError('SQL session profile must be under .local/')
    return path


def account_name(account):
    if (not isinstance(account, str) or not 3 <= len(account) <= 254 or account.count('@') != 1
            or any(c.isspace() or ord(c) < 32 for c in account)):
        raise ValueError('Expected SQL session account')
    return account


def cli(args, profile, interactive=False):
    env = dict(os.environ, AZURE_CONFIG_DIR=str(profile_path(profile)),
               AZURE_CORE_ENABLE_BROKER_ON_WINDOWS='false', AZURE_CORE_LOGIN_EXPERIENCE_V2='off')
    command = [str(ROOT/'.local/azure-cli-env/Scripts/python.exe'), '-m', 'azure.cli', *args]
    result = subprocess.run(command, env=env, text=True, capture_output=not interactive, timeout=360 if interactive else 90)
    if result.returncode:
        raise RuntimeError('Enterprise Azure CLI authentication unavailable')
    return None if interactive else json.loads(result.stdout)


def get_sql_token(tenant, account, profile):
    tenant, account = str(UUID(tenant)), account_name(account)
    if not profile_path(profile).is_dir():
        raise SignInRequired(account, profile)
    try:
        current = cli(['account', 'show', '--output', 'json', '--only-show-errors'], profile)
    except RuntimeError:
        raise SignInRequired(account, profile) from None
    if current.get('tenantId', '').lower() != tenant.lower() or current.get('user', {}).get('name', '').casefold() != account.casefold():
        raise RuntimeError('SQL profile account or tenant differs from configuration')
    try:
        result = cli(['account', 'get-access-token', '--tenant', tenant, '--resource', SQL_RESOURCE,
                      '--output', 'json', '--only-show-errors'], profile)
    except RuntimeError:
        raise SignInRequired(account, profile) from None
    token = result['accessToken']
    part = token.split('.')[1]
    claims = json.loads(base64.urlsafe_b64decode(part+'='*(-len(part)%4)))
    if claims.get('tid', '').lower() != tenant.lower() or claims.get('aud', '').rstrip('/') != SQL_RESOURCE.rstrip('/'):
        raise RuntimeError('SQL token tenant or audience mismatch')
    return token


def sign_in(tenant, account, profile):
    tenant = str(UUID(tenant))
    cli(['login', '--tenant', tenant, '--allow-no-subscriptions', '--scope', SQL_RESOURCE+'.default', '--output', 'none'],
        profile, interactive=True)
    get_sql_token(tenant, account, profile)


def session_status(tenant, account, profile):
    """Local check only (no token request): is the configured account signed in here?"""
    tenant, account = str(UUID(tenant)), account_name(account)
    if not profile_path(profile).is_dir():
        return {'status': 'SIGN_IN_REQUIRED', 'account': account, 'profile': profile}
    try:
        current = cli(['account', 'show', '--output', 'json', '--only-show-errors'], profile)
    except RuntimeError:
        return {'status': 'SIGN_IN_REQUIRED', 'account': account, 'profile': profile}
    if current.get('tenantId', '').lower() != tenant.lower() or current.get('user', {}).get('name', '').casefold() != account.casefold():
        return {'status': 'ACCOUNT_MISMATCH', 'account': account, 'profile': profile}
    return {'status': 'READY', 'account': account, 'profile': profile}

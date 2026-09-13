"""Azure CLI SQL tokens in an isolated enterprise profile; no token exports."""
import base64
import json
import os
from pathlib import Path
import subprocess
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
ACCOUNT = 'admin@skynwhy.com'
SQL_RESOURCE = 'https://database.windows.net/'


def cli(args, interactive=False):
    env = dict(os.environ, AZURE_CONFIG_DIR=str(ROOT/'.local/azure-fabric-sql'),
               AZURE_CORE_ENABLE_BROKER_ON_WINDOWS='false', AZURE_CORE_LOGIN_EXPERIENCE_V2='off')
    command = [str(ROOT/'.local/azure-cli-env/Scripts/python.exe'), '-m', 'azure.cli', *args]
    result = subprocess.run(command, env=env, text=True, capture_output=not interactive, timeout=360 if interactive else 90)
    if result.returncode:
        raise RuntimeError('Enterprise Azure CLI authentication unavailable')
    return None if interactive else json.loads(result.stdout)


def get_sql_token(tenant):
    tenant = str(UUID(tenant))
    account = cli(['account', 'show', '--output', 'json', '--only-show-errors'])
    if account.get('tenantId', '').lower() != tenant.lower() or account.get('user', {}).get('name', '').casefold() != ACCOUNT.casefold():
        raise RuntimeError('Enterprise SQL profile account or tenant mismatch')
    result = cli(['account', 'get-access-token', '--tenant', tenant, '--resource', SQL_RESOURCE, '--output', 'json', '--only-show-errors'])
    token = result['accessToken']
    part = token.split('.')[1]
    claims = json.loads(base64.urlsafe_b64decode(part+'='*(-len(part)%4)))
    if claims.get('tid', '').lower() != tenant.lower() or claims.get('aud', '').rstrip('/') != SQL_RESOURCE.rstrip('/'):
        raise RuntimeError('SQL token tenant or audience mismatch')
    return token


def sign_in(tenant):
    tenant = str(UUID(tenant))
    cli(['login', '--tenant', tenant, '--allow-no-subscriptions', '--scope', SQL_RESOURCE+'.default', '--output', 'none'], interactive=True)
    get_sql_token(tenant)

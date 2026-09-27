"""Validated, secret-free connection configuration. Paths are repository-relative."""
import json
import re
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]


def keys(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError('Unexpected or missing configuration fields')


def text(value):
    if not isinstance(value, str) or not value.strip() or '\x00' in value:
        raise ValueError('Expected a nonempty configuration string')
    return value


def load_config(path):
    config = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    keys(config, ['version', 'sql', 'fabric', 'storage'])
    if config['version'] != 1:
        raise ValueError('Unsupported configuration version')
    sql, fabric = config['sql'], config['fabric']
    keys(sql, ['server', 'database', 'visibility_schema', 'auth'])
    if not re.fullmatch(r'[A-Za-z0-9.-]+', text(sql['server'])):
        raise ValueError('SQL server must be a hostname')
    text(sql['database']); text(sql['visibility_schema'])
    keys(sql['auth'], ['mode', 'credential_file'])
    if sql['auth']['mode'] != 'dpapi_file':
        raise ValueError('Unsupported SQL authentication mode')
    optional = [k for k in ('native_reader', 'sql_session', 'sql_reader', 'xmla_client', 'refresh_timing_reader') if k in fabric]
    keys(fabric, ['workspace_id', 'auth'] + optional)
    fabric['workspace_id'] = str(UUID(text(fabric['workspace_id'])))
    keys(fabric['auth'], ['mode', 'tenant_id', 'python'])
    if fabric['auth']['mode'] != 'fabric_cli':
        raise ValueError('Unsupported Fabric authentication mode')
    fabric['auth']['tenant_id'] = str(UUID(text(fabric['auth']['tenant_id'])))
    if 'native_reader' in fabric:
        from investigator.native_identity import profile
        profile(fabric['native_reader'])
        if fabric['native_reader']['tenant_id'] != fabric['auth']['tenant_id']:
            raise ValueError('Native reader and metadata tenant differ')
    if 'xmla_client' in fabric:
        # A second interface to the semantic surface, for specific failures only.
        keys(fabric['xmla_client'], ['library'])
        from fabric_sql_auth import profile_path
        profile_path(fabric['xmla_client']['library'])
        if 'native_reader' not in fabric:
            raise ValueError('XMLA failure detail requires the native reader identity')
    if 'refresh_timing_reader' in fabric:
        from fabric_sql_auth import account_name,profile_path
        timing=fabric['refresh_timing_reader']
        keys(timing,['account','profile'])
        account_name(timing['account']);profile_path(timing['profile'])
        if any(timing['account'].casefold()==fabric.get(k,{}).get('account','').casefold() for k in ('native_reader','sql_reader')):
            raise ValueError('Optional refresh metadata identity must be distinct from the execution reader')
        if any(timing['profile']==fabric.get(k,{}).get('profile') for k in ('sql_reader','sql_session')):
            raise ValueError('Refresh metadata must use a separate identity profile')
    for name in ('sql_session', 'sql_reader'):
        # Azure CLI SQL sessions: one account per isolated profile under .local/.
        if name in fabric:
            from fabric_sql_auth import account_name, profile_path
            section = fabric[name]
            keys(section, ['account', 'profile'] + (['server'] if name == 'sql_reader' else []))
            account_name(section['account']); profile_path(section['profile'])
            if name == 'sql_reader' and not re.fullmatch(r'[A-Za-z0-9.-]+', text(section['server'])):
                raise ValueError('SQL reader server must be a hostname')
    if 'sql_session' in fabric and 'sql_reader' in fabric and (
            fabric['sql_session']['profile'] == fabric['sql_reader']['profile']):
        raise ValueError('SQL reader and SQL session must use separate profiles')
    keys(config['storage'], ['database'])
    for section, key in [(sql['auth'], 'credential_file'), (fabric['auth'], 'python'), (config['storage'], 'database')]:
        section[key] = str((ROOT / text(section[key])).resolve())
    return config

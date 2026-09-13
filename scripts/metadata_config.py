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
    keys(fabric, ['workspace_id', 'auth'])
    fabric['workspace_id'] = str(UUID(text(fabric['workspace_id'])))
    keys(fabric['auth'], ['mode', 'tenant_id', 'python'])
    if fabric['auth']['mode'] != 'fabric_cli':
        raise ValueError('Unsupported Fabric authentication mode')
    fabric['auth']['tenant_id'] = str(UUID(text(fabric['auth']['tenant_id'])))
    keys(config['storage'], ['database'])
    for section, key in [(sql['auth'], 'credential_file'), (fabric['auth'], 'python'), (config['storage'], 'database')]:
        section[key] = str((ROOT / text(section[key])).resolve())
    return config

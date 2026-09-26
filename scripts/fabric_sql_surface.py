"""The Fabric SQL analytics endpoint as an execution surface: its self-report.

This module only asks the endpoint who it is serving and which database. It
accepts no query text. Reads of data go through the compile-and-admit path.
The reader session comes from `fabric.sql_reader`. It never falls back to the
publisher session: a missing session is an explicit unavailability that names
the sign-in required.
"""
import json
import re
import subprocess

from fabric_sql_auth import ROOT, SignInRequired, get_sql_token

ENGINE = 'FABRIC_SQL'
SCRIPT = ROOT/'infra/scripts/Read-FabricSqlSurface.ps1'


def database_name(database):
    """Every connection names its database; relying on the endpoint default is a defect."""
    if not isinstance(database, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', database):
        raise ValueError('An explicit database name is required')
    return database


def declared(reader, database):
    return {'engine': ENGINE, 'connection': 'sql://'+reader['server'], 'object': database_name(database),
            'identity': reader['account']}


def self_report(config, database, *, token=get_sql_token, run=subprocess.run):
    """Return the declared surface and the surface's own answer about itself."""
    database = database_name(database)
    reader = config['fabric'].get('sql_reader')
    if reader is None:
        return {'status': 'UNAVAILABLE', 'reason': 'SQL_READER_NOT_CONFIGURED', 'execution_surface': None,
                'surface_report': None}
    surface = declared(reader, database)
    try:
        access = token(config['fabric']['auth']['tenant_id'], reader['account'], reader['profile'])
    except SignInRequired as exc:
        return {'status': 'UNAVAILABLE', 'reason': 'SIGN_IN_REQUIRED', 'execution_surface': surface,
                'surface_report': None, 'account': exc.account, 'profile': exc.profile,
                'sign_in': 'python scripts/connect_fabric_sql.py --config <config> --session sql_reader'}
    except Exception as exc:
        return {'status': 'UNAVAILABLE', 'reason': 'TOKEN_UNAVAILABLE', 'error_type': type(exc).__name__,
                'execution_surface': surface, 'surface_report': None}
    payload = json.dumps({'server': reader['server'], 'database': database, 'access_token': access})
    access = None
    completed = run(['powershell', '-NoProfile', '-NonInteractive', '-File', str(SCRIPT)], input=payload,
                    capture_output=True, text=True, encoding='utf-8', timeout=120)
    try:
        answer = json.loads(completed.stdout)
    except (TypeError, ValueError):
        answer = {'status': 'UNAVAILABLE', 'stage': 'response', 'error_type': 'InvalidResponse'}
    if completed.returncode or answer.get('status') != 'REACHABLE':
        return {'status': 'UNAVAILABLE', 'reason': 'SURFACE_UNREACHABLE', 'execution_surface': surface,
                'surface_report': None, **{k: answer.get(k) for k in ('stage', 'error_type', 'sql_error_number')}}
    report = {'identity': answer.get('login_name'), 'object': answer.get('database_name')}
    return {'status': 'REACHABLE', 'reason': None, 'execution_surface': surface,
            'surface_report': report if all(isinstance(v, str) and v for v in report.values()) else None}

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
import sys

from fabric_sql_auth import ROOT, SignInRequired, get_sql_token

ENGINE = 'FABRIC_SQL'
SCRIPT = ROOT/'infra/scripts/Read-FabricSqlSurface.ps1'


from investigator.adapters.sql_principal import expected as sql_principal


def database_name(database):
    """Every connection names its database; relying on the endpoint default is a defect."""
    if not isinstance(database, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', database):
        raise ValueError('An explicit database name is required')
    return database


def declared(reader, database):
    return {'engine': ENGINE, 'connection': 'sql://'+reader['server'], 'object': database_name(database),
            'identity': sql_principal(reader)}


def reader_availability(config):
    """Configuration availability only; a cloud credential is not a signed-in receipt."""
    reader=config['fabric'].get('sql_reader')
    if not reader:return None
    if reader.get('mode') in ('managed_identity','key_vault_user_cache','federated_reader'):
        from investigator.adapters.vault_user_cache import credential, SQL
        auth=credential(reader)
        if auth['tenant_id']!=config['fabric']['auth']['tenant_id']:
            raise ValueError('SQL reader tenant differs')
        if auth['mode']=='key_vault_user_cache' and auth['scope']!=SQL:
            raise ValueError('SQL reader audience differs')
        return {'status':'CONFIGURED','account':reader['account'],
                'authentication_verified':False,'permission_verified':False,
                'limitation':'Credential declaration only; authentication and guarded surface reads remain to be established.'}
    from fabric_sql_auth import session_status
    return session_status(config['fabric']['auth']['tenant_id'],reader['account'],reader['profile'])


def self_report(config, database, *, token=get_sql_token, run=subprocess.run):
    """Return the declared surface and the surface's own answer about itself."""
    database = database_name(database)
    reader = config['fabric'].get('sql_reader')
    if reader is None:
        return {'status': 'UNAVAILABLE', 'reason': 'SQL_READER_NOT_CONFIGURED', 'execution_surface': None,
                'surface_report': None}
    surface = declared(reader, database)
    if reader.get('mode') in ('managed_identity','key_vault_user_cache','federated_reader'):
        from investigator.adapters.vault_user_cache import credential
        from investigator.physical_reads import run as physical_run
        payload = {'server':reader['server'],'database':database,'control_mode':'SELF_REPORT',
                   'authentication':credential(reader)}
        completed = physical_run([sys.executable,str(ROOT/'scripts/managed_sql_worker.py')],
            input=json.dumps(payload), timeout=120, fallback=run, capture_output=True,text=True,encoding='utf-8')
        try:
            answer = json.loads(completed.stdout)
        except (TypeError,ValueError):
            answer = {}
        if completed.returncode or answer.get('status') != 'REACHABLE':
            return {'status':'UNAVAILABLE','reason':'SURFACE_UNREACHABLE','execution_surface':surface,'surface_report':None}
        return {'status':'REACHABLE','reason':None,'execution_surface':surface,
                'surface_report':{'identity':answer['login_name'],'object':answer['database_name']}}
    from investigator.live_gateway import authorize_sql_control
    authorize_sql_control(reader['server'],database,'SELF_REPORT')
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
            'surface_report': report}


READ_SCRIPT = ROOT/'infra/scripts/Read-FabricSqlAggregate.ps1'


class LowerReadError(RuntimeError):
    """A failed compiled read. Carries no exception text."""
    def __init__(self, stage=None, number=None, kind=None):
        super().__init__('Fabric SQL read unavailable')
        self.stage = stage if stage in ('setup', 'connect', 'query', 'token', 'response') else None
        self.error_number = number if type(number) is int else None
        self.error_kind = kind if kind in ('SqlException', 'InvalidOperationException', 'MethodException', 'ArgumentException') else 'TransportError'


def read(config, database, request, *, token=get_sql_token, run=subprocess.run, attestation=True):
    """Execute one compiled, admitted request as the configured reader.

    The request comes from the admission path. This function adds only the
    connection: the reader's token, the endpoint, and the always-named database.
    """
    database = database_name(database)
    reader = config['fabric'].get('sql_reader')
    if reader is None:
        raise LowerReadError('setup')
    if reader.get('mode') in ('managed_identity','key_vault_user_cache','federated_reader'):
        return _managed_read(config, database, request, reader, run,attestation=attestation)
    try:
        access = token(config['fabric']['auth']['tenant_id'], reader['account'], reader['profile'])
    except SignInRequired:
        raise LowerReadError('token') from None
    payload = json.dumps({'server': reader['server'], 'database': database, 'access_token': access,
                          'query': request['query'], 'parameters': request.get('parameters', []),
                          'read_only_objects': request['read_only_objects'], 'max_rows': request['max_rows'],
                          'result_columns': request['result_columns']})
    access = None
    from investigator.physical_reads import run as physical_run
    from sql_layer_policy import policy as layer_policy
    completed = physical_run(['powershell', '-NoProfile', '-NonInteractive', '-File', str(READ_SCRIPT)], fallback=run, input=payload,
                    capture_output=True, text=True, encoding='utf-8',
                    timeout=layer_policy(config,request,default_timeout=150)['worker_timeout_seconds'])
    try:
        answer = json.loads(completed.stdout)
    except (TypeError, ValueError):
        raise LowerReadError('response') from None
    if completed.returncode or not isinstance(answer, dict) or answer.get('error'):
        raise LowerReadError(answer.get('stage') if isinstance(answer, dict) else None,
                             answer.get('error_number') if isinstance(answer, dict) else None,
                             answer.get('error_kind') if isinstance(answer, dict) else None)
    return answer


def _managed_read(config, database, request, reader, fallback,*,attestation=True):
    from investigator.adapters.vault_user_cache import credential
    from investigator.physical_reads import run as physical_run
    from sql_layer_policy import policy as layer_policy
    payload = {key:request[key] for key in ('query','read_only_objects','max_rows','result_columns')}
    payload.update(parameters=request.get('parameters',[]),server=reader['server'],database=database,
                   authentication=credential(reader),require_read_only=True)
    if attestation:payload['surface_kind']='FABRIC_SQL'
    completed = physical_run([sys.executable,str(ROOT/'scripts/managed_sql_worker.py')],input=json.dumps(payload),
        timeout=layer_policy(config,request,default_timeout=150)['worker_timeout_seconds'],fallback=fallback,
        capture_output=True,text=True,encoding='utf-8')
    try:
        answer=json.loads(completed.stdout)
    except (TypeError,ValueError):
        raise LowerReadError('response') from None
    if completed.returncode or not isinstance(answer,dict) or answer.get('error'):
        detail=answer if isinstance(answer,dict) else {}
        raise LowerReadError(detail.get('stage'),detail.get('error_number'),detail.get('error_kind'))
    return answer

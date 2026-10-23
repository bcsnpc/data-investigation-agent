"""Bounded MI-only ODBC worker; mirrors the guarded PowerShell read protocol.

Only public identity coordinates cross stdin/tapes. The access token exists
inside this process, is never a connection-string field, and is never printed.
"""
import datetime
from decimal import Decimal
import json
import re
import struct
import sys
from contextlib import contextmanager
from threading import Event, RLock, Thread

from investigator.adapters.managed_identity import FIELDS, Tokens, validate

DB_GUARD = """SELECT COUNT(*) FROM sys.fn_my_permissions(NULL,'DATABASE')
WHERE permission_name NOT IN ('CONNECT','SELECT','VIEW DEFINITION','VIEW DATABASE STATE',
'VIEW DATABASE PERFORMANCE STATE','VIEW DATABASE SECURITY STATE')"""
OBJECT_GUARD = """SELECT COUNT(*) FROM sys.fn_my_permissions(?,'OBJECT')
WHERE permission_name NOT IN ('SELECT','VIEW DEFINITION')"""
IDENTITY = 'SELECT SUSER_SNAME() AS login_name, DB_NAME() AS database_name'
TYPES = {str:'String', int:'Int64', float:'Double', Decimal:'Decimal', bool:'Boolean',
         datetime.datetime:'DateTime', datetime.date:'DateTime', bytes:'Byte[]'}


class Protocol:
    def __init__(self, metered=False, source=None, sink=None):
        self.metered = metered
        self.source, self.sink = source or sys.stdin, sink or sys.stdout
        self.lock=RLock()
        self.last_action=None

    def emit(self, value):
        with self.lock:
            self.sink.write(json.dumps(value, separators=(',', ':')) + '\n')
            self.sink.flush()

    @contextmanager
    def lifecycle(self,progress,interval=10):
        if not self.metered:
            yield
            return
        import os
        stop=Event()
        def frame(event):
            self.emit({'worker_event':event,'pid':os.getpid(),
                       'last_action':self.last_action or progress['stage']})
        def heartbeat():
            while not stop.wait(interval):
                try:frame('HEARTBEAT')
                except OSError:return
        frame('START')
        worker=Thread(target=heartbeat,daemon=True);worker.start()
        try:yield
        finally:
            stop.set();worker.join(timeout=1);frame('EXIT')

    def before(self, kind, obj=None, guard=False):
        self.last_action=kind
        if not self.metered:
            return True
        self.emit({'physical_read':'REQUEST','kind':kind,
                   **({'cache_guard':True, 'object':obj} if guard else {})})
        decision = self.source.readline().strip()
        if decision == 'REUSE' and guard:
            return False
        if decision != 'ALLOW':
            raise ValueError('Physical read not admitted')
        return True

    def done(self, kind, guard=False):
        if self.metered:
            self.emit({'physical_read':'DONE','kind':kind,'status':'AVAILABLE',
                       **({'guard_passed':True} if guard else {})})


def bind_parameters(query, parameters):
    """Replace compiler @parameters outside SQL quoted tokens, never literals."""
    values = {}
    for item in parameters:
        name = item.get('name', '')
        if not re.fullmatch(r'@[A-Za-z][A-Za-z0-9_]*', name) or name in values:
            raise ValueError('Invalid parameter')
        value = item.get('value')
        if value is not None and (not isinstance(value, (str, int, float, bool)) or len(str(value)) > 200):
            raise ValueError('Parameter outside bounds')
        values[name] = None if value is None else str(value)
    # Quoted string/identifier tokens precede variable tokens, including escapes.
    tokens = re.compile(r"N?'(?:''|[^'])*'|\[(?:\]\]|[^\]])*\]|\"(?:\"\"|[^\"])*\"|@@\w+|@[A-Za-z][A-Za-z0-9_]*")
    ordered, used = [], set()
    def replace(match):
        token = match.group()
        if token.startswith('@') and not token.startswith('@@'):
            if token not in values:
                raise ValueError('Unbound parameter')
            ordered.append(values[token]); used.add(token)
            return '?'
        return token
    result = tokens.sub(replace, query)
    if used != set(values):
        raise ValueError('Unused parameter')
    return result, ordered


def _connection_string(payload):
    server, database = payload['server'], payload['database']
    if not isinstance(server, str) or not re.fullmatch(r'[A-Za-z0-9.-]+', server):
        raise ValueError('Invalid server')
    if not isinstance(database, str) or not 1 <= len(database) <= 128 or any(ord(c) < 32 for c in database):
        raise ValueError('Invalid database')
    return ('DRIVER={ODBC Driver 18 for SQL Server};SERVER=tcp:' + server + ',1433;DATABASE={' +
            database.replace('}', '}}') + '};Encrypt=yes;TrustServerCertificate=no;ApplicationIntent=ReadOnly;')


def execute(payload, *, connect=None, tokens=None, protocol=None, progress=None):
    from investigator.live_gateway import authorize_sql_payload, authorize_sql_control
    protocol = protocol or Protocol()
    progress = progress if progress is not None else {}
    progress['stage'] = 'setup'
    from investigator.adapters.vault_user_cache import MODE, validate as user_validate, provider
    from investigator.adapters.federated_reader import validate as federated_validate
    auth = (federated_validate if payload['authentication'].get('mode') == 'federated_reader' else user_validate if payload['authentication'].get('mode') == MODE else validate)(payload['authentication'])
    connection_string = _connection_string(payload)
    control = payload.get('control_mode')
    if control:
        if control not in ('PREWARM', 'SELF_REPORT'):
            raise ValueError('Unsupported SQL control')
        authorize_sql_control(payload['server'], payload['database'], control)
    else:
        payload = authorize_sql_payload(payload)
        if payload.get('require_read_only') is not True or not 1 <= len(payload.get('read_only_objects', [])) <= 24:
            raise ValueError('Read-only object guards required')
        if type(payload.get('max_rows')) is not int or not 2 <= payload['max_rows'] <= 251:
            raise ValueError('Row bound required')
        if not 1 <= len(payload.get('result_columns', [])) <= 16:
            raise ValueError('Result columns required')
    if connect is None:
        import pyodbc
        pyodbc.pooling = False  # No cross-run connection/permission state.
        connect = pyodbc.connect
    progress['stage'] = 'token'
    token = (tokens or provider(auth)).get_token('https://database.windows.net/.default').encode('utf-16-le')
    packed = struct.pack('<I', len(token)) + token
    progress['stage'] = 'connect'
    connection = connect(connection_string, attrs_before={1256:packed, 101:1}, timeout=30, autocommit=True)
    del token, packed
    try:
        connection.timeout = 30
        if control == 'PREWARM':
            return {'status':'CONNECTED','stage':'connect'}
        progress['stage'] = 'query'
        cursor = connection.cursor()
        try:
            protocol.before('sql_identity')
            cursor.execute(IDENTITY)
            identity = cursor.fetchone()
            if not identity or cursor.fetchone() is not None or cursor.nextset():
                raise ValueError('Invalid identity response')
            if identity[1] != payload['database'] or not identity[0]:
                raise ValueError('Database/identity binding failed')
            protocol.done('sql_identity')
            if control == 'SELF_REPORT':
                return {'status':'REACHABLE','login_name':str(identity[0]),'database_name':str(identity[1])}
            for kind, obj, query, args in [('sql_database_permissions', None, DB_GUARD, [])] + [
                    ('sql_object_permissions', obj, OBJECT_GUARD, [obj]) for obj in payload['read_only_objects']]:
                if protocol.before(kind, obj, guard=True):
                    cursor.execute(query, *args)
                    row = cursor.fetchone()
                    if not row or row[0] != 0 or cursor.fetchone() is not None or cursor.nextset():
                        raise ValueError('Read-only permission guard refused')
                    protocol.done(kind, guard=True)
            query, values = bind_parameters(payload['query'], payload.get('parameters', []))
            columns = payload['result_columns']
            fabric = payload.get('surface_kind') == 'FABRIC_SQL'
            if fabric:
                query = ("SELECT q.*, SUSER_SNAME() AS __surface_identity, DB_NAME() AS __surface_object, "
                         "LEFT(@@VERSION, CHARINDEX(' (', @@VERSION) - 1) AS __surface_engine FROM (" + query + ') AS q')
            protocol.before('sql_quantity')
            cursor.execute(query, *values)
            protocol.done('sql_quantity')
            expected = columns + (['__surface_identity','__surface_object','__surface_engine'] if fabric else [])
            if [col[0] for col in cursor.description] != expected:
                raise ValueError('Unexpected columns')
            types = {col[0]:TYPES.get(col[1], 'Unknown') for col in cursor.description[:len(columns)]}
            rows, reports = [], []
            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                if len(rows) >= payload['max_rows']:
                    raise ValueError('Row cap exceeded')
                formatted = [None if v is None else str(v) for v in row]
                if any(v is not None and len(v) > 1000 for v in formatted):
                    raise ValueError('Value cap exceeded')
                rows.append(dict(zip(columns, formatted)))
                if fabric:
                    report = dict(zip(('identity','object','engine'), formatted[-3:]))
                    if report['object'] != payload['database'] or not all(report.values()) or (reports and report != reports[0]):
                        raise ValueError('Query surface binding failed')
                    reports.append(report)
            if cursor.nextset():
                raise ValueError('Unexpected extra result')
            result = {'rows':rows,'column_types':types,'read_only_verified':True,
                      'execution_identity':{'principal':str(identity[0]),'server':payload['server'],
                      'database':payload['database'],'provenance':'TRANSPORT_PERMISSION_CHECK'}}
            if fabric:
                result.update(surface_report=reports[0] if reports else None, surface_report_binding='VALUE_QUERY')
                if reports:
                    result['execution_identity'].update(principal=reports[0]['identity'],provenance='SURFACE_SELF_REPORT')
            return result
        finally:
            cursor.close()
    finally:
        connection.close()


def main():
    protocol = Protocol('--metered' in sys.argv)
    progress = {'stage':'setup'}
    code=0
    with protocol.lifecycle(progress):
        try:
            payload = json.loads(sys.stdin.readline(2*1024*1024))
            result = execute(payload, protocol=protocol, progress=progress)
        except Exception as exc:
            # Preserve numeric SQL error and SQLSTATE, never driver text/token/query.
            args = getattr(exc, 'args', ())
            sqlstate = args[0] if args and re.fullmatch(r'[A-Z0-9]{5}', str(args[0])) else None
            numbers = re.findall(r'\((-?\d+)\)', str(args[1])) if len(args)>1 else []
            result={'error':'ManagedSqlReadFailed','stage':progress['stage'],
                    'error_number':(-2 if sqlstate in ('HYT00','HYT01') else int(numbers[-1]) if numbers else None),
                    'error_kind':'SqlException' if sqlstate else 'InvalidOperationException','sqlstate':sqlstate}
            code=1
    protocol.emit(result)
    return code


if __name__ == '__main__':
    raise SystemExit(main())

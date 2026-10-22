"""Small, harmless reader probes through the existing gateway and meters.

No az sign-in, owner fallback, role operation, model dispatch or arbitrary SQL.
Bindings are deployment-owned references, never supplied by a model.
"""
import hashlib
import json
from urllib.request import Request, build_opener


class NotTestable(RuntimeError):
    pass


class ProbeFailure(RuntimeError):
    def __init__(self, reason):
        self.safe_reason = reason
        super().__init__(reason)


class LiveProbes:
    def __init__(self, bindings, *, http=None, sql=None):
        self.bindings, self.http, self.sql = bindings, http, sql
        self.meter = None

    def close(self):
        if self.meter is not None:
            self.meter.close()

    def _count(self, callback):
        from scan_estate_graph import Meter
        from ..shared_state import configured_state
        if self.meter is None:
            state = configured_state()
            if state is None or 'budget' not in self.bindings:
                raise NotTestable('SHARED_REQUEST_BUDGET_NOT_BOUND')
            self.meter = Meter(state, self.bindings['budget'], 100)
        return self.meter(callback)

    def probe(self, row, identity):
        spec = row['probe']
        if spec.get('kind') == 'not_testable':
            raise NotTestable(spec['reason'])
        binding = self.bindings.get('probes', {}).get(row['id'])
        if not binding:
            raise NotTestable('NO_ACTUAL_IDENTITY_PROBE_BINDING')
        authentication = self.bindings.get('identities', {}).get(row['identity'])
        if (not authentication or not identity.get('principal_id')
                or authentication.get('principal_id') != identity['principal_id']):
            raise ProbeFailure('ACTUAL_IDENTITY_BINDING_MISMATCH')
        # Managed/federated providers verify the audience, tenant and principal
        # of the actual token; no DeveloperCredential or CLI fallback exists.
        if authentication.get('mode') not in ('managed_identity', 'federated_reader'):
            raise NotTestable('IDENTITY_AUTHENTICATION_MODE_NOT_SUPPORTED_BY_ACCESS_PROBE')
        kind = spec.get('kind')
        if kind == 'http':
            result = self._http(binding, authentication)
        elif kind == 'sql':
            result = self._sql(binding, authentication)
        elif kind == 'sql_object':
            result = self._sql_object(binding, authentication)
        elif kind == 'postgres':
            result = self._postgres(binding, authentication)
        else:
            raise NotTestable('NO_HARMLESS_PROBE_IMPLEMENTED_FOR_THIS_ACTION')
        return {'identity': row['identity'], 'resource': row['resource'], 'permission_observed': True,
                'principal_id': identity['principal_id'], 'receipt': result,
                'limitation': spec.get('limitation', 'Proves this bounded read only; no write or admin grant inferred.')}

    def _http(self, binding, authentication):
        from .vault_user_cache import provider
        from ..live_gateway import open_http
        from metadata_auth import NoRedirect
        method = binding.get('method', 'GET')
        # POST is restricted to a single constant DAX health read; no refresh,
        # run, connection test, create or permission endpoint is accepted.
        body = None
        url = binding['url']
        from urllib.parse import urlsplit
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.username or parsed.password:
            raise ProbeFailure('ACCESS_PROBE_HTTPS_ENDPOINT_REQUIRED')
        if parsed.hostname.endswith('.vault.azure.net') and '/secrets/' in parsed.path and not parsed.path.endswith('/versions'):
            raise ProbeFailure('ACCESS_PROBE_SECRET_VALUE_READ_REFUSED')
        if method == 'POST':
            if not url.endswith('/executeQueries'):
                raise ProbeFailure('ACCESS_PROBE_MUTATION_REFUSED')
            body = json.dumps({'queries': [{'query': 'EVALUATE ROW("access_check",1)'}],
                               'serializerSettings': {'includeNulls': True}}).encode()
        elif method != 'GET':
            raise ProbeFailure('ACCESS_PROBE_MUTATION_REFUSED')
        token = provider(authentication).get_token(binding['scope'])
        headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', **binding.get('headers', {})}
        # Caller may not replace the identity-bearing header.
        headers['Authorization'] = 'Bearer ' + token
        request = Request(url, data=body, method=method, headers=headers)
        def send():
            with open_http(self.http or build_opener(NoRedirect()), request, timeout=30,
                           identity=binding['channel']) as response:
                raw = response.read(1048577)
                status = getattr(response, 'status', 200)
            if len(raw) > 1048576:
                raise ProbeFailure('ACCESS_PROBE_RESPONSE_TOO_LARGE')
            if not 200 <= status < 300:
                raise ProbeFailure('HTTP_' + str(status))
            value = json.loads(raw) if raw else {}
            if isinstance(value, dict) and ('error' in value or value.get('results') and any('error' in r for r in value['results'])):
                raise ProbeFailure('PROVIDER_REPORTED_ERROR')
            for dotted, expected in binding.get('expect', {}).items():
                actual = value
                for part in dotted.split('.'):
                    actual = actual.get(part) if isinstance(actual, dict) else None
                if actual != expected:
                    raise ProbeFailure('DECLARED_RESOURCE_SETTING_DIFFERS')
            # Raw bodies (especially Key Vault) must never enter a receipt.
            return {'transport': 'HTTP', 'status': status, 'response_sha256': hashlib.sha256(raw).hexdigest()}
        return self._count(send)

    def _sql(self, binding, authentication):
        from fabric_sql_surface import self_report
        # A SQL self-report is a bounded gateway-controlled metadata read. It
        # proves connection/login only, not SELECT on arbitrary tables.
        reader = {**authentication, 'account': binding['account'], 'server': binding['server']}
        config = {'fabric': {'auth': {'tenant_id': authentication['tenant_id']}, 'sql_reader': reader}}
        from ..physical_reads import scope
        def execute():
            with scope(lambda kind, fn: self._count(fn)):
                return (self.sql or self_report)(config, binding['database'])
        result = self._count(execute)
        if result.get('status') != 'REACHABLE':
            raise ProbeFailure(result.get('reason', 'SQL_UNREACHABLE'))
        from fabric_sql_surface import declared
        expected = declared(reader, binding['database'])
        if result.get('surface_report') != {'identity': expected['identity'], 'object': expected['object']}:
            raise ProbeFailure('SQL_SERVED_IDENTITY_OR_DATABASE_DIFFERS')
        return {'transport': 'SQL_SELF_REPORT', 'surface_report': result['surface_report'],
                'limitation': 'Connection and login only, not table SELECT permission.'}

    def _sql_object(self, binding, authentication):
        import re
        from ..daily_smoke import _gold_read
        from .sql_principal import expected
        from ..physical_reads import scope
        obj = binding['object']
        if not re.fullmatch(r'\[[A-Za-z_][A-Za-z0-9_]*\]\.\[[A-Za-z_][A-Za-z0-9_]*\]', obj):
            raise ProbeFailure('ACCESS_PROBE_OBJECT_IDENTIFIER_INVALID')
        payload = {'server': binding['server'], 'database': binding['database'], 'authentication': authentication,
                   'query': 'SELECT TOP (1) 1 AS access_check FROM ' + obj,
                   'read_only_objects': [obj], 'result_columns': ['access_check'],
                   'max_rows': 1, 'require_read_only': True}
        def execute():
            with scope(lambda kind, fn: self._count(fn)):
                return _gold_read(payload)
        result = self._count(execute)
        observed = result['execution_identity']
        if (observed.get('principal') != expected({**authentication, 'account': binding['account']})
                or observed.get('server') != binding['server'] or observed.get('database') != binding['database']):
            raise ProbeFailure('SQL_SERVED_IDENTITY_OR_DATABASE_DIFFERS')
        return {'transport': 'GUARDED_SQL', 'execution_identity': observed, 'object': obj,
                'read_only_verified': True}

    def _postgres(self, binding, authentication):
        # Exactly this constant privilege query under a read-only transaction;
        # no migration, role grant, owner login or mutating no-op is executed.
        import re
        from .vault_user_cache import provider
        from ..postgres_connection import connect
        from .platform_credentials import trust_roots
        from ..live_gateway import authorize_platform_database
        if authentication['mode'] != 'managed_identity':
            raise ProbeFailure('POSTGRES_REQUIRES_WORKER_MANAGED_IDENTITY')
        table = binding['table']
        if not re.fullmatch(r'dia_state\.[a-z_]+', table):
            raise ProbeFailure('POSTGRES_PLATFORM_TABLE_REQUIRED')
        privilege = binding.get('privilege', 'SELECT')
        if privilege not in ('SELECT', 'INSERT', 'UPDATE', 'DELETE'):
            raise ProbeFailure('POSTGRES_PRIVILEGE_NOT_DECLARED')
        authorize_platform_database(binding['channel'], binding['host'], binding['database'])
        password = provider(authentication).get_token('https://ossrdbms-aad.database.windows.net/.default')
        with connect(host=binding['host'], dbname=binding['database'], user=binding['user'], password=password,
                     sslmode='verify-full', sslrootcert=trust_roots(), connect_timeout=15, autocommit=True,
                     options='-c default_transaction_read_only=on -c statement_timeout=15000') as db:
            query = "SELECT current_database(), current_user, current_setting('transaction_read_only'), has_table_privilege(current_user,%s,%s)"
            answer = db.execute(query, (table, privilege)).fetchone()
        if (answer[0] != binding['database'] or answer[1] != binding['user'] or answer[2] != 'on'
                or answer[3] is not True):
            raise ProbeFailure('POSTGRES_IDENTITY_OR_PRIVILEGE_DIFFERS')
        return {'transport': 'POSTGRES_PLATFORM_CONTROL', 'statement': query, 'parameters': [table, privilege],
                'database': answer[0], 'current_user': answer[1], 'transaction_read_only': answer[2],
                'privilege_observed': answer[3]}

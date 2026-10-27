"""Versioned shared application state. SQLite is an explicit offline backend.

No estate data connector lives here. PostgreSQL transactions serialize budget
admission and revision changes; there is no SQL-dialect rewriting layer.
"""
from contextlib import contextmanager, closing
from contextvars import ContextVar

TRANSACTION_ACTIVE = ContextVar("shared_state_transaction_active", default=False)
TRANSACTION_FINISHED = ContextVar("shared_state_transaction_finished", default=None)


def after_transaction(callback):
    """Defer external publication until commit/rollback and connection close.

    This does not authorize network access. The ordinary gateway still checks
    every request when the callback eventually executes.
    """
    if not TRANSACTION_ACTIVE.get():
        callback()
        return
    callbacks = TRANSACTION_FINISHED.get()
    if callbacks is None: raise RuntimeError('TRANSACTION_FINISH_QUEUE_MISSING')
    if callback not in callbacks: callbacks.append(callback)
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sqlite3


class StateConflict(ValueError):
    pass


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def sha(value):
    return hashlib.sha256(encoded(value).encode('utf8')).hexdigest()


def amount(value):
    if isinstance(value, bool) or isinstance(value, float) or not isinstance(value, (int, str, Decimal)):
        raise ValueError('EXACT_AMOUNT_REQUIRED')
    result = Decimal(value)
    if not result.is_finite() or result < 0:
        raise ValueError('NONNEGATIVE_FINITE_AMOUNT_REQUIRED')
    if len(result.as_tuple().digits)>38 or not -18<=result.as_tuple().exponent<=38:
        raise ValueError('AMOUNT_PRECISION_BOUND_EXCEEDED')
    return result


def decimal_text(value):
    return format(amount(value), 'f')


def exact_sum(values):
    """Add decimal coefficients as integers, independent of decimal context."""
    values=[amount(value) for value in values]
    if not values:return Decimal(0)
    exponent=min(v.as_tuple().exponent for v in values)
    total=sum(int(''.join(map(str,v.as_tuple().digits)))*10**(v.as_tuple().exponent-exponent) for v in values)
    return Decimal((0,tuple(map(int,str(total))),exponent))


# Text payloads preserve their exact encoded bytes and hashes on both backends.
# Decimal accounting is calculated in Python without float conversion. PostgreSQL
# stores exact NUMERIC; offline SQLite stores canonical decimal text.
DDL = '''
CREATE TABLE IF NOT EXISTS state_documents(
 namespace TEXT NOT NULL, identity TEXT NOT NULL, revision BIGINT NOT NULL,
 body TEXT NOT NULL, body_hash TEXT NOT NULL,
 PRIMARY KEY(namespace,identity));
CREATE TABLE IF NOT EXISTS state_accounts(
 identity TEXT PRIMARY KEY, unit TEXT NOT NULL, ceiling {number} NOT NULL,
 protected {number} NOT NULL, opening {number} NOT NULL, violated INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS state_reservations(
 account TEXT NOT NULL REFERENCES state_accounts(identity), identity TEXT NOT NULL,
 owner TEXT NOT NULL, reserved {number} NOT NULL, charged {number} NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('RESERVED','SETTLED','UNCERTAIN','VIOLATION')),
 detail TEXT NOT NULL, PRIMARY KEY(account,identity));
CREATE TABLE IF NOT EXISTS state_migrations(
 identity TEXT PRIMARY KEY, source_hash TEXT NOT NULL, verification TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS estate_graph_nodes(
 estate TEXT NOT NULL, identity TEXT NOT NULL, confidence TEXT NOT NULL
 CHECK(confidence IN ('DECLARED','INFERRED','VERIFIED','UNKNOWN')),
 provenance TEXT NOT NULL, body TEXT NOT NULL, PRIMARY KEY(estate,identity));
CREATE TABLE IF NOT EXISTS estate_graph_edges(
 estate TEXT NOT NULL, identity TEXT NOT NULL, source TEXT NOT NULL, target TEXT NOT NULL,
 confidence TEXT NOT NULL CHECK(confidence IN ('DECLARED','INFERRED','VERIFIED','UNKNOWN')),
 provenance TEXT NOT NULL, body TEXT NOT NULL, PRIMARY KEY(estate,identity),
 FOREIGN KEY(estate,source) REFERENCES estate_graph_nodes(estate,identity),
 FOREIGN KEY(estate,target) REFERENCES estate_graph_nodes(estate,identity));
'''

USAGE_DDL = '''
CREATE TABLE IF NOT EXISTS state_usage(
 environment TEXT NOT NULL, session_id TEXT NOT NULL, reservation_key TEXT NOT NULL,
 day TEXT NOT NULL, kind TEXT NOT NULL, reserved TEXT NOT NULL, actual TEXT,
 status TEXT NOT NULL, policy_hash TEXT NOT NULL, created DOUBLE PRECISION NOT NULL,
 owner TEXT NOT NULL, PRIMARY KEY(environment,session_id,reservation_key));
CREATE INDEX IF NOT EXISTS state_usage_window ON state_usage(environment,kind,created);
CREATE TABLE IF NOT EXISTS state_read_batches(
 environment TEXT NOT NULL, batch_id TEXT NOT NULL, approval TEXT NOT NULL,
 issued DOUBLE PRECISION NOT NULL, expires DOUBLE PRECISION NOT NULL,
 PRIMARY KEY(environment,batch_id));
CREATE TABLE IF NOT EXISTS state_read_batch_runs(
 environment TEXT NOT NULL, session_id TEXT NOT NULL, batch_id TEXT NOT NULL,
 purpose TEXT NOT NULL, allowance BIGINT NOT NULL, PRIMARY KEY(environment,session_id));
CREATE TABLE IF NOT EXISTS state_read_allocations(
 environment TEXT NOT NULL, session_id TEXT NOT NULL, reservation_key TEXT NOT NULL,
 batch_id TEXT, purpose TEXT NOT NULL, PRIMARY KEY(environment,session_id,reservation_key));
CREATE TABLE IF NOT EXISTS state_usage_acknowledgments(
 environment TEXT NOT NULL, session_id TEXT NOT NULL, reservation_key TEXT NOT NULL,
 violation_hash TEXT NOT NULL, approval TEXT NOT NULL, created DOUBLE PRECISION NOT NULL,
 PRIMARY KEY(environment,session_id,reservation_key));
'''


class SharedState:
    """Repository for tickets, case-file sections, catalog and readiness records.

    Connection callbacks return a fresh DB-API connection. For Entra auth the
    callback obtains a fresh token in memory; neither DSNs nor tokens are stored.
    """
    def __init__(self, connector, *, backend, mode):
        if backend not in ('postgresql', 'sqlite') or mode not in ('live', 'offline'):
            raise ValueError('EXPLICIT_STORAGE_BACKEND_AND_MODE_REQUIRED')
        if backend == 'sqlite' and mode != 'offline':
            raise ValueError('LIVE_SHARED_STATE_REQUIRES_POSTGRESQL')
        self.connector, self.backend, self.mode = connector, backend, mode
        self.connection_failures=[]

    @classmethod
    def offline(cls, path):
        def connect():
            db = sqlite3.connect(path, timeout=30)
            db.execute('PRAGMA foreign_keys=ON')
            return db
        return cls(connect, backend='sqlite', mode='offline')

    def sql(self, db, query, args=()):
        # Queries in this module have no literal '?' characters. This is only
        # parameter binding, never translation of caller-provided SQL.
        return db.execute(query.replace('?', '%s') if self.backend == 'postgresql' else query, args)

    def sqlmany(self, db, query, rows):
        """Batch internal writes in the caller's existing atomic transaction."""
        with closing(db.cursor()) as cursor:
            cursor.executemany(query.replace('?', '%s') if self.backend == 'postgresql' else query, rows)

    @contextmanager
    def transaction(self,*,_lease_release=False,_read_only=False):
        if type(_read_only)is not bool or (_read_only and _lease_release):
            raise ValueError('READ_TRANSACTION_MODE_INVALID')
        db = self.connector()
        if self.backend=='postgresql':
            from .postgres_connection import ObservedConnection
            db=ObservedConnection(db)
        outer_callbacks = TRANSACTION_FINISHED.get() if TRANSACTION_ACTIVE.get() else None
        callbacks = outer_callbacks if outer_callbacks is not None else []
        callback_marker = TRANSACTION_FINISHED.set(callbacks)
        marker = None
        primary = None
        try:
            from .shared_writer_lease import check as check_lease
            if self.backend == 'postgresql':
                # Writers must see leases committed while waiting for the lock.
                # Readers take one coherent, database-enforced read-only snapshot
                # without blocking reservation writers.
                db.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY'if _read_only
                           else'SET TRANSACTION ISOLATION LEVEL READ COMMITTED')
                db.execute("SET LOCAL lock_timeout = '5s'")
                db.execute("SET LOCAL statement_timeout = '30s'")
                db.execute("SET LOCAL idle_in_transaction_session_timeout = '30s'")
                check_lease(self,db,release_only=_lease_release)
                # One application-state lock gives portable serializable writes
                # including absent-row creation. It is held only for short local
                # state operations, never while a model or estate request runs.
                if not _read_only:db.execute('SELECT pg_advisory_xact_lock(183746812)')
            else:
                if _read_only:db.execute('PRAGMA query_only=ON')
                db.execute('BEGIN'if _read_only else'BEGIN IMMEDIATE')
            check_lease(self,db,release_only=_lease_release)
            marker = TRANSACTION_ACTIVE.set(True)
            yield db
            db.commit()
        except BaseException as error:
            primary = error
            try: db.rollback()
            except BaseException as rollback_error:
                error.add_note('Transaction rollback also failed: '+type(rollback_error).__name__)
            raise
        finally:
            closed = False
            try:
                db.close()
                closed = True
            finally:
                if marker is not None: TRANSACTION_ACTIVE.reset(marker)
                TRANSACTION_FINISHED.reset(callback_marker)
                if closed and outer_callbacks is None:
                    for callback in callbacks:
                        try: callback()
                        except BaseException as publication_error:
                            if primary is None: raise
                            primary.add_note('After-transaction publication also failed: '+type(publication_error).__name__)

    def migrate(self):
        text = DDL.format(number='NUMERIC' if self.backend == 'postgresql' else 'TEXT')
        from .graph_value_migration import sql as graph_value_schema
        from .facts_migration import sql as facts_schema
        migrations = {1:text,2:USAGE_DDL,3:graph_value_schema(self.backend),4:facts_schema(self.backend)}
        with self.transaction() as db:
            db.execute('CREATE TABLE IF NOT EXISTS state_schema_versions(version INTEGER PRIMARY KEY, sha256 TEXT NOT NULL)')
            rows = db.execute('SELECT version,sha256 FROM state_schema_versions ORDER BY version').fetchall()
            applied = dict(rows)
            for version,digest in rows:
                if version not in migrations or digest != hashlib.sha256(migrations[version].encode()).hexdigest():
                    raise StateConflict('SCHEMA_VERSION_OR_HASH_DIFFERS')
            if sorted(applied) != list(range(1,len(applied)+1)):
                raise StateConflict('SCHEMA_VERSION_SEQUENCE_DIFFERS')
            for version,text in migrations.items():
                if version in applied:
                    continue
                for statement in text.split(';'):
                    if statement.strip():
                        db.execute(statement)
                self.sql(db, 'INSERT INTO state_schema_versions VALUES(?,?)', (version,hashlib.sha256(text.encode()).hexdigest()))

    def _get(self, db, namespace, identity):
        row = self.sql(db, 'SELECT revision,body,body_hash FROM state_documents WHERE namespace=? AND identity=?', (namespace, identity)).fetchone()
        if row is None:
            raise KeyError(identity)
        body = json.loads(row[1])
        if sha(body) != row[2]:
            raise StateConflict('STATE_DOCUMENT_HASH_DIFFERS')
        return {'revision': row[0], 'body': body}

    def get(self, namespace, identity):
        return self._read_transaction(lambda db:self._get(db,namespace,identity))

    def _read_transaction(self,read):
        """Retry this read once on a fresh connection."""
        def operation():
            with self.transaction(_read_only=True)as db:return read(db)
        return self._retry_connection_operation('READ_TRANSACTION',operation)

    def _retry_connection_operation(self,name,operation):
        """Only callers with read/idempotency semantics may use this helper."""
        from .postgres_connection import dropped_connection
        import time
        for attempt in range(2):
            try:return operation()
            except Exception as error:
                if self.backend!='postgresql' or not dropped_connection(error):raise
                self.connection_failures.append({'operation':name,'attempt':attempt+1,
                    'error_type':type(error).__name__,'sqlstate':getattr(error,'sqlstate',None),
                    'connection_timing':getattr(error,'postgres_connection_timing',None),'retry':attempt==0})
                self.connection_failures=self.connection_failures[-100:]
                if attempt:raise
                time.sleep(30)

    def list(self, namespace, limit=40):
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError('BOUNDED_LIST_REQUIRED')
        def read(db):
            rows = self.sql(db, 'SELECT identity FROM state_documents WHERE namespace=? ORDER BY identity LIMIT ?', (namespace, limit)).fetchall()
            return [self._get(db, namespace, r[0]) for r in rows]
        return self._read_transaction(read)

    def put(self, namespace, identity, body, *, revision=None):
        with self.transaction() as db:
            try:
                prior = self._get(db, namespace, identity)
            except KeyError:
                prior = None
            if prior is None:
                if revision is not None:
                    raise StateConflict('STATE_REVISION_DIFFERS')
                self.sql(db, 'INSERT INTO state_documents VALUES(?,?,?,?,?)', (namespace, identity, 0, encoded(body), sha(body)))
                return {'revision': 0, 'body': body}
            if type(revision) is not int or revision != prior['revision']:
                raise StateConflict('STATE_REVISION_DIFFERS')
            self.sql(db, 'UPDATE state_documents SET revision=?,body=?,body_hash=? WHERE namespace=? AND identity=?', (revision+1, encoded(body), sha(body), namespace, identity))
            return {'revision': revision+1, 'body': body}

    def update(self, namespace, identity, revision, operation):
        with self.transaction() as db:
            prior = self._get(db, namespace, identity)
            if type(revision) is not int or revision != prior['revision']:
                raise StateConflict('STATE_REVISION_DIFFERS')
            body = operation(prior['body'])
            self.sql(db, 'UPDATE state_documents SET revision=?,body=?,body_hash=? WHERE namespace=? AND identity=?', (revision+1, encoded(body), sha(body), namespace, identity))
            return {'revision': revision+1, 'body': body}

    def _snapshot(self, db, identity):
        row = self.sql(db, 'SELECT unit,ceiling,protected,opening,violated FROM state_accounts WHERE identity=?', (identity,)).fetchone()
        if row is None:
            raise KeyError(identity)
        reservations = self.sql(db, 'SELECT identity,owner,reserved,charged,status,detail FROM state_reservations WHERE account=? ORDER BY identity', (identity,)).fetchall()
        return {'identity': identity, 'unit': row[0], 'ceiling': decimal_text(row[1]),
                'protected': decimal_text(row[2]), 'opening': decimal_text(row[3]),
                'charged': decimal_text(exact_sum([row[3]]+[r[3] for r in reservations])),
                'violated': bool(row[4]), 'reservations': [
                    {'identity': r[0], 'owner': r[1], 'reserved': decimal_text(r[2]), 'charged': decimal_text(r[3]), 'status': r[4], 'detail': json.loads(r[5])} for r in reservations]}

    def snapshot(self, identity):
        return self._read_transaction(lambda db:self._snapshot(db,identity))

    def _totals(self,db,identity):
        """Exact admission counters, without historical detail JSON or bodies."""
        row=self.sql(db,'SELECT unit,ceiling,protected,opening,violated FROM state_accounts WHERE identity=?',(identity,)).fetchone()
        if row is None:raise KeyError(identity)
        if self.backend=='postgresql':
            charged=self.sql(db,'SELECT COALESCE(SUM(charged),0) FROM state_reservations WHERE account=?',(identity,)).fetchone()[0]
        else:
            charged=exact_sum(r[0] for r in self.sql(db,'SELECT charged FROM state_reservations WHERE account=?',(identity,)).fetchall())
        return {'identity':identity,'unit':row[0],'ceiling':decimal_text(row[1]),'protected':decimal_text(row[2]),
                'opening':decimal_text(row[3]),'charged':decimal_text(exact_sum([row[3],charged])),'violated':bool(row[4])}

    def totals(self,identity):
        return self._read_transaction(lambda db:self._totals(db,identity))

    def reserve(self, identity, key, owner, bound, *, detail=None):
        bound = amount(bound)
        if bound <= 0:
            raise ValueError('POSITIVE_RESERVATION_REQUIRED')
        detail = detail or {}
        with self.transaction() as db:
            snapshot = self._totals(db, identity)
            row=self.sql(db,'SELECT owner,reserved,detail FROM state_reservations WHERE account=? AND identity=?',(identity,key)).fetchone()
            prior={'owner':row[0],'reserved':row[1],'detail':json.loads(row[2])} if row else None
            if prior:
                if prior['owner'] != owner or amount(prior['reserved']) != bound or prior['detail'] != detail:
                    raise StateConflict('RESERVATION_IDENTITY_DIFFERS')
                # Admission is never a transport retry. A caller must not use a
                # previously reserved key to perform another physical request.
                raise StateConflict('RESERVATION_ALREADY_ADMITTED')
            if snapshot['violated']:
                raise StateConflict('ACCOUNT_VIOLATION_LATCHED')
            if exact_sum([snapshot['charged'],bound,snapshot['protected']]) > amount(snapshot['ceiling']):
                raise StateConflict('ACCOUNT_CAP_REACHED')
            self.sql(db, 'INSERT INTO state_reservations VALUES(?,?,?,?,?,?,?)', (identity, key, owner, decimal_text(bound), decimal_text(bound), 'RESERVED', encoded(detail)))
            return key

    def settle(self, identity, key, owner, actual=None, *, detail=None,full_snapshot=True):
        # Repeating this exact reservation ID is safe even if the first COMMIT
        # succeeded but its response was lost: non-RESERVED rows are unchanged.
        return self._retry_connection_operation('RESERVATION_SETTLEMENT',
            lambda:self._settle_once(identity,key,owner,actual,detail=detail,full_snapshot=full_snapshot))

    def _settle_once(self, identity, key, owner, actual=None, *, detail=None,full_snapshot=True):
        if type(full_snapshot)is not bool:raise ValueError('SNAPSHOT_MODE_BOOLEAN_REQUIRED')
        with self.transaction() as db:
            row = self.sql(db, 'SELECT owner,reserved,status,detail FROM state_reservations WHERE account=? AND identity=?', (identity,key)).fetchone()
            if row is None or row[0] != owner:
                raise StateConflict('RESERVATION_OWNER_DIFFERS')
            if row[2] != 'RESERVED':
                return self._snapshot(db, identity) if full_snapshot else self._totals(db,identity)
            charged = amount(row[1]) if actual is None else amount(actual)
            status = 'UNCERTAIN' if actual is None else ('VIOLATION' if charged > amount(row[1]) else 'SETTLED')
            payload = json.loads(row[3])
            if detail is not None:
                payload['settlement'] = detail
            self.sql(db, 'UPDATE state_reservations SET charged=?,status=?,detail=? WHERE account=? AND identity=?', (decimal_text(charged),status,encoded(payload),identity,key))
            if status == 'VIOLATION':
                self.sql(db, 'UPDATE state_accounts SET violated=1 WHERE identity=?', (identity,))
            return self._snapshot(db, identity) if full_snapshot else self._totals(db,identity)

    def import_accounts(self, identity, source):
        """All-or-nothing, one-time accounting import. No cap or total defaults.

        Original rows belong in the source document alongside computed opening
        totals. Re-imports prove the same source hash, not a reset of live totals.
        """
        source_hash = sha(source)
        with self.transaction() as db:
            prior = self.sql(db, 'SELECT source_hash,verification FROM state_migrations WHERE identity=?', (identity,)).fetchone()
            if prior:
                if prior[0] != source_hash:
                    raise StateConflict('MIGRATION_SOURCE_CHANGED')
                return json.loads(prior[1])
            proof = []
            for account in source['accounts']:
                if set(account) != {'identity','unit','ceiling','protected','opening','violated'}:
                    raise ValueError('COMPLETE_ACCOUNT_IMPORT_REQUIRED')
                for field in ('ceiling','protected','opening'):
                    amount(account[field])
                if type(account['violated']) is not bool:
                    raise ValueError('EXPLICIT_VIOLATION_STATE_REQUIRED')
                if amount(account['protected']) > amount(account['ceiling']):
                    raise ValueError('PROTECTED_RESERVE_EXCEEDS_CEILING')
                self.sql(db, 'INSERT INTO state_accounts VALUES(?,?,?,?,?,?)', (account['identity'],account['unit'],decimal_text(account['ceiling']),decimal_text(account['protected']),decimal_text(account['opening']),int(account['violated'])))
                after = self._snapshot(db, account['identity'])
                before = {k: decimal_text(account[k]) for k in ('ceiling','protected','opening')}
                measured = {k: after[k] for k in before}
                if measured != before or after['charged'] != before['opening']:
                    raise StateConflict('MIGRATION_TOTALS_DIFFER')
                proof.append({'identity':account['identity'],'before':before,'after':measured,'matched':True})
            verification = {'source_sha256':source_hash,'accounts':proof}
            self.sql(db, 'INSERT INTO state_migrations VALUES(?,?,?)', (identity,source_hash,encoded(verification)))
            self.sql(db, 'INSERT INTO state_documents VALUES(?,?,?,?,?)', ('migration_source',identity,0,encoded(source),source_hash))
            return verification


def configured_state(environ=None):
    """Cloud configuration has no SQLite fallback and no password DSN.

    Cloud authentication selects exactly the configured managed identity. Owner
    migration is a separate explicitly supplied connector; no CLI fallback is
    available to a worker. A token is refreshed for every connection.
    """
    import os
    env = os.environ if environ is None else environ
    backend = env.get('INVESTIGATOR_STATE_BACKEND')
    if backend is None:
        return None  # Existing offline replay remains byte-for-byte compatible.
    if backend != 'postgresql':
        raise ValueError('CONFIGURED_LIVE_STATE_REQUIRES_POSTGRESQL')
    from .privacy_capture import ACTIVE as PRIVACY_CAPTURE
    if PRIVACY_CAPTURE.get() is not None or env.get('INVESTIGATOR_RECORDING_CLASS','EXACT') != 'EXACT':
        # Projection discovers values and dependent identities across a capture.
        # Raw shared-state writes cannot precede that boundary. Do not silently
        # degrade a projected installation to exact storage.
        raise ValueError('POSTGRES_PRIVACY_PROJECTED_STATE_NOT_IMPLEMENTED')
    required = ('INVESTIGATOR_PG_HOST','INVESTIGATOR_PG_DATABASE','INVESTIGATOR_PG_USER','AZURE_CLIENT_ID')
    if any(not env.get(k) for k in required):
        raise ValueError('POSTGRES_CONNECTION_CONFIGURATION_MISSING')
    def connect():
        from .postgres_connection import connect as postgres_connect
        from .live_gateway import authorize_platform_database
        authorize_platform_database(env.get('DIA_GATEWAY_STATE_IDENTITY','state'),env[required[0]],env[required[1]])
        from .adapters.platform_credentials import credential_type, trust_roots
        from .postgres_connection import database_token
        token=database_token(credential_type(),env['AZURE_CLIENT_ID'])
        return postgres_connect(host=env[required[0]], dbname=env[required[1]], user=env[required[2]],
                              password=token, sslmode='verify-full', sslrootcert=trust_roots(),
                              options='-c search_path=dia_state', connect_timeout=15)
    return SharedState(connect, backend='postgresql', mode='live')

"""PostgreSQL authority for application rows, with a transient transaction view.

The application SQL is interpreted in memory, never translated to PostgreSQL.
The durable local catalog is only an exact replay mirror. Every live access to
these tables starts from hash-checked shared rows; missing migration refuses.
Short optimistic transactions fence concurrent revisions before any dispatch.
"""
from contextlib import contextmanager, closing
from contextvars import ContextVar
import copy
import json
import re
import sqlite3

from .shared_state import StateConflict, encoded, sha
from .process_tape import ACTIVE, event, value

VERSION = 'shared-application-rows-v1'
NAMESPACE = 'application_table'
TABLES = frozenset('''claim_intakes claim_revisions claim_investigations
 claim_execution_failures claim_handoffs claim_glossary_events claim_screenshot_reviews
 claim_screenshot_confirmations claim_screenshot_portal_maps claim_metric_selections
 v2_runs v2_steps v2_run_events v2_cancellations adaptive_sessions adaptive_events
 adaptive_syntheses workspace_previews workspace_jobs workspace_intakes workspace_form_controls
 workspace_image_reads workspace_image_reviews workspace_images workspace_image_objects
 agent_progress native_diagnostics source_diagnostics flexible_diagnostics
 native_capability_decisions failure_details aggregate_receipt_seals
 record_readbacks record_comparisons record_aggregate_assessments
 comparison_assessments proof_preflights'''.split())
CURRENT = ContextVar('shared_application_connection', default=None)
BOOTSTRAP_REPLAY = ContextVar('shared_application_bootstrap_replay', default=False)


@contextmanager
def bootstrap_replay():
    """Controller constructors restore sealed schemas, not operation reads."""
    token=BOOTSTRAP_REPLAY.set(True)
    try:yield
    finally:BOOTSTRAP_REPLAY.reset(token)


def key(environment, table):
    if table not in TABLES:raise StateConflict('APPLICATION_TABLE_NOT_ALLOWED')
    return encoded([environment, table])


def enabled(store):
    tape = ACTIVE.get()
    if tape is not None and tape.replaying:
        return not BOOTSTRAP_REPLAY.get() and tape.bootstrap.get('state', {}).get('shared_application') == VERSION
    # Replay controller construction can occur outside the active tape. The
    # recorded catalog port is not a live PostgreSQL application-state source.
    if getattr(store.__dict__.get('shared_catalog'),'replay_only',False):return False
    shared=store.__dict__.get('shared_catalog') is not None
    if shared:
        import os
        from .privacy_capture import ACTIVE as privacy
        if privacy.get() is not None or os.environ.get('INVESTIGATOR_RECORDING_CLASS','EXACT')!='EXACT':
            raise StateConflict('POSTGRES_PRIVACY_PROJECTED_STATE_NOT_IMPLEMENTED')
    return shared


def schema(db, table):
    row = db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
    return row[0] if row else None


def export_table(db, table):
    key('', table)
    ddl = schema(db, table)
    if ddl is None:return None
    columns = [r[1] for r in db.execute('PRAGMA table_info("'+table+'")')]
    rows = [list(r) for r in db.execute('SELECT rowid,* FROM "'+table+'" ORDER BY rowid')]
    if any(isinstance(v, (bytes, bytearray, memoryview)) for r in rows for v in r):
        raise StateConflict('APPLICATION_OPAQUE_BYTES_REQUIRE_BLOB_MIGRATION')
    return {'schema': ddl, 'columns': columns, 'rows': rows}


def validate_table(table, payload):
    if payload is None:return
    if set(payload) != {'schema', 'columns', 'rows'}:raise StateConflict('APPLICATION_TABLE_SHAPE')
    if any(not isinstance(c,str) or not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',c) for c in payload['columns']):
        raise StateConflict('APPLICATION_COLUMN_IDENTITY')
    # Shared state contains rows, not executable SQL authority. Accept exactly
    # one ordinary table declaration; reject views, triggers and SELECT sources.
    import sqlglot
    from sqlglot import exp
    try: parsed = sqlglot.parse(payload['schema'], read='sqlite')
    except Exception as exc:raise StateConflict('APPLICATION_SCHEMA_INVALID') from exc
    if (len(parsed) != 1 or not isinstance(parsed[0], exp.Create)
            or parsed[0].args.get('kind') != 'TABLE' or parsed[0].args.get('expression') is not None
            or not isinstance(parsed[0].this, exp.Schema)
            or parsed[0].this.this.name != table):raise StateConflict('APPLICATION_SCHEMA_INVALID')
    with closing(sqlite3.connect(':memory:')) as db:
        db.execute(payload['schema'])
        if [r[1] for r in db.execute('PRAGMA table_info("'+table+'")')] != payload['columns']:
            raise StateConflict('APPLICATION_COLUMNS_DIFFER')
    ids = []
    for row in payload['rows']:
        if (not isinstance(row, list) or len(row) != len(payload['columns'])+1
                or type(row[0]) is not int or row[0] <= 0
                or any(type(v) not in (str, int, float, type(None)) for v in row)):
            raise StateConflict('APPLICATION_ROW_SHAPE')
        ids.append(row[0])
    if ids != sorted(set(ids)):raise StateConflict('APPLICATION_ROW_IDENTITY')


def restore_table(db, table, payload):
    validate_table(table, payload)
    if payload is None:return
    prior = schema(db, table)
    if prior is not None:
        if [r[1] for r in db.execute('PRAGMA table_info("'+table+'")')] != payload['columns']:
            raise StateConflict('APPLICATION_MIRROR_COLUMNS_DIFFER')
        db.execute('DELETE FROM "'+table+'"')
    else:db.execute(payload['schema'])
    slots = ','.join('?' for _ in range(len(payload['columns'])+1))
    db.executemany('INSERT INTO "'+table+'"(rowid,'+','.join('"'+c+'"' for c in payload['columns'])+') VALUES('+slots+')', payload['rows'])


def source(database, environment):
    """An operator-owned, read-only snapshot; never an implicit worker import."""
    from pathlib import Path
    with closing(sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro', uri=True)) as db:
        db.execute('BEGIN')
        tables = {t: export_table(db, t) for t in sorted(TABLES) if schema(db, t) is not None}
    return {'version': VERSION, 'environment': environment, 'tables': tables}


def migrate(state, identity, source):
    if set(source) != {'version', 'environment', 'tables'} or source['version'] != VERSION:
        raise StateConflict('APPLICATION_MIGRATION_SCHEMA')
    fingerprint = sha(source)
    for table, payload in source['tables'].items():
        key(source['environment'], table); validate_table(table, payload)
    with state.transaction() as db:
        old = state.sql(db, 'SELECT source_hash,verification FROM state_migrations WHERE identity=?', (identity,)).fetchone()
        if old:
            if old[0] != fingerprint:raise StateConflict('MIGRATION_SOURCE_CHANGED')
            return json.loads(old[1])
        proofs = []
        for table, payload in source['tables'].items():
            identity_key = key(source['environment'], table)
            try:state._get(db, NAMESPACE, identity_key)
            except KeyError:pass
            else:raise StateConflict('APPLICATION_MIGRATION_TARGET_EXISTS')
            state.sql(db, 'INSERT INTO state_documents VALUES(?,?,?,?,?)', (NAMESPACE, identity_key, 0, encoded(payload), sha(payload)))
            actual = state._get(db, NAMESPACE, identity_key)['body']
            if encoded(actual) != encoded(payload):raise StateConflict('APPLICATION_MIGRATION_BYTES_DIFFER')
            proofs.append({'table': table, 'rows_before': len(payload['rows']), 'rows_after': len(actual['rows']),
                           'sha256_before': sha(payload), 'sha256_after': sha(actual), 'matched': True})
        proof = {'source_sha256': fingerprint, 'environment': source['environment'], 'tables': proofs}
        from .shared_case_file import publish_changed
        publish_changed(state, db, source['environment'], source['tables'])
        state.sql(db, 'INSERT INTO state_migrations VALUES(?,?,?)', (identity, fingerprint, encoded(proof)))
        return proof


class Connection:
    """Trusted application SQL only. No user/model SQL reaches this interface."""
    def __init__(self, store, mirror):
        self.store, self.mirror = store, mirror
        self.memory = sqlite3.connect(':memory:')
        self.memory.row_factory = sqlite3.Row
        self.memory.execute('PRAGMA temp_store=MEMORY')
        self.memory.execute('PRAGMA journal_mode=MEMORY')
        self.loaded = {}; self.schema_sql = {}
        self.state = store.shared_catalog.state if store.shared_catalog is not None else None

    @property
    def row_factory(self):return self.memory.row_factory
    @row_factory.setter
    def row_factory(self, value):self.memory.row_factory = value; self.mirror.row_factory = value
    @property
    def in_transaction(self):return self.memory.in_transaction or self.mirror.in_transaction

    def create_function(self, *args, **kwargs):
        self.memory.create_function(*args, **kwargs); self.mirror.create_function(*args, **kwargs)

    def commit(self):
        self.finish();self.memory.commit();self.mirror.commit();self.loaded.clear()

    def rollback(self):
        self.memory.rollback();self.mirror.rollback();self.loaded.clear()

    def _load(self, table):
        if table in self.loaded:return
        def read():
            try:return self.state.get(NAMESPACE, key(self.store.environment, table))
            except KeyError:
                old = export_table(self.mirror, table)
                if old is not None and old['rows']:
                    raise StateConflict('APPLICATION_MIGRATION_REQUIRED:'+table)
                return {'revision': None, 'body': old}
        from .shared_application_capture import read as capture_table
        saved = capture_table(table,read)
        if set(saved) != {'revision', 'body'} or (saved['revision'] is not None and type(saved['revision']) is not int):
            raise StateConflict('APPLICATION_SNAPSHOT_SHAPE')
        validate_table(table, saved['body'])
        self.loaded[table] = copy.deepcopy(saved)
        restore_table(self.memory, table, saved['body'])

    def execute(self, sql, args=()):
        # SQL is generated by the existing controllers. Tokenization is only
        # routing; it never grants any external query or rewrites its semantics.
        tokens = set(re.findall(r'[A-Za-z_][A-Za-z_0-9]*', sql))
        tables = tokens & TABLES
        referenced = re.findall(r'\b(?:FROM|JOIN|INTO|UPDATE|TABLE(?:\s+IF\s+NOT\s+EXISTS)?)\s+["\[]?([A-Za-z_][A-Za-z_0-9]*)',sql,re.I)
        for table in referenced:
            if table.startswith(('claim_','v2_','workspace_','adaptive_')) and table not in TABLES and table!='adaptive_usage':
                raise StateConflict('APPLICATION_TABLE_NOT_REGISTERED:'+table)
        if 'sqlite_master' in tokens and args and args[0] in TABLES:tables.add(args[0])
        if sql.strip().upper() in ('BEGIN', 'BEGIN IMMEDIATE'):
            if not self.memory.in_transaction:self.memory.execute('BEGIN')
            if not self.mirror.in_transaction:self.mirror.execute('BEGIN IMMEDIATE')
            return self.memory.execute('SELECT 1 WHERE 0')
        for table in sorted(tables):self._load(table)
        if tables:
            result = self.memory.execute(sql, args)
            return result
        return self.mirror.execute(sql, args)

    def executemany(self, sql, values):
        result = None
        for args in values:result = self.execute(sql, args)
        return result

    def executescript(self, script):
        statement = ''
        for line in script.splitlines(keepends=True):
            for char in line:
                statement += char
                if char == ';' and sqlite3.complete_statement(statement):
                    self.execute(statement); statement = ''
        if statement.strip():self.execute(statement)

    def finish(self):
        if not self.loaded:return
        final = {t: export_table(self.memory, t) for t in self.loaded}
        changed = {t: p for t, p in final.items() if p != self.loaded[t]['body']}
        receipt = {'tables': {t: sha(p) for t, p in final.items()}, 'changed': sorted(changed)}
        tape = ACTIVE.get()
        if tape is None or not tape.replaying:
            with self.state.transaction() as db:
                for table, saved in self.loaded.items():
                    try:current = self.state._get(db, NAMESPACE, key(self.store.environment, table))
                    except KeyError:current = {'revision': None, 'body': saved['body']}
                    if current != saved:raise StateConflict('APPLICATION_REVISION_CHANGED:'+table)
                for table, payload in changed.items():
                    identity = key(self.store.environment, table); revision = self.loaded[table]['revision']
                    if revision is None:
                        self.state.sql(db, 'INSERT INTO state_documents VALUES(?,?,?,?,?)', (NAMESPACE, identity, 0, encoded(payload), sha(payload)))
                    else:self.state.sql(db, 'UPDATE state_documents SET revision=?,body=?,body_hash=? WHERE namespace=? AND identity=?',
                                        (revision+1, encoded(payload), sha(payload), NAMESPACE, identity))
                from .shared_case_file import publish_changed
                publish_changed(self.state, db, self.store.environment, changed)
        if self.loaded:event('CONFIGURATION', {'shared_application_commit': receipt})
        # Only after the authority commits may replay artifacts be materialized.
        for table, payload in final.items():restore_table(self.mirror, table, payload)


@contextmanager
def connection(store, mirror):
    current = CURRENT.get()
    if current is not None and current.store is store:
        yield current; return
    view = Connection(store, mirror); token = CURRENT.set(view)
    try:
        yield view
        view.finish()
    finally:
        CURRENT.reset(token); view.memory.close()

"""Transactional, budget-only attachment for isolated session catalogs.

Live connections address the existing accounting file; sealed replay catalogs
materialize those inputs and never attach an installation's live file.
"""
from contextlib import closing
from pathlib import Path
import re
import sqlite3

TABLES = frozenset(('adaptive_usage', 'read_batches', 'read_batch_runs',
                   'read_allocations', 'usage_violation_acknowledgments',
                   'budget_mutations', 'budget_mutations_v2'))
SCHEMA = 'shared_budget'
TOKEN = re.compile(r"'(?:''|[^'])*'|--[^\n]*|/\*[\s\S]*?\*/|\"(?:\"\"|[^\"])*\"|\b[A-Za-z_][A-Za-z_0-9]*\b")


def qualify(sql):
    """Rewrite fixed consumer-owned SQL identifiers, never literals or values."""
    if re.match(r'\s*PRAGMA\s+table_info\s*\(', sql, re.I):
        if any(re.search(r'\(\s*' + table + r'\s*\)', sql, re.I) for table in TABLES):
            return re.sub(r'(?i)PRAGMA\s+', 'PRAGMA ' + SCHEMA + '.', sql, count=1)
    if re.match(r'\s*PRAGMA\s+schema_version\s*;?\s*$', sql, re.I):
        return 'PRAGMA ' + SCHEMA + '.schema_version'
    budget_master = 'sqlite_master' in sql and any(word in sql for word in ('budget_', 'adaptive_usage', 'read_batches', 'read_allocations'))
    def substitute(match):
        token = match.group()
        name = token[1:-1] if token.startswith('"') else token
        if name in TABLES or name == 'sqlite_master' and budget_master:
            # A pre-qualified identifier is rejected rather than double-bound.
            prefix = sql[:match.start()].rstrip()
            if prefix.endswith('.'):
                raise ValueError('SHARED_ACCOUNTING_EXPLICIT_SCHEMA_FORBIDDEN')
            return SCHEMA + '.' + token
        return token
    return TOKEN.sub(substitute, sql)


def attach(db, accounting):
    accounting = Path(accounting).resolve()
    if not accounting.is_file():
        raise ValueError('SHARED_ACCOUNTING_EXISTING_FILE_REQUIRED')
    if db.execute('PRAGMA journal_mode').fetchone()[0] != 'delete':
        raise ValueError('SHARED_ACCOUNTING_ATOMIC_DELETE_JOURNAL_REQUIRED')
    sqlite3.Connection.execute(db, 'ATTACH DATABASE ? AS ' + SCHEMA, (str(accounting),))
    if sqlite3.Connection.execute(db, 'PRAGMA ' + SCHEMA + '.journal_mode').fetchone()[0] != 'delete':
        raise ValueError('SHARED_ACCOUNTING_ATOMIC_DELETE_JOURNAL_REQUIRED')
    existing = {r[0] for r in sqlite3.Connection.execute(db, 'SELECT name FROM ' + SCHEMA + '.sqlite_master WHERE type=\'table\'')}
    if not TABLES <= existing:
        raise ValueError('SHARED_ACCOUNTING_UNINITIALIZED')
    sqlite3.Connection.execute(db,'''CREATE TABLE IF NOT EXISTS isolated_budget_ownership(
        environment TEXT,session_id TEXT,reservation_key TEXT,
        PRIMARY KEY(environment,session_id,reservation_key))''')
    def owned(environment,session,key):
        return int(sqlite3.Connection.execute(db,'''SELECT 1 FROM isolated_budget_ownership
            WHERE environment=? AND session_id=? AND reservation_key=?''',(environment,session,key)).fetchone() is not None)
    db.create_function('isolated_budget_owned',3,owned)
    # TEMP machinery is private to this connection, never written into the
    # shared catalog. Only reservations acquired by this isolated catalog may
    # be settled; old unowned charges cannot quietly be released.
    sqlite3.Connection.execute(db,'''CREATE TEMP TRIGGER isolated_budget_settlement
        BEFORE UPDATE ON shared_budget.adaptive_usage
        WHEN isolated_budget_owned(OLD.environment,OLD.session_id,OLD.reservation_key)=0
        BEGIN SELECT RAISE(ABORT,'SHARED_ACCOUNTING_RESERVATION_NOT_OWNED'); END''')
    def authorize(action, table, column, database, trigger):
        if database != SCHEMA:
            return sqlite3.SQLITE_OK
        if action in (sqlite3.SQLITE_READ, sqlite3.SQLITE_INSERT):
            if table in TABLES or table == 'sqlite_sequence':
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_READ and table == 'sqlite_master' and getattr(db, '_budget_schema_query', False):
                return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_UPDATE and table == 'adaptive_usage' and column in ('actual','status'):
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_PRAGMA and table in ('table_info', 'schema_version'):
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY
    db.set_authorizer(authorize)
    db.shared_accounting = str(accounting)


def register_owned(db,sql,parameters,result):
    if re.match(r'\s*INSERT\s+INTO\s+shared_budget\.adaptive_usage\b',sql,re.I) and result.rowcount==1:
        if not isinstance(parameters,(tuple,list)) or len(parameters)<3:
            raise ValueError('SHARED_ACCOUNTING_RESERVATION_PARAMETERS_REQUIRED')
        sqlite3.Connection.execute(db,'INSERT OR IGNORE INTO isolated_budget_ownership VALUES(?,?,?)',tuple(parameters[:3]))


def materialize(destination, accounting):
    """Seal only budget state into a private bootstrap; original rows untouched."""
    with closing(sqlite3.connect(Path(accounting).resolve().as_uri() + '?mode=ro', uri=True)) as shared:
        shared.execute('BEGIN')
        with closing(sqlite3.connect(destination)) as clone:
            from .budget_delta_v2 import register_codec
            register_codec(clone)
            machinery = list(clone.execute("SELECT name,sql FROM sqlite_master WHERE type='trigger' AND (name LIKE 'budget_delta_%' OR name LIKE 'budget_v2_delta_%' OR name LIKE 'budget_mutations_no_%' OR name LIKE 'budget_mutations_v2_no_%')"))
            with clone:
                for name, sql in machinery:
                    clone.execute('DROP TRIGGER "' + name + '"')
                for table in TABLES:
                    clone.execute('DELETE FROM ' + table)
                    columns = len(shared.execute('PRAGMA table_info(' + table + ')').fetchall())
                    clone.executemany('INSERT INTO ' + table + ' VALUES(' + ','.join('?' for _ in range(columns)) + ')', shared.execute('SELECT * FROM ' + table))
                for name, sql in machinery:
                    clone.execute(sql)
        shared.rollback()

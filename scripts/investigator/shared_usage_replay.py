"""Versioned offline execution of the shared governor, never a live authority.

The replay mirror contains admission inputs, not recorded admission answers.
Run the real SharedUsage algorithm against an in-memory state repository so
clock consumption, refusals and inserted reservation bytes remain identical.
"""
from contextlib import contextmanager
import sqlite3
from .shared_state import SharedState, encoded, sha
from .shared_usage import SharedUsage, TABLES
from .process_tape import TapeError

VERSION = 'FRESH_SHARED_USAGE_V1'
WORKSPACE_VERSION = 'OWNED_SHARED_USAGE_V1'


def validate_workspace(marker):
    if (not isinstance(marker, dict) or set(marker) != {'version', 'owner', 'baseline_owners'}
            or marker['version'] != WORKSPACE_VERSION
            or not isinstance(marker['owner'], str) or not marker['owner']
            or not isinstance(marker['baseline_owners'], list)):
        raise TapeError('TAPE_SHARED_USAGE_CONTRACT_DIFFERS')
    keys = set()
    for row in marker['baseline_owners']:
        if not isinstance(row, list) or len(row) != 3 or any(not isinstance(v, str) or not v for v in row):
            raise TapeError('TAPE_SHARED_USAGE_OWNER_INVALID')
        if tuple(row[:2]) in keys:raise TapeError('TAPE_SHARED_USAGE_OWNER_DUPLICATE')
        keys.add(tuple(row[:2]))
    return marker


def capture_backend(governor):
    """Seal public ownership with a mirror-consistent baseline before capture."""
    shared = governor.shared
    with governor.runtime.db() as local:
        shared.mirror(local)
        with shared.state.transaction() as db:
            rows = shared.state.sql(db, 'SELECT session_id,reservation_key,owner FROM state_usage WHERE environment=?',
                                    (governor.environment,)).fetchall()
        actual = {(r[0], r[1]) for r in local.execute(
            'SELECT session_id,reservation_key FROM adaptive_usage WHERE environment=?', (governor.environment,))}
        if actual != {(r[0], r[1]) for r in rows}:
            raise TapeError('TAPE_SHARED_BASELINE_CHANGED_DURING_CAPTURE')
    return {'version': WORKSPACE_VERSION, 'owner': shared.owner,
            'baseline_owners': sorted([list(r) for r in rows])}


def declaration(session):
    if not isinstance(session, str) or not session:
        raise ValueError('SHARED_REPLAY_FRESH_SESSION_REQUIRED')
    return {'version': VERSION, 'fresh_sessions': [session, session + ':prewarm-controls']}


class MemoryState(SharedState):
    def __init__(self):
        self.connection = sqlite3.connect(':memory:')
        super().__init__(None, backend='sqlite', mode='offline')
        self.migrate()

    @contextmanager
    def transaction(self,*,_lease_release=False,_read_only=False):
        if type(_read_only)is not bool or (_read_only and _lease_release):
            raise ValueError('READ_TRANSACTION_MODE_INVALID')
        try:
            self.connection.execute('PRAGMA query_only='+('ON'if _read_only else'OFF'))
            self.connection.execute('BEGIN'if _read_only else'BEGIN IMMEDIATE')
            yield self.connection
            self.connection.commit()
        except BaseException:
            self.connection.rollback()
            raise
        finally:
            self.connection.execute('PRAGMA query_only=OFF')


class ReplayUsage(SharedUsage):
    def __init__(self, governor, tape):
        marker = tape.bootstrap['state']['shared_usage_replay']
        self.tape = tape
        self.owners = {}
        workspace = marker.get('version') == WORKSPACE_VERSION
        if workspace:
            validate_workspace(marker)
            for row in marker['baseline_owners']:
                key = tuple(row[:2])
                self.owners[key] = row[2]
            self.sessions = None
            owner = marker['owner']
        else:
            session = tape.bootstrap['state']['inputs']['session_id']
            if marker != declaration(session):raise TapeError('TAPE_SHARED_USAGE_CONTRACT_DIFFERS')
            self.sessions = frozenset(marker['fresh_sessions'])
            owner = 'SEALED_FRESH_SESSION'
        if not tape.replaying:
            raise TapeError('TAPE_SHARED_USAGE_CONTRACT_DIFFERS')
        self.applying = False
        state = MemoryState()
        expected = {'policy': governor.policy,
                    'round_policy': governor.runtime.config.get('_estate', {}).get('round')}
        with state.transaction() as db:
            state.sql(db, 'INSERT INTO state_documents VALUES(?,?,?,?,?)',
                      ('usage_policy', governor.environment, 0, encoded(expected), sha(expected)))
        super().__init__(governor, state, owner=owner)
        if workspace:
            with governor.runtime.db() as local:
                actual = {(r[0], r[1]) for r in local.execute(
                    'SELECT session_id,reservation_key FROM adaptive_usage WHERE environment=?', (self.environment,))}
                if actual != set(self.owners):raise TapeError('TAPE_SHARED_BASELINE_OWNERS_DIFFER')

    def mirror(self, local):
        # The tape's checkpoint applies external deltas immediately AFTER this
        # pre-decision hook. Do not replace them from a stale memory snapshot.
        if self.applying:
            super().mirror(local)

    def _load(self, local, session):
        allowed = self.sessions if self.sessions is not None else getattr(self.tape, 'budget_owned_sessions', set())
        if session not in allowed:
            raise TapeError('TAPE_SHARED_USAGE_SESSION_DIFFERS')
        with self.state.transaction() as db:
            for original, (target, columns) in TABLES.items():
                self.state.sql(db, 'DELETE FROM ' + target)
                rows = local.execute('SELECT ' + ','.join(columns) + ' FROM ' + original +
                                     ' WHERE environment=?', (self.environment,)).fetchall()
                for row in rows:
                    values = list(row)
                    names = list(columns)
                    if original == 'adaptive_usage':
                        names.append('owner')
                        values.append(self.owners.get((row[1], row[2]),
                            self.owner if self.sessions is not None and row[1] in self.sessions else 'EXTERNAL_BASELINE'))
                    self.state.sql(db, 'INSERT INTO ' + target + '(' + ','.join(names) +
                                   ') VALUES(' + ','.join('?' for _ in values) + ')', values)

    def reserve(self, local, session, key, *args, **kwargs):
        self._load(local, session)
        self.applying = True
        try:
            result = super().reserve(local, session, key, *args, **kwargs)
            self.owners[(session, key)] = self.owner
            return result
        finally:
            self.applying = False

    def settle(self, local, session, key, *args, **kwargs):
        self._load(local, session)
        self.applying = True
        try:
            return super().settle(local, session, key, *args, **kwargs)
        finally:
            self.applying = False

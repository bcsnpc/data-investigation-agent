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
    def transaction(self):
        try:
            self.connection.execute('BEGIN IMMEDIATE')
            yield self.connection
            self.connection.commit()
        except BaseException:
            self.connection.rollback()
            raise


class ReplayUsage(SharedUsage):
    def __init__(self, governor, tape):
        marker = tape.bootstrap['state']['shared_usage_replay']
        session = tape.bootstrap['state']['inputs']['session_id']
        if not tape.replaying or marker != declaration(session):
            raise TapeError('TAPE_SHARED_USAGE_CONTRACT_DIFFERS')
        self.sessions = frozenset(marker['fresh_sessions'])
        self.applying = False
        state = MemoryState()
        expected = {'policy': governor.policy,
                    'round_policy': governor.runtime.config.get('_estate', {}).get('round')}
        with state.transaction() as db:
            state.sql(db, 'INSERT INTO state_documents VALUES(?,?,?,?,?)',
                      ('usage_policy', governor.environment, 0, encoded(expected), sha(expected)))
        super().__init__(governor, state, owner='SEALED_FRESH_SESSION')

    def mirror(self, local):
        # The tape's checkpoint applies external deltas immediately AFTER this
        # pre-decision hook. Do not replace them from a stale memory snapshot.
        if self.applying:
            super().mirror(local)

    def _load(self, local, session):
        if session not in self.sessions:
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
                        values.append(self.owner if row[1] in self.sessions else 'EXTERNAL_BASELINE')
                    self.state.sql(db, 'INSERT INTO ' + target + '(' + ','.join(names) +
                                   ') VALUES(' + ','.join('?' for _ in values) + ')', values)

    def reserve(self, local, session, key, *args, **kwargs):
        self._load(local, session)
        self.applying = True
        try:
            return super().reserve(local, session, key, *args, **kwargs)
        finally:
            self.applying = False

    def settle(self, local, session, key, *args, **kwargs):
        self._load(local, session)
        self.applying = True
        try:
            return super().settle(local, session, key, *args, **kwargs)
        finally:
            self.applying = False

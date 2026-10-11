"""Keep sealed external budget inputs durable across caller rollbacks.

Only replay registers these rows. Caller-owned writes retain normal SQLite
transaction semantics; a rollback never commits them.
"""
import sqlite3


class ReplayBudgetConnection(sqlite3.Connection):
    def preserve_external_budget(self, changes):
        pending = getattr(self, '_external_budget', {})
        pending.update(changes)
        self._external_budget = pending

    def _restore_external_budget(self):
        pending = getattr(self, '_external_budget', {})
        self._external_budget = {}
        if not pending:
            return
        try:
            for (table, keys), (columns, key_columns, row) in pending.items():
                where = ' AND '.join('"' + c + '"=?' for c in key_columns)
                super().execute('DELETE FROM ' + table + ' WHERE ' + where, keys)
                if row is not None:
                    super().execute('INSERT INTO ' + table + ' VALUES (' +
                                    ','.join('?' for _ in columns) + ')', row)
            super().commit()
        except BaseException:
            super().rollback()
            raise

    def commit(self):
        super().commit()
        self._external_budget = {}

    def rollback(self):
        super().rollback()
        self._restore_external_budget()

    def execute(self, sql, *args, **kwargs):
        if getattr(self,'shared_accounting',None):
            from .shared_accounting import qualify
            sql=qualify(sql)
            self._budget_schema_query='shared_budget.sqlite_master' in sql
        command = sql.strip().rstrip(';').upper()
        if command.startswith('ROLLBACK TO') and getattr(self, '_external_budget', {}):
            from .process_tape import TapeError
            raise TapeError('TAPE_BUDGET_REPLAY_SAVEPOINT_UNSUPPORTED')
        result = super().execute(sql, *args, **kwargs)
        if command == 'ROLLBACK':
            self._restore_external_budget()
        elif command in ('COMMIT', 'END'):
            self._external_budget = {}
        return result

    def executemany(self,sql,*args,**kwargs):
        if getattr(self,'shared_accounting',None):
            from .shared_accounting import qualify
            sql=qualify(sql)
        return super().executemany(sql,*args,**kwargs)

    def __exit__(self, kind, value, traceback):
        if kind is not None:
            self.rollback()
        else:
            try:
                self.commit()
            except BaseException:
                self.rollback()
                raise
        return False

    def close(self):
        if getattr(self, '_external_budget', {}):
            self.rollback()
        super().close()


def preserve(db, staged, schemas):
    """Register already-validated external deltas before modifying SQLite."""
    if not staged or not db.in_transaction:
        return False
    hook = getattr(db, 'preserve_external_budget', None)
    if not callable(hook):
        from .process_tape import TapeError
        raise TapeError('TAPE_BUDGET_REPLAY_TRANSACTION_HOOK_REQUIRED')
    hook({(table, key): (schemas[table]['columns'], schemas[table]['keys'], row)
          for (table, key), row in staged.items()})
    return True

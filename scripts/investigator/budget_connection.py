"""Exact catalog connections prepared for the consumer-owned REAL journal.

Projected stores retain their privacy_storage connection path. This factory
preserves sqlite3's storage class and does not choose an installation class.
"""
import sqlite3

from .budget_delta_v2 import register_codec


def connect(*args, **kwargs):
    from .budget_replay_transaction import ReplayBudgetConnection
    kwargs.setdefault('factory', ReplayBudgetConnection)
    shared = kwargs.pop('shared_accounting', None)
    db = sqlite3.connect(*args, **kwargs)
    try:
        register_codec(db)
        if shared is not None:
            from .shared_accounting import attach
            attach(db,shared)
    except BaseException:
        db.close()
        raise
    return db

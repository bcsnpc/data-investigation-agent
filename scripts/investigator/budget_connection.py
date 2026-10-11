"""Exact catalog connections prepared for the consumer-owned REAL journal.

Projected stores retain their privacy_storage connection path. This factory
preserves sqlite3's storage class and does not choose an installation class.
"""
import sqlite3

from .budget_delta_v2 import register_codec


def connect(*args, **kwargs):
    db = sqlite3.connect(*args, **kwargs)
    try:
        register_codec(db)
    except BaseException:
        db.close()
        raise
    return db

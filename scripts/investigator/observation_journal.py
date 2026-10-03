"""Retain original observation objects as they are produced, also on a hold."""
from contextvars import ContextVar
from contextlib import contextmanager

_journal = ContextVar('process_observation_journal', default=None)


class Journal(list):
    pending_probes = ()


def pending(probes):
    journal = _journal.get()
    if journal is not None:
        journal.pending_probes = tuple(probes)


def record(observation):
    journal = _journal.get()
    if journal is not None and observation is not None:
        journal.append(observation)
    return observation


@contextmanager
def scope(journal):
    token = _journal.set(journal)
    try:
        yield
    finally:
        _journal.reset(token)

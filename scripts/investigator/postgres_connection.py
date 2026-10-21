"""Bounded platform PostgreSQL connection opening, never transaction replay."""
import time

CONNECT_TIMEOUT_SECONDS = 15
STATEMENT_TIMEOUT_MS = 30000


def connection_timeout(exc):
    # Only connection acquisition is retried. Auth, SQL, and transactions are not.
    if isinstance(exc, TimeoutError):
        return True
    return type(exc).__name__ == 'OperationalError' and any(
        text in str(exc).casefold() for text in ('connection timeout', 'connection timed out', 'timeout expired'))


def connect(*, connector=None, sleep=None, **kwargs):
    if connector is None:
        import psycopg
        connector = psycopg.connect
    sleep = sleep or time.sleep
    kwargs['connect_timeout'] = CONNECT_TIMEOUT_SECONDS
    options = kwargs.get('options', '')
    # Startup options cover the very first statement, before SET LOCAL exists.
    kwargs['options'] = options + ' -c statement_timeout=30000 -c lock_timeout=5000 -c idle_in_transaction_session_timeout=30000'
    for attempt in range(3):
        try:
            return connector(**kwargs)
        except Exception as exc:
            if attempt == 2 or not connection_timeout(exc):
                raise
            sleep((30, 60)[attempt])

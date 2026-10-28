"""Bounded platform PostgreSQL connection opening, never transaction replay."""
import time

CONNECT_TIMEOUT_SECONDS = 15
STATEMENT_TIMEOUT_MS = 30000


def database_token(credential_factory,client_id,*,clock=time.time,minimum_seconds=60):
    """Do not start a short transaction with an expired/expiring Entra token.

    Each acquisition uses the existing credential type and identity. The SDK
    owns renewal; a second fresh credential is tried once, without changing
    principal, audience, secret, role or server authentication settings.
    """
    for _ in range(2):
        with credential_factory(client_id=client_id) as credential:
            value=credential.get_token('https://ossrdbms-aad.database.windows.net/.default')
        expiry=getattr(value,'expires_on',None)
        if type(expiry) in (int,float) and expiry-clock()>minimum_seconds:
            return value.token
    raise RuntimeError('POSTGRES_TOKEN_RENEWAL_UNAVAILABLE')

def dropped_connection(error):
    if getattr(error,'postgres_connect_attempts',0):return False
    if isinstance(error,(ConnectionError,TimeoutError)):return True
    try:from psycopg import Error,OperationalError
    except ImportError:return False
    if not isinstance(error,Error):return False
    code=getattr(error,'sqlstate',None)
    return (code is None and isinstance(error,OperationalError)) or (code is not None and
        (code.startswith('08') or code in ('25P03','57P01','57P02','57P03')))


def connection_timeout(exc):
    # Only connection acquisition is retried. Auth, SQL, and transactions are not.
    if isinstance(exc, TimeoutError):
        return True
    operational=type(exc).__name__=='OperationalError'
    try:
        from psycopg import OperationalError
        operational=operational or isinstance(exc,OperationalError)
    except ImportError:pass
    if str(getattr(exc,'sqlstate','') or '').startswith('28'):return False
    return operational and any(
        text in str(exc).casefold() for text in ('connection timeout', 'connection timed out', 'timeout expired'))


def connect(*, connector=None, sleep=None, **kwargs):
    if connector is None:
        import psycopg
        connector = psycopg.connect
    sleep = sleep or time.sleep
    kwargs['connect_timeout'] = CONNECT_TIMEOUT_SECONDS
    kwargs.update(keepalives=1,keepalives_idle=30,keepalives_interval=10,keepalives_count=3)
    options = kwargs.get('options', '')
    # Startup options cover the very first statement, before SET LOCAL exists.
    kwargs['options'] = options + ' -c statement_timeout=30000 -c lock_timeout=5000 -c idle_in_transaction_session_timeout=30000'
    for attempt in range(2):
        started=time.monotonic()
        try:
            return connector(**kwargs)
        except Exception as exc:
            exc.postgres_connection_timing={'operation':'connect','idle_before_request_seconds':None,
                'failed_request_seconds':round(max(0,time.monotonic()-started),6),
                'attempt':attempt+1,'meaning':'Connection acquisition failed before a session was obtained; not evidence of an idle socket drop.'}
            if attempt == 1 or not connection_timeout(exc):
                exc.postgres_connect_attempts=attempt+1
                raise
            sleep(30)


class ObservedConnection:
    """No arguments or SQL text in drop diagnostics; no statement replay.

    The interval is client-observed time since the last response, not a claim
    about server-side session state. Used for one short shared transaction.
    """
    def __init__(self,connection,*,clock=time.monotonic):
        self.connection=connection;self.clock=clock
        self.opened=self.responded=clock()

    def __getattr__(self,name):return getattr(self.connection,name)

    def _call(self,operation,call,*args,**kwargs):
        started=self.clock();idle=max(0,started-self.responded)
        try:
            closed=getattr(self.connection,'closed',False)
            if type(closed) in (bool,int) and closed:raise ConnectionError('POSTGRES_STALE_SOCKET_CLOSED')
            result=call(*args,**kwargs)
        except Exception as error:
            timing={'operation':operation,'idle_before_request_seconds':round(idle,6),
                'failed_request_seconds':round(max(0,self.clock()-started),6),
                'connection_age_seconds':round(max(0,self.clock()-self.opened),6),
                'meaning':'Client interval since last response; server idle-drop cause unproven.'}
            error.postgres_connection_timing=timing
            import json
            error.add_note('POSTGRES_CONNECTION_TIMING '+json.dumps(timing,sort_keys=True))
            raise
        self.responded=self.clock()
        return result

    def execute(self,*args,**kwargs):return self._call('execute',self.connection.execute,*args,**kwargs)
    def commit(self):return self._call('commit',self.connection.commit)
    def rollback(self):return self._call('rollback',self.connection.rollback)
    def cursor(self,*args,**kwargs):return ObservedCursor(self,self.connection.cursor(*args,**kwargs))


class ObservedCursor:
    def __init__(self,connection,cursor):self.connection,self.raw=connection,cursor
    def __getattr__(self,name):return getattr(self.raw,name)
    def __enter__(self):self.raw.__enter__();return self
    def __exit__(self,*args):return self.raw.__exit__(*args)
    def execute(self,*args,**kwargs):return self.connection._call('cursor.execute',self.raw.execute,*args,**kwargs)
    def executemany(self,*args,**kwargs):return self.connection._call('cursor.executemany',self.raw.executemany,*args,**kwargs)

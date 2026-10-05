"""Bounded retry of documented Azure SQL transient connection failures only."""
import time
from datetime import datetime, timezone
import subprocess
from investigator.process_tape import utc_now, ACTIVE, TapeError
from investigator.onboarding import Conflict

# Microsoft Learn: troubleshoot-common-errors-issues#transient-fault-error-messages-40197-40613-and-others
# Deliberately excludes authentication/firewall/quota failures and error text.
TRANSIENT_CONNECTION_ERRORS = frozenset((615,926,4060,4221,40197,40501,40613,49918,49919,49920))


def read_with_retry(read, sleep=time.sleep, *, serverless=False, record_wait=None):
    attempts = []
    # Bounded additional waiting, not a promise that a paused/free-quota source
    # will become available. Each attempt must pass physical admission anew.
    delays=(5,10,20,25) if serverless else (10,20)
    for index in range(len(delays)+1):
        started = utc_now()
        try:
            if index:
                from investigator.physical_reads import retry_connection
                result = retry_connection(lambda: _read_attempt(read))
            else:
                result = _read_attempt(read)
        except subprocess.TimeoutExpired:
            result = {'error': 'SQL_READ_TIMEOUT', 'stage': 'unknown'}
        except (Conflict,TapeError):
            # Admission/refusal and sealed replay failures are not SQL responses.
            raise
        except (ValueError, TypeError):
            result = {'error': 'SQL_RESPONSE_INVALID', 'stage': 'unknown'}
        retryable = (result.get('error') == 'SQL_READ_FAILED'
                     and result.get('stage') == 'connect'
                     and result.get('sql_error_number') in TRANSIENT_CONNECTION_ERRORS)
        paused=(serverless and result.get('error')=='SQL_READ_FAILED'
                and result.get('stage')=='connect' and result.get('sql_error_number')==40613)
        # Serverless declaration does not authorize longer retries of other
        # transient signatures. It specifically enables the paused signature.
        if serverless:retryable=paused
        delay = delays[index] if retryable and index < len(delays) else 0
        attempts.append({'attempt': index + 1, 'started_at': started,
                         'finished_at': utc_now(),
                         'status': 'FAILED' if result.get('error') else 'SUCCEEDED',
                         'stage': result.get('stage'), 'sql_error_number': result.get('sql_error_number'),
                         'retry_delay_seconds': delay})
        if paused:attempts[-1]['condition']='source paused; waiting for resume'
        if not delay:
            return dict(result, connection_attempts=attempts)
        tape=ACTIVE.get()
        if tape is None or not tape.replaying:
            if record_wait:record_wait(delay,lambda:sleep(delay))
            else:sleep(delay)


def _read_attempt(read):
    result=read()
    if result.get('error')=='SQL_READ_FAILED' and result.get('stage')=='connect':
        from investigator.physical_reads import connection_failure
        connection_failure(result.get('sql_error_number'))
    return result

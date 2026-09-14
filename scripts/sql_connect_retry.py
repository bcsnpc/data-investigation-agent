"""Bounded retry of Azure SQL auto-resume failures before query execution."""
import time
from datetime import datetime, timezone
import subprocess


def read_with_retry(read, sleep=time.sleep):
    attempts = []
    for index in range(3):
        started = datetime.now(timezone.utc).isoformat()
        try:
            result = read()
        except subprocess.TimeoutExpired:
            result = {'error': 'SQL_READ_TIMEOUT', 'stage': 'unknown'}
        except (ValueError, TypeError):
            result = {'error': 'SQL_RESPONSE_INVALID', 'stage': 'unknown'}
        retryable = (result.get('error') == 'SQL_READ_FAILED'
                     and result.get('stage') == 'connect'
                     and result.get('sql_error_number') == 40613)
        delay = (10, 20)[index] if retryable and index < 2 else 0
        attempts.append({'attempt': index + 1, 'started_at': started,
                         'finished_at': datetime.now(timezone.utc).isoformat(),
                         'status': 'FAILED' if result.get('error') else 'SUCCEEDED',
                         'stage': result.get('stage'), 'sql_error_number': result.get('sql_error_number'),
                         'retry_delay_seconds': delay})
        if not delay:
            return dict(result, connection_attempts=attempts)
        sleep(delay)

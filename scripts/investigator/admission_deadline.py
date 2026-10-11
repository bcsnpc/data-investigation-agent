"""Optional owner-installed admission cutoff; in-flight workers still finish."""
from datetime import datetime
import os


class AdmissionClosed(ValueError):
    pass


def require_open():
    value=os.environ.get('INVESTIGATOR_LIVE_ADMISSION_DEADLINE')
    if value is None:return
    cutoff=datetime.fromisoformat(value)
    if cutoff.tzinfo is None:raise ValueError('ADMISSION_DEADLINE_TIMEZONE_REQUIRED')
    if datetime.now().astimezone().timestamp()>=cutoff.timestamp():
        raise AdmissionClosed('LIVE_ADMISSION_DEADLINE_REACHED')

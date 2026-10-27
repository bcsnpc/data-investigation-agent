"""Fixture-control plans and bounded read retry; no installed transport or identity.

The caller journals the original native definition, verifies the served plan,
waits for its owned job to terminate and restores the original semantic hash.
This does not alter the investigator's image, deadlines or budget authority.
"""
import base64
from copy import deepcopy
import time

from .apply import PipelineFailureScenario
from investigator.process_tape import bytes_of


def source_read_after_resume(read, *, sleep=time.sleep):
    """Retry one read after native serverless-unavailable, never a mutation.

    The callback receives a distinct ordinal so the caller can preserve both
    receipts and charge both physical dispatches. Other errors are unchanged.
    """
    result = read(0)
    if result.get('exit') and result.get('body', {}).get('error_number') == 40613:
        sleep(30)
        return read(1)
    return result


def copy_timeout_window(before, *, minutes=30):
    if type(minutes) is not int or not 10 <= minutes <= 60:
        raise ValueError('COPY_CONTROL_RUNTIME_BOUND')
    result = deepcopy(before)
    content = PipelineFailureScenario.content(before)
    selected = [a for a in content['properties']['activities']
                if a.get('type') == 'InvokeCopyJob']
    if not selected:
        raise ValueError('NATIVE_COPY_ACTIVITY_REQUIRED')
    for activity in selected:
        activity.setdefault('policy', {})['timeout'] = f'0.{minutes // 60:02}:{minutes % 60:02}:00'
    part = next(p for p in result['definition']['parts']
                if p['path'] == 'pipeline-content.json')
    part['payload'] = base64.b64encode(bytes_of(content)).decode()
    return result

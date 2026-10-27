"""Pure plans for a temporary copy-job control window; no transport or identity.

The caller journals the original native definition, verifies the served plan,
waits for its owned job to terminate and restores the original semantic hash.
This does not alter the investigator's image, deadlines or budget authority.
"""
import base64
from copy import deepcopy

from .apply import PipelineFailureScenario
from investigator.process_tape import bytes_of


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

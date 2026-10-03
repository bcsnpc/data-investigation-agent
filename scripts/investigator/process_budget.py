"""Separate diagnostic sub-budgets within the unchanged run ceiling."""
from contextlib import contextmanager
from contextvars import ContextVar
from .usage_governance import UsageHold

_phase = ContextVar('diagnostic_phase', default='WALK')


def current():
    return _phase.get()


@contextmanager
def phase(name):
    if name not in ('WALK', 'REPRODUCTION'):
        raise ValueError('Unknown diagnostic phase')
    token = _phase.set(name)
    try:
        yield
    finally:
        _phase.reset(token)


def allocation(cap, scope):
    from .question_kind import reproduction
    possible = reproduction(scope)['applicable'] or bool(
        (scope.get('selection_request') or scope.get('definition_target')) and scope.get('report_binding'))
    side = min(4, cap // 2) if possible else 0
    return {'WALK': cap - side, 'REPRODUCTION': side}


def remaining(state):
    limits = allocation(state['envelope']['limits']['cloud_calls'], state['envelope'])
    name = current()
    used = state.get('diagnostic_phase_counts', {}).get(name, 0)
    return min(state['envelope']['limits']['cloud_calls'] - state['cloud_calls'], limits[name] - used)


def admit(state, tool):
    if remaining(state) <= 0:
        raise UsageHold('Diagnostic ' + current().lower() + ' sub-budget exhausted before ' + tool)


def charge(state):
    counts = state.setdefault('diagnostic_phase_counts', {'WALK': 0, 'REPRODUCTION': 0})
    counts[current()] += 1

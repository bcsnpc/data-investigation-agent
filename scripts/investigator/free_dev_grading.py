"""Classify free DEV outcomes without hiding engine errors or budget stops.

These are reporting decisions, never changes to an outcome or a grader score.
Missing counters remain unknown; a partial run is not evidence of zero calls.
"""
import math


ENVIRONMENT_STOPS = frozenset({
    'ProviderUnavailable: NVIDIA_TRANSPORT_UNAVAILABLE_ENVIRONMENT_AFFECTED',
    'ProviderUnavailable: NVIDIA_ASYNC_RESULT_PENDING_ENVIRONMENT_AFFECTED',
})


def result_body(value):
    result = value.get('result', value)
    if not isinstance(result, dict):
        raise ValueError('FREE_DEV_RESULT_OBJECT_REQUIRED')
    return result


def disposition(value):
    result = result_body(value)
    status = result.get('status')
    if status in ('UNESTABLISHED', 'ENVIRONMENT_AFFECTED'):
        return 'ENVIRONMENT_UNSCORED'
    if status == 'INTERRUPTED':
        if result.get('stop') in ENVIRONMENT_STOPS:
            return 'ENVIRONMENT_UNSCORED'
        # INTERRUPTED is also the normal envelope for initialization errors
        # and exhausted per-run limits. Neither may disappear from the score.
        if str(result.get('stop', '')).startswith(('UsageHold:', 'SpendHold:')):
            return 'SCORED_BUDGET_STOP'
        return 'SCORED_ENGINE_INTERRUPTION'
    return 'SCORED_OUTCOME'


def gradeable_result(value):
    return disposition(value) != 'ENVIRONMENT_UNSCORED'


def _number(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            if value >= 0 and math.isfinite(value):
                return value
        except OverflowError:
            pass
    return None


def metrics(value):
    result = result_body(value)
    timing = result.get('timing')
    cost = result.get('cost')
    timing = timing if isinstance(timing, dict) else {}
    cost = cost if isinstance(cost, dict) else {}
    charged = _number(cost.get('charged_microdollars'))
    return {
        'physical_requests': _number(result.get('physical_requests')),
        'model_calls': _number(result.get('model_calls')),
        'investigator_cost_usd': None if charged is None else charged / 1e6,
        'engine_wall_seconds': _number(timing.get('wall_seconds')),
        'model_seconds': _number(timing.get('model_seconds')),
        'native_query_seconds': _number(timing.get('native_query_sum_seconds')),
    }

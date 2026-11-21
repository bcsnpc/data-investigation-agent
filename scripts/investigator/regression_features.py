"""Trusted installation-only R26/R27 ablations. Safety/budget/identity are never flags."""
import json
from pathlib import Path
from contextvars import ContextVar
from contextlib import contextmanager

FEATURES=json.loads(Path(__file__).with_suffix('.json').read_text(encoding='utf-8'))['features']
DEFAULTS={key:value['default'] for key,value in FEATURES.items()}
ACTIVE=ContextVar('investigator_regression_features',default=None)

def validate(overrides):
    if not isinstance(overrides,dict) or not set(overrides)<=DEFAULTS.keys():
        raise ValueError('UNKNOWN_REGRESSION_FEATURE')
    if any(type(value)is not bool for value in overrides.values()):
        raise ValueError('REGRESSION_FEATURE_BOOLEAN_REQUIRED')
    return {**DEFAULTS,**overrides}

def snapshot():
    return dict(ACTIVE.get() or DEFAULTS)

def enabled(name):
    if name not in DEFAULTS:raise ValueError('UNKNOWN_REGRESSION_FEATURE:'+name)
    return (ACTIVE.get() or DEFAULTS)[name]

@contextmanager
def configured(overrides):
    token=ACTIVE.set(validate(overrides))
    try:yield snapshot()
    finally:ACTIVE.reset(token)

def baseline_prompt(name):
    return json.loads(Path(__file__).with_name("regression_baseline_prompts.json").read_text(encoding="utf-8"))["prompts"][name]

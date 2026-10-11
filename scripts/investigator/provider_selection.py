"""Request-local model selection; never mutates process-wide provider settings."""
from contextlib import contextmanager
from contextvars import ContextVar

DEPLOYMENT = ContextVar('investigator_provider_deployment', default=None)

@contextmanager
def agent_selection(runtime):
    selected = runtime.config.get('_estate', {}).get('investigation', {}).get('agent_deployment')
    if selected is None:
        yield
        return
    mode = runtime.config['_estate']['investigation'].get('mode')
    if mode not in ('AGENT', 'HYBRID') or not isinstance(selected, str) or not selected.strip():
        raise ValueError('AGENT_DEPLOYMENT_CONFIGURATION')
    token = DEPLOYMENT.set(selected)
    try:
        yield
    finally:
        DEPLOYMENT.reset(token)

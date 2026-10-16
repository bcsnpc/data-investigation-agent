"""Request-local candidate accounting; legacy form counters remain compatible."""
from contextlib import contextmanager
from contextvars import ContextVar
from .form_candidates import NotMeasurable

ACTIVE=ContextVar('governed_candidate_read_budget',default=None)

@contextmanager
def scope(session_id,used,cap):
    if type(used)is not int or type(cap)is not int or not 0<=used<=cap<=12:
        raise ValueError('Candidate read budget is invalid')
    state={'session_id':session_id,'used':used,'cap':cap}
    token=ACTIVE.set(state)
    try:yield state
    finally:ACTIVE.reset(token)

def consume(workspace):
    state=ACTIVE.get()
    if state is not None:
        if state['used']>=state['cap']:raise NotMeasurable('Candidate diagnostic cap reached')
        ordinal=state['used'];state['used']+=1
        return state['session_id'],ordinal
    ordinal=getattr(workspace,'_form_candidate_count',0)
    if ordinal>=workspace.dynamic_read_limit:raise NotMeasurable('Per-form diagnostic cap reached')
    workspace._form_candidate_count=ordinal+1
    return workspace._form_candidate_session,ordinal

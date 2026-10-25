"""Closed, value-free source failure classes; an outage is never a negative row."""
from datetime import datetime, timezone
import socket
import re
from urllib.error import URLError

MESSAGES={
    'TIMEOUT':'The source did not answer before the request deadline.',
    'UNREACHABLE':'The source could not be reached over the network.',
    'CAPACITY_UNAVAILABLE':'The source capacity is paused or unavailable.',
    'AUTHENTICATION_EXPIRED':'The source sign-in failed or expired; check the reader credential.',
    'PERMISSION_REFUSED':'The source refused this reader permission.',
    'THROTTLED':'The source is rate limiting requests.',
    'QUERY_ERROR':'The source query or its declared read route could not be completed.'}
TRANSIENT=frozenset({'TIMEOUT','UNREACHABLE','CAPACITY_UNAVAILABLE','THROTTLED'})

def classify(error):
    """Use typed status/provider codes; never publish arbitrary exception prose."""
    nested=error.reason if isinstance(error,URLError) and isinstance(error.reason,BaseException) else error
    status=next((getattr(error,k)for k in ('http_status','status_code','code')if type(getattr(error,k,None))is int),None)
    number=getattr(error,'error_number',None)
    code=getattr(error,'provider_code',None)
    safe=getattr(error,'safe_reason','')
    if status is None and isinstance(safe,str) and re.fullmatch(r'HTTP_[0-9]{3}',safe):status=int(safe[5:])
    if status==429 or number in (40501,10928,10929):return 'THROTTLED'
    if code in ('CapacityNotActive','CapacityPaused') or number in (40613,40197) or status==503:return 'CAPACITY_UNAVAILABLE'
    if status==401 or number==18456 or code=='Unauthorized':return 'AUTHENTICATION_EXPIRED'
    if isinstance(error,PermissionError) or status==403 or number in (229,230,262) or code in ('Forbidden','AccessDenied','InsufficientPrivileges','InsufficientPermissions'):return 'PERMISSION_REFUSED'
    if isinstance(nested,TimeoutError) or status in (408,504) or number==-2 or getattr(error,'sqlstate',None) in ('HYT00','HYT01'):return 'TIMEOUT'
    if isinstance(nested,(ConnectionError,socket.gaierror)) or status in (502,):return 'UNREACHABLE'
    return 'QUERY_ERROR'

class QuantityNotComparable(ValueError):
    """The compiler refused a faithful quantity; no source call failed."""

class SourceReadUnavailable(ValueError):
    """Preserve safe native fields already retained by the compiled read port."""
    def __init__(self,reason,failure):
        super().__init__(reason)
        if isinstance(failure,dict):
            for field in ('http_status','status_code','error_number','sqlstate','provider_code'):
                value=failure.get(field)
                if isinstance(value,(int,str)):setattr(self,field,value)

def result(error,*,at,attempts=1,first_at=None):
    kind=classify(error) if error is not None else None
    return {'reachable':error is None,'failure_class':kind,'message':MESSAGES[kind] if kind else 'The bounded source read succeeded.',
        'first_observed_at':first_at or at,'last_observed_at':at,'attempts':attempts,
        'retryable':kind in TRANSIENT,'owner':'source or capacity owner' if kind in ('UNREACHABLE','CAPACITY_UNAVAILABLE','TIMEOUT') else 'identity/access owner' if kind in ('AUTHENTICATION_EXPIRED','PERMISSION_REFUSED') else 'pipeline or source owner'}

def call(operation,*,observe,clock=None,sleep=None):
    """Retry transient reads twice, retaining each failed attempt before retry.

    The operation keeps its original gateway/meter; this adds no allowance.
    Budget, secret and policy refusals propagate without becoming outages.
    """
    from .estate_graph_incremental import is_stop_condition
    from .planner_recording import _safe
    from .estate_graph_contract import canonical
    clock=clock or (lambda:datetime.now(timezone.utc).isoformat())
    if sleep is None:
        from .model_transport_retry import backoff
        sleep=lambda seconds:backoff(1 if seconds==30 else 2)
    first=clock()
    for attempt in range(1,4):
        try:value=operation()
        except Exception as error:
            if isinstance(error,QuantityNotComparable):raise
            if is_stop_condition(error):raise
            entry=result(error,at=clock(),first_at=first,attempts=attempt)
            _safe(canonical(entry).encode());observe(entry)
            if entry['retryable'] and attempt<3:sleep(30 if attempt==1 else 45);continue
            try:error.source_availability=entry
            except (AttributeError,TypeError):pass
            raise
        observe(result(None,at=clock(),first_at=first,attempts=attempt))
        return value

def fact(subject,value,*,at,evidence,collector):
    from .facts_collectors import observation
    return observation(subject,'AVAILABILITY',value,at,evidence,collector)

"""Pending transport-layer retries of one frozen read request; no ticket retry."""
import copy
from investigator import physical_reads,process_tape as journal
from investigator.model_transport_retry import backoff

class PhysicalThrottle(RuntimeError):
    http_status=429

def rejected(exc):
    return any(getattr(exc,key,None)==429 for key in ('http_status','status_code','code'))

def execute(request,transport,tool):
    tape=journal.ACTIVE.get();physical=physical_reads._scope.get()
    # Archived captures retain their original transport and accounting order.
    if physical is None or (tape is not None and tape.replaying and tape.bootstrap.get('state',{}).get('physical_transport_retries')!=2):
        return transport(request)
    sealed=journal.bytes_of(request)
    def call():
        result=transport(copy.deepcopy(request))
        if isinstance(result,dict) and result.get('status')=='UNAVAILABLE' and type(result.get('http_status')) is int and result['http_status']==429:
            raise PhysicalThrottle('Physical reader returned HTTP 429')
        return result
    for attempt in (1,2,3):
        if journal.bytes_of(request)!=sealed:raise ValueError('Read retry changed frozen request')
        try:
            if attempt==1:return call()
            # Existing meter must atomically admit and retain each physical
            # attempt, preserving its unchanged run deadline and all guards.
            return physical['meter'](tool,call)
        except Exception as exc:
            if attempt==1 and rejected(exc) and physical['first']:
                physical['first']=False
                physical['first_report']={'status':'FAILED','request_kind':tool,'http_status':429,'transport_attempt':1}
            if not rejected(exc) or attempt==3:raise
            journal.event('CONFIGURATION',{'control':'READ_TRANSPORT_RETRY','tool':tool,'http_status':429,
                'completed_attempt':attempt,'next_attempt':attempt+1,'request_hash':__import__('hashlib').sha256(sealed).hexdigest()})
            backoff(attempt)


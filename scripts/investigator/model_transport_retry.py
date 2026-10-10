"""Pending generic retry consumer; install only with owner admission callbacks.

Every logical owner must bind its original reservation. Retrying an unbound
provider is refused. Owner callbacks enforce phase/deadline/local call bounds in
the same transaction as a new daily reservation; no ticket is submitted twice.
"""
from contextlib import contextmanager
from contextvars import ContextVar
import copy,time
from investigator import process_tape as journal

ACTIVE=ContextVar('model_transport_retry',default=None)


class Scope:
    def __init__(self,governor,session_id,key,characters,output_tokens,admit_extra,metadata,deadline,clock):
        if governor is None or not callable(admit_extra):raise ValueError('Retry requires governed owner admission')
        self.governor=governor;self.session_id=session_id;self.original=key;self.current=key
        self.characters=characters;self.output_tokens=output_tokens
        self.admit_extra=admit_extra;self.metadata=metadata
        self.deadline=deadline;self.clock=clock
    def settle(self,usage=None,uncertain=False):
        from .local_accounting import boundary
        def settle():
            with self.governor.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE')
                self.governor.settle(db,self.session_id,self.current,usage,uncertain=uncertain)
        return boundary('MODEL_OWNER_SETTLE',settle)
    def reserve(self,attempt):
        key=self.original+':transport-retry:'+str(attempt-1)
        with self.governor.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE')
            committed=self.admit_extra(db,key,self.characters,self.output_tokens)
            self.governor.reserve(db,self.session_id,key,'planner',self.characters,output_tokens=self.output_tokens)
        self.current=key
        if callable(committed):committed()  # In-memory counters only after durable admission.


@contextmanager
def scope(governor,session_id,key,characters,output_tokens,*,admit_extra,metadata=None,deadline=None,clock=time.time):
    tape=journal.ACTIVE.get()
    if tape is not None and tape.replaying and getattr(tape,'bootstrap',{}).get('state',{}).get('provider_transport_retries')!=2:
        # Archived captures predate physical model retry accounting. Replay
        # their original operation/event ordering, including old refusals.
        yield None
        return
    value=Scope(governor,session_id,key,characters,output_tokens,admit_extra,metadata or {},deadline,clock)
    token=ACTIVE.set(value)
    try:yield value
    finally:ACTIVE.reset(token)


def timeout(maximum):
    owner=ACTIVE.get()
    if owner is None or owner.deadline is None:return maximum
    remaining=owner.deadline-owner.clock()
    if remaining<1:
        from investigator.usage_governance import UsageHold
        raise UsageHold('Transport retry cannot fit the existing deadline')
    return min(maximum,remaining)


def backoff(attempt):
    seconds=2**attempt  # 2 and 4 seconds; never a long blocking sleep.
    def wait():
        time.sleep(seconds)
        return {'attempt':attempt,'seconds':seconds,'completed':True}
    saved=journal.value('CONFIGURATION','provider_transport_backoff',wait)
    if saved!={'attempt':attempt,'seconds':seconds,'completed':True}:
        raise journal.TapeError('PROVIDER_BACKOFF_CONTROL_DIFFERS')


def is_throttle(exc):return getattr(exc,'status_code',None)==429 or getattr(exc,'code',None)==429


def dispatch(body,invoke):
    """invoke must own one HTTP call and one dollar guard, SDK retries disabled."""
    owner=ACTIVE.get();sealed=journal.bytes_of(body)
    for attempt in (1,2,3):
        if journal.bytes_of(body)!=sealed:raise ValueError('Transport retry changed the provider body')
        if attempt>1:owner.reserve(attempt)
        try:
            if attempt==1:response=invoke(body)
            else:
                from investigator.planner_recording import recording
                with recording({**owner.metadata,'session_id':owner.session_id,'transport_attempt':attempt,
                    'original_reservation':owner.original,'reservation':owner.current,
                    'retry_reason':'PROVIDER_HTTP_429'},distinct=True):
                    response=invoke(body)
            usage=getattr(response,'usage',None)
            usage=usage.model_dump() if hasattr(usage,'model_dump') else usage
            if owner:owner.settle(usage,uncertain=usage is None)
            return response
        except Exception as exc:
            if owner:owner.settle(getattr(exc,'usage',None),uncertain=True)
            if not is_throttle(exc) or attempt==3:raise
            if owner is None:
                tape=journal.ACTIVE.get()
                if tape is not None and getattr(tape,'bootstrap',{}).get('state',{}).get('provider_transport_retries')==2:
                    journal.event('CONFIGURATION',{'control':'PROVIDER_THROTTLE_UNRETRIED','reason':'NO_GOVERNED_TRANSPORT_RETRY_SCOPE','http_status':429})
                raise
            journal.event('CONFIGURATION',{'control':'PROVIDER_TRANSPORT_RETRY','completed_attempt':attempt,
                'http_status':429,'original_reservation':owner.original,'next_attempt':attempt+1})
            backoff(attempt)


def intake_scope(intake,body,payload,key):
    from investigator.question_intake import reservation_characters,reservation_output_tokens,snapshot,fingerprint
    from investigator.onboarding import digest
    from investigator.usage_governance import UsageHold
    governor=intake.workspace.agent.governor
    if governor is None:
        from contextlib import nullcontext
        return nullcontext()
    sid='intake:'+body['id'];size=reservation_characters(intake.resolver,payload)
    output=reservation_output_tokens(intake.resolver,payload)
    def admit(db,retry_key,characters,tokens):
        import json
        row=db.execute('SELECT body,hash FROM workspace_intakes WHERE id=?',(body['id'],)).fetchone()
        current=json.loads(row['body']) if row else None
        if current is None or digest(current)!=row['hash'] or current['status']!='RESOLVING':
            raise UsageHold('Intake transport retry is no longer admitted')
        if (digest(snapshot(intake.workspace))!=current['catalog_hash'] or fingerprint()!=current['engine_hash']
                or digest(intake.workspace.agent.config)!=current['config_hash']
                or digest(intake.workspace.agent.planner_profile)!=current['planner_hash']):
            raise UsageHold('Intake transport retry context changed')
        if intake.workspace.clock()>=current['expires']:raise UsageHold('Intake transport retry deadline')
        reserved=[json.loads(r[0]) for r in db.execute('SELECT reserved FROM adaptive_usage WHERE environment=? AND session_id=?',
            (governor.environment,sid))]
        if len(reserved)>=6 or sum(r['input_characters'] for r in reserved)+characters>intake.workspace.dynamic_input_limit:
            raise UsageHold('Intake transport retry local call or input limit')
        event={'reservation_key':retry_key,'input_characters':characters,'output_tokens':tokens,'reason':'PROVIDER_HTTP_429'}
        current.setdefault('transport_attempts',[]).append(event)
        intake.save(db,current)
        def committed():body['transport_attempts']=copy.deepcopy(current['transport_attempts'])
        return committed
    return scope(governor,sid,key,size,output,admit_extra=admit,deadline=body['expires'],clock=intake.workspace.clock,
        metadata={'phase':'INTAKE_TRANSPORT_RETRY','context_version':body.get('context_id')})


def adaptive_scope(agent,identity,key,size,output,phase):
    from investigator.usage_governance import UsageHold
    if agent.governor is None:
        from contextlib import nullcontext
        return nullcontext()
    with agent.runtime.db() as db:initial=agent.load(db,identity)
    def admit(db,retry_key,characters,tokens):
        current=agent.load(db,identity);agent.admit(current,db)
        if current['status']!=phase or agent.clock()>=current['deadline']:
            raise UsageHold('Investigation transport retry phase or deadline changed')
        calls=current['planner_calls']+current.get('transport_planner_calls',0)
        if calls>=current['envelope']['limits']['planner_calls'] or current['input_characters']+characters>current['envelope']['limits']['input_characters']:
            raise UsageHold('Investigation transport retry local call or input limit')
        current['transport_planner_calls']=current.get('transport_planner_calls',0)+1
        current['input_characters']+=characters
        agent.save(db,current,'MODEL_TRANSPORT_RESERVED',{'reservation_key':retry_key,'input_characters':characters,'reason':'PROVIDER_HTTP_429'})
    return scope(agent.governor,identity,key,size,output,admit_extra=admit,deadline=initial['deadline'],clock=agent.clock,
        metadata={'phase':phase+'_TRANSPORT_RETRY','context_version':initial.get('discovery_version')})


def synthesis_scope(agent,identity,key,size,deadline):
    from investigator.evidence_synthesis import read,save
    from investigator.onboarding import digest
    from investigator.usage_governance import UsageHold
    if agent.governor is None:
        from contextlib import nullcontext
        return nullcontext()
    def admit(db,retry_key,characters,tokens):
        current=read(db,identity,full=True);source=agent.load(db,identity)
        if not current or current['status']!='RUNNING' or agent.clock()>=current['deadline']:
            raise UsageHold('Synthesis transport retry phase or deadline changed')
        agent.admit(source,db)
        if digest(source)!=current['source_hash']:raise UsageHold('Synthesis frozen investigation changed')
        if current.get('transport_calls',0)>=4:raise UsageHold('Synthesis transport retry local call limit')
        current['transport_calls']=current.get('transport_calls',0)+1
        current.setdefault('transport_attempts',[]).append({'reservation_key':retry_key,'input_characters':characters,
            'output_tokens':tokens,'reason':'PROVIDER_HTTP_429'})
        save(db,identity,current,source_state=source)
    return scope(agent.governor,identity,key,size,agent.generation_options['max_output_tokens'],admit_extra=admit,
        deadline=deadline,clock=agent.clock,metadata={'phase':'SYNTHESIS_TRANSPORT_RETRY'})


def retry_read(request,invoke_once,record_control):
    """Each invoke_once must separately meter and receipt one physical read.

    This helper never owns a free transport or bypasses guards. Call it inside a
    logical read, with invoke_once wrapping the existing physical admission.
    """
    sealed=journal.bytes_of(request)
    for attempt in (1,2,3):
        if journal.bytes_of(request)!=sealed:raise ValueError('Transport retry changed the read request')
        try:return invoke_once(copy.deepcopy(request))
        except Exception as exc:
            if not is_throttle(exc) or attempt==3:raise
            record_control({'control':'READ_TRANSPORT_RETRY','completed_attempt':attempt,'next_attempt':attempt+1,'http_status':429})
            backoff(attempt)

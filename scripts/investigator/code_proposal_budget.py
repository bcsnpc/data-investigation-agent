"""Govern a code-only model handoff using the existing usage reservation store."""
from .onboarding import encoded
from .usage_governance import UsageHold
from .process_tape import clock as tape_clock
from .planner_recording import recording
import time


class Proposer:
    input_fields=frozenset(('code','layers'))
    phase='CODE_BINDING_PROPOSAL'
    reservation_prefix='code-binding-proposal:'
    response_type=list
    def __init__(self,provider,*,governor,session_id,options,deadline,max_calls,max_input,
                 event,context_version,clock=time.time):
        self.provider=provider;self.governor=governor;self.session_id=session_id
        from .generation_policy import validate
        self.options=validate(options);self.deadline=deadline;self.max_calls=max_calls;self.max_input=max_input
        self.event=event;self.context_version=context_version;self.clock=clock
        self.calls=0;self.input_characters=0

    def __call__(self,payload,schema):
        if set(payload)!=self.input_fields:raise ValueError('Proposal input differs from its closed handoff')
        size=len(encoded(payload))
        if size>self.options['max_payload_characters']:raise UsageHold('Code proposal per-call input limit')
        if self.calls>=self.max_calls or self.input_characters+size>self.max_input:
            raise UsageHold('Code proposal cumulative call or input limit')
        if tape_clock('code-proposal',self.clock)+self.options['timeout_seconds']>self.deadline:
            raise UsageHold('Code proposal deadline admission')
        number=self.calls+1;key=self.reservation_prefix+str(number)
        with self.governor.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE')
            self.governor.reserve(db,self.session_id,key,'planner',size,
                output_tokens=self.options['max_output_tokens'])
        self.calls=number;self.input_characters+=size
        self.event(self.phase+'_RESERVED',{'call':number,'input_characters':size,'reservation_key':key})
        metadata=None;received=False
        try:
            with recording({'session_id':self.session_id,'phase':self.phase,'planner_call':number,
                'context_version':self.context_version,'payload':payload,
                'reservation':{'key':key,'input_characters':size,'output_tokens':self.options['max_output_tokens']}}):
                proposals,metadata=self.provider(payload,schema,self.options);received=True
            if not isinstance(proposals,self.response_type):raise ValueError('Proposal provider returned an invalid response shape')
            self.event(self.phase+'_COMPLETED',{'call':number,'proposals':len(proposals) if self.response_type is list else 1})
            return proposals
        except Exception as exc:
            metadata=metadata or getattr(exc,'provider_metadata',None)
            self.event(self.phase+'_FAILED',{'call':number,'error_type':type(exc).__name__})
            raise
        finally:
            usage=metadata.get('usage') if isinstance(metadata,dict) else None
            with self.governor.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE')
                self.governor.settle(db,self.session_id,key,usage,uncertain=not received and not usage)

"""Observational outer timings; never native tape clocks or semantic inputs."""
import time
from datetime import datetime,timezone


class GuidedTiming:
    """Observation only: no timing field is sent in a model request."""
    def __init__(self,context,*,now=None):
        self.context=context;self.now=now or (lambda:datetime.now(timezone.utc).isoformat())
        started=getattr(context,'started_at',None)
        self.stamps={'worker_started_at_utc':datetime.fromtimestamp(started,timezone.utc).isoformat()
                     if isinstance(started,(float,int)) else None,
                     'guided_started_at_utc':self.now(),'first_model_dispatch_at_utc':None,
                     'answer_completed_at_utc':None,
                     'first_model_time_source':'CLIENT_DISPATCH_INTENT_AFTER_RESERVATION_BEFORE_SEND'}
    def __getattr__(self,name):return getattr(self.context,name)
    def record(self,kind,value):
        if (kind=='guided-case-event' and isinstance(value,dict)
                and value.get('event')=='REASONING_REQUEST' and self.stamps['first_model_dispatch_at_utc'] is None):
            self.stamps['first_model_dispatch_at_utc']=self.now()
        return self.context.record(kind,value)
    def finish(self,result):
        self.stamps['answer_completed_at_utc']=self.now()
        result.setdefault('timing',{})['timestamps']=dict(self.stamps)
        self.context.record('guided-observational-timestamps',dict(self.stamps))
        return result


class RunTiming:
    def __init__(self,clock=None):
        self.clock=clock or time.perf_counter;self.started=self.clock()
        self.started_at=datetime.now(timezone.utc).isoformat()
        self.local_seconds=0.0;self.publication_seconds=0.0;self.publications=0
        self.seal_seconds=None;self.steps=[];self.pending_models={};self.models=[]
    def step(self,name,elapsed,status):
        self.steps.append({'name':name,'wall_seconds':max(0,elapsed),'status':status})
    def tape_event(self,tape,event):
        kind=event['kind'];key=str(tape.path)
        if kind=='PROVIDER_REQUEST':self.pending_models.setdefault(key,[]).append(event['at'])
        elif kind in ('PROVIDER_RESPONSE','PROVIDER_FAILURE') and self.pending_models.get(key):
            start=self.pending_models[key].pop(0);end=event['at']
            self.models.append({'started_epoch':start,'ended_epoch':end,
                'wall_seconds':end-start if end>=start else None,
                'source':'EXISTING_NATIVE_TAPE_PROVIDER_EVENT_TIMESTAMPS','status':kind.removeprefix('PROVIDER_')})
    def summary(self):
        def phase(names):
            selected=[step for step in self.steps if step['name'] in names]
            return {'wall_seconds':sum(step['wall_seconds'] for step in selected) if selected else None,
                    'source':'OUTER_CAPTURE_STEP_CLOCK' if selected else 'NOT_SEPARATELY_OBSERVED','inclusive':True}
        return {'version':'dia-run-timing-v1','worker_timing_started_at':self.started_at,'wall_seconds':max(0,self.clock()-self.started),
            'phases':{'startup':{'wall_seconds':None,'source':'AZURE_START_AND_IMAGE_PULL_TIME_NOT_AVAILABLE_INSIDE_WORKER'},
                'dependency_io':phase({'input-materialization','retained-context-current-image','retain-approved-context','retain-verification-capture'}),
                'intake':phase({'intake','form-intake','claim-intake'}),
                'investigation':phase({'investigation','ledger-investigation'}),
                'model':{'wall_seconds':sum(call['wall_seconds'] for call in self.models) if self.models and all(call['wall_seconds'] is not None for call in self.models) else None,
                         'source':'EXISTING_NATIVE_TAPE_PROVIDER_EVENT_TIMESTAMPS' if self.models else 'NO_PAIRED_PROVIDER_EVENTS_OBSERVED','inclusive':True},
                'capture_publish':{'wall_seconds':self.publication_seconds,'publications':self.publications,'source':'OUTER_CAPTURE_TRANSPORT_CLOCK','inclusive':True},
                'capture_local':{'wall_seconds':self.local_seconds,'source':'SERIALIZATION_SECRET_AUDIT_AND_FSYNC_CLOCK'},
                'seal':{'wall_seconds':self.seal_seconds,'source':'OUTER_SEAL_CLOCK' if self.seal_seconds is not None else 'NOT_COMPLETED'}},
            'steps':self.steps,'model_calls':self.models,'unpaired_model_requests':sum(len(values) for values in self.pending_models.values()),
            'overlap':'Inclusive phases overlap; do not add them. Publication during investigation/model observation is included in those wall times.',
            'semantic_tapes_changed':False}

"""Atomic public entry point for a privacy-projected installation.

The existing procedure runs unchanged. Intermediate intake/preview state cannot
be returned before all typed values are identified; no asynchronous raw API is
exposed. Exact installations continue using the ordinary workspace interface.
"""
from pathlib import Path
from secrets import token_hex
from .privacy_capture import Capture,ACTIVE
from .privacy_projection import ProjectionError,canonical
from .privacy_tape import PrivacyTape
from .process_tape import active as tape_active


def _admission_state(workspace,tape,replaying):
    """Legacy packets keep their recorded contract; new pins are strict."""
    import copy
    from .budget_tape_contract import ACCOUNTING_HISTORY,ACCOUNTING_VERSION
    from .local_accounting import PIN as LOCAL_ACCOUNTING_PIN
    if replaying:
        if 'state' not in tape.bootstrap:return None
        state=copy.deepcopy(tape.bootstrap['state'])
    else:
        state={'local_accounting':LOCAL_ACCOUNTING_PIN,'accounting_version':ACCOUNTING_VERSION,'snapshot_clock':'ONE_CLOCK_V1',
            'physical_transport_retries':2,'provider_transport_retries':2,
            'workspace_concurrency_limit':workspace.concurrency_limit}
        if getattr(getattr(workspace,'agent',None),'governor',None) is not None:
            state['budget_checkpoint']='DELTA_V1'
    if not isinstance(state,dict):raise ProjectionError('PRIVACY_ADMISSION_STATE')
    for name,expected in (('local_accounting',LOCAL_ACCOUNTING_PIN),('budget_checkpoint','DELTA_V1'),('snapshot_clock','ONE_CLOCK_V1'),
                          ('physical_transport_retries',2),('provider_transport_retries',2)):
        if name in state and (type(state[name]) is not type(expected) or state[name]!=expected):
            raise ProjectionError('PRIVACY_ADMISSION_PIN_DIFFERS')
    if 'accounting_version' in state and (type(state['accounting_version']) is not int or state['accounting_version'] not in ACCOUNTING_HISTORY):
        raise ProjectionError('PRIVACY_ACCOUNTING_VERSION')
    return state


class Installation:
    def __init__(self,workspace,capture,recording_root):
        self._workspace=workspace;self.capture=capture;self.recording_root=Path(recording_root)
        self.running=False

    def investigate(self,request,*,synthesis_provider=None,_replay=None):
        if self.running:raise ProjectionError('PRIVACY_INSTALLATION_RUN_ALREADY_ACTIVE')
        self.running=True
        root=self.recording_root/token_hex(16)
        tape=_replay or PrivacyTape(root/'tape.json',self.capture.projection)
        self.capture.running=True
        result=None;error=None
        try:
            with self.capture.active(),tape_active(tape):
                bootstrap={'tape_class':'PRIVACY_PROJECTED',
                    'config':self._workspace.agent.config,
                    'profile':self._workspace.agent.planner_profile,
                    'owner':self._workspace.owner,
                    'stores':[store.image() for store in self.capture.stores],
                    'ledgers':{str(path):rows for path,rows in self.capture.ledgers.items()},
                    'request':request}
                state=_admission_state(self._workspace,tape,_replay is not None)
                if state is not None:bootstrap['state']=state
                tape.event('BOOTSTRAP',canonical(bootstrap))
                governor=self._workspace.agent.governor
                if governor is not None:
                    from .budget_delta import prepare_memory
                    with governor.runtime.db() as db:
                        prepare_memory(tape,db,governor.environment)
                intake=self._workspace.intake.resolve(request)
                if intake['status']!='PROPOSED':result={'intake':intake,'status':intake['status']}
                else:
                    proposal=intake['proposal']
                    preview_request={k:proposal[k] for k in ('model_id','measure_id','filters','dimension_ids')}
                    preview_request.update(symptom=intake['text'],predecessor=None,intake_id=intake['id'])
                    if 'reported_figure' in proposal:preview_request['reported_figure']=proposal['reported_figure']
                    preview=self._workspace.preview(preview_request)
                    session=self._workspace.start(preview['id'])
                    self._workspace.run_once()
                    state=self._workspace.agent.get(session['id'])
                    if state['envelope'].get('strategy'):
                        self._workspace.agent.synthesize(session['id'],synthesis_provider)
                    result=self._workspace.session(session['id'])
                    if state['envelope'].get('strategy'):
                        result['synthesis']=self._workspace.agent.get(session['id']).get('synthesis')
                tape.event('FINAL',canonical(result))
        except BaseException as failure:
            error=failure
            result={'status':'FAILED','error_type':type(failure).__name__,'message':str(failure)}
        finally:
            try:
                with self.capture.active():projected=self.capture.finish(tape,result)
            except BaseException as capture_failure:
                # Preserve an exclusion without persisting the refused raw body
                # or leaking its exception text through an alternate output.
                if not tape.replaying:
                    root.mkdir(parents=True,exist_ok=True)
                    with (root/'capture-exclusion.json').open('xb') as stream:
                        stream.write(canonical({'tape_class':'PRIVACY_PROJECTED',
                            'status':'CAPTURE_REFUSED','error_type':type(capture_failure).__name__,
                            'run_error_type':type(error).__name__ if error else None}))
                raise ProjectionError('PRIVACY_CAPTURE_REFUSED') from None
            finally:
                self.capture.running=False;self.running=False
        # Error bodies are public only after projection. Never re-raise a raw
        # exception message containing a value that the capture just protected.
        return {'tape_class':'PRIVACY_PROJECTED','recording':str(tape.path),'result':projected}

    def replay(self,path):
        """Replay this installation's sealed capture; no durable writes."""
        import base64
        from .privacy_projection import Projection
        from .privacy_identities import Identities
        from .provider_tape_contract import parse
        p=Projection(self.capture.projection.policy,lambda _:self.capture.projection._key)
        tape=PrivacyTape(path,p,replay=True)
        bootstrap=parse(base64.b64decode(tape.events[0]['body']))
        if tape.events[0]['kind']!='BOOTSTRAP' or len(bootstrap['stores'])!=len(self.capture.stores):
            raise ProjectionError('PRIVACY_BOOTSTRAP_DIFFERS')
        if bootstrap['config']!=p.project(self._workspace.agent.config) or bootstrap['profile']!=self._workspace.agent.planner_profile:
            raise ProjectionError('PRIVACY_REPLAY_INSTALLATION_DIFFERS')
        self.capture.projection=p;self.capture.identities=Identities(p)
        self.capture.ledgers={Path(path):rows for path,rows in bootstrap['ledgers'].items()}
        for store,image in zip(self.capture.stores,bootstrap['stores']):
            store.projection=p;store.restore(image)
        self._workspace.owner=bootstrap['owner']
        self._workspace.agent.config=bootstrap['config']
        self._workspace.agent.runtime.config=bootstrap['config']
        return self.investigate(bootstrap['request'],_replay=tape)

    def read(self,identity):
        if self.running:raise ProjectionError('PRIVACY_INTERMEDIATE_STATE_NOT_PUBLIC')
        with self.capture.active():
            result=self._workspace.session(identity)
            self.capture.prepare(final=result)
            return self.capture.projection.project(result)

    def close(self):self.capture.close()

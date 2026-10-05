"""Connect public intake/procedure operations to one private bounded-worker tape."""
from functools import wraps
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
from uuid import uuid4 as fresh_id
from . import process_tape as journal

ROOT=Path(__file__).resolve().parents[2]


def backup(source,destination):
    with closing(sqlite3.connect(Path(source).resolve().as_uri()+'?mode=ro',uri=True)) as original:
        with closing(sqlite3.connect(destination)) as copy:original.backup(copy)


def agent_of(owner):
    if hasattr(owner,'workspace'):return owner.workspace.agent
    if hasattr(owner,'agent'):return owner.agent
    return owner


def operation(name):
    def decorate(method):
        @wraps(method)
        def invoke(owner,*args,**kwargs):
            agent=agent_of(owner)
            if journal.ACTIVE.get() is not None:
                # The replay driver supplies the same outer operation events.
                return method(owner,*args,**kwargs)
            enabled=agent.planner_profile.get('adapter') not in (None,'injected') or os.environ.get('INVESTIGATOR_RECORD_RUNS')=='1'
            if not enabled:return method(owner,*args,**kwargs)
            tapes=getattr(agent,'_run_tapes',None)
            if tapes is None:agent._run_tapes=tapes={}
            request=args[0] if args else None
            key=request.get('intake_id') if isinstance(request,dict) else request
            if name=='create':
                from .onboarding import digest
                key=digest(request)
            tape=tapes.get(str(key))
            if tape is None and name in ('create','run','synthesize'):
                from .process_debugging import VERSION
                envelope=request if name=='create' else agent.get(request)['envelope']
                if envelope.get('strategy')!=VERSION:
                    # The existing adaptive-path recorder/harness remains its
                    # own contract. This bootstrap extends the process path.
                    return method(owner,*args,**kwargs)
            if tape is None:
                if name not in ('intake','preview','create'):
                    raise journal.TapeError('LIVE_RUN_MISSING_RECORDING_BOOTSTRAP')
                root=ROOT/'.local/process-tapes'/str(fresh_id())
                root.mkdir(parents=True,exist_ok=False)
                backup(agent.store.database,root/'catalog.sqlite')
                backup(agent.store.inventory,root/'inventory.sqlite')
                from .context_search import latest
                from .runtime import fingerprint
                context=latest(agent.store)
                bootstrap={'entry_point':'workspace','context_identity':context['version'] if context else 'catalog-sha256:'+journal.sha((root/'catalog.sqlite').read_bytes()),
                    'config':agent.config,'profile':agent.planner_profile,
                    'usage_policy':agent.governor.policy if agent.governor else None,'engine_hash':fingerprint(),
                    'state':{'environment':agent.store.environment,
                        'workspace_owner':getattr(getattr(owner,'workspace',owner),'owner',None),
                        'artifacts':{name:journal.sha((root/name).read_bytes()) for name in ('catalog.sqlite','inventory.sqlite')},
                        'dynamic_read_limit':getattr(getattr(owner,'workspace',owner),'dynamic_read_limit',12),
                        'dynamic_input_limit':getattr(getattr(owner,'workspace',owner),'dynamic_input_limit',384000)}}
                if getattr(agent.store,'context_pins',None):
                    bootstrap['state']['context_pins']=agent.store.context_pins
                tape=journal.Tape(root/'tape.json',bootstrap)
            error=None;result=None
            with journal.active(tape):
                journal.event('OPERATION_START',{'name':name,'args':list(args),'kwargs':kwargs})
                journal.event('CONFIGURATION',{'config':agent.config,'profile':agent.planner_profile,
                    'usage_policy':agent.governor.policy if agent.governor else None})
                try:
                    result=method(owner,*args,**kwargs)
                    return result
                except BaseException as exc:
                    error=exc
                    raise
                finally:
                    journal.event('OPERATION_END',{'name':name,'error':type(error).__name__ if error else None})
                    if result is not None:
                        if name=='intake':tapes[result['id']]=tape
                        elif name=='preview':
                            from .onboarding import digest
                            tapes[digest(result['envelope'])]=tape
                        elif name=='create':tapes[result['id']]=tape
                    terminal=error is not None or name=='synthesize' or name=='intake' and result.get('status')!='PROPOSED'
                    if terminal:
                        final={'operation':name,'error':type(error).__name__ if error else None,
                               'outputs':((result or {}).get('synthesis') or {}).get('outputs') or (result or {}).get('refusal_outputs'),
                               'status':(result or {}).get('status'),'result':result}
                        try:tape.finish(final)
                        except journal.TapeError as failure:
                            if error is not None:error.add_note(str(failure))
                            else:raise
        return invoke
    return decorate

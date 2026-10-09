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
            workspace=getattr(agent,'_acceptance_workspace',None)
            if workspace is not None:
                from .acceptance_context import assert_run_context
                assert_run_context(workspace)
            if agent.config.get('_estate',{}).get('recording',{}).get('tape_class')=='PRIVACY_PROJECTED':
                # Validate the existing context-pin invariant first, then
                # refuse before legacy backup() can create raw artifacts.
                from .privacy_capture import ACTIVE as PROJECTED_CAPTURE
                capture=PROJECTED_CAPTURE.get()
                if capture is None or not capture.running or getattr(agent.store,'privacy_capture',None) is not capture:
                    raise journal.TapeError('PRIVACY_PROJECTED_REQUIRES_ATOMIC_INSTALLATION_RUN')
                if journal.ACTIVE.get() is None or journal.ACTIVE.get().tape_class!='PRIVACY_PROJECTED':
                    raise journal.TapeError('PRIVACY_PROJECTED_CANNOT_USE_EXACT_CAPTURE')
                # One outer atomic capture owns every operation, including
                # originals that legacy recording cannot bootstrap.
                journal.event('OPERATION_START',{'name':name,'args':list(args),'kwargs':kwargs})
                failure=None
                try:return method(owner,*args,**kwargs)
                except BaseException as exc:failure=exc;raise
                finally:journal.event('OPERATION_END',{'name':name,'error':type(failure).__name__ if failure else None})
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
                if name not in {'intake','preview','create',*journal.SMART_OPERATIONS}:
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
                if getattr(agent.store,'acceptance_fixture_state',None):
                    bootstrap['state']['fixture_state']=agent.store.acceptance_fixture_state
                if name in journal.SMART_OPERATIONS:
                    bootstrap['state']['smart_intake']=owner.configuration
                    bootstrap['state']['smart_ownership']=owner.ownership
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
                    trace_error=None
                    if (name=='synthesize' and error is None and result is not None
                            and agent.config.get('_estate',{}).get('trace_footer')):
                        try:attach_trace_footer(agent,key,tape,result)
                        except Exception as failure:error=trace_error=failure
                    if result is not None:
                        if name=='intake':tapes[result['id']]=tape
                        elif name=='preview':
                            from .onboarding import digest
                            tapes[digest(result['envelope'])]=tape
                        elif name=='create':tapes[result['id']]=tape
                        elif name=='run' and error is None:
                            # Retain the actual return, not a later reconstruction
                            # containing synthesis or ticket-state changes.
                            tape.pending_read_final=json.loads(journal.bytes_of({
                                'operation':'run','error':None,
                                'outputs':result.get('refusal_outputs'),
                                'status':result.get('status'),'result':result}))
                    smart_read=(name=='run' and error is None and result is not None and
                                result.get('status') not in ('READY','PLANNING','EXECUTING') and
                                has_smart_ticket(agent,str(key)))
                    terminal=error is not None or name=='synthesize' or name in journal.SMART_OPERATIONS or name=='intake' and result.get('status')!='PROPOSED' or smart_read
                    if terminal:
                        final={'operation':name,'error':type(error).__name__ if error else None,
                               'outputs':((result or {}).get('synthesis') or {}).get('outputs') or (result or {}).get('refusal_outputs'),
                               'status':(result or {}).get('status'),'result':result}
                        try:tape.finish(final)
                        except journal.TapeError as failure:
                            if error is not None:error.add_note(str(failure))
                            else:raise
                        if smart_read:retain_read_capture(agent,str(key),tape)
                    if trace_error is not None:raise trace_error
        return invoke
    return decorate


def has_smart_ticket(agent, identity):
    """Only attached interactive reads get a separate durable completion."""
    with agent.store.connect() as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='smart_tickets'").fetchone():return False
        from .ticket_state import Tickets
        for row in db.execute('SELECT id FROM smart_tickets'):
            ticket=Tickets._get(db,row[0])['ticket']
            if ticket.get('session_id')==identity:return True
    return False


def retain_read_capture(agent, identity, tape):
    """Persist only a hash-pinned pointer after the actual FINAL was sealed."""
    if not tape.finished:raise journal.TapeError('READ_CAPTURE_NOT_SEALED')
    path=str(tape.path.resolve());fingerprint=journal.sha(tape.path.read_bytes())
    with agent.store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS smart_read_captures(id TEXT PRIMARY KEY,path TEXT NOT NULL,sha256 TEXT NOT NULL)')
        prior=db.execute('SELECT path,sha256 FROM smart_read_captures WHERE id=?',(identity,)).fetchone()
        if prior and tuple(prior)!=(path,fingerprint):raise journal.TapeError('READ_CAPTURE_POINTER_CHANGED')
        db.execute('INSERT OR IGNORE INTO smart_read_captures VALUES(?,?,?)',(identity,path,fingerprint))


def retained_read_capture(agent, identity):
    """Cold resume validates original bytes; never backfill from current state."""
    if not hasattr(agent,'store'):return None
    with agent.store.connect() as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='smart_read_captures'").fetchone():return None
        row=db.execute('SELECT path,sha256 FROM smart_read_captures WHERE id=?',(identity,)).fetchone()
    if row is None:return None
    path=Path(row[0]).resolve();root=(ROOT/'.local/process-tapes').resolve()
    if not path.is_relative_to(root):raise journal.TapeError('READ_CAPTURE_OUTSIDE_RECORDING_ROOT')
    if journal.sha(path.read_bytes())!=row[1]:raise journal.TapeError('READ_CAPTURE_HASH_DIFFERS')
    recorded=journal.Tape(path)
    final=json.loads(journal.validate_event(recorded.events[-1],len(recorded.events)))
    if final.get('operation')!='run' or (final.get('result') or {}).get('id')!=identity:
        raise journal.TapeError('READ_CAPTURE_SESSION_DIFFERS')
    return {'status':'SEALED','tape_sha256':row[1]}


def seal_read_stage(agent, identity):
    """Close the old read capture before a separate ticket composition capture.

    The closure is a recorded control input. Replay consumes its hash; values
    and claims still come from the separately hash-checked bootstrap database.
    A missing live capture refuses instead of fabricating the run's return.
    """
    def seal():
        prior=getattr(agent,'_run_tapes',{}).get(str(identity))
        enabled=agent.planner_profile.get('adapter') not in (None,'injected') or os.environ.get('INVESTIGATOR_RECORD_RUNS')=='1'
        if prior is None:
            retained=retained_read_capture(agent,str(identity))
            if retained is not None:return retained
            if enabled:return {'status':'UNAVAILABLE','reason':'READ_STAGE_CAPTURE_UNAVAILABLE'}
            return {'status':'RECORDING_DISABLED'}
        if not prior.finished:
            pending=getattr(prior,'pending_read_final',None)
            if pending is None or pending['result']['id']!=identity:
                return {'status':'UNAVAILABLE','reason':'READ_STAGE_RETURN_UNAVAILABLE'}
            prior.finish(pending)
        return {'status':'SEALED','tape_sha256':journal.sha(prior.path.read_bytes())}
    closure=journal.value('CONFIGURATION','ticket_read_stage_closure',seal)
    if closure['status']=='UNAVAILABLE':
        from .onboarding import Conflict
        raise Conflict(closure['reason'])
    return closure


def attach_trace_footer(agent,identity,tape,result):
    """Persist one engine-rendered footer; never re-write historical outputs."""
    synthesis=result.get('synthesis') or {}
    if synthesis.get('status')!='COMPLETED' or not synthesis.get('outputs'):return
    from .tape_trace import recorded_summary,footer
    summary=recorded_summary(tape,result)
    from .evidence_synthesis import read,save
    with agent.runtime.db() as db:
        db.execute('BEGIN IMMEDIATE')
        record=read(db,identity,full=True)
        if record is None or record['status']!='COMPLETED':raise journal.TapeError('TRACE_OUTPUT_RECORD_MISSING')
        if 'recorded_stage_cost_time' in record:return
        output=record['outputs']['technical_output']['explanation']
        output['text']+='\n\n'+footer(summary)
        record['recorded_stage_cost_time']=summary
        save(db,identity,record,source_state=agent.load(db,identity))
    updated=agent.get(identity)
    result.clear();result.update(updated)

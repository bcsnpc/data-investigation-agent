"""Isolated ticket runners sharing one atomic budget; estate switches are serial.

Factories must create fresh Workspace/Agent instances. They must not mutate
process environment or redirect global stdout. Replay is a separate serial step:
archived replay consumers install process-global contract adapters.
"""
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from contextvars import Context
from dataclasses import dataclass
import copy, json
from pathlib import Path
from threading import Lock
from uuid import uuid4


@dataclass(frozen=True)
class Slot:
    run_id: str
    estate: str
    label: str
    directory: Path
    request: dict


@dataclass
class Concurrency:
    """Operator-visible ramp only; this never changes manifest/governor limits."""
    workers: int = 4

    def observe(self, results):
        # Only a complete, clean batch earns the next explicitly allowed level.
        # A provider throttle or worker timeout reduces the next admission width.
        def detail(row):return row.get('result') if isinstance(row.get('result'),dict) else {}
        timeout_or_throttle=any(r.get('error_type') in ('TimeoutError','UsageHold')
            or detail(r).get('http_status')==429
            or detail(r).get('throttled')
            or detail(r).get('timeout') for r in results)
        before=self.workers
        if timeout_or_throttle:self.workers=max(1,self.workers-1)
        elif results and all(r.get('status')=='RETURNED' for r in results):
            self.workers=next((level for level in (4,6,8) if level>self.workers),self.workers)
        return {'before':before,'after':self.workers,
                'reason':'THROTTLE_OR_TIMEOUT' if timeout_or_throttle else 'CLEAN_BATCH' if self.workers>before else 'NO_RAMP'}


def run_estates(groups, *, root, budget_database, workspace_factory, execute,
                stop=lambda result: False, workers=4):
    """One attempt per input; finish admitted work, then stop admitting on a cap.

    groups is an ordered sequence of (estate, [(label, request), ...]).
    execute(workspace, slot) owns actual ticket creation, recording and receipts.
    Results and control logs are distinct from investigation evidence/ledgers.
    No retries, caps, policies, identities or fixture state are changed here.
    """
    if type(workers) is not int or not 1 <= workers <= 8:
        raise ValueError('Parallel ticket bound is one through eight')
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=True)
    budget_database=Path(budget_database).resolve()
    instances=[];lock=Lock();results=[];halted=False
    def attempt(slot):
        log=slot.directory/'control.jsonl'
        def note(value):
            with log.open('a',encoding='utf-8') as stream:
                stream.write(json.dumps(value,sort_keys=True)+'\n')
        note({'event':'START','run_id':slot.run_id,'estate':slot.estate,'label':slot.label})
        try:
            workspace=workspace_factory(slot)
            with lock:
                if any(workspace is old or workspace.agent is old.agent for old in instances):
                    raise ValueError('Parallel runs require fresh workspace and agent instances')
                instances.append(workspace)  # Hold references: object IDs cannot be recycled.
            actual=Path(workspace.agent.governor.runtime.store.database).resolve()
            if actual!=budget_database:
                raise ValueError('Parallel runs must share the declared atomic budget database')
            value=execute(workspace,slot)
            result={'run_id':slot.run_id,'estate':slot.estate,'label':slot.label,
                    'status':'RETURNED','result':value}
            json.dumps(result)  # Serialization errors belong to this ticket too.
        except Exception as exc:
            result={'run_id':slot.run_id,'estate':slot.estate,'label':slot.label,
                    'status':'FAILED','error_type':type(exc).__name__,'error_message':str(exc)}
        (slot.directory/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2),encoding='utf-8')
        note({'event':'END','status':result['status']})
        return result
    for estate,jobs in groups:
        pending_jobs=list(jobs)
        if len({label for label,_ in pending_jobs})!=len(pending_jobs):
            raise ValueError('Ticket labels must be unique within an estate')
        with ThreadPoolExecutor(max_workers=workers) as pool:
            pending={}
            def admit():
                label,request=pending_jobs.pop(0)
                identity=str(uuid4());directory=root/identity;directory.mkdir(exist_ok=False)
                slot=Slot(identity,estate,label,directory,copy.deepcopy(request))
                # Do not inherit any caller's active tape/privacy/physical scope.
                pending[pool.submit(Context().run,attempt,slot)]=slot
            while pending_jobs or pending:
                while pending_jobs and len(pending)<workers and not halted:admit()
                if not pending:break
                done,_=wait(pending,return_when=FIRST_COMPLETED)
                for future in done:
                    pending.pop(future);result=future.result();results.append(result)
                    if result['status']=='FAILED' or stop(result):halted=True
        if halted:break
    return {'results':results,'stopped':halted}

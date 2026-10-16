"""Atomic bounded queue admission and explicit parallel environmental inputs."""
from .onboarding import Conflict
from . import process_tape as journal

ACTIVE_STATES=('SUBMITTING','QUEUED','RUNNING')

def admit(db,owner,limit):
    # The caller must keep this check and its subsequent insert in one
    # BEGIN IMMEDIATE transaction. No provider/estate request occurs here.
    if not db.in_transaction:raise Conflict('Workspace admission requires an atomic transaction')
    if db.execute("SELECT 1 FROM workspace_jobs WHERE owner=? AND status IN ('SUBMITTING','QUEUED','RUNNING')",(owner,)).fetchone():
        raise Conflict('This workspace already has an active investigation; wait or cancel it first')
    def external():
        return {'owner':owner,'limit':limit,'external_active':[
            list(row) for row in db.execute("SELECT preview_id,owner,status FROM workspace_jobs WHERE owner<>? AND status IN ('SUBMITTING','QUEUED','RUNNING') ORDER BY preview_id",(owner,))]}
    tape=journal.ACTIVE.get()
    pinned=tape is not None and 'workspace_concurrency_limit' in tape.bootstrap.get('state',{})
    body=journal.value('CONFIGURATION','workspace_admission_inputs',external) if pinned else external()
    if (set(body)!={'owner','limit','external_active'} or body['owner']!=owner or body['limit']!=limit
            or not isinstance(body['external_active'],list) or len(body['external_active'])>100000):
        raise Conflict('Workspace admission environmental input differs')
    rows=body['external_active'];ids=[]
    for row in rows:
        if (not isinstance(row,list) or len(row)!=3 or any(not isinstance(v,str) or not v for v in row)
                or row[1]==owner or row[2] not in ACTIVE_STATES):
            raise Conflict('Workspace admission environmental input is invalid')
        ids.append(row[0])
    if len(set(ids))!=len(ids):raise Conflict('Workspace admission environmental input duplicates a job')
    if len(rows)>=limit:raise Conflict('Another investigation is active; wait or cancel it first')

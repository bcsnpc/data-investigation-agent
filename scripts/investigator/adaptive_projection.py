"""Read the same saved session in business/technical projections; no query dispatch."""
import json
import sqlite3
from .onboarding import digest
from .adaptive_runtime import outcome


def read(store,model_id,identity,audience='technical'):
    if audience not in ('business','technical'):raise ValueError('Unknown view')
    store.get(model_id)
    with store.connect() as db:
        db.row_factory=sqlite3.Row
        exists=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='adaptive_sessions'").fetchone()
        row=db.execute('SELECT state,state_hash FROM adaptive_sessions WHERE id=? AND model_id=?',(identity,model_id)).fetchone() if exists else None
        if row is None:raise KeyError('Session not found')
        state=json.loads(row['state'])
        if digest(state)!=row['state_hash']:raise ValueError('Session integrity differs')
        events=[{'kind':r['kind'],'created':r['created']} for r in db.execute('SELECT kind,created FROM adaptive_events WHERE session_id=? ORDER BY id',(identity,))]
    result=outcome(state)
    shared={'id':identity,'scope_hash':state['scope_hash'],'context_hash':state['context_hash'],
            'status':state['status'],'outcome_hash':digest(result),'question':state['question'],
            'outcome':result,'activity':events,'audience':audience}
    if audience=='technical':
        shared.update(envelope=state['envelope'],decisions=state['decisions'],
                      budgets={k:state[k] for k in ('planner_calls','cloud_calls','input_characters')})
    else:
        shared['summary']='Additional evidence is needed before we can explain the reported difference.'
        if state['status']=='CANCELLED':shared['summary']='The investigation was cancelled. Captured results remain available.'
        elif state['status']=='NEEDS_INPUT':shared['summary']='Please clarify the question below before further checks.'
        elif state['status'] in ('READY','PLANNING','EXECUTING'):shared['summary']='The investigation is checking the approved information.'
    return shared

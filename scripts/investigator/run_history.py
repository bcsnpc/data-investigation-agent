"""Identifier-only links to earlier records; never prior conclusions as evidence."""
import copy,json
from .onboarding import digest


def cells(state):
    from .read_address import validate
    result=set()
    for observation in state.get('observations',[]):
        address=observation.get('read_address')
        if isinstance(address,dict) and address.get('kind')=='CELL':
            validate(address)
            result.add(address['cell']['id'])
    return result


def capture(db,state):
    current=db.execute('SELECT rowid FROM adaptive_sessions WHERE id=?',(state['id'],)).fetchone()
    if current is None:raise ValueError('History requires a persisted current run')
    target=cells(state);by_cell={c:set() for c in target};tickets=set()
    key=digest({'model_id':state['model_id'],'ticket':state['envelope']['symptom']})
    rows=db.execute('SELECT id,state,state_hash FROM adaptive_sessions WHERE model_id=? AND rowid<? ORDER BY rowid',
                    (state['model_id'],current['rowid'])).fetchall()
    for row in rows:
        try:previous=json.loads(row['state'])
        except (ValueError,TypeError):
            return {'version':1,'status':'UNAVAILABLE','reason':'PRIOR_RECORD_INVALID','record_id':row['id']}
        if not isinstance(previous,dict) or digest(previous)!=row['state_hash'] or previous.get('id')!=row['id'] or previous.get('model_id')!=state['model_id']:
            return {'version':1,'status':'UNAVAILABLE','reason':'PRIOR_RECORD_INTEGRITY_DIFFERS','record_id':row['id']}
        if digest({'model_id':previous['model_id'],'ticket':previous['envelope']['symptom']})==key:tickets.add(row['id'])
        try:prior_cells=cells(previous)
        except ValueError:
            return {'version':1,'status':'UNAVAILABLE','reason':'PRIOR_CELL_ADDRESS_INVALID','record_id':row['id']}
        for cell in target & prior_cells:by_cell[cell].add(row['id'])
    return {'version':1,'status':'RECORDED','ticket_key':key,'same_ticket':sorted(tickets),
            'same_cells':[{'cell_id':c,'run_ids':sorted(ids)} for c,ids in sorted(by_cell.items())]}


def attach(outputs,state):
    history=state.get('previous_runs')
    if history is None:return       # Historical records are never backfilled.
    if history['status']=='UNAVAILABLE':
        line='Previous runs: unavailable; '+history['reason']+' for record '+history['record_id']+'.'
    else:
        parts=['same ticket '+(', '.join(history['same_ticket']) or 'none')]
        parts.extend('same cell '+r['cell_id']+' '+(', '.join(r['run_ids']) or 'none') for r in history['same_cells'])
        line='Previous runs: '+'; '.join(parts)+'.'
    outputs['technical_output']['previous_runs']=copy.deepcopy(history)
    outputs['technical_output']['explanation']['text']+='\n\n'+line

"""Materialize one pinned model/current scan, never a historical catalog copy."""
import json,sqlite3
from contextlib import closing
from pathlib import Path
from .onboarding import ModelStore,digest,encoded

def materialize(source,target,*,model,context,inventory,environment):
    from cloud_stage_worker import offline
    # Both source pins were hash-checked by the cloud assembly before this call.
    source=Path(source);target=Path(target)
    with offline():store=ModelStore(target,inventory,environment)
    with closing(sqlite3.connect(source.as_uri()+'?mode=ro',uri=True))as origin,store.connect()as dest:
        origin.row_factory=sqlite3.Row
        row=origin.execute('SELECT * FROM models WHERE id=?',(model['id'],)).fetchone()
        if row is None or row['context_id']!=model['context_id']:raise ValueError('TICKET_MODEL_CONTEXT_PIN_DIFFERS')
        saved=origin.execute('SELECT * FROM model_contexts WHERE id=? AND model_id=?',(model['context_id'],model['id'])).fetchone()
        if saved is None or digest(json.loads(saved['body']))!=saved['hash'] or saved['hash']!=digest(model['context']):raise ValueError('TICKET_MODEL_CONTEXT_HASH_DIFFERS')
        for table,value in (('models',row),('model_contexts',saved)):
            columns=list(value.keys());dest.execute('INSERT INTO '+table+'('+','.join(columns)+') VALUES('+','.join('?'for _ in columns)+')',tuple(value))
        if origin.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='discovery_models'").fetchone():
            dest.execute('CREATE TABLE discovery_models(model_id TEXT,denied INTEGER,policy_hash TEXT)')
            policy=origin.execute('SELECT model_id,denied,policy_hash FROM discovery_models WHERE model_id=?',(model['id'],)).fetchone()
            if policy is not None:dest.execute('INSERT INTO discovery_models VALUES(?,?,?)',tuple(policy))
        dest.execute('CREATE TABLE enterprise_scans(id,environment,status,started,body,hash)')
        dest.execute('INSERT INTO enterprise_scans VALUES(?,?,?,?,?,?)',(context['version'],environment,'PARTIAL',0,encoded(context),digest(context)))
    # This cache retains only the approved current context, no past observations,
    # runs, model histories, other model rows or historical scan bodies.
    return store,{'models':1,'model_contexts':1,'enterprise_scans':1,'historical_scans':0,'historical_runs':0,
        'model_context_hash':digest(model['context']),'enterprise_context_hash':digest(context),'bytes':target.stat().st_size}

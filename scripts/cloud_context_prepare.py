"""Explicit retained-context readoption into private cloud replay snapshots.

No collection, credential acquisition, model call, or PostgreSQL publication.
The prior snapshots are read-only; an operator must publish the selected model.
"""
import argparse
import copy
import hashlib
import json
from contextlib import closing
from pathlib import Path
import sqlite3
from investigator.onboarding import ModelStore,digest
from investigator.estate_manifest import load
from investigator.adapters.estate_installation import configuration
from investigator.enterprise_discovery import Discovery
from investigator.runtime import fingerprint


def prepare(manifest_path,source_catalog,source_inventory,folder,*,model_id,context_id,context_hash,actor,decision):
    manifest_path=Path(manifest_path);manifest=load(manifest_path);config=configuration(manifest)
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False)
    for name,source in [('catalog.sqlite',source_catalog),('inventory.sqlite',source_inventory)]:
        source=Path(source).resolve();target=(folder/name).resolve()
        if source==target:raise ValueError('SOURCE_SNAPSHOT_ALIAS')
        with closing(sqlite3.connect(source.as_uri()+'?mode=ro',uri=True)) as db:
            with closing(sqlite3.connect(target)) as dest:db.backup(dest)
    # This operator preparation is offline. Do not inherit cloud authority and
    # accidentally edit a publication through a local materialisation.
    from investigator.shared_state import configured_state
    if configured_state() is not None:raise ValueError('PREPARATION_REQUIRES_OFFLINE_STATE_MODE')
    store=ModelStore(folder/'catalog.sqlite',folder/'inventory.sqlite',manifest['environment'])
    before=store.get(model_id)
    with store.connect() as db:
        row=db.execute('SELECT body,hash,status FROM enterprise_scans WHERE id=? AND environment=?',
            (context_id,manifest['environment'])).fetchone()
    if not row or row['hash']!=context_hash or row['status'] not in ('COMPLETE','PARTIAL'):
        raise ValueError('SOURCE_CONTEXT_PIN_DIFFERS')
    body=json.loads(row['body'])
    if digest(body)!=context_hash:raise ValueError('SOURCE_CONTEXT_HASH_DIFFERS')
    original_assets=copy.deepcopy(body['assets'])
    authority={'owner':actor,'decision':decision,'metadata_not_recollected':True,
               'source_context':context_id,'source_hash':context_hash}
    for key in ('version','graph','changes','inventory_scan_id','created'):body.pop(key,None)
    body.update(profile_hash=digest(config),calls=0,retained_metadata_approval=authority)
    # The narrow selected model is explicitly re-enabled only in this private
    # publication candidate. Other published PG models remain unchanged.
    with store.connect() as db:
        db.execute('UPDATE discovery_models SET denied=0 WHERE model_id=?',(model_id,))
    approved=Discovery(store,config).run(lambda:body,'cloud-readoption:'+digest(authority)[:40])
    selected=store.get(model_id)
    if not selected['enabled']:raise ValueError('SELECTED_MODEL_REMAINS_UNAVAILABLE')
    context={'version':approved['id'],**approved['body']}
    def stable_assets(rows):
        return [{k:v for k,v in a.items() if k not in ('last_seen_scan','availability')} for a in rows]
    if stable_assets(original_assets)!=stable_assets(context['assets']):
        raise ValueError('READOPTION_CHANGED_RETAINED_ASSETS')
    approval={'context_id':approved['id'],'context_hash':approved['hash'],'config_hash':digest(config),
        'engine_hash':fingerprint(),'manifest_sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        'authority':authority,'physical_requests':0,'model_calls':0}
    publication={'version':'cloud-selected-model-publication-v1','environment':manifest['environment'],
        'model_before':before,'model_after':selected,'approval':approval,
        'context':selected['context'],'context_hash':digest(selected['context'])}
    for name,value in [('approval.json',approval),('context.json',context),('model.json',selected),('publication-candidate.json',publication)]:
        (folder/name).write_text(json.dumps(value,indent=2,sort_keys=True),encoding='utf8')
    return publication


def publish(state, candidate):
    """Operator compare-and-swap; history retained, one model only, no readiness."""
    from investigator.shared_catalog import SharedCatalog
    from investigator.shared_state import encoded,sha,StateConflict
    c=candidate
    if c['version']!='cloud-selected-model-publication-v1':raise ValueError('PUBLICATION_CONTRACT')
    before,after=c['model_before'],c['model_after'];env=c['environment']
    if any(before[k]!=after[k] for k in ('id','environment','workspace','native_id')):
        raise ValueError('PUBLICATION_TARGET_CHANGED')
    if before['environment']!=env or digest(c['context'])!=c['context_hash'] or c['context']!=after['context']:
        raise ValueError('PUBLICATION_CONTEXT_CHANGED')
    catalog=SharedCatalog(state,env);key=catalog._key(before['id'])
    with state.transaction() as db:
        prior=state._get(db,'catalog_model',key)
        if prior['body']!=before:raise StateConflict('PUBLICATION_MODEL_CHANGED')
        history_key=key+':'+str(prior['revision'])
        state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',('catalog_model_history',history_key,0,encoded(before),sha(before)))
        context_key=catalog._key(after['id'],after['context_id'])
        context={'body':c['context'],'hash':c['context_hash']}
        existing=state.sql(db,'SELECT body FROM state_documents WHERE namespace=? AND identity=?',('catalog_context',context_key)).fetchone()
        if existing:
            if json.loads(existing[0])!=context:raise StateConflict('PUBLICATION_CONTEXT_CONFLICT')
        else:state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',('catalog_context',context_key,0,encoded(context),sha(context)))
        state.sql(db,'UPDATE state_documents SET revision=?,body=?,body_hash=? WHERE namespace=? AND identity=?',
            (prior['revision']+1,encoded(after),sha(after),'catalog_model',key))
        proof={'approval':c['approval'],'model_id':after['id'],'before_hash':sha(before),'after_hash':sha(after),
               'context_hash':c['context_hash'],'readiness':'NOT_EARNED_BY_PUBLICATION'}
        state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',('catalog_publication',sha(c),0,encoded(proof),sha(proof)))
    return proof


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('manifest','source-catalog','source-inventory','folder'):parser.add_argument('--'+name,type=Path,required=True)
    for name in ('model-id','context-id','context-hash','actor','decision'):parser.add_argument('--'+name,required=True)
    args=parser.parse_args();value=prepare(args.manifest,args.source_catalog,args.source_inventory,args.folder,
        model_id=args.model_id,context_id=args.context_id,context_hash=args.context_hash,actor=args.actor,decision=args.decision)
    print(json.dumps({'model_id':value['model_after']['id'],'context_id':value['model_after']['context_id'],
        'approval':value['approval'],'status':'PREPARED_NOT_PUBLISHED_NOT_READY'}))

if __name__=='__main__':main()

"""Immutable published catalog snapshots for cloud workers.

Onboarding remains an operator publication step. A worker reads an approved
publication and cannot change model enablement in its private replay catalog.
"""
import copy
from .onboarding import digest,Conflict
from .shared_state import sha,encoded,StateConflict


class SharedCatalog:
    def __init__(self,state,environment):
        self.state=state;self.environment=environment

    def _key(self,*parts):
        return encoded([self.environment,*parts])

    def context(self,identity,context_id):
        saved=self.state.get('catalog_context',self._key(identity,context_id))['body']
        if digest(saved['body'])!=saved['hash']:raise Conflict('Context integrity failure')
        return saved['body']

    def get(self,identity,context_pin=None):
        value=self.state.get('catalog_model',self._key(identity))['body']
        if value['environment']!=self.environment or value['id']!=identity:raise Conflict('Shared catalog identity differs')
        if context_pin:
            value['context_id']=context_pin['context_id']
        value['context']=self.context(identity,value['context_id']) if value['context_id'] else None
        if context_pin and digest(value['context'])!=context_pin['hash']:raise Conflict('Pinned context hash differs')
        return value

    def list(self,enabled_only=False):
        # Listing is bounded at publication, rather than silently truncating a
        # larger estate. Identifier inventory is an explicitly retained document.
        index=self.state.get('catalog_index',self.environment)['body']
        models=[self.get(identity) for identity in index['model_ids']]
        return sorted([m for m in models if not enabled_only or m['enabled']],key=lambda m:(m['name'],m['id']))


def export_catalog(store):
    """Call on the existing approved SQLite store while admissions are drained."""
    models=store.list();contexts=[]
    for model in models:
        for context in model['context_history']:
            body=store.context(model['id'],context['id'])
            if digest(body)!=context['hash']:raise Conflict('Context integrity failure')
            contexts.append({'model_id':model['id'],'context_id':context['id'],'body':body,'hash':context['hash']})
    return {'version':'shared-catalog-import-v1','environment':store.environment,'models':models,'contexts':contexts}


def import_catalog(state,identity,source):
    if set(source)!={'version','environment','models','contexts'} or source['version']!='shared-catalog-import-v1':
        raise ValueError('CATALOG_IMPORT_SCHEMA_DIFFERS')
    env=source['environment'];catalog=SharedCatalog(state,env);fingerprint=sha(source)
    model_ids=[m['id'] for m in source['models']]
    if len(model_ids)!=len(set(model_ids)):raise ValueError('CATALOG_MODEL_DUPLICATED')
    with state.transaction() as db:
        prior=state.sql(db,'SELECT source_hash,verification FROM state_migrations WHERE identity=?',(identity,)).fetchone()
        if prior:
            if prior[0]!=fingerprint:raise StateConflict('MIGRATION_SOURCE_CHANGED')
            import json
            return json.loads(prior[1])
        def put(namespace,key,value):
            state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',(namespace,key,0,encoded(value),sha(value)))
        for context in source['contexts']:
            if context['model_id']not in model_ids or digest(context['body'])!=context['hash']:
                raise Conflict('Imported context identity or hash differs')
            put('catalog_context',catalog._key(context['model_id'],context['context_id']),{'body':context['body'],'hash':context['hash']})
        for model in source['models']:
            if model['environment']!=env:raise Conflict('Imported model environment differs')
            if model['context_id'] and not any(c['model_id']==model['id'] and c['context_id']==model['context_id'] and c['body']==model['context'] for c in source['contexts']):
                raise Conflict('Imported active context differs')
            put('catalog_model',catalog._key(model['id']),model)
        put('catalog_index',env,{'model_ids':model_ids,'source_sha256':fingerprint})
        proof={'source_sha256':fingerprint,'models':len(model_ids),'contexts':len(source['contexts']),'hashes_verified':True}
        state.sql(db,'INSERT INTO state_migrations VALUES(?,?,?)',(identity,fingerprint,encoded(proof)))
        return proof


def publish_readiness(state,certificate):
    """Operator retention only: storing a certificate does not make it READY.

    The existing route assessor still verifies all sealed evidence/current pins.
    """
    key=digest(certificate)
    try:
        retained=state.get('readiness_certificate',key)['body']
    except KeyError:
        state.put('readiness_certificate',key,certificate)
    else:
        if retained!=certificate:raise Conflict('Shared readiness certificate differs')
    return key

"""Operator-controlled catalog, ticket and readiness migration bundle.

Each component is atomic and immutable. A partially applied bundle is resumable
with the identical bundle hash; it never reports all components applied early.
"""
from contextlib import contextmanager
import json
from .shared_state import encoded,sha,StateConflict
from .shared_catalog import export_catalog,import_catalog
from .shared_ticket_migration import export_tickets,import_tickets
from .onboarding import ModelStore,digest


class RetainedCatalog(ModelStore):
    """Use existing ModelStore read semantics inside one read-only transaction."""
    def __init__(self,connection,environment):
        self.retained_connection=connection;self.environment=environment
        self.shared_catalog=None;self.context_pins={}
    @contextmanager
    def connect(self):yield self.retained_connection


def export_documents(connection,environment,certificates=()):
    components=[export_catalog(RetainedCatalog(connection,environment)),export_tickets(connection,environment),
                {'version':'shared-readiness-import-v1','environment':environment,
                 'certificates':[{'sha256':digest(c),'body':c} for c in certificates]}]
    return {'version':'shared-documents-import-v1','environment':environment,'components':components}


def validate_bundle(source):
    versions=['shared-catalog-import-v1','shared-tickets-import-v1','shared-readiness-import-v1']
    if set(source)!={'version','environment','components'} or source['version']!='shared-documents-import-v1':raise ValueError('DOCUMENT_BUNDLE_SCHEMA_DIFFERS')
    if [c.get('version') for c in source['components']]!=versions:raise ValueError('DOCUMENT_BUNDLE_COMPONENTS_DIFFER')
    if any(c.get('environment')!=source['environment'] for c in source['components']):raise ValueError('DOCUMENT_BUNDLE_ENVIRONMENT_DIFFERS')
    from .shared_ticket_migration import validate
    validate(source['components'][1])
    return source


def import_readiness(state,identity,source):
    if set(source)!={'version','environment','certificates'} or source['version']!='shared-readiness-import-v1':raise ValueError('READINESS_IMPORT_SCHEMA_DIFFERS')
    fingerprint=sha(source);keys=[]
    for record in source['certificates']:
        if set(record)!={'sha256','body'} or digest(record['body'])!=record['sha256']:raise StateConflict('READINESS_CERTIFICATE_HASH_DIFFERS')
        if record['sha256']in keys:raise StateConflict('READINESS_CERTIFICATE_DUPLICATED')
        keys.append(record['sha256'])
    with state.transaction() as db:
        prior=state.sql(db,'SELECT source_hash,verification FROM state_migrations WHERE identity=?',(identity,)).fetchone()
        if prior:
            if prior[0]!=fingerprint:raise StateConflict('MIGRATION_SOURCE_CHANGED')
            return json.loads(prior[1])
        for record in source['certificates']:
            try:saved=state._get(db,'readiness_certificate',record['sha256'])['body']
            except KeyError:
                state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',('readiness_certificate',record['sha256'],0,encoded(record['body']),sha(record['body'])))
                saved=state._get(db,'readiness_certificate',record['sha256'])['body']
            if saved!=record['body']:raise StateConflict('READINESS_CERTIFICATE_DRIFT')
        proof={'source_sha256':fingerprint,'certificate_hashes':keys,'certificates':len(keys),
               'hashes_verified':True,'status':'RETAINED_NOT_REASSESSED'}
        state.sql(db,'INSERT INTO state_migrations VALUES(?,?,?)',(identity,fingerprint,encoded(proof)))
        return proof


def import_documents(state,identity,source,*,checkpoint=None):
    validate_bundle(source)
    # Bind the combined plan first so a later retry cannot swap an unapplied component.
    fingerprint=sha(source)
    with state.transaction() as db:
        try:saved=state._get(db,'document_import_plan',identity)['body']
        except KeyError:
            saved={'source_sha256':fingerprint}
            state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',('document_import_plan',identity,0,encoded(saved),sha(saved)))
        if saved['source_sha256']!=fingerprint:raise StateConflict('DOCUMENT_BUNDLE_SOURCE_CHANGED')
    proofs=[]
    for suffix,handler,component in zip(('catalog','tickets','readiness'),(import_catalog,import_tickets,import_readiness),source['components']):
        proof=handler(state,identity+':'+suffix,component);proofs.append({'component':suffix,'proof':proof})
        if checkpoint:checkpoint(proofs)
    return {'source_sha256':fingerprint,'status':'APPLIED','components':proofs,
            'limitation':'Readiness evidence retained unchanged; no current READY claim is manufactured by migration.'}

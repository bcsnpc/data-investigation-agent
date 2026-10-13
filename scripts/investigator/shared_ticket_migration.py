"""Exact historical smart-ticket import; retained evidence references are not copied blobs."""
import json
from .onboarding import digest
from .shared_state import encoded,sha,StateConflict
from .ticket_protocol import VERSION

COLUMNS=('id','request_key','request_hash','request','revision','body','body_hash')


def validate(source):
    if set(source)!={'version','environment','columns','rows'} or source['version']!='shared-tickets-import-v1' or source['columns']!=list(COLUMNS):
        raise ValueError('TICKET_IMPORT_SCHEMA_DIFFERS')
    if not isinstance(source['environment'],str) or not source['environment']:raise ValueError('TICKET_IMPORT_ENVIRONMENT_REQUIRED')
    ids=set();keys=set()
    for row in source['rows']:
        if not isinstance(row,list) or len(row)!=len(COLUMNS):raise ValueError('TICKET_IMPORT_ROW_SHAPE_DIFFERS')
        identity,key,request_hash,raw_request,revision,raw_body,body_hash=row
        if identity in ids or key in keys:raise StateConflict('TICKET_IMPORT_DUPLICATE_ID_OR_REQUEST_KEY')
        ids.add(identity);keys.add(key)
        if not isinstance(identity,str) or not identity or not isinstance(key,str) or not 1<=len(key)<=100 or type(revision)is not int or revision<0:
            raise ValueError('TICKET_IMPORT_ID_KEY_OR_REVISION_INVALID')
        body=json.loads(raw_body);request=json.loads(raw_request)
        if digest(request)!=request_hash or digest(body)!=body_hash or body.get('id')!=identity or body.get('version')!=VERSION:
            raise StateConflict('TICKET_IMPORT_HASH_ID_OR_CONTRACT_DIFFERS')
    return source


def export_tickets(connection,environment):
    # A caller-owned read-only snapshot; no Tickets constructor/schema creation.
    rows=[list(row) for row in connection.execute('SELECT '+','.join(COLUMNS)+' FROM smart_tickets ORDER BY id')]
    return validate({'version':'shared-tickets-import-v1','environment':environment,'columns':list(COLUMNS),'rows':rows})


def import_tickets(state,identity,source):
    validate(source);fingerprint=sha(source)
    with state.transaction() as db:
        prior=state.sql(db,'SELECT source_hash,verification FROM state_migrations WHERE identity=?',(identity,)).fetchone()
        if prior:
            if prior[0]!=fingerprint:raise StateConflict('MIGRATION_SOURCE_CHANGED')
            return json.loads(prior[1])
        proofs=[]
        for row in source['rows']:
            ticket_id,key,request_hash,raw_request,revision,raw_body,body_hash=row
            request=json.loads(raw_request);ticket=json.loads(raw_body)
            for namespace,record_id,value,rev in (
                ('ticket',ticket_id,{'request':request,'ticket':ticket},revision),
                ('ticket_request',key,{'id':ticket_id,'request_hash':request_hash},0)):
                if state.sql(db,'SELECT 1 FROM state_documents WHERE namespace=? AND identity=?',(namespace,record_id)).fetchone():
                    raise StateConflict('TICKET_IMPORT_TARGET_ID_OR_REQUEST_KEY_EXISTS')
                state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',(namespace,record_id,rev,encoded(value),sha(value)))
            saved=state._get(db,'ticket',ticket_id);link=state._get(db,'ticket_request',key)['body']
            # Serialized originals are retained separately without normalization.
            # Runtime documents preserve content/revision/request-key semantics.
            reconstructed=[saved['body']['ticket']['id'],key,link['request_hash'],raw_request,
                           saved['revision'],raw_body,body_hash]
            matched=(saved['body']['request']==request and saved['body']['ticket']==ticket
                     and digest(saved['body']['request'])==request_hash and digest(saved['body']['ticket'])==body_hash
                     and link['id']==ticket_id and reconstructed==row)
            if not matched:raise StateConflict('TICKET_IMPORT_POST_WRITE_DRIFT')
            proofs.append({'id':ticket_id,'request_key':key,'revision_before':revision,'revision_after':saved['revision'],
                           'row_sha256_before':sha(row),'row_sha256_after':sha(reconstructed),'matched':True})
        # Preserve exact JSON strings even if a historical producer formatted them differently.
        state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',('ticket_import_source',identity,0,encoded(source),fingerprint))
        retained=state._get(db,'ticket_import_source',identity)['body']
        if retained!=source:raise StateConflict('TICKET_IMPORT_RAW_SOURCE_DRIFT')
        proof={'source_sha256':fingerprint,'rows_before':len(source['rows']),'rows_after':len(proofs),
               'rows_sha256_before':sha(source['rows']),'rows_sha256_after':sha(retained['rows']),
               'tickets':proofs,'retained_source_namespace':'ticket_import_source',
               'limitation':'Ticket case history and embedded evidence retained; referenced captures still require their pinned snapshots/blobs.'}
        state.sql(db,'INSERT INTO state_migrations VALUES(?,?,?)',(identity,fingerprint,encoded(proof)))
        return proof

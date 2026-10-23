"""Durable re-enrichment work signals on existing definition change detection."""
from .shared_state import encoded, sha


def enqueue(state,db,estate,owner,definition_hash,at):
    body={'estate':estate,'owner':owner,'definition_hash':definition_hash,'changed_at':at,'status':'PENDING'}
    state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?) ON CONFLICT(namespace,identity) DO NOTHING',
        ('enrichment_queue',sha([estate,owner,definition_hash]),0,encoded(body),sha(body)))

"""Append-only owner collection observations; definition history stays immutable."""
from . import estate_graph_contract as c
from .shared_state import encoded
from .shared_state import sha, StateConflict
import json

NAMESPACE = 'graph_owner_collection'
STATES = frozenset({'REFRESHING', 'CURRENT', 'UNAVAILABLE', 'DELETED'})


def record(state, estate, owner, at, status, reason=None, *, failure=None,payload_reference=None,catalog_manifest_reference=None):
    at = c.timestamp(at)
    if status not in STATES or (reason is not None and not c.text(reason)):
        raise ValueError('GRAPH_COLLECTION_STATUS')
    identity = encoded([estate, owner])
    try: prior = state.get(NAMESPACE, identity)
    except KeyError: prior = {'revision': None, 'body': {'events': []}}
    events = prior['body']['events']
    if events and at < events[-1]['at']: raise ValueError('GRAPH_COLLECTION_TIME_MUST_ADVANCE')
    if len(events) >= 10000: raise ValueError('GRAPH_COLLECTION_HISTORY_BOUND')
    event = {'at': at, 'status': status, 'reason': reason}
    if failure is not None:event['failure']=failure
    for name,payload_reference in (('payload_reference',payload_reference),('catalog_manifest_reference',catalog_manifest_reference)):
        if payload_reference is None:continue
        from urllib.parse import urlsplit
        import re
        if (not isinstance(payload_reference,dict)or set(payload_reference)!={'sha256','bytes','uri'}
                or not re.fullmatch('[a-f0-9]{64}',payload_reference.get('sha256',''))
                or type(payload_reference['bytes'])is not int or not 0<=payload_reference['bytes']<=16*1024*1024
                or not isinstance(payload_reference['uri'],str)):
            raise ValueError('GRAPH_FAILURE_REFERENCE_SHAPE')
        uri=urlsplit(payload_reference['uri'])
        if not uri.scheme or uri.username or uri.password or uri.query or uri.fragment or not uri.path.endswith('/files/'+payload_reference['sha256']):
            raise ValueError('GRAPH_FAILURE_REFERENCE_URI')
        event[name]=dict(payload_reference)
    if events and events[-1] == event: return
    state.put(NAMESPACE, identity, {'events': [*events, event]}, revision=prior['revision'])


def unavailable(state, estate, owners, *, at=None):
    if len(owners) > 1000: raise ValueError('GRAPH_COLLECTION_OWNER_BOUND')
    when = c.timestamp(at) if at else None; result = {}
    identities = {encoded([estate, owner]): owner for owner in owners}
    if not identities:return result
    rows = state._read_transaction(lambda db: state.sql(db,
        'SELECT identity,body,body_hash FROM state_documents WHERE namespace=? AND identity IN (' +
        ','.join('?' for _ in identities) + ')', (NAMESPACE, *sorted(identities))).fetchall())
    for identity, raw, body_hash in rows:
        body = json.loads(raw)
        if sha(body) != body_hash:raise StateConflict('STATE_DOCUMENT_HASH_DIFFERS')
        owner = identities[identity]
        events = body['events']
        eligible = [event for event in events if when is None or event['at'] <= when]
        if eligible and eligible[-1]['status'] in ('REFRESHING', 'UNAVAILABLE'):
            result[owner] = eligible[-1]
    return result

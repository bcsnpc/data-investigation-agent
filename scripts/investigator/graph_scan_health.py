"""Append-only owner collection observations; definition history stays immutable."""
from . import estate_graph_contract as c
from .shared_state import encoded

NAMESPACE = 'graph_owner_collection'
STATES = frozenset({'REFRESHING', 'CURRENT', 'UNAVAILABLE', 'DELETED'})


def record(state, estate, owner, at, status, reason=None):
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
    if events and events[-1] == event: return
    state.put(NAMESPACE, identity, {'events': [*events, event]}, revision=prior['revision'])


def unavailable(state, estate, owners, *, at=None):
    if len(owners) > 1000: raise ValueError('GRAPH_COLLECTION_OWNER_BOUND')
    when = c.timestamp(at) if at else None; result = {}
    for owner in sorted(owners):
        try: events = state.get(NAMESPACE, encoded([estate, owner]))['body']['events']
        except KeyError: continue
        eligible = [event for event in events if when is None or event['at'] <= when]
        if eligible and eligible[-1]['status'] in ('REFRESHING', 'UNAVAILABLE'):
            result[owner] = eligible[-1]
    return result

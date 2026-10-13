"""Bounded owner-level graph refresh; unchanged definitions are never re-extracted."""
import copy
from .shared_state import encoded, sha
from . import estate_graph_contract as contract

NAMESPACE = 'graph_scan_cursor'


class IncrementalScanner:
    def __init__(self, repository, collector, extract, *, max_owners=100):
        if type(max_owners) is not int or not 1 <= max_owners <= 1000:
            raise ValueError('GRAPH_SCAN_OWNER_BOUND')
        self.repo, self.collector, self.extract, self.limit = repository, collector, extract, max_owners

    def run(self, estate, at):
        from .graph_scan_health import record as health
        at = contract.timestamp(at)
        identity = encoded([estate, self.collector.identity])
        try: previous = self.repo.state.get(NAMESPACE, identity)
        except KeyError: previous = {'revision': None, 'body': {'owners': {}, 'observed_at': None}}
        old = previous['body']['owners']; latest = copy.deepcopy(old)
        if previous['body']['observed_at'] and at <= previous['body']['observed_at']:
            raise ValueError('GRAPH_SCAN_TIME_MUST_ADVANCE')
        try: listing = self.collector.list_changes()
        except (RuntimeError, PermissionError, TimeoutError) as error:
            for owner in old:
                health(self.repo.state, estate, owner, at, 'UNAVAILABLE', 'Item listing unavailable: ' + type(error).__name__)
            raise
        if set(listing) != {'items', 'complete'} or type(listing['complete']) is not bool:
            raise ValueError('GRAPH_CHANGE_LISTING_SHAPE')
        if not isinstance(listing['items'], list) or len(listing['items']) > self.limit:
            raise ValueError('GRAPH_SCAN_OWNER_BOUND')
        signals = {}
        for signal in listing['items']:
            if set(signal) != {'owner', 'fingerprint', 'deleted'} or not isinstance(signal['owner'], str) or not signal['owner']:
                raise ValueError('GRAPH_CHANGE_SIGNAL_SHAPE')
            if signal['owner'] in signals or type(signal['deleted']) is not bool:
                raise ValueError('GRAPH_CHANGE_SIGNAL_DUPLICATE_OR_STATE')
            if signal['fingerprint'] is not None and (not isinstance(signal['fingerprint'], str) or len(signal['fingerprint']) != 64):
                raise ValueError('GRAPH_CHANGE_SIGNAL_FINGERPRINT')
            signals[signal['owner']] = signal
        if listing['complete']:
            for owner in old.keys() - signals.keys():
                signals[owner] = {'owner': owner, 'fingerprint': None, 'deleted': True}
        if len(signals) > self.limit: raise ValueError('GRAPH_SCAN_OWNER_BOUND')
        from .graph_scan_health import unavailable
        unconfirmed=unavailable(self.repo.state,estate,set(signals))
        results = []
        for owner, signal in sorted(signals.items()):
            before = old.get(owner)
            if signal['deleted']:
                if before and not before.get('deleted'):
                    digest = sha({'deleted': owner, 'previous': before['definition_hash']})
                    result = self.repo.replace({'estate': estate, 'owner': owner, 'observed_at': at,
                        'definition_hash': digest, 'nodes': [], 'edges': []})
                    health(self.repo.state, estate, owner, at, 'DELETED')
                    latest[owner] = {'signal': signal['fingerprint'], 'definition_hash': digest, 'deleted': True}
                    results.append({'owner': owner, 'status': 'DELETED', 'graph': result})
                continue
            if before and not before.get('deleted') and signal['fingerprint'] is not None and before['signal'] == signal['fingerprint'] and owner not in unconfirmed:
                results.append({'owner': owner, 'status': 'UNCHANGED_SIGNAL'}); continue
            try:
                health(self.repo.state, estate, owner, at, 'REFRESHING', 'Current owner definition is awaiting a bounded refresh.')
                payload = self.collector.fetch(owner)
                if set(payload) != {'assets', 'source_asset_ids'} or not isinstance(payload['assets'], list):
                    raise ValueError('GRAPH_OWNER_DEFINITION_SHAPE')
                digest = sha(payload)
                if before and not before.get('deleted') and before['definition_hash'] == digest:
                    result = {'status': 'UNCHANGED_DEFINITION'}
                else:
                    graph = self.extract(estate, owner, at, payload)
                    if graph['estate'] != estate or graph['owner'] != owner or graph['observed_at'] != at:
                        raise ValueError('GRAPH_EXTRACT_OWNER_DIFFERS')
                    result = {'status': 'RESCANNED', 'graph': self.repo.replace(graph)}
                health(self.repo.state, estate, owner, at, 'CURRENT')
                latest[owner] = {'signal': signal['fingerprint'], 'definition_hash': digest, 'deleted': False}
                results.append({'owner': owner, **result})
            except (RuntimeError, PermissionError, TimeoutError) as error:
                # Do not advance this owner's cursor. Permission denial never deletes it.
                health(self.repo.state, estate, owner, at, 'UNAVAILABLE', 'Owner definition refresh unavailable: ' + type(error).__name__)
                results.append({'owner': owner, 'status': 'UNAVAILABLE', 'reason': type(error).__name__})
        self.repo.state.put(NAMESPACE, identity, {'owners': latest, 'observed_at': at}, revision=previous['revision'])
        return {'estate': estate, 'observed_at': at, 'listing_complete': listing['complete'], 'owners': results}

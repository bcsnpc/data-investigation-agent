"""Bounded owner-level graph refresh; unchanged definitions are never re-extracted."""
import copy
from .shared_state import encoded, sha
from . import estate_graph_contract as contract

NAMESPACE = 'graph_scan_cursor'


def is_stop_condition(error):
    """Policy and budget refusals stop a scan, never become ordinary coverage gaps."""
    from .live_gateway import GatewayDenied
    from .usage_governance import UsageHold
    from .shared_state import StateConflict
    from .discovery_collect import BudgetExceeded
    from .model_spend import SpendHold
    from .action_budget import RetrievalBudgetExceeded
    return isinstance(error,(GatewayDenied,UsageHold,StateConflict,BudgetExceeded,SpendHold,RetrievalBudgetExceeded)) or str(error)=='GRAPH_PHYSICAL_REQUEST_CAP'


class IncrementalScanner:
    def __init__(self, repository, collector, extract, *, max_owners=100, reconcile=None, observation_clock=None):
        if type(max_owners) is not int or not 1 <= max_owners <= 1000:
            raise ValueError('GRAPH_SCAN_OWNER_BOUND')
        self.repo, self.collector, self.extract, self.limit = repository, collector, extract, max_owners
        self.reconcile=reconcile
        self.observation_clock=observation_clock

    def run(self, estate, at):
        from .graph_scan_health import record as health
        at = contract.timestamp(at)
        identity = encoded([estate, self.collector.identity])
        try: previous = self.repo.state.get(NAMESPACE, identity)
        except KeyError: previous = {'revision': None, 'body': {'owners': {}, 'observed_at': None}}
        old = previous['body']['owners']; latest = copy.deepcopy(old)
        if previous['body']['observed_at'] and at <= previous['body']['observed_at']:
            raise ValueError('GRAPH_SCAN_TIME_MUST_ADVANCE')
        configured=getattr(self.collector,'configured_owners',())
        if not isinstance(configured,(tuple,list,set,frozenset)):configured=()
        if len(configured)>self.limit or any(not isinstance(owner,str)or not owner for owner in configured):
            raise ValueError('GRAPH_OWNER_ALLOWLIST')
        watched=set(old)|set(configured)
        if len(watched)>self.limit:raise ValueError('GRAPH_SCAN_OWNER_BOUND')
        from .adapters.metadata_error import safe_failure
        try: listing = self.collector.list_changes()
        except Exception as error:
            detail=safe_failure(error)
            for owner in watched:
                health(self.repo.state, estate, owner, at, 'UNAVAILABLE', 'Item listing unavailable: ' + type(error).__name__,failure=detail)
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
        if not listing['complete']:
            for owner in sorted(watched-signals.keys()):
                reason='GRAPH_OWNER_NOT_VISIBLE: configured or retained owner absent from incomplete listing; deletion is not established.'
                health(self.repo.state,estate,owner,at,'UNAVAILABLE',reason)
                results.append({'owner':owner,'status':'UNAVAILABLE','reason':reason})
        for owner, signal in sorted(signals.items()):
            owner_at=contract.timestamp(self.observation_clock()) if self.observation_clock else at
            before = old.get(owner)
            if signal['deleted']:
                if before and not before.get('deleted'):
                    digest = sha({'deleted': owner, 'previous': before['definition_hash']})
                    result = (self.reconcile(estate,owner,owner_at,{'assets':[],'source_asset_ids':[]}) if self.reconcile else
                        self.repo.replace({'estate': estate, 'owner': owner, 'observed_at': owner_at,
                        'definition_hash': digest, 'nodes': [], 'edges': []}))
                    health(self.repo.state, estate, owner, owner_at, 'DELETED')
                    latest[owner] = {'signal': signal['fingerprint'], 'definition_hash': digest, 'deleted': True}
                    results.append({'owner': owner, 'status': 'DELETED', 'graph': result})
                continue
            if before and not before.get('deleted') and signal['fingerprint'] is not None and before['signal'] == signal['fingerprint'] and owner not in unconfirmed:
                results.append({'owner': owner, 'status': 'UNCHANGED_SIGNAL'}); continue
            try:
                health(self.repo.state, estate, owner, owner_at, 'REFRESHING', 'Current owner definition is awaiting a bounded refresh.')
                payload = self.collector.fetch(owner)
                if self.observation_clock:owner_at=contract.timestamp(self.observation_clock())
                if set(payload) != {'assets', 'source_asset_ids'} or not isinstance(payload['assets'], list):
                    raise ValueError('GRAPH_OWNER_DEFINITION_SHAPE')
                digest = sha(payload)
                if before and not before.get('deleted') and before['definition_hash'] == digest:
                    result = {'status': 'UNCHANGED_DEFINITION'}
                elif self.reconcile is not None:
                    result={'status':'RESCANNED','graph':self.reconcile(estate,owner,owner_at,payload)}
                else:
                    graph = self.extract(estate, owner, owner_at, payload)
                    if graph['estate'] != estate or graph['owner'] != owner or graph['observed_at'] != owner_at:
                        raise ValueError('GRAPH_EXTRACT_OWNER_DIFFERS')
                    result = {'status': 'RESCANNED', 'graph': self.repo.replace(graph)}
                health(self.repo.state, estate, owner, owner_at, 'CURRENT')
                latest[owner] = {'signal': signal['fingerprint'], 'definition_hash': digest, 'deleted': False}
                results.append({'owner': owner, **result})
            except Exception as error:
                # Do not advance this owner's cursor. Permission denial never deletes it.
                detail=safe_failure(error)
                from .graph_asset_catalog import failure_reference,failure_manifest_reference
                reference=failure_reference(error,estate,owner)
                retained={'payload_reference':reference,'catalog_manifest_reference':failure_manifest_reference(error,estate,owner)} if reference is not None else {}
                if reference is None:
                    from .adapters.graph_change_collector import failure_definition_reference
                    reference=failure_definition_reference(error,owner)
                    if reference is not None:retained={'payload_reference':reference}
                health(self.repo.state, estate, owner, owner_at, 'UNAVAILABLE', 'Owner definition refresh unavailable: ' + type(error).__name__,failure=detail,**retained)
                if is_stop_condition(error):raise
                results.append({'owner': owner, 'status': 'UNAVAILABLE', 'reason': type(error).__name__,'failure':detail,**retained})
        self.repo.state.put(NAMESPACE, identity, {'owners': latest, 'observed_at': at}, revision=previous['revision'])
        return {'estate': estate, 'observed_at': at, 'listing_complete': listing['complete'], 'owners': results}

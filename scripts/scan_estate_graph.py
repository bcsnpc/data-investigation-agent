"""Scheduled, bounded live graph refresh. Default is a deployment plan, not reads."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from investigator.shared_state import sha


class Meter:
    def __init__(self, state, accounts, limit):
        if not isinstance(accounts, list) or not accounts or len(set(accounts)) != len(accounts):
            raise ValueError('EXISTING_SHARED_BUDGET_ACCOUNTS_REQUIRED')
        if type(limit) is not int or not 1 <= limit <= 100: raise ValueError('GRAPH_PHYSICAL_REQUEST_BOUND')
        self.state, self.accounts, self.limit, self.used = state, accounts, limit, 0
        self.owner = 'graph-scan:' + str(uuid4())
        for account in accounts:
            if state.snapshot(account)['unit'] != 'requests': raise ValueError('GRAPH_REQUEST_ACCOUNT_UNIT')
    def __call__(self, execute):
        if self.used >= self.limit: raise ValueError('GRAPH_PHYSICAL_REQUEST_CAP')
        key = str(uuid4()); admitted = []
        try:
            for account in self.accounts:
                self.state.reserve(account, key, self.owner, '1', detail={'purpose': 'graph_metadata'})
                admitted.append(account)
        except BaseException:
            for account in admitted: self.state.settle(account, key, self.owner, '0')
            raise
        self.used += 1
        try: return execute()
        finally:
            for account in admitted: self.state.settle(account, key, self.owner, '1')


def validate(config):
    required = {'estate', 'workspace', 'owners', 'authentication', 'storage', 'definition_uri_prefix',
                'budget_accounts', 'max_requests', 'approval'}
    if not isinstance(config, dict) or set(config) != required: raise ValueError('GRAPH_SCHEDULE_CONFIGURATION')
    if not isinstance(config['approval'], str) or not config['approval'].strip():
        raise ValueError('GRAPH_SCHEDULE_OWNER_APPROVAL_REQUIRED')
    return config


def execute(config):
    import os
    from investigator.privacy_capture import ACTIVE
    if ACTIVE.get() is not None or os.environ.get('INVESTIGATOR_RECORDING_CLASS', 'EXACT') != 'EXACT':
        raise ValueError('GRAPH_PROJECTED_DEFINITION_CAPTURE_NOT_IMPLEMENTED')
    from investigator.shared_state import configured_state
    from investigator.estate_graph_repository import GraphRepository
    from investigator.estate_graph_incremental import IncrementalScanner
    from investigator.adapters.graph_change_collector import FabricChanges
    from investigator.adapters.estate_graph_static import extract
    from investigator.adapters.blob_artifacts import recording_stores
    from investigator.graph_definitions import DefinitionSink
    from metadata_auth import MetadataHttp
    config = validate(config)
    state = configured_state()
    if state is None: raise ValueError('SHARED_GRAPH_STATE_REQUIRED')
    # Migrations are operator-owned; a scheduled reader must not create tables.
    repo = GraphRepository(state)
    meter = Meter(state, config['budget_accounts'], config['max_requests'])
    mode = config['authentication'].get('mode')
    if mode == 'federated_reader':
        from investigator.adapters.federated_reader import Tokens
    elif mode == 'managed_identity':
        from investigator.adapters.managed_identity import Tokens
    else: raise ValueError('GRAPH_SCHEDULE_IDENTITY_MODE_UNSUPPORTED')
    http = MetadataHttp(Tokens(config['authentication']), meter=meter)
    collector = FabricChanges(config['workspace'], config['owners'], http)
    files, _ = recording_stores(config['storage'])
    sink = DefinitionSink(files, config['definition_uri_prefix'], recording_class='EXACT')
    scanner = IncrementalScanner(repo, collector, lambda estate, owner, at, payload:
        extract(estate, payload['assets'], sink, observed_at=at, owner=owner, source_asset_ids=payload['source_asset_ids']))
    at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    try:
        result = scanner.run(config['estate'], at)
        result.update(physical_requests=meter.used, approval=config['approval'], config_hash=sha(config))
        state.put('graph_scan_run', meter.owner, result)
        return result
    except BaseException as error:
        state.put('graph_scan_run', meter.owner, {'estate': config['estate'], 'observed_at': at,
            'status': 'FAILED', 'error_type': type(error).__name__, 'physical_requests': meter.used,
            'approval': config['approval'], 'config_hash': sha(config)})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args(); config = validate(json.loads(args.config.read_text(encoding='utf-8-sig')))
    result = execute(config) if args.apply else {'status': 'PLAN_ONLY', 'config_hash': sha(config),
        'schedule': '0 */6 * * *', 'owners': len(config['owners']), 'approval': config['approval'],
        'requirements': ['Existing Container Apps Job; no new resource', 'Existing shared request accounts and reserve',
                         'Exact gateway grants and reader permissions; no automatic elevation',
                         'Operator-migrated graph tables', 'Owner-approved deployment and controlled change/revert']}
    with args.receipt.open('x', encoding='utf8') as handle: json.dump(result, handle, indent=2)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__': main()

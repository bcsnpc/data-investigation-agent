"""Acquire semantic refresh evidence through the configured read-only connector."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from uuid import UUID

from investigation_checks import canonical, run_checks, timestamp
from metadata_auth import WorkerTransport
from metadata_config import ROOT, load_config
from metadata_connectors import FabricMetadataConnector, PowerBIMetadataConnector


def collect(config, model_id, lineage_run, max_age_seconds=None):
    model_id = str(UUID(model_id))
    fabric = config['fabric']
    auth = fabric['auth']
    transport = WorkerTransport(auth['python'], auth['tenant_id'], ROOT/'scripts/metadata_worker.py')
    connector = PowerBIMetadataConnector(FabricMetadataConnector(fabric['workspace_id'], transport, transport.tables))
    history = connector.get_refresh_history({'id': model_id, 'type': 'SemanticModel'})
    # Retain identifiers and timestamps, not service error payloads or credentials.
    retained = [{key: row.get(key) for key in ('requestId', 'refreshType', 'startTime', 'endTime', 'status')} for row in history]
    successful = [row for row in retained if row['status'] == 'Completed' and row['endTime']]
    last = max(successful, key=lambda row: timestamp(row['endTime'])) if successful else None
    data = {'last_success_at': last['endTime'] if last else None, 'history': retained}
    captured = datetime.now(timezone.utc).isoformat()
    item = {'asset': f"fabric://{fabric['workspace_id']}/{model_id}", 'captured_at': captured,
            'query_id': f"powerbi:groups/{fabric['workspace_id']}/datasets/{model_id}/refreshes",
            'data': data, 'result_hash': hashlib.sha256(canonical(data).encode()).hexdigest()}
    return run_checks(config['storage']['database'], {'lineage_run': lineage_run, 'as_of': captured,
        'checks': [{'kind': 'freshness', 'observation': item, 'max_age_seconds': max_age_seconds}]})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT/'infra/metadata/development.json')
    parser.add_argument('--model', required=True)
    parser.add_argument('--lineage-run', required=True)
    parser.add_argument('--max-age-seconds', type=int)
    args = parser.parse_args()
    print(json.dumps(collect(load_config(args.config), args.model, args.lineage_run, args.max_age_seconds), indent=2))

"""Targeted immutable report/model definition scan; no business queries or SQL scan."""
import argparse
from pathlib import Path
from uuid import UUID
import json
from metadata_config import ROOT, load_config
from metadata_auth import WorkerTransport
from metadata_connectors import FabricMetadataConnector, PowerBIMetadataConnector
from metadata_inventory import Inventory, collect_fabric


def collect(database, connector, selected_ids):
    selected = [str(UUID(value)) for value in selected_ids]
    if not 1 <= len(selected) <= 20 or len(set(selected)) != len(selected):
        raise ValueError('Select 1 to 20 unique report/model IDs')
    # Discovery is read-only; validate all selections before creating a scan.
    items = connector.discover_assets()
    chosen = [item for item in items if item['id'] in selected]
    if len(chosen) != len(selected) or {i['id'] for i in chosen} != set(selected):
        raise ValueError('Selected assets are missing or ambiguous')
    if any(i['type'] not in ('Report', 'SemanticModel') for i in chosen):
        raise ValueError('Only Report and SemanticModel selections are supported')

    class Selected:
        workspace = connector.workspace
        def discover_assets(self): return chosen
        def get_definition(self, asset): return connector.get_definition(asset)
        def get_refresh_history(self, asset): return connector.get_refresh_history(asset)

    # collect_fabric accepts separate discovery and Power BI readers. This adapter
    # uses the supplied reader for both definitions and model refresh history.
    reader = Selected()
    store = Inventory(database)
    try:
        store.observe('scan', 'selection_scope', 'AVAILABLE', 'explicit operator selection',
                      {'asset_ids': selected, 'scope': 'selected_report_model_metadata',
                       'report_model_association_verified': False, 'snapshot_comparable': False})
        collect_fabric(store, reader, reader)
        return dict(store.finish(), scope='selected_report_model_metadata', selected_ids=selected,
                    snapshot_comparable=False, report_model_association_verified=False)
    except Exception:
        store.finish(failed=True)
        raise
    finally:
        store.db.close()


class ReportReader:
    def __init__(self, fabric):
        self.workspace = fabric.workspace
        self.reader = PowerBIMetadataConnector(fabric)
    def discover_assets(self): return self.reader.discover_assets()
    def get_definition(self, asset): return self.reader.get_definition(asset)
    def get_refresh_history(self, asset): return self.reader.get_refresh_history(asset)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT/'infra/metadata/development.json')
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--item', action='append', required=True, help='Repeat for each report/model UUID')
    args = parser.parse_args()
    config = load_config(args.config)
    auth = config['fabric']['auth']
    transport = WorkerTransport(auth['python'], auth['tenant_id'], ROOT/'scripts/metadata_worker.py')
    fabric = FabricMetadataConnector(config['fabric']['workspace_id'], transport, transport.tables)
    try:
        result = collect(args.database, ReportReader(fabric), args.item)
    except Exception as error:
        print(json.dumps({'status': 'FAILED', 'error_type': type(error).__name__}))
        raise SystemExit(1)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['status'] == 'COMPLETE' else 1)

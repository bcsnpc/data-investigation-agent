"""Read-only metadata discovery with immutable SQLite scan snapshots.

No business queries, refreshes, deployments or inferred lineage are performed.
"""
import argparse
import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from metadata_config import ROOT, load_config
from metadata_auth import WorkerTransport, PowerShellSqlCatalog
from metadata_protocol import pages, definition
from metadata_connectors import SqlMetadataConnector, FabricMetadataConnector, PowerBIMetadataConnector


def utc():
    return datetime.now(timezone.utc).isoformat()


def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


class Inventory:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.executescript('''
        PRAGMA foreign_keys=ON;
        CREATE TABLE IF NOT EXISTS scans(id TEXT PRIMARY KEY, started TEXT, ended TEXT, status TEXT);
        CREATE TABLE IF NOT EXISTS assets(scan_id TEXT REFERENCES scans(id), id TEXT, parent_id TEXT,
          kind TEXT, name TEXT, source TEXT, collected_at TEXT, owner TEXT,
          content_hash TEXT, metadata TEXT, PRIMARY KEY(scan_id,id));
        CREATE TABLE IF NOT EXISTS observations(scan_id TEXT REFERENCES scans(id), asset_id TEXT,
          capability TEXT, status TEXT, source TEXT, collected_at TEXT, detail TEXT);
        ''')
        self.scan = str(uuid.uuid4())
        self.db.execute('INSERT INTO scans VALUES(?,?,NULL,?)', (self.scan, utc(), 'RUNNING'))
        self.db.commit()

    def asset(self, id, kind, name, source, metadata, parent=None):
        content = encode(metadata)
        self.db.execute('INSERT INTO assets VALUES(?,?,?,?,?,?,?,?,?,?)',
                        (self.scan, id, parent, kind, name, source, utc(), None,
                         hashlib.sha256(content.encode()).hexdigest(), content))
        return id

    def observe(self, asset, capability, status, source, detail):
        self.db.execute('INSERT INTO observations VALUES(?,?,?,?,?,?,?)',
                        (self.scan, asset, capability, status, source, utc(), encode(detail)))

    def finish(self, failed=False):
        gaps = self.db.execute("SELECT count(*) FROM observations WHERE scan_id=? AND status='UNAVAILABLE'", (self.scan,)).fetchone()[0]
        state = 'FAILED' if failed else ('PARTIAL' if gaps else 'COMPLETE')
        self.db.execute('UPDATE scans SET ended=?,status=? WHERE id=?', (utc(), state, self.scan))
        self.db.commit()
        counts = dict(self.db.execute('SELECT kind,count(*) FROM assets WHERE scan_id=? GROUP BY kind', (self.scan,)))
        return {'scan_id': self.scan, 'status': state, 'assets': counts, 'unavailable_capabilities': gaps}


def expand_definition(store, item_id, kind, parts, source):
    for path, content in parts.items():
        store.asset(item_id + '/part/' + quote(path, safe=''), 'DefinitionPart', path, source,
                    {'path': path, 'content': content}, item_id)
    if kind == 'SemanticModel':
        if 'model.bim' not in parts:
            raise ValueError('TMSL model.bim unavailable')
        model = json.loads(parts['model.bim'])['model']
        for table in model.get('tables', []):
            tid = item_id + '/table/' + quote(table['name'], safe='')
            store.asset(tid, 'SemanticTable', table['name'], source, table, item_id)
            for key, child_kind in [('columns', 'SemanticColumn'), ('measures', 'Measure')]:
                for child in table.get(key, []):
                    store.asset(tid + '/' + key + '/' + quote(child['name'], safe=''), child_kind, child['name'], source, child, tid)
        for relationship in model.get('relationships', []):
            store.asset(item_id + '/relationship/' + quote(relationship['name'], safe=''), 'SemanticRelationship', relationship['name'], source, relationship, item_id)
    elif kind == 'Report':
        if not any(path.endswith('/page.json') for path in parts):
            raise ValueError('Native PBIR pages unavailable')
        for path, content in parts.items():
            if path.endswith('/page.json') or path.endswith('/visual.json'):
                obj = json.loads(content)
                child_kind = 'ReportPage' if path.endswith('/page.json') else 'ReportVisual'
                # Page/visual IDs come from the live definition, not configured report names.
                parent = item_id if child_kind == 'ReportPage' else item_id + '/page/' + path.split('/')[2]
                aid = item_id + '/page/' + path.split('/')[2] if child_kind == 'ReportPage' else item_id + '/visual/' + quote(path, safe='')
                store.asset(aid, child_kind, obj.get('displayName', obj.get('name', path)), source, obj, parent)


def collect_sql(store, snapshot):
    source = 'Azure SQL sys catalog'
    root = 'sql://' + snapshot['server'].removeprefix('tcp:').split(',')[0] + '/' + snapshot['database']
    store.asset(root, 'SqlDatabase', snapshot['database'], source, {'captured_at': snapshot['collected_at_utc']})
    for obj in snapshot['objects']:
        oid = obj['object_id']
        data = dict(obj)
        for key in ('columns', 'keys', 'definitions'):
            data[key] = [x for x in snapshot[key] if x['object_id'] == oid]
        for key in ('foreign_keys', 'checks'):
            data[key] = [x for x in snapshot[key] if x['parent_object_id'] == oid]
        aid = root + '/object/' + str(oid)
        store.asset(aid, 'SqlObject', obj['schema_name'] + '.' + obj['name'], source, data, root)
        for col in data['columns']:
            store.asset(aid + '/column/' + str(col['column_id']), 'SqlColumn', col['name'], source, col, aid)
    allowed = bool(snapshot['permissions'] and snapshot['permissions'][0]['can_view_definition'])
    store.observe(root, 'catalog_visibility', 'AVAILABLE' if allowed else 'UNAVAILABLE', source,
                  {'view_definition': allowed, 'scope': snapshot.get('visibility_schema', 'app') + ' schema; other objects only when visible to configured identity'})
    store.observe(root, 'business_owner', 'UNKNOWN', source, 'Database principals are not assumed to be business owners.')
    store.observe(root, 'data_freshness', 'NOT_COLLECTED', source, 'Catalog modification dates are schema dates, not business-data watermarks.')


def attempt(store, aid, capability, endpoint, fn):
    savepoint = "capability_" + uuid.uuid4().hex
    store.db.execute("SAVEPOINT " + savepoint)
    try:
        value = fn()
        store.db.execute("RELEASE " + savepoint)
        store.observe(aid, capability, 'AVAILABLE', endpoint, value)
        return value
    except Exception as exc:
        store.db.execute("ROLLBACK TO " + savepoint)
        store.db.execute("RELEASE " + savepoint)
        # CLI errors may contain auth output; never persist or print raw exception text.
        store.observe(aid, capability, 'UNAVAILABLE', endpoint, {'error_type': type(exc).__name__})
        return None


def collect_fabric(store, connector, powerbi):
    workspace = connector.workspace
    endpoint = f'workspaces/{workspace}/items'
    items = connector.discover_assets()
    root = 'fabric://' + workspace
    store.asset(root, 'Workspace', workspace, endpoint, {'id': workspace})
    for item in items:
        aid = root + '/' + item['id']
        base = f"workspaces/{workspace}/items/{item['id']}"
        kind = item['type']
        store.asset(aid, kind, item['displayName'], endpoint, item, root)
        store.observe(aid, 'business_owner', 'UNKNOWN', endpoint, 'No verified team ownership mapping configured.')
        if kind in ('Notebook', 'DataPipeline', 'CopyJob', 'SemanticModel', 'Report'):
            target = base + '/getDefinition' + ('?format=TMSL' if kind == 'SemanticModel' else '')
            def extract():
                reader = powerbi if kind in ('SemanticModel', 'Report') else connector
                parts = reader.get_definition(item)
                expand_definition(store, aid, kind, parts, target)
                return {'parts': len(parts)}
            attempt(store, aid, 'definition', target, extract)
        if kind == 'Lakehouse':
            target = f"workspaces/{workspace}/lakehouses/{item['id']}/tables"
            inventory = attempt(store, aid, 'tables', target, lambda: connector.get_tables(item))
            for table in (inventory or {}).get('tables', []):
                name = (table.get('schema_name', table.get('schemaName', '')) + '.' + table['name']).lstrip('.')
                tid = aid + '/table/' + quote(name, safe='')
                store.asset(tid, 'LakehouseTable', name, inventory['source'], table, aid)
                for column in table.get('columns') or []:
                    store.asset(tid + '/column/' + quote(column['name'], safe=''), 'LakehouseColumn', column['name'], inventory['source'], column, tid)
            has_columns = bool(inventory and inventory.get('column_schema'))
            store.observe(aid, 'column_schema', 'AVAILABLE' if has_columns else 'NOT_COLLECTED', target,
                          'OneLake table details' if has_columns else 'Fabric table listing has no column schemas.')
        if kind in ('Notebook', 'DataPipeline', 'CopyJob'):
            target = base + '/jobs/instances'
            attempt(store, aid, 'run_history', target, lambda: connector.get_refresh_history(item))
            store.observe(aid, 'expected_refresh_frequency', 'UNKNOWN', target, 'No verified schedule contract configured.')
        if kind == 'SemanticModel':
            target = f"groups/{workspace}/datasets/{item['id']}/refreshes"
            attempt(store, aid, 'refresh_history', target, lambda: powerbi.get_refresh_history(item))
        print('Collected ' + kind + ': ' + item['displayName'], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'infra/metadata/development.json')
    parser.add_argument('--database', type=Path, help='Override inventory database location')
    args = parser.parse_args()
    config = load_config(args.config)
    database = args.database or Path(config['storage']['database'])
    sql_reader = PowerShellSqlCatalog(ROOT / 'infra/scripts/Get-SqlMetadata.ps1', config['sql']['auth']['credential_file'])
    sql = SqlMetadataConnector(config['sql'], sql_reader)
    auth = config['fabric']['auth']
    transport = WorkerTransport(auth['python'], auth['tenant_id'], ROOT / 'scripts/metadata_worker.py')
    fabric = FabricMetadataConnector(config['fabric']['workspace_id'], transport, transport.tables)
    powerbi = PowerBIMetadataConnector(fabric)
    store = Inventory(database)
    def sql_scan():
        collect_sql(store, sql.discover_assets())
        return {'collected': True}
    sql_result = attempt(store, 'scan', 'sql_collection', 'Azure SQL catalog', sql_scan)
    def fabric_scan():
        collect_fabric(store, fabric, powerbi)
        return {'collected': True}
    fabric_result = attempt(store, 'scan', 'fabric_collection', 'Fabric workspace', fabric_scan)
    summary = store.finish(failed=sql_result is None and fabric_result is None)
    output = Path(database).parent / 'latest.json'
    output.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    store.db.close()
    return 1 if summary['status'] != 'COMPLETE' else 0


if __name__ == '__main__':
    raise SystemExit(main())

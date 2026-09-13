"""Acquire bounded order metrics and retain ordered boundary evidence."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import uuid

from investigation_checks import canonical, compare, compatible, number, timestamp
from investigation_query_worker import filters
from lineage_graph import load_graph
from metadata_auth import WorkerTransport
from metadata_config import ROOT, load_config
from snapshot_provenance import continuity

LAYERS = ('sql', 'bronze', 'silver', 'gold', 'semantic')
MEASURES = {'order_count': 'Order Count', 'net_cash': 'Net Cash'}


def boundaries(graph, chain):
    """A missing earlier boundary prevents identification of the first divergence."""
    if len(chain) < 2 or len({x['asset'] for x in chain}) != len(chain):
        raise ValueError('An ordered path of distinct assets is required')
    results = []
    prefix_verified = True
    first_verified = None
    first_observed = None
    observed_prefix = True
    for left, right in zip(chain, chain[1:]):
        trace = graph.traverse(right['asset'])
        if left['asset'] not in {a['id'] for a in trace['assets']}:
            raise ValueError('Boundary is not connected by captured lineage')
        item = {'upstream': left['asset'], 'downstream': right['asset']}
        if left.get('status') != 'AVAILABLE' or right.get('status') != 'AVAILABLE':
            item.update(status='UNAVAILABLE', observed_value='UNKNOWN')
        else:
            item.update(compare(left, right, 'total'))
            # Numerical agreement is diagnostic only, never snapshot proof.
            reasons = compatible(left, right)
            other_gaps = [r for r in reasons if not r.startswith('source_snapshot:')]
            item['observed_value'] = ('UNKNOWN' if other_gaps else
                                      'MATCH' if number(left['data']) == number(right['data']) else 'MISMATCH')
        item['lineage_gaps'] = trace['unresolved']
        if observed_prefix and item['observed_value'] == 'MISMATCH' and first_observed is None:
            first_observed = {'upstream': left['asset'], 'downstream': right['asset']}
        observed_prefix = observed_prefix and item['observed_value'] == 'MATCH'
        if prefix_verified and item['status'] == 'MISMATCH' and not trace['unresolved'] and first_verified is None:
            first_verified = {'upstream': left['asset'], 'downstream': right['asset']}
        prefix_verified = prefix_verified and item['status'] == 'MATCH' and not trace['unresolved']
        results.append(item)
    return {'boundaries': results, 'first_verified_divergence': first_verified,
            'first_observed_difference': first_observed, 'classification': 'UNRESOLVED',
            'limitation': 'Observed value differences are candidates; even a comparable divergence does not prove a technical defect'}


def metric_observation(asset, metric, result, currency, order_id, layer):
    base = {'asset': asset, 'layer': layer, 'metric_contract': metric+'-orderops-v1',
            'grain': 'order', 'currency': currency, 'filters': {'order_id': order_id},
            'source_snapshot': None,
            'snapshot_gap': 'Independent live reads have no proven common source snapshot'}
    if result.get('error'):
        return dict(base, status='UNAVAILABLE', **{key: result.get(key) for key in ('error', 'error_type', 'stage', 'sql_error_number')})
    value = result['values'][metric]
    number(value)
    run_evidence = {key: val for key, val in result['values'].items() if key not in MEASURES}
    return dict(base, status='AVAILABLE', data=value, captured_at=result['captured_at'],
                run_evidence=run_evidence,
                run_evidence_hash=hashlib.sha256(canonical(run_evidence).encode()).hexdigest(),
                query_id=hashlib.sha256(result['query'].encode()).hexdigest(), query=result['query'],
                result_hash=hashlib.sha256(canonical(value).encode()).hexdigest())


def asset_path(graph, config, estate, metric):
    workspace = config['fabric']['workspace_id']
    sql = config['sql']
    ids = [graph.find('SqlObject', 'app.orders', f"sql://{sql['server']}/{sql['database']}")]
    for layer, table in [('bronze', 'app.orders'), ('silver', 'fact_order'), ('gold', 'order_line_summary')]:
        ids.append(graph.find('LakehouseTable', table, f"fabric://{workspace}/{estate[layer+'_lakehouse_id']}"))
    model = f"fabric://{workspace}/{estate['semantic_model_id']}"
    table = graph.find('SemanticTable', 'FactOrderLine', model)
    ids.append(graph.find('Measure', MEASURES[metric], table) if table else None)
    if not all(ids):
        raise ValueError('Supported metric assets missing from lineage build')
    return ids


def worker(config, request):
    auth = config['fabric']['auth']
    result = subprocess.run([auth['python'], str(ROOT/'scripts/investigation_query_worker.py')],
                            input=json.dumps(dict(request, tenant=auth['tenant_id'])),
                            text=True, capture_output=True, timeout=180)
    if result.returncode:
        # Worker emits only fixed status and an exception class, never error bodies.
        try:
            failure = json.loads(result.stdout)
            return {'error': 'QUERY_UNAVAILABLE', 'error_type': failure.get('error_type', 'WorkerReadFailed')}
        except (ValueError, AttributeError):
            return {'error': 'QUERY_UNAVAILABLE', 'error_type': 'WorkerReadFailed'}
    return json.loads(result.stdout)


def acquire(config, estate, lineage_run, currency, order_id, query=worker):
    filters(currency, order_id)
    if estate['workspace_id'] != config['fabric']['workspace_id']:
        raise ValueError('Estate and auth workspace differ')
    graph = load_graph(config['storage']['database'], lineage_run)
    paths = {metric: asset_path(graph, config, estate, metric) for metric in MEASURES}
    # Validate all planned paths before any cloud query.
    for ids in paths.values():
        boundaries(graph, [{'asset': x, 'status': 'UNAVAILABLE'} for x in ids])
    auth = config['fabric']['auth']
    http = WorkerTransport(auth['python'], auth['tenant_id'], ROOT/'scripts/metadata_worker.py')
    raw = {}
    acquisitions = {}
    for layer in LAYERS:
        request = {'layer': layer, 'currency': currency, 'order_id': order_id}
        try:
            if layer == 'sql':
                request.update(server=config['sql']['server'], database=config['sql']['database'],
                               credential_file=config['sql']['auth']['credential_file'])
            elif layer == 'semantic':
                request.update(workspace=estate['workspace_id'], model=estate['semantic_model_id'])
            else:
                endpoint = f"workspaces/{estate['workspace_id']}/lakehouses/{estate[layer+'_lakehouse_id']}"
                props = http(endpoint)['text']['properties']['sqlEndpointProperties']
                request.update(server=props['connectionString'], database=props['id'])
                acquisitions[layer] = {'endpoint': endpoint, 'properties': props,
                                       'captured_at': datetime.now(timezone.utc).isoformat()}
            raw[layer] = query(config, request)
            if not raw[layer].get('error'):
                for metric in MEASURES:
                    number(raw[layer]['values'][metric])
                timestamp(raw[layer]['captured_at'])
                if not isinstance(raw[layer]['query'], str) or not raw[layer]['query']:
                    raise ValueError('Query evidence missing')
        except (RuntimeError, subprocess.TimeoutExpired, KeyError, ValueError) as exc:
            raw[layer] = {'error': 'QUERY_UNAVAILABLE', 'error_type': type(exc).__name__}
    chains = {metric: [metric_observation(asset, metric, raw[layer], currency, order_id, layer)
                       for layer, asset in zip(LAYERS, ids)] for metric, ids in paths.items()}
    results = {metric: boundaries(graph, chain) for metric, chain in chains.items()}
    run = str(uuid.uuid4())
    captured = datetime.now(timezone.utc).isoformat()
    request = {'kind': 'cross_layer_metrics', 'lineage_run': lineage_run, 'as_of': captured,
               'observations': chains, 'endpoint_evidence': acquisitions,
               'adapter_hashes': {path: hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in
                                  ('scripts/investigation_query_worker.py', 'infra/scripts/Read-InvestigationMetric.ps1')},
               'scope': 'Currency and optional order filter; no product/date/report slicer reproduction'}
    output = {'id': run, 'lineage_run': lineage_run, 'classification': 'UNRESOLVED',
              'metrics': results, 'provenance': continuity(raw),
              'values': {layer: value.get('values', value) for layer, value in raw.items()}}
    with closing(sqlite3.connect(config['storage']['database'])) as db:
        db.execute('CREATE TABLE IF NOT EXISTS investigation_runs(id TEXT PRIMARY KEY, lineage_run TEXT NOT NULL, created TEXT NOT NULL, request TEXT NOT NULL, result TEXT NOT NULL)')
        db.execute('INSERT INTO investigation_runs VALUES(?,?,?,?,?)', (run, lineage_run, captured, canonical(request), canonical(output)))
        db.commit()
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT/'infra/metadata/development.json')
    parser.add_argument('--estate', type=Path, default=ROOT/'infra/fabric/environment.json')
    parser.add_argument('--lineage-run', required=True)
    parser.add_argument('--currency', required=True)
    parser.add_argument('--order-id')
    args = parser.parse_args()
    result = acquire(load_config(args.config), json.loads(args.estate.read_text()), args.lineage_run, args.currency, args.order_id)
    print(json.dumps(result, indent=2))

"""Operator probe: prove the independent lower surface before building on it.

Two self-reports, each compared with its declared surface by the engine's own
attestation rule:
1. The presentation baseline through the adapter's `evaluate()`, which now asks
   Power BI who it served (`USERPRINCIPALNAME()`).
2. The Fabric SQL analytics endpoint bound by the resolved `declared_source`
   layer, as the configured reader, asking the endpoint who connected and to
   which database (`SUSER_SNAME()`, `DB_NAME()`).

The database comes from the discovered binding, never from configuration. No
lower-layer quantity is compiled, and no table is read. Receipts carry value
fingerprints, not values; a fingerprint of a scalar is not confidential.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def lower_database(path, assets):
    """The SQL database named by the resolved binding's declared endpoint, or None."""
    layer = next((x for x in path.get('layers', []) if x.get('kind') == 'declared_source'), None)
    endpoint = ((layer or {}).get('binding') or {}).get('declared_connection_asset_id')
    asset = next((a for a in assets if a.get('id') == endpoint), None)
    return (layer, endpoint, asset['name']) if asset and asset.get('kind') == 'SQLEndpoint' else (layer, endpoint, None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True); parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--environment', required=True); parser.add_argument('--model-id', required=True)
    parser.add_argument('--measure-id', required=True); parser.add_argument('--usage-policy', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True); parser.add_argument('--approve', action='store_true')
    args = parser.parse_args()
    if not args.approve:
        parser.error('Explicit --approve required; each probe consumes a cloud-read reservation')
    import sqlite3
    from types import SimpleNamespace
    from investigator import context_search
    from investigator.onboarding import ModelStore
    from investigator.runtime import Runtime
    from investigator.usage_governance import UsageGovernor
    from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
    from investigator.process_debugging import attest, attest_surface
    from metadata_config import load_config
    from fabric_sql_auth import session_status
    from fabric_sql_surface import self_report
    from run_native_diagnostic import transport as native_transport
    from run_source_diagnostic import transport as source_transport
    config = load_config(args.config); store = ModelStore(args.database, config['storage']['database'], args.environment)

    @contextmanager
    def db():
        connection = sqlite3.connect(args.database); connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()
    governor = UsageGovernor(SimpleNamespace(db=db, store=store),
                             json.loads(args.usage_policy.read_text(encoding='utf-8-sig')), time.time)
    identity = 'surface-self-report-probe-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'); counter = [0]

    def meter(tool, execute):
        counter[0] += 1; key = f'{identity}:{counter[0]}:{tool}'
        with db() as c:
            c.execute('BEGIN IMMEDIATE'); governor.reserve(c, identity, key, 'cloud')
        uncertain = True
        try:
            result = execute(); uncertain = False; return result
        finally:
            with db() as c:
                c.execute('BEGIN IMMEDIATE'); governor.settle(c, identity, key, uncertain=uncertain)

    reader = config['fabric'].get('sql_reader')
    session = (session_status(config['fabric']['auth']['tenant_id'], reader['account'], reader['profile'])
               if reader else {'status': 'NOT_CONFIGURED'})
    runtime = Runtime(store, config, lambda p: native_transport(config, p), lambda p: source_transport(config, p))
    model = store.get(args.model_id)
    adapter = MicrosoftProcessAdapter(store, config, model, runtime.native_transport, runtime.source_transport,
                                      meter_read=meter, lower_surface=session)
    args.out.mkdir(parents=True, exist_ok=True)
    before = governor.snapshot(); path = adapter.resolve_path(args.measure_id)
    receipts = []

    started = datetime.now(timezone.utc).isoformat()
    semantic = attest(adapter.evaluate(path['layers'][0], args.measure_id, {}))
    evidence = semantic.evidence or {}
    receipts.append({'probe': 'semantic_dax_self_report', 'started_utc': started,
        'finished_utc': datetime.now(timezone.utc).isoformat(), 'status': semantic.status, 'reason': semantic.reason,
        'execution_surface': semantic.execution_surface, 'surface_report': semantic.surface_report,
        'surface_attestation': evidence.get('surface_attestation'), 'receipt_id': evidence.get('id'),
        'request_hash': evidence.get('request_hash'),
        'values_fingerprint': fingerprint(semantic.value) if semantic.status == 'OBSERVED' else None})

    started = datetime.now(timezone.utc).isoformat()
    layer, endpoint, database = lower_database(path, context_search.latest(store)['assets'])
    if database is None:
        receipts.append({'probe': 'fabric_sql_self_report', 'started_utc': started, 'status': 'NOT_APPLICABLE',
                         'reason': 'The resolved path declares no SQL endpoint for its lower layer.',
                         'declared_endpoint': endpoint})
    else:
        answer = meter('fabric_sql_self_report', lambda: self_report(config, database))
        attestation = (attest_surface(answer['execution_surface'], answer['surface_report'])
                       if answer['status'] == 'REACHABLE' else None)
        receipts.append({'probe': 'fabric_sql_self_report', 'started_utc': started,
            'finished_utc': datetime.now(timezone.utc).isoformat(),
            'status': 'OBSERVED' if attestation and attestation['status'] == 'MATCHED' else 'UNAVAILABLE',
            'reason': answer.get('reason') or (attestation or {}).get('reason'),
            'layer': layer['id'], 'binding_provenance': layer['binding'].get('provenance'),
            'declared_endpoint': endpoint, 'database_source': 'DISCOVERED_ENDPOINT_ASSET_NAME',
            'execution_surface': answer['execution_surface'], 'surface_report': answer['surface_report'],
            'surface_attestation': attestation,
            **{k: answer.get(k) for k in ('stage', 'error_type', 'sql_error_number', 'sign_in') if answer.get(k)}})
    record = {'probe_session': identity, 'environment': args.environment, 'model_id': model['id'],
              'measure_id': args.measure_id, 'reader_session': session,
              'capabilities_declared': sorted(adapter.capabilities()),
              'capability_gaps': adapter.capability_gaps(), 'receipts': receipts,
              'cloud_reservations': counter[0], 'usage_before': before, 'usage_after': governor.snapshot()}
    (args.out/'surface-self-report.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps({'probe_session': identity, 'cloud_reservations': counter[0],
                      'statuses': {r['probe']: r['status'] for r in receipts}}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

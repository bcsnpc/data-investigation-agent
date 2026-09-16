"""Explicit isolated-fixture verification through the durable native runtime.

This uses an operator fixture manifest, not a fabricated report scan or a hidden
acceptance evaluator. Its fixed verification actions are not the agent planner.
"""
import argparse
from collections import Counter
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sqlite3
from urllib.parse import quote
from uuid import UUID, uuid5, NAMESPACE_URL

from import_fixture import validate
from investigator.onboarding import digest, encoded, fields, Conflict
from investigator.semantic_graph import analyze
from investigator.runtime import Runtime
from investigator import record_readback
from investigator.native_identity import profile
from metadata_config import load_config
from run_native_diagnostic import transport


def compile_fixture(bundle, workspace, native_id, scope):
    bundle = validate(bundle)
    fields(scope, ['table', 'measures', 'filter_column', 'filter_values', 'dimension', 'record_columns', 'key_columns'])
    workspace, native_id = str(UUID(workspace)), str(UUID(native_id))
    root = 'fabric://' + workspace + '/' + native_id
    assets, columns, measures, tables = [], {}, {}, {}
    for source in bundle['spec']['tables']:
        tid = root + '/table/' + quote(source['name'], safe='')
        tables[source['name']] = tid
        assets.append({'id': tid, 'kind': 'SemanticTable', 'name': source['name'], 'metadata': {'partitions': [{'mode': 'import'}]}})
        for column in source['columns']:
            cid = tid + '/columns/' + quote(column['name'], safe='')
            columns[(source['name'], column['name'])] = cid
            assets.append({'id': cid, 'kind': 'SemanticColumn', 'parent_id': tid, 'name': column['name'],
                           'metadata': {'dataType': column['type']}})
        for measure in source['measures']:
            mid = tid + '/measures/' + quote(measure['name'], safe='')
            measures[measure['name']] = mid
            assets.append({'id': mid, 'kind': 'Measure', 'parent_id': tid, 'name': measure['name'],
                           'metadata': {'expression': measure['expression']}})
    for asset in assets: asset['content_hash'] = digest(asset)
    table = scope['table']
    if table not in tables or not isinstance(scope['measures'], list) or not scope['measures']:
        raise ValueError('Select fixture table and measures')
    model_id = str(uuid5(NAMESPACE_URL, root + '/reader-runtime-verification'))
    provenance = {'origin': 'OPERATOR_FIXTURE_MANIFEST', 'bundle_hash': bundle['bundle_hash'],
                  'input_hash': bundle['input_hash'], 'model_hash': bundle['model_hash'],
                  'compiler_hash': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  'remote_definition_verified': False, 'report_context_available': False}
    context_id = str(uuid5(NAMESPACE_URL, digest(provenance)))
    context = {'id': context_id, 'model_id': model_id, 'provenance': provenance,
               'measures': [{'id': a['id'], 'name': a['name']} for a in assets if a['kind'] == 'Measure'],
               # Existing compiler shape only. This container is NOT a Power BI report.
               'reports': [{'model_assets': assets, 'origin': 'FIXTURE_ASSET_CONTAINER_NO_REPORT'}],
               'semantic_graph': analyze(assets)}
    model = {'id': model_id, 'native_id': native_id, 'workspace': workspace, 'revision': 1,
             'name': 'Isolated reader runtime verification', 'enabled': True, 'context_id': context_id,
             'context': context, 'reports': [], 'business': {}, 'environment': 'isolated-reader-verification'}
    filters = [{'column_id': columns[(table, scope['filter_column'])], 'operator': 'in', 'values': scope['filter_values']}]
    common = {'model_id': model_id, 'revision': 1, 'context_id': context_id, 'filters': filters}
    scalar = dict(common, measure_ids=[measures[m] for m in scope['measures']], dimension_id=None, include_dependencies=True)
    dimension = dict(scalar, dimension_id=columns[(table, scope['dimension'])])
    record = dict(common, object_id=tables[table], column_ids=[columns[(table, c)] for c in scope['record_columns']],
                  key_column_ids=[columns[(table, c)] for c in scope['key_columns']], limit=250)
    request = {'model_id': model_id, 'call_budget': 3, 'actions': [
        {'tool': 'native', 'input': scalar}, {'tool': 'native', 'input': dimension}, {'tool': 'native_records', 'input': record}]}
    return model, request


class FixtureStore:
    """Separate immutable local verification catalog; never writes onboarding tables."""
    def __init__(self, database, model):
        self.database, self.model_id = Path(database), model['id']
        self.database.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS reader_fixture_context(id TEXT PRIMARY KEY,body TEXT,hash TEXT)')
            existing = db.execute('SELECT hash FROM reader_fixture_context WHERE id=?', (model['id'],)).fetchone()
            if existing and existing[0] != digest(model):
                raise Conflict('Fixture changed; use a separate verification database')
            db.execute('INSERT OR IGNORE INTO reader_fixture_context VALUES(?,?,?)', (model['id'], encoded(model), digest(model)))

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database, timeout=10); db.row_factory = sqlite3.Row
        try:
            with db: yield db
        finally: db.close()

    def get(self, identity):
        with self.connect() as db:
            row = db.execute('SELECT body,hash FROM reader_fixture_context WHERE id=?', (identity,)).fetchone()
        if row is None: raise KeyError('Fixture context unavailable')
        value = json.loads(row[0])
        if digest(value) != row[1]: raise ValueError('Fixture context integrity differs')
        return value


def assessment(result, bundle, scope, reader, joint=False):
    """Evaluator-only content comparison. No expected metric values enter runtime."""
    complete = result['status'] == 'COMPLETED' and len(result['steps']) == (1 if joint else 3)
    outputs = [s.get('result') or {} for s in result['steps']]
    identities = [(o.get('result') or {}).get('execution_identity') for o in outputs]
    bound = complete and all(i is not None and all(i.get(k) == reader[k] for k in
                            ('mode', 'tenant_id', 'principal_id', 'account')) for i in identities)
    complete = complete and all(o.get('result', {}).get('completeness') == 'COMPLETE_RESPONSE' for o in outputs)
    content_matches = False
    if complete:
        data = outputs[0 if joint else 2]['result']
        source = next(t for t in bundle['inputs'] if t['name'] == scope['table'])
        names = [c['name'] for c in source['columns']]
        fi = names.index(scope['filter_column'])
        projected = [names.index(c) for c in scope['record_columns']]
        expected = Counter()
        for row in source['rows']:
            # Type-sensitive selection: True must not compare equal to integer 1.
            if not any(type(row[fi]) is type(v) and row[fi] == v for v in scope['filter_values']): continue
            values = [record_readback.value(row[i], source['columns'][i]['type'], 'native_records') for i in projected]
            expected[encoded(values)] += 1
        observed = Counter({encoded(row['values']): int(row['multiplicity']) for row in data['rows']})
        content_matches = data['completeness'] == 'COMPLETE_RESPONSE' and expected == observed
    joint_result=(outputs[0].get('result') or {}).get('joint_aggregate') if joint and outputs else None
    joint_passed=not joint or (joint_result or {}).get('status')=='CAPTURE_RECONCILES'
    return {**({'joint_aggregate':joint_result} if joint else {}),
            'run_id': result['id'], 'status': result['status'], 'calls_reserved': result['calls_reserved'],
            'native_reader_bound': bound,
            'projected_fixture_rows_match': content_matches,
            'runtime_verification_passed': complete and bound and content_matches and joint_passed,
            'execution_identities': identities, 'receipts': [o.get('id') for o in outputs],
            'generation_proven': False, 'live_acceptance_ready': False, 'cause_verified': False,
            'limitation': 'Operator fixture transport/runtime verification; not report onboarding, hidden generality or causal acceptance.'}


def run(config, bundle, native_id, scope, database, key, *, execute=transport, status_only=False, joint_measure=None):
    reader = profile(config['fabric']['native_reader'])
    if native_id not in reader['model_ids']: raise ValueError('Model is outside reader scope')
    model, request = compile_fixture(bundle, config['fabric']['workspace_id'], native_id, scope)
    if joint_measure is not None:
        matches=[m['id'] for m in model['context']['measures'] if m['name']==joint_measure]
        if len(matches)!=1:raise ValueError('Choose one exact fixture measure name')
        action=request['actions'][2]
        action['input']['aggregate_measure_id']=matches[0]
        request=dict(request,call_budget=1,actions=[action])
    store = FixtureStore(database, model)
    runtime = Runtime(store, config, lambda r: execute(config, r), None)
    with store.connect() as db:
        prior = db.execute('SELECT connection_hash FROM v2_runs WHERE model_id=? AND request_key=?', (model['id'], key)).fetchone()
    if prior and prior[0] != digest(config):
        raise Conflict('Saved verification used a different connection or reader profile')
    # Validate all actions before reserving, so malformed scope never dispatches.
    if status_only:
        with store.connect() as db:
            row = db.execute('SELECT id,request FROM v2_runs WHERE model_id=? AND request_key=?', (model['id'], key)).fetchone()
        if row is None or json.loads(row['request']) != request: raise ValueError('Saved verification scope differs or is absent')
        result = runtime.get(row['id'])
    else:
        saved = runtime.create(request, key)
        result = runtime.get(saved['id']) if saved['status'] == 'COMPLETED' else runtime.execute(saved['id'])
    # Readback must still agree with its sealed source receipt, not just cached step JSON.
    from investigator.receipt_integrity import verify as verify_seal
    for step in result['steps']:
        receipt = step.get('result')
        if not receipt: continue
        if step['tool'] == 'native':
            with store.connect() as db:
                if verify_seal(db, 'native', receipt['id'])['state'] != 'SEALED':
                    raise Conflict('Verification requires a sealed native receipt')
                saved = json.loads(db.execute('SELECT result FROM native_diagnostics WHERE id=?', (receipt['id'],)).fetchone()[0])
        else:
            saved = record_readback.read(store, model['id'], receipt['id'])['result']
        if saved != receipt['result']: raise Conflict('Saved runtime step and receipt differ')
    return {'summary': assessment(result, bundle, scope, reader, joint_measure is not None), 'run': result, 'bundle_hash': bundle['bundle_hash']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('config', 'bundle', 'scope', 'database', 'output'): parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--model', required=True); parser.add_argument('--request-key', required=True)
    parser.add_argument('--approve', action='store_true'); parser.add_argument('--status-only', action='store_true')
    parser.add_argument('--joint-measure',help='Capture a direct count/sum and the projected records in one native response')
    args = parser.parse_args()
    if not args.approve and not args.status_only: parser.error('Explicit --approve is required for live reads')
    try:
        result = run(load_config(args.config), json.loads(args.bundle.read_text(encoding='utf-8')),
                     args.model, json.loads(args.scope.read_text(encoding='utf-8')), args.database, args.request_key,
                     status_only=args.status_only,joint_measure=args.joint_measure)
        args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result['summary']))
        raise SystemExit(0 if result['summary']['runtime_verification_passed'] else 2)
    except Exception as exc:
        print(json.dumps({'status': 'UNAVAILABLE', 'error_type': type(exc).__name__}))
        raise SystemExit(1)

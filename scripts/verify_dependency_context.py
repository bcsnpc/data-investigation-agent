"""Operator-controlled native context parity reads; not hidden acceptance or an LLM planner."""
import argparse
import json
from pathlib import Path

from investigator.onboarding import fields, digest, Conflict
from investigator.native_identity import profile
from investigator.runtime import Runtime
from investigator.receipt_integrity import verify as verify_seal
from verify_reader_runtime import compile_fixture, FixtureStore
from run_native_diagnostic import transport
from metadata_config import load_config


def request(model, base, cases):
    if not isinstance(cases, list) or not 1 <= len(cases) <= 8: raise ValueError('Select one to eight bounded context cases')
    names = {m['name']: m['id'] for m in model['context']['measures']}; actions = []
    for case in cases:
        fields(case, ['measure', 'context_path'])
        if not isinstance(case['context_path'], list): raise ValueError('Expected context path')
        plan = dict(base['actions'][0]['input'], measure_ids=[names[case['measure']]], include_dependencies=False)
        if case['context_path']: plan['context_path'] = [names[name] for name in case['context_path']]
        actions.append({'tool': 'native', 'input': plan})
    return {'model_id': model['id'], 'call_budget': len(actions), 'actions': actions}


def run(config, bundle, model_id, scope, cases, database, key, *, execute=transport, status_only=False):
    profile(config['fabric']['native_reader'])
    if model_id not in config['fabric']['native_reader']['model_ids']: raise ValueError('Fixture model is not allowed')
    model, base = compile_fixture(bundle, config['fabric']['workspace_id'], model_id, scope)
    plan = request(model, base, cases); store = FixtureStore(database, model)
    runtime = Runtime(store, config, lambda r: execute(config, r), None)
    with store.connect() as db:
        prior = db.execute('SELECT id,request,connection_hash FROM v2_runs WHERE model_id=? AND request_key=?', (model['id'], key)).fetchone()
    if prior and (json.loads(prior[1]) != plan or prior[2] != digest(config)):
        raise Conflict('Saved context verification used another scope or connection')
    if status_only:
        if not prior: raise ValueError('No saved context verification')
        result = runtime.get(prior[0])
    else:
        saved = runtime.create(plan, key)
        result = runtime.get(saved['id']) if saved['status'] == 'COMPLETED' else runtime.execute(saved['id'])
    values = []
    for case, step in zip(cases, result['steps']):
        receipt = step.get('result')
        if not receipt: continue
        with store.connect() as db:
            if verify_seal(db, 'native', receipt['id'])['state'] != 'SEALED': raise Conflict('Sealed native evidence required')
            saved = json.loads(db.execute('SELECT result FROM native_diagnostics WHERE id=?', (receipt['id'],)).fetchone()[0])
        if saved != receipt['result']: raise Conflict('Step and receipt differ')
        values.append({'case': case, 'receipt_id': receipt['id'], 'status': receipt['status'],
                       'values': saved.get('rows', []), 'dependency_context': saved.get('dependency_context'),
                       'execution_identity': saved.get('execution_identity')})
    return {'run_id': result['id'], 'status': result['status'], 'cases': values, 'run': result,
            'generation_proven': False, 'cause_verified': False, 'live_acceptance_ready': False,
            'limitation': 'Operator fixture diagnostic reads. Values are native; parity expectations are evaluated separately.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('config', 'bundle', 'scope', 'cases', 'database', 'output'): parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--model', required=True); parser.add_argument('--request-key', required=True)
    parser.add_argument('--approve', action='store_true'); parser.add_argument('--status-only', action='store_true')
    args = parser.parse_args()
    if not args.approve and not args.status_only: parser.error('Explicit --approve required for native reads')
    try:
        result = run(load_config(args.config), json.loads(args.bundle.read_text(encoding='utf-8')),
                     args.model, json.loads(args.scope.read_text(encoding='utf-8')), json.loads(args.cases.read_text(encoding='utf-8')),
                     args.database, args.request_key, status_only=args.status_only)
        args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps({k: v for k, v in result.items() if k != 'run'}))
        raise SystemExit(0 if result['status'] == 'COMPLETED' else 2)
    except Exception as exc:
        print(json.dumps({'status': 'UNAVAILABLE', 'error_type': type(exc).__name__}))
        raise SystemExit(1)

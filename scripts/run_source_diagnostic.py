"""Explicit operator invocation of one metadata-bound source aggregate."""
import argparse
import json
from pathlib import Path
import subprocess

from investigator.onboarding import ModelStore
from investigator.source_diagnostics import run, snapshot
from metadata_config import load_config, ROOT
from sql_connect_retry import read_with_retry


class SourceReadError(RuntimeError):
    def __init__(self, number=None, kind=None, attempts=None):
        super().__init__('Source transport unavailable')
        self.error_number = number if type(number) is int else None
        self.error_kind = kind if kind in ('SqlException', 'InvalidOperationException', 'MethodException', 'ArgumentException') else 'TransportError'
        self.connection_attempts = attempts


class SourceReadTimeout(TimeoutError):
    def __init__(self, attempts):
        super().__init__('Source completion is uncertain')
        self.connection_attempts = attempts


def read_once(config, request):
    payload = {'server': config['sql']['server'], 'database': config['sql']['database'],
               'credential_file': config['sql']['auth']['credential_file'],
               'query': request['query'], 'parameters': request['parameters']}
    completed = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-File',
        str(ROOT / 'infra/scripts/Read-CatalogAggregate.ps1')],
        input=json.dumps(payload), capture_output=True, text=True, encoding='utf-8', timeout=90)
    if len(completed.stdout) > 8192:
        raise RuntimeError('Source transport unavailable')
    result = json.loads(completed.stdout)
    if completed.returncode:
        return {'error':'SQL_READ_FAILED','stage':result.get('stage','unknown'),
                'sql_error_number':result.get('error_number'),'error_kind':result.get('error_kind')}
    return result


def transport(config, request):
    result=read_with_retry(lambda:read_once(config,request))
    if result.get('error') == 'SQL_READ_TIMEOUT' or (result.get('stage')=='query' and result.get('sql_error_number')==-2):
        raise SourceReadTimeout(result['connection_attempts'])
    if result.get('error'):
        raise SourceReadError(result.get('sql_error_number'),result.get('error_kind'),result['connection_attempts'])
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--environment', required=True)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--catalog-model-id')
    parser.add_argument('--approve', action='store_true')
    args = parser.parse_args()
    config = load_config(args.config)
    store = ModelStore(args.database, config['storage']['database'], args.environment)
    if args.catalog_model_id:
        if args.plan:parser.error('Choose catalog discovery or a plan')
        model = store.get(args.catalog_model_id)
        objects, columns = snapshot(store, model, config)
        print(json.dumps({'model_id': model['id'], 'revision': model['revision'], 'context_id': model['context_id'],
              'objects': [{'id': a['id'], 'schema': a['metadata']['schema_name'], 'name': a['metadata']['name'],
                           'columns': [{'id': c['id'], 'name': c['metadata']['name'], 'type': c['metadata']['data_type']}
                                       for c in columns.values() if c['parent_id'] == a['id']]} for a in objects.values()]}))
    else:
        if not args.approve or not args.plan:parser.error('Explicit --plan and --approve required')
        plan = json.loads(args.plan.read_text(encoding='utf-8-sig'))
        result = run(store, plan, config, lambda request: transport(config, request))
        print(json.dumps(result))
        raise SystemExit(0 if result['status'] == 'COMPLETED' else 1)

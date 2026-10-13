"""Deploy the approved platform template using the existing owner Azure CLI login.

No credentials are accepted or written. This command does not start a worker.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import re


def validate_staged_postgres(params):
    if params.get('deployCompute', False) and not params.get('deployPostgres', True):
        if not re.fullmatch(r'[a-z0-9-]+\.postgres\.database\.azure\.com', params.get('existingPostgresHost', '')):
            raise ValueError('COMPUTE_ONLY_REQUIRES_EXPLICIT_POSTGRES_HOST')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--az-python', required=True)
    p.add_argument('--parameters', type=Path, required=True)
    p.add_argument('--receipts', type=Path, required=True)
    p.add_argument('--deployment-name', required=True)
    p.add_argument('--what-if', action='store_true')
    args = p.parse_args()
    params = json.loads(args.parameters.read_text(encoding='utf-8-sig'))
    validate_staged_postgres(params)
    if any('password' in k.lower() or 'secret' in k.lower() for k in params):
        raise SystemExit('Credential parameters are forbidden')
    args.receipts.mkdir(parents=True, exist_ok=True)
    az = [args.az_python, '-m', 'azure.cli']
    def call(name, words):
        proc = subprocess.run(az + words + ['--only-show-errors', '-o', 'json'], capture_output=True, text=True, encoding='utf-8')
        receipt = {'at': dt.datetime.now(dt.timezone.utc).isoformat(), 'command': ['az'] + words,
                   'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}
        dest = args.receipts / (name + '.json')
        if dest.exists():
            raise SystemExit('Receipt exists; use a new receipt directory')
        dest.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
        if proc.returncode:
            print(proc.stderr)
            raise SystemExit(proc.returncode)
        return json.loads(proc.stdout) if proc.stdout else None
    account = call('account', ['account', 'show'])
    if account['state'] != 'Enabled':
        raise SystemExit('Subscription not enabled')
    call('resources-before', ['resource', 'list', '--subscription', account['id']])
    template = Path(__file__).resolve().parents[1] / 'infra/platform/main.bicep'
    cmd = ['deployment', 'sub', 'what-if' if args.what_if else 'create', '--name', args.deployment_name,
           '--location', params.get('location', 'eastus'), '--template-file', str(template), '--parameters']
    cmd += [k + '=' + (str(v).lower() if isinstance(v, bool) else str(v)) for k, v in params.items()]
    result = call('deployment', cmd)
    call('resources-after', ['resource', 'list', '--subscription', account['id'], '--resource-group', params['resourceGroupName']])
    print(json.dumps({'deployment': args.deployment_name, 'provisioningState': result.get('properties', {}).get('provisioningState'),
                      'receipts': str(args.receipts)}))


if __name__ == '__main__':
    main()

"""Run/reconcile a pinned typed-action investigation; no adaptive planner yet."""
import argparse
import json
from pathlib import Path

from investigator.onboarding import ModelStore
from investigator.runtime import Runtime
from metadata_config import load_config
from run_native_diagnostic import transport as native_transport
from run_source_diagnostic import transport as source_transport


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--environment',required=True)
    selection=parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--request',type=Path)
    selection.add_argument('--run-id')
    parser.add_argument('--request-key')
    parser.add_argument('--approve',action='store_true')
    parser.add_argument('--reconcile',action='store_true')
    parser.add_argument('--status-only',action='store_true')
    args=parser.parse_args()
    if not args.status_only and not args.approve:parser.error('Explicit --approve required')
    if args.request and (not args.request_key or args.reconcile or args.status_only):parser.error('New run requires --request-key and execution')
    config=load_config(args.config)
    store=ModelStore(args.database,config['storage']['database'],args.environment)
    runtime=Runtime(store,config,lambda req:native_transport(config,req),lambda req:source_transport(config,req))
    identity=args.run_id
    if args.request:
        identity=runtime.create(json.loads(args.request.read_text(encoding='utf-8-sig')),args.request_key)['id']
    if args.status_only:result=runtime.get(identity)
    else:
        if args.reconcile:runtime.reconcile(identity)
        result=runtime.execute(identity)
    print(json.dumps(result))
    raise SystemExit(0 if args.status_only or result['status']=='COMPLETED' else 1)

"""Discover an approved environment and publish supported models into ticket context.

Finite repeat mode supports an external scheduler; it does not install a service.
"""
import argparse
import json
from pathlib import Path
import time
from uuid import uuid4

from metadata_config import load_config, ROOT
from metadata_auth import WorkerTransport, PowerShellSqlCatalog
from investigator.onboarding import ModelStore
from investigator.discovery_collect import Collector
from investigator.enterprise_discovery import Discovery


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--environment',required=True)
    parser.add_argument('--cycles',type=int,default=1)
    parser.add_argument('--interval-seconds',type=int,default=300)
    parser.add_argument('--request-key')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if not 1<=args.cycles<=12 or not 60<=args.interval_seconds<=86400:parser.error('Invalid bounded schedule')
    if args.request_key and args.cycles!=1:parser.error('Request key requires one scan')
    config=load_config(args.config)
    store=ModelStore(args.database,config['storage']['database'],args.environment)
    discovery=Discovery(store,config)
    auth=config['fabric']['auth']
    transport=WorkerTransport(auth['python'],auth['tenant_id'],ROOT/'scripts/metadata_worker.py')
    sql=PowerShellSqlCatalog(ROOT/'infra/scripts/Get-SqlMetadata.ps1',config['sql']['auth']['credential_file'])
    summaries=[]
    for i in range(args.cycles):
        if i:time.sleep(args.interval_seconds)
        result=discovery.run(Collector(config,transport,sql).run,args.request_key or str(uuid4()))
        body=result['body']
        summary={'id':result['id'],'status':result['status'],'inventory_scan_id':body.get('inventory_scan_id'),
                 'calls':body.get('calls'),'changes':body.get('changes'),
                 'coverage':body.get('coverage'),'models_available':len(store.list(True))}
        summaries.append(summary)
        print(json.dumps(summary),flush=True)
        if args.output:args.output.write_text(json.dumps(summaries,indent=2),encoding='utf-8')
    return 0


if __name__=='__main__':raise SystemExit(main())

"""Discover an approved environment and publish supported models into ticket context.

Finite repeat mode supports an external scheduler; it does not install a service.
"""
import argparse
import json
from pathlib import Path
import time
from uuid import uuid4

from metadata_config import ROOT
from metadata_auth import WorkerTransport, PowerShellSqlCatalog
from investigator.onboarding import ModelStore
from investigator.discovery_collect import Collector
from investigator.enterprise_discovery import Discovery


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--cycles',type=int,default=1)
    parser.add_argument('--interval-seconds',type=int,default=300)
    parser.add_argument('--request-key')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if not 1<=args.cycles<=12 or not 60<=args.interval_seconds<=86400:parser.error('Invalid bounded schedule')
    if args.request_key and args.cycles!=1:parser.error('Request key requires one scan')
    from investigator.estate_manifest import load
    from investigator.adapters.estate_installation import configuration
    manifest=load(args.manifest);config=configuration(manifest)
    store=ModelStore(ROOT/manifest['storage']['catalog'],config['storage']['database'],manifest['environment'])
    discovery=Discovery(store,config)
    from investigator.runtime import Runtime
    from investigator.usage_governance import UsageGovernor
    from investigator.estate_manifest import policy
    governor=UsageGovernor(Runtime(store,config,None,None),policy(manifest),time.time)
    auth=config['fabric']['auth']
    transport=WorkerTransport(auth['python'],auth['tenant_id'],ROOT/'scripts/metadata_worker.py')
    sql=PowerShellSqlCatalog(ROOT/'infra/scripts/Get-SqlMetadata.ps1',config['sql']['auth']['credential_file'])
    summaries=[]
    for i in range(args.cycles):
        if i:time.sleep(args.interval_seconds)
        from investigator.adapters.warehouse_catalog import read as warehouse_catalog
        request_key=args.request_key or str(uuid4());session_id='discovery:'+request_key
        sequence=0
        def admitted(execute):
            nonlocal sequence
            sequence+=1
            return governor.metered_read(session_id,'metadata-'+str(sequence),execute)
        def http(*a,**k):return admitted(lambda:transport(*a,**k))
        def catalog(*a,**k):return admitted(lambda:sql(*a,**k))
        def warehouse(*a,**k):return admitted(lambda:warehouse_catalog(*a,**k))
        result=discovery.run(Collector(config,http,catalog,warehouse_reader=warehouse).run,request_key)
        body=result['body']
        summary={'id':result['id'],'status':result['status'],'inventory_scan_id':body.get('inventory_scan_id'),
                 'calls':body.get('calls'),'changes':body.get('changes'),
                 'coverage':body.get('coverage'),'models_available':len(store.list(True))}
        summaries.append(summary)
        print(json.dumps(summary),flush=True)
        if args.output:args.output.write_text(json.dumps(summaries,indent=2),encoding='utf-8')
    return 0


if __name__=='__main__':raise SystemExit(main())

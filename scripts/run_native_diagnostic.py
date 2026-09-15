"""Explicit approved, single-query catalog diagnostic through native Power BI."""
import argparse
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from urllib.request import Request, build_opener
from uuid import UUID

from investigator.onboarding import ModelStore
from investigator.native_diagnostics import run
from metadata_auth import FabricCliTokens, NoRedirect
from metadata_config import load_config, ROOT


def execute(request,tenant):
    workspace=str(UUID(request['workspace']));model=str(UUID(request['native_model_id']))
    token=FabricCliTokens(tenant).get_token('https://analysis.windows.net/powerbi/api/.default')
    body={'queries':[{'query':request['query']}],'serializerSettings':{'includeNulls':True}}
    http=Request(f'https://api.powerbi.com/v1.0/myorg/groups/{workspace}/datasets/{model}/executeQueries',
                 data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
    with build_opener(NoRedirect()).open(http,timeout=90) as response:
        raw=response.read(2*1024*1024+1)
    if len(raw)>2*1024*1024:raise ValueError('Native response exceeds budget')
    return raw.decode('utf-8')


def transport(config, request):
    """Trusted native worker, also used by the durable operator runtime."""
    with tempfile.TemporaryDirectory() as directory:
        frozen=Path(directory)/'profile.json'
        frozen.write_text(json.dumps(config),encoding='utf-8')
        p=subprocess.run([config['fabric']['auth']['python'],str(ROOT/'scripts/run_native_diagnostic.py'),
            '--config',str(frozen),'--transport-worker'],input=json.dumps(request),
            capture_output=True,text=True,encoding='utf-8',timeout=120)
    if p.returncode:raise RuntimeError('Native transport unavailable')
    return json.loads(p.stdout,parse_float=Decimal)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--database',type=Path)
    parser.add_argument('--environment')
    parser.add_argument('--plan',type=Path)
    parser.add_argument('--approve',action='store_true')
    parser.add_argument('--transport-worker',action='store_true',help=argparse.SUPPRESS)
    args=parser.parse_args();config=load_config(args.config)
    if args.transport_worker:
        try:
            request=json.load(sys.stdin)
            if request['workspace']!=config['fabric']['workspace_id']:raise ValueError('Workspace differs')
            print(execute(request,config['fabric']['auth']['tenant_id']))
        except Exception as exc:
            print(json.dumps({'error':type(exc).__name__}));raise SystemExit(1)
    else:
        if not args.approve or not args.plan or not args.database or not args.environment:
            parser.error('Explicit --approve, --plan, --database and --environment required')
        plan=json.loads(args.plan.read_text(encoding='utf-8-sig'))
        store=ModelStore(args.database,config['storage']['database'],args.environment)
        if store.get(plan['model_id'])['workspace']!=config['fabric']['workspace_id']:parser.error('Workspace differs')
        result=run(store,plan,lambda request:transport(config,request));print(json.dumps(result))
        raise SystemExit(0 if result['status']=='COMPLETED' else 1)

"""Collect bounded acceptance-prerequisite metadata; never publish or query data."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from investigator.onboarding import ModelStore
from investigator.proof_preflight import run, read
from metadata_config import load_config


def worker():
    from metadata_auth import FabricCliTokens, MetadataHttp
    try:
        request=json.load(sys.stdin)
        result=MetadataHttp(FabricCliTokens(request['tenant']))(request['endpoint'],request['method'],request['audience'])
        raw=json.dumps(result)
        if len(raw)>9_000_000:raise ValueError('Response budget exceeded')
        print(raw)
    except Exception as exc:
        # The metadata transport emits only this fixed HTTP-status pattern.
        match=re.fullmatch(r'Metadata HTTP status ([0-9]{3})',str(exc))
        print(json.dumps({'status_code':int(match[1]) if match else None,'error_type':type(exc).__name__}))


def transport(config):
    def call(endpoint,method,audience):
        result=subprocess.run([config['fabric']['auth']['python'],str(Path(__file__).resolve()),'--worker'],
            input=json.dumps({'tenant':config['fabric']['auth']['tenant_id'],'endpoint':endpoint,'method':method,'audience':audience}),
            capture_output=True,text=True,encoding='utf-8',timeout=105)
        if result.returncode or len(result.stdout)>9_000_000:raise RuntimeError('Preflight worker unavailable')
        return json.loads(result.stdout)
    return call


if __name__=='__main__':
    if sys.argv[1:]==['--worker']:worker();raise SystemExit(0)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True);parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--environment',required=True);parser.add_argument('--model-id',required=True)
    parser.add_argument('--preflight-id');parser.add_argument('--output',type=Path)
    parser.add_argument('--require-ready',action='store_true',help='Exit 2 when live acceptance prerequisites remain blocked')
    args=parser.parse_args();config=load_config(args.config)
    store=ModelStore(args.database,config['storage']['database'],args.environment)
    model=store.get(args.model_id)
    if model['workspace']!=config['fabric']['workspace_id']:parser.error('Configured workspace differs from registered model')
    result=read(store,args.model_id,args.preflight_id) if args.preflight_id else run(store,args.model_id,transport(config))
    raw=json.dumps(result,indent=2)
    if args.output:args.output.write_text(raw,encoding='utf-8')
    print(raw)
    if args.require_ready and not result.get('assessment',{}).get('live_acceptance_ready'):raise SystemExit(2)

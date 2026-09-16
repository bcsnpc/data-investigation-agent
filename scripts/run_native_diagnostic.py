"""Explicit approved, single-query catalog diagnostic through native Power BI."""
import argparse
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from urllib.request import Request, build_opener
from urllib.error import URLError
from uuid import UUID

from investigator.onboarding import ModelStore
from investigator.native_diagnostics import run
from metadata_auth import FabricCliTokens, NoRedirect
from metadata_config import load_config, ROOT
from investigator.native_identity import KEY, profile, make, require


def execute(request,tenant,reader=None):
    workspace=str(UUID(request['workspace']));model=str(UUID(request['native_model_id']))
    if reader is None:
        token=FabricCliTokens(tenant).get_token('https://analysis.windows.net/powerbi/api/.default')
    else:
        profile(reader)
        if reader['tenant_id'] != tenant or model not in reader['model_ids']:
            raise ValueError('Native reader target differs')
        from connect_fixture_reader import application, token as reader_token
        import base64
        token=reader_token(application(tenant),reader['account'],tenant,'https://analysis.windows.net/powerbi/api/.default')
        part=token.split('.')[1]
        claims=json.loads(base64.urlsafe_b64decode(part+'='*(-len(part)%4)))
        if claims.get('oid') != reader['principal_id']:
            raise ValueError('Native reader principal differs')
    body={'queries':[{'query':request['query']}],'serializerSettings':{'includeNulls':True}}
    http=Request(f'https://api.powerbi.com/v1.0/myorg/groups/{workspace}/datasets/{model}/executeQueries',
                 data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
    with build_opener(NoRedirect()).open(http,timeout=90) as response:
        raw=response.read(2*1024*1024+1)
    if len(raw)>2*1024*1024:raise ValueError('Native response exceeds budget')
    decoded=raw.decode('utf-8')
    if reader is not None:
        response=json.loads(decoded,parse_float=Decimal)
        evidence=make(response,request,reader)
        # Append only our metadata, preserving the provider's exact numeric JSON.
        decoded=decoded.rstrip()
        if not decoded.endswith('}'):raise ValueError('Expected native response object')
        decoded=decoded[:-1]+','+json.dumps(KEY)+':'+json.dumps(evidence)+'}'
    return decoded


def transport(config, request):
    """Trusted native worker, also used by the durable operator runtime."""
    if request['workspace'] != config['fabric']['workspace_id']:
        raise ValueError('Workspace differs')
    reader=config['fabric'].get('native_reader')
    if reader is not None:
        profile(reader)
        if request['native_model_id'] not in reader['model_ids']:
            raise ValueError('Native model is outside reader allowlist')
    with tempfile.TemporaryDirectory() as directory:
        frozen=Path(directory)/'profile.json'
        frozen.write_text(json.dumps(config),encoding='utf-8')
        p=subprocess.run([config['fabric']['auth']['python'],str(ROOT/'scripts/run_native_diagnostic.py'),
            '--config',str(frozen),'--transport-worker'],input=json.dumps(request),
            capture_output=True,text=True,encoding='utf-8',timeout=120)
    if p.returncode:
        try:failure=json.loads(p.stdout)
        except (ValueError,TypeError):failure={}
        if isinstance(failure,dict) and failure.get('completion_uncertain') is True:
            raise TimeoutError('Native completion is uncertain')
        raise RuntimeError('Native transport unavailable')
    response=json.loads(p.stdout,parse_float=Decimal)
    return require(response,request,reader) if reader is not None else response


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
            print(execute(request,config['fabric']['auth']['tenant_id'],config['fabric'].get('native_reader')))
        except Exception as exc:
            print(json.dumps({'error':type(exc).__name__,
                              'completion_uncertain':isinstance(exc,(TimeoutError,URLError))}));raise SystemExit(1)
    else:
        if not args.approve or not args.plan or not args.database or not args.environment:
            parser.error('Explicit --approve, --plan, --database and --environment required')
        plan=json.loads(args.plan.read_text(encoding='utf-8-sig'))
        store=ModelStore(args.database,config['storage']['database'],args.environment)
        if store.get(plan['model_id'])['workspace']!=config['fabric']['workspace_id']:parser.error('Workspace differs')
        result=run(store,plan,lambda request:transport(config,request));print(json.dumps(result))
        raise SystemExit(0 if result['status']=='COMPLETED' else 1)

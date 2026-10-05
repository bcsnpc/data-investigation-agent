"""Explicit approved, single-query catalog diagnostic through native Power BI."""
import argparse
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from urllib.request import Request, build_opener
import re
from urllib.error import HTTPError, URLError
from uuid import UUID

from investigator.onboarding import ModelStore
from investigator.native_diagnostics import run
from metadata_auth import FabricCliTokens, NoRedirect
from metadata_config import load_config, ROOT, worker_configuration
from investigator.native_identity import KEY, profile, make, require, allows


class NativeRejected(RuntimeError):
    """The service answered and refused the query: deterministic, not uncertain."""
    def __init__(self,http_status,service_error_code=None):
        super().__init__('Native service rejected the query')
        self.http_status=http_status if type(http_status) is int else None
        self.service_error_code=service_error_code if isinstance(service_error_code,str) else None


def worker_failure(exc):
    """Classify a worker failure. Only genuinely uncertain completion is reported
    as uncertain. A 4xx is an answer from the service, not a lost request; a 5xx
    or a transport-level failure may hide a query that ran, so it stays uncertain."""
    failure={'error':type(exc).__name__}
    if isinstance(exc,HTTPError):
        failure['http_status']=exc.code if type(exc.code) is int else None
        code=None
        try:
            body=json.loads(exc.read(20001)[:20000])
            code=(body.get('error') or {}).get('code')
        except Exception:
            pass
        if isinstance(code,str) and re.fullmatch(r'[A-Za-z0-9_.]{1,80}',code):
            failure['service_error_code']=code
        failure['completion_uncertain']=not (type(exc.code) is int and 400<=exc.code<500)
    else:
        failure['completion_uncertain']=isinstance(exc,(TimeoutError,URLError))
    return failure


def execute(request,tenant,reader=None):
    workspace=str(UUID(request['workspace']));model=str(UUID(request['native_model_id']))
    if reader is None:
        if request.get('requires_native_reader'):raise ValueError('Discovered execution requires a read-only reader')
        token=FabricCliTokens(tenant).get_token('https://analysis.windows.net/powerbi/api/.default')
    else:
        profile(reader)
        if reader['tenant_id'] != tenant or not allows(reader,workspace,model):
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
        if not allows(reader,request['workspace'],request['native_model_id']):
            raise ValueError('Native model is outside reader allowlist')
    with tempfile.TemporaryDirectory() as directory:
        frozen=Path(directory)/'profile.json'
        frozen.write_text(json.dumps(worker_configuration(config,request)),encoding='utf-8')
        from investigator.tape_worker import run as worker_run
        p=worker_run([config['fabric']['auth']['python'],str(ROOT/'scripts/run_native_diagnostic.py'),
            '--config',str(frozen),'--transport-worker'],input=json.dumps(request),
            capture_output=True,text=True,encoding='utf-8',timeout=120)
    if p.returncode:
        try:failure=json.loads(p.stdout)
        except (ValueError,TypeError):failure={}
        if isinstance(failure,dict) and failure.get('completion_uncertain') is True:
            raise TimeoutError('Native completion is uncertain')
        if isinstance(failure,dict) and failure.get('error')=='HTTPError' and failure.get('completion_uncertain') is False:
            raise NativeRejected(failure.get('http_status'),failure.get('service_error_code'))
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
            print(json.dumps(worker_failure(exc)));raise SystemExit(1)
    else:
        if not args.approve or not args.plan or not args.database or not args.environment:
            parser.error('Explicit --approve, --plan, --database and --environment required')
        plan=json.loads(args.plan.read_text(encoding='utf-8-sig'))
        store=ModelStore(args.database,config['storage']['database'],args.environment)
        if store.get(plan['model_id'])['workspace']!=config['fabric']['workspace_id']:parser.error('Workspace differs')
        result=run(store,plan,lambda request:transport(config,request));print(json.dumps(result))
        raise SystemExit(0 if result['status']=='COMPLETED' else 1)

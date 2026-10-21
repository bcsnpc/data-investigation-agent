"""One fixed runner registry; no user-supplied code, shell, or module imports."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
from types import SimpleNamespace
from .process_tape import bytes_of, validate_bootstrap_header,uuid4
from .planner_recording import _safe
from .run_capture import DurableCapture,blob_sink

VERSION='dia-runner-estate-v1'
KINDS=frozenset({'investigation','verification','probe','scan','replay','prepare','smoke'})

def load(path):
    value=json.loads(Path(path).read_bytes())
    required={'version','manifest','image','capture','checks','output_root','bootstrap'}
    if not isinstance(value,dict) or set(value)!=required or value['version']!=VERSION:raise ValueError('RUNNER_ESTATE_SCHEMA')
    if not re.fullmatch(r'[^\s]+@sha256:[0-9a-f]{64}',value['image']):raise ValueError('RUNNER_PINNED_IMAGE_REQUIRED')
    validate_bootstrap_header(value['bootstrap'])
    if not isinstance(value['checks'],dict) or not value['checks']:raise ValueError('RUNNER_CHECKS_REQUIRED')
    for name,check in value['checks'].items():
        if not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',name) or set(check)!={'kind','options'} or check['kind'] not in KINDS or not isinstance(check['options'],dict):raise ValueError('RUNNER_TYPED_CHECK_REQUIRED')
    _safe(bytes_of(value))
    return value

def transient(error):
    # Authentication/authorisation and billing refusals are never retried for
    # model calls. SQL 18456 is an explicitly approved transient connection case.
    if getattr(error,'code',None) in (401,403) or getattr(error,'status_code',None) in (401,403):return False
    text=str(error).lower()
    if any(s in text for s in ('billing','unauthorized','forbidden','permission denied','secret_detected')):return False
    return isinstance(error,(TimeoutError,ConnectionError)) or getattr(error,'error_number',None)==18456 or getattr(error,'code',None) in (408,429,502,503,504) or any(s in text for s in ('18456','connection reset','temporarily unavailable'))

def retry(call,*,record,sleep=time.sleep):
    for attempt in range(3):
        try:return call()
        except Exception as exc:
            record('attempt-failure',{'attempt':attempt+1,'error_type':type(exc).__name__,'message':str(exc),'retry':attempt<2 and transient(exc)})
            if attempt==2 or not transient(exc):raise
            sleep(30+15*attempt)

def handlers():
    def verification(plan,ctx):
        from cloud_verification_run import execute
        o=plan['options']
        return execute(plan['manifest'],o['prepared'],o['spec'],spec_sha256=o['spec_sha256'],session=plan['run_id'],deadline=time.time()+o.get('deadline_seconds',1800),capture=ctx.root/'verification')
    def investigation(plan,ctx):
        if 'ticket' in plan['options']:
            from .estate_installation import build
            from cloud_form_worker import run_form
            from run_adaptive_investigation import local_azure_key
            manifest,workspace=build(plan['manifest'])
            try:
                m=manifest['model'];settings={**m['credential'],'endpoint':m['endpoint'],'deployment':m['deployment']}
                with local_azure_key(settings):
                    return run_form(workspace,json.loads(Path(plan['options']['ticket']).read_bytes()))
            finally:
                close=getattr(workspace,'close',None)
                if close is not None:close()
        from cloud_form_worker import main
        o=plan['options']
        target=ctx.root/'investigation'
        main(['--bundle',o['bundle'],'--sha256',o['sha256'],'--job-root',str(target)])
        return json.loads((target/'result.json').read_bytes())
    def scan(plan,ctx):
        from scan_estate_graph import execute
        return execute(plan['options']['config'])
    def replay(plan,ctx):
        from cloud_verification_capture import replay
        return replay(plan['options']['capture'],ctx.root/'replay')
    def prepare(plan,ctx):
        from cloud_stage_worker import prepare_phase
        return prepare_phase(Path(plan['options']['inputs']),ctx.root/'prepared')
    def probe(plan,ctx):
        from fabric_sql_surface import read
        from scan_estate_graph import Meter
        from .shared_state import configured_state
        from .physical_reads import scope,guard_scope
        from .process_tape import Tape,active
        o=plan['options'];state=configured_state()
        if state is None:raise ValueError('RUNNER_SHARED_BUDGET_REQUIRED')
        meter=Meter(state,o['budget'],o['max_requests'])
        tape=Tape(ctx.root/'probe-tape.json',bootstrap=plan['bootstrap'])
        try:
            with active(tape),guard_scope(lambda value:ctx.record('guard',value)):
                def measured():
                    with scope(lambda kind,fn:meter(fn)):
                        return read(o['config'],o['database'],o['request'])
                result=meter(measured)
                ctx.record('native-result',result)
                tape.finish(result)
                return result
        finally:meter.close()
    def smoke(plan,ctx):
        from .daily_smoke import handler
        return handler({**plan,'target':plan['options']},ctx)
    return {'verification':verification,'investigation':investigation,'scan':scan,'replay':replay,'prepare':prepare,'probe':probe,'smoke':smoke}

def run(config,target,*,registry=None,put=None,sleep=time.sleep,run_id=None):
    check=config['checks'].get(target)
    if check is None and Path(target).is_file():
        # The file is submitted through the same normal form contract; it never
        # supplies a handler, script or unvalidated SQL payload.
        check={'kind':'investigation','options':{'ticket':str(Path(target).resolve())}}
    if check is None:raise ValueError('RUNNER_UNKNOWN_CHECK:'+target)
    run_id=run_id or str(uuid4())
    plan={'manifest':config['manifest'],'bootstrap':config['bootstrap'],'run_id':run_id,**check}
    # Full header and secret validation precede capture transport and handler.
    validate_bootstrap_header(config['bootstrap']);_safe(bytes_of(config))
    sink=put or blob_sink(config['capture'])
    ctx=DurableCapture(Path(config['output_root'])/run_id,sink,run_id=run_id,bootstrap=config['bootstrap'])
    registry=registry or handlers()
    keys=('INVESTIGATOR_OPERATING_MODE','INVESTIGATOR_BUDGET_CATEGORY')
    previous={key:os.environ.get(key) for key in keys}
    try:
        with ctx.observing():
            os.environ['INVESTIGATOR_OPERATING_MODE']='BUILD_PHASE'
            os.environ['INVESTIGATOR_BUDGET_CATEGORY']='SCAN' if check['kind'] in ('scan','smoke') else 'INVESTIGATION'
            attempt=0
            def perform():
                nonlocal attempt
                attempt+=1
                root=ctx.root/('attempt-'+str(attempt));root.mkdir()
                view=SimpleNamespace(root=root,record=ctx.record,
                    step=lambda name,fn:retry(lambda:ctx.step(name,fn),record=ctx.record,sleep=sleep))
                return ctx.step(check['kind'],lambda:registry[check['kind']](plan,view))
            result=retry(perform,record=ctx.record,sleep=sleep)
            # Native result is durable independently of Tape.finish/export.
            ref=ctx.record('result',result)
            ctx.record('status',{'status':'COMPLETED','partial':False,'result':ref})
        return {'run_id':run_id,'status':'COMPLETED','result':result}
    except BaseException as exc:
        ctx.fail(exc)
        raise
    finally:
        for key,value in previous.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value

def command(estate,target):
    return ['python','/app/scripts/dia.py','run',target,'--estate',str(estate),'--runtime','worker']

def main(args):
    if args.runtime=='worker':
        from cloud_stage_environment import install
        install()
        if 'DIA_RUNNER_ESTATE_JSON' in os.environ:
            raw=os.environ['DIA_RUNNER_ESTATE_JSON'].encode();_safe(raw)
            path=Path(args.estate);path.parent.mkdir(parents=True,exist_ok=True)
            if path.exists() and path.read_bytes()!=raw:raise ValueError('RUNNER_ESTATE_MATERIALIZATION_DIFFERS')
            if not path.exists():
                with path.open('xb') as stream:stream.write(raw)
        config=load(args.estate)
        try:result=run(config,args.target)
        except Exception as exc:
            # Exact safe failure lives in the durable capture. Never let an
            # exception chain print a provider body or credential to job logs.
            print(json.dumps({'status':'FAILED','error_type':type(exc).__name__}))
            return 1
        print(json.dumps(result));return 0
    config=load(args.estate)
    if args.runtime=='local':
        # Same digest and entrypoint as Azure. Mount only the explicitly selected
        # estate working directory; credential refs stay refs, never shell args.
        root=Path(args.estate).resolve().parent
        names=('DIA_PLATFORM_GATEWAY_POLICY','DIA_CLOUD_SLIM_RECORDING_JSON','DIA_RUNNER_ESTATE_JSON',
               'INVESTIGATOR_STATE_BACKEND','INVESTIGATOR_PG_HOST','INVESTIGATOR_PG_DATABASE','INVESTIGATOR_PG_USER',
               'AZURE_CLIENT_ID','DIA_GATEWAY_HTTP_IDENTITY','DIA_GATEWAY_SQL_IDENTITY','DIA_GATEWAY_MODEL_IDENTITY',
               'DIA_GATEWAY_STATE_IDENTITY','DIA_PLATFORM_CONTROL_RECEIPTS','DIA_GATEWAY_AUDIT_FILE','DIA_LIVE_ACCESS_DISABLED')
        forwarded=[part for name in names if name in os.environ for part in ('--env',name)]
        cmd=['docker','run','--rm','--entrypoint','python','--mount',f'type=bind,source={root},target=/estate',*forwarded,config['image'],'/app/scripts/dia.py','run',args.target,'--estate','/estate/'+Path(args.estate).name,'--runtime','worker']
        return subprocess.run(cmd,check=False).returncode
    # Azure launches use the same fixed argv and retain job's already installed
    # managed identity/environment. No inline Python or arbitrary command.
    output=subprocess.run(['az','containerapp','job','start','--name','job-dia-worker','--resource-group','rg-dia-platform','--command',*command(args.estate,args.target)],check=False)
    return output.returncode

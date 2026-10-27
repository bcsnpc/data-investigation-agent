"""One fixed runner registry; no user-supplied code, shell, or module imports."""
import argparse
import copy
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
KINDS=frozenset({'investigation','legacy-baseline','verification','probe','scan','replay','prepare','smoke','authorization-check','value-verification','collect-facts','facts-dispatcher','ledger-investigation','guided-investigation','enrichment-batch','access-check'})
PUBLIC_ENV=frozenset(('DIA_PLATFORM_GATEWAY_POLICY','DIA_CLOUD_SLIM_RECORDING_JSON',
    'INVESTIGATOR_STATE_BACKEND','INVESTIGATOR_PG_HOST','INVESTIGATOR_PG_DATABASE','INVESTIGATOR_PG_USER',
    'AZURE_CLIENT_ID','DIA_GATEWAY_HTTP_IDENTITY','DIA_GATEWAY_SQL_IDENTITY','DIA_GATEWAY_MODEL_IDENTITY',
    'DIA_GATEWAY_STATE_IDENTITY','DIA_PLATFORM_CONTROL_RECEIPTS','DIA_GATEWAY_AUDIT_FILE','DIA_LIVE_ACCESS_DISABLED'))

def collector_options(options):
    """Use the consumer's contract before launching a paid cloud execution."""
    from cloud_facts_collector import validate
    if set(options)!={'config'}:raise ValueError('FACT_COLLECTOR_RUNNER_OPTIONS')
    return validate(options['config'])

def load(path):
    value=json.loads(Path(path).read_bytes())
    required={'version','manifest','image','capture','checks','output_root'}
    if not isinstance(value,dict) or not required<=set(value)<=required|{'bootstrap','run_id','input','platform_cost_observation','deployment','environment','per_execution','schedule','access_check','explain','investigator_spec'} or value['version']!=VERSION:raise ValueError('RUNNER_ESTATE_SCHEMA')
    if 'per_execution' in value and type(value['per_execution'])is not bool:raise ValueError('RUNNER_PER_EXECUTION_FLAG')
    if not isinstance(value.get('environment',{}),dict) or not set(value.get('environment',{}))<=PUBLIC_ENV or any(not isinstance(v,str) for v in value.get('environment',{}).values()):raise ValueError('RUNNER_PUBLIC_ENVIRONMENT')
    if 'run_id' in value and not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',value['run_id']):raise ValueError('RUN_ID_INVALID')
    if not re.fullmatch(r'[^\s]+@sha256:[0-9a-f]{64}',value['image']):raise ValueError('RUNNER_PINNED_IMAGE_REQUIRED')
    if 'bootstrap' in value:validate_bootstrap_header(value['bootstrap'])
    if not isinstance(value['checks'],dict) or not value['checks']:raise ValueError('RUNNER_CHECKS_REQUIRED')
    for name,check in value['checks'].items():
        if not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',name) or set(check)!={'kind','options'} or check['kind'] not in KINDS or not isinstance(check['options'],dict):raise ValueError('RUNNER_TYPED_CHECK_REQUIRED')
        if check['kind']=='collect-facts':collector_options(check['options'])
        if 'manual_release_allocation' in check['options']:
            if (check['kind']!='smoke' or check['options']['manual_release_allocation']!='INVESTIGATION'
                    or not (value.get('per_execution') is True or
                            value.get('per_execution') is False and bool(value.get('run_id'))) or 'schedule' in value):
                raise ValueError('MANUAL_RELEASE_ALLOCATION_REQUIRES_UNSCHEDULED_SMOKE')
    _safe(bytes_of(value))
    return value

def capture_header(config,check=None):
    """Construct provenance, never accept a caller's invented engine identity."""
    from .runtime import fingerprint
    from .source_revision import committed_revision
    plan={k:config[k] for k in ('version','manifest','image','checks')}
    identity=hashlib.sha256(bytes_of(plan)).hexdigest()
    value={'entry_point':'runner_capture','context_identity':'runner-plan:'+identity,
           'config':{'_estate':{'operating_mode':'BUILD_PHASE'}},'profile':{},'usage_policy':None,
           'engine_hash':fingerprint(),'state':{'runner_contract':'dia-runner-capture-v1',
           'runner_image':config['image'],'engine_revision':committed_revision(),'plan_sha256':identity}}
    if check is None and len(config['checks'])==1:check=next(iter(config['checks'].values()))
    if check and check['kind']=='probe' and {'config','database','request'}<=set(check['options']):
        value['entry_point']='runner_probe'
        value['state']['runner_probe']={k:check['options'][k] for k in ('config','database','request')}
    validate_bootstrap_header(value)
    return value

def transient(error):
    # Authentication/authorisation and billing refusals are never retried for
    # model calls. SQL 18456 is an explicitly approved transient connection case.
    if getattr(error,'code',None) in (401,403) or getattr(error,'status_code',None) in (401,403):return False
    text=str(error).lower()
    if any(s in text for s in ('billing','unauthorized','forbidden','permission denied','secret_detected')):return False
    from urllib.error import URLError
    if isinstance(error,URLError) and isinstance(error.reason,(TimeoutError,ConnectionError)):return True
    if getattr(error,'stage',None)=='connect'and getattr(error,'error_number',None)==40613:return True
    return isinstance(error,(TimeoutError,ConnectionError)) or getattr(error,'error_number',None)==18456 or getattr(error,'code',None) in (408,429,502,503,504) or any(s in text for s in ('18456','connection reset','temporarily unavailable'))

def retry(call,*,record,sleep=time.sleep):
    for attempt in range(3):
        try:return call()
        except Exception as exc:
            from .run_database_audits import invalidate
            invalidate()
            record('attempt-failure',{'attempt':attempt+1,'error_type':type(exc).__name__,'message':str(exc),'retry':attempt<2 and transient(exc)})
            if attempt==2 or not transient(exc):raise
            sleep(30+15*attempt)

def handlers():
    def enrichment_batch(plan,ctx):
        from cloud_enrichment import execute
        return execute(plan,ctx)
    def guided_investigation(plan,ctx):
        from cloud_guided_investigator import execute
        return execute(plan,ctx)
    def ledger_investigation(plan,ctx):
        from cloud_investigator import execute
        return execute(plan,ctx)
    def facts_dispatcher(plan,ctx):
        from cloud_facts_dispatcher import execute
        if set(plan['options'])!={'configs'}:raise ValueError('FACT_DISPATCHER_RUNNER_OPTIONS')
        return ctx.step('facts-dispatcher',lambda:execute(plan['options']['configs']))
    def access_result(plan,ctx):
        if plan['options']:raise ValueError('ACCESS_CHECK_RUNNER_OPTIONS')
        return ctx.access_result
    def collect_facts(plan,ctx):
        from cloud_facts_collector import execute
        config=collector_options(plan['options'])
        return ctx.step('collect-facts',lambda:execute(config))
    def value_verification(plan,ctx):
        from cloud_value_execution import run
        return run(plan,ctx)
    def authorization_check(plan,ctx):
        from cloud_dax_authorization import run
        return run(plan,ctx)
    def verification(plan,ctx):
        from cloud_verification_run import execute
        from cloud_runner_context import prepare_for_verification, retain_dependencies
        o=plan['options']
        overall_seconds=o.get('deadline_seconds',1800)
        if type(overall_seconds)is not int or not 1<=overall_seconds<=1800:raise ValueError('VERIFICATION_OVERALL_BOUND')
        started=getattr(ctx,'started_at',None)
        overall_deadline=(time.time() if started is None else started)+overall_seconds
        window={'seconds':o.get('verification_seconds',900),'finalization_seconds':o.get('finalization_seconds',120),
            'demo_seconds':o.get('demo_seconds',300) if 'demo_ticket' in o else 0}
        from cloud_binding_verifier import validate_native_window
        validate_native_window(window)
        prepared=prepare_for_verification(plan,ctx) if 'inputs' in o else Path(o['prepared'])
        ctx.step('retain-approved-context',lambda:retain_dependencies(prepared,ctx,kind='prepared',phase='BEFORE_READS'))
        capture=ctx.root/'verification-capture'
        result=execute(plan['manifest'],prepared,o['spec'],spec_sha256=o['spec_sha256'],session=plan['run_id'],deadline=overall_deadline,native_window=window,capture=capture,
            retain=lambda folder,phase:retain_dependencies(folder,ctx,kind='verification',phase=phase))
        if 'demo_ticket' in o:
            if time.time()+window['finalization_seconds']+window['demo_seconds']>=overall_deadline:
                ctx.record('demo-not-admitted',{'reason':'OVERALL_DEADLINE_RESERVE','overall_deadline':overall_deadline})
                return {'status':'DEMO_DEFERRED_FOR_DEADLINE','verification':result,'demo':None}
            from cloud_runner_context import demo_after_verification
            return demo_after_verification(result,plan,ctx,prepared)
        return result
    def investigation(plan,ctx):
        if 'verification_proof'in plan['options']:
            from cloud_runner_context import demo_from_proof
            return demo_from_proof(plan,ctx)
        if 'ticket' in plan['options']:
            from .estate_installation import build
            from cloud_form_worker import run_form
            from run_adaptive_investigation import local_azure_key
            manifest,workspace=build(plan['manifest'])
            try:
                m=manifest['model'];settings={**m['credential'],'endpoint':m['endpoint'],'deployment':m['deployment']}
                with local_azure_key(settings):
                    from .normal_audit import mode,normal_context
                    if mode(plan['options'].get('recording_mode','NORMAL'))=='NORMAL':
                        with normal_context(ctx,plan.get('run_id','legacy-baseline'))as audit:
                            result=run_form(workspace,json.loads(Path(plan['options']['ticket']).read_bytes()))
                            audit.record('legacy-baseline-result',result)
                            return result
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
        from .runner_replay import replay
        return replay(plan['options'],ctx.root/'replay')
    def prepare(plan,ctx):
        from cloud_stage_worker import prepare_phase
        return prepare_phase(Path(plan['options']['inputs']),ctx.root/'prepared')
    def probe(plan,ctx):
        from fabric_sql_surface import read
        from scan_estate_graph import Meter
        from .shared_state import configured_state
        from .physical_reads import scope,guard_scope
        from .process_tape import Tape,active
        o=plan['options']
        bootstrap=copy.deepcopy(plan['bootstrap'])
        if bootstrap['entry_point']!='runner_probe':raise ValueError('RUNNER_PROBE_HEADER_REQUIRED')
        validate_bootstrap_header(bootstrap)
        tape=Tape(ctx.root/'probe-tape.json',bootstrap=bootstrap)
        state=configured_state()
        if state is None:raise ValueError('RUNNER_SHARED_BUDGET_REQUIRED')
        meter=Meter(state,o['budget'],o['max_requests'])
        try:
            with active(tape),guard_scope(lambda value:ctx.record('guard',value)):
                def measured():
                    with scope(lambda kind,fn:meter(fn)):
                        return read(o['config'],o['database'],o['request'])
                result=meter(measured)
                ctx.record('native-result',result)
                tape.finish(result)
                ctx.record('sealed-tape',{'name':tape.path.name,'value':json.loads(tape.path.read_bytes())})
                return result
        finally:meter.close()
    def smoke(plan,ctx):
        from .daily_smoke import run_smoke,_gold_read,capture_roundtrip
        from scan_estate_graph import Meter
        from .shared_state import configured_state
        from .physical_reads import scope
        o=plan['options'];state=configured_state()
        if state is None:raise ValueError('RUNNER_SMOKE_SHARED_BUDGET_REQUIRED')
        meter=Meter(state,o['budget'],o['max_requests'])
        def gold(payload):
            def execute():
                with scope(lambda kind,fn:meter(fn)):return _gold_read(payload)
            return meter(execute)
        demo_kind=o.get('demo_kind','ledger-investigation')
        if demo_kind not in ('ledger-investigation','legacy-baseline'):raise ValueError('SMOKE_ENGINE_KIND')
        demo_handler=ledger_investigation if demo_kind=='ledger-investigation' else investigation
        demo=(lambda:demo_handler({**plan,'options':o['demo']},ctx)) if o['config']['demo_earned'] else None
        try:return run_smoke(o['config'],ctx,state=state,gold_read=gold,blob_roundtrip=lambda config,body:capture_roundtrip(ctx,body),demo=demo)
        finally:meter.close()
    return {'verification':verification,'investigation':ledger_investigation,'guided-investigation':guided_investigation,'legacy-baseline':investigation,'scan':scan,'replay':replay,'prepare':prepare,'probe':probe,'smoke':smoke,'authorization-check':authorization_check,'value-verification':value_verification,'collect-facts':collect_facts,'facts-dispatcher':facts_dispatcher,'ledger-investigation':ledger_investigation,'enrichment-batch':enrichment_batch,'access-check':access_result}

def run(config,target,*,registry=None,put=None,sleep=time.sleep,run_id=None):
    from .run_database_audits import scope
    with scope():return _run(config,target,registry=registry,put=put,sleep=sleep,run_id=run_id)


def delivery_exit(kind,result):
    """Delivery, not READY/verification/attestation labels, decides ticket exit."""
    if kind not in ('investigation','ledger-investigation','guided-investigation','smoke'):
        return 0,'CHECK_REPORT_DELIVERED'
    if isinstance(result,dict):
        outputs=result.get('outputs',{})
        if kind=='guided-investigation':
            return (0,'ANSWER_DELIVERED') if result.get('status')=='ANSWERED' and outputs.get('business') else (1,'ANSWER_NOT_DELIVERED')
        if result.get('verdict') and all(isinstance(outputs.get(k),str) and outputs[k] for k in ('business','technical')):
            return 0,'ANSWER_DELIVERED'
        demo=result.get('demo',{})
        ticket=demo.get('ticket',{}) if isinstance(demo,dict) else {}
        if ticket.get('state') in ('FINDINGS_SHARED','RESOLVED','CLOSED') and ticket.get('findings'):
            return 0,'ANSWER_DELIVERED_WITH_LABELS' if result.get('handoff_warnings') or result.get('verification_label') else 'ANSWER_DELIVERED'
        if result.get('status') in ('HELD','CLARIFYING','NEEDS_INPUT','NEW','FAILED','ERROR'):
            return 1,'ANSWER_NOT_DELIVERED'
        if result.get('status')=='DEMO_FINISHED':return 1,'ANSWER_NOT_DELIVERED'
    # Non-ticket controls (including smoke without an earned demo) retain their
    # existing report contract; an internal exception still exits non-zero.
    return 0,'HANDLER_REPORT_DELIVERED'


def _run(config,target,*,registry=None,put=None,sleep=time.sleep,run_id=None):
    started_at=time.time()
    check=config['checks'].get(target)
    if check is None and Path(target).is_file():
        # The file is submitted through the same normal form contract; it never
        # supplies a handler, script or unvalidated SQL payload.
        if 'investigator_spec' not in config:raise ValueError('RUNNER_DEFAULT_INVESTIGATOR_SPEC_REQUIRED')
        path=Path(target).resolve()
        check={'kind':'ledger-investigation','options':{'spec':config['investigator_spec'],'ticket':{'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}}}
    if check is None:raise ValueError('RUNNER_UNKNOWN_CHECK:'+target)
    run_id=run_id or config.get('run_id') or str(uuid4())
    if 'bootstrap' in config:validate_bootstrap_header(config['bootstrap'])
    bootstrap=capture_header(config,check)
    plan={'manifest':config['manifest'],'bootstrap':bootstrap,'run_id':run_id,**check}
    # Full header and secret validation precede capture transport and handler.
    validate_bootstrap_header(bootstrap);_safe(bytes_of(config))
    sink=put or blob_sink(config['capture'])
    ctx=DurableCapture(Path(config['output_root'])/run_id,sink,run_id=run_id,bootstrap=bootstrap)
    last_step='admission'
    registry=registry or handlers()
    keys=('INVESTIGATOR_OPERATING_MODE','INVESTIGATOR_BUDGET_CATEGORY','INVESTIGATOR_WORKER_ID','DIA_STREAMING_CAPTURE')
    previous={key:os.environ.get(key) for key in keys}
    try:
        from .build_phase import manual_smoke_allocation
        # Host binding freezes per_execution=False and keeps its exact run_id.
        manual_smoke=(check['kind']=='smoke' and
                      (config.get('per_execution') is True or config.get('per_execution') is False and bool(config.get('run_id'))) and 'schedule' not in config
                      and check['options'].get('manual_release_allocation')=='INVESTIGATION')
        with ctx.observing(),manual_smoke_allocation(manual_smoke):
            os.environ['DIA_STREAMING_CAPTURE']='1'
            os.environ['INVESTIGATOR_OPERATING_MODE']='BUILD_PHASE'
            os.environ['INVESTIGATOR_WORKER_ID']=run_id
            os.environ['INVESTIGATOR_BUDGET_CATEGORY']='SCAN' if check['kind'] in ('scan','smoke') else 'INVESTIGATION'
            from scan_estate_graph import READ_OBSERVER
            observer_token=READ_OBSERVER.set(lambda label,value:ctx.record('physical-result',{'label':label,**value}))
            if 'input' in config:
                def materialize():
                    from cloud_stage_worker import transport,extract
                    o=config['input'];download,_=transport(config['capture'])
                    raw=download(o['url'],o['compressed_limit'])
                    if len(raw)>o['compressed_limit']:raise ValueError('RUNNER_INPUT_COMPRESSED_BOUND')
                    extract(raw,Path(o['directory']),expected=o['sha256'],expanded_limit=o['expanded_limit'])
                    return {'sha256':o['sha256'],'bytes':len(raw)}
                ctx.step('input-materialization',materialize)
            if check['kind'] != 'replay':
                from .access_check import configured as check_access
                access = ctx.step('check-access', lambda: check_access(config.get('access_check'),retain=ctx.record))
                ctx.access_result=access
                # Build-phase admission mismatches warn. The gateway/read-only
                # exceptions propagate; verification and tenant-only warnings
                # cannot turn into capability refusals here.
                if access['status'] != 'PASS':
                    ctx.record('admission-warning', {'kind':'CHECK_ACCESS', 'table':access})
            attempt=0
            def perform():
                nonlocal attempt
                attempt+=1
                root=ctx.root/('attempt-'+str(attempt));root.mkdir()
                view=SimpleNamespace(root=root,record=ctx.record,readback=ctx.readback,started_at=started_at,
                    access_result=getattr(ctx,'access_result',None),
                    step=lambda name,fn:retry(lambda:ctx.step(name,fn),record=ctx.record,sleep=sleep))
                return ctx.step(check['kind'],lambda:registry[check['kind']](plan,view))
            if getattr(ctx,'access_result',{}).get('status')=='FAIL' and check['kind']not in ('access-check','investigation','ledger-investigation','guided-investigation','smoke'):
                # Standalone probes still return their failed access report.
                # Investigations retain that report but check reachable layers:
                # each native read still verifies its own identity/read-only
                # guards and records blocked source availability. No fallback
                # identity or permission is introduced by a preflight warning.
                result={'status':'HELD','reason':'CHECK_ACCESS_FAILED','access_check':ctx.access_result,
                        'investigation_executed':False}
                ctx.record('admission-failure',result)
            else:
                last_step=check['kind']
                result=retry(perform,record=ctx.record,sleep=sleep)
            # Native result is durable independently of Tape.finish/export.
            ref=ctx.record('result',result)
            exit_code,exit_reason=delivery_exit(check['kind'],result)
            ctx.record('worker-exit',{'exit_code':exit_code,'reason':exit_reason,'last_step':last_step,
                                     'result':ref,'stage':'EXIT_INTENT_BEFORE_FINAL_SEAL'})
            ctx.record('status',{'status':'COMPLETED','partial':False,'result':ref})
            seal=ctx.seal()
            try:timing=ctx.publish_timing(seal)
            except Exception as error:timing={'status':'OBSERVATIONAL_TIMING_UNAVAILABLE','error_type':type(error).__name__}
        return {'run_id':run_id,'status':'COMPLETED','result':result,'exit_code':exit_code,'exit_reason':exit_reason,'timing':timing}
    except BaseException as exc:
        # Intent is durable even if publication/finalization fails. A platform
        # kill before this point is distinguishable by the record's absence.
        try:ctx.record('worker-exit',{'exit_code':1,'reason':'UNDELIVERED_EXCEPTION',
                                   'error_type':type(exc).__name__,'last_step':last_step})
        except Exception:pass
        ctx.fail(exc)
        try:ctx.publish_timing(None)
        except Exception:pass # Timing cannot replace the original failed-run evidence.
        raise
    finally:
        if 'observer_token' in locals():READ_OBSERVER.reset(observer_token)
        for key,value in previous.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value

def command(estate,target):
    return ['python','/app/scripts/dia.py','run',target,'--estate',str(estate),'--runtime','worker']


def azure_launch(config,target,*,execute=subprocess.run):
    from .adapters.runner_deployment import launch
    return launch(config,target,execute=execute)


def main(args):
    if args.runtime=='worker':
        from cloud_stage_environment import install
        if 'DIA_RUNNER_ESTATE_JSON' in os.environ:
            raw=os.environ['DIA_RUNNER_ESTATE_JSON'].encode();_safe(raw)
            path=Path(args.estate);path.parent.mkdir(parents=True,exist_ok=True)
            if path.exists() and path.read_bytes()!=raw:raise ValueError('RUNNER_ESTATE_MATERIALIZATION_DIFFERS')
            if not path.exists():
                with path.open('xb') as stream:stream.write(raw)
        config=load(args.estate)
        from .adapters.runner_schedule import bind_execution
        config=bind_execution(config)
        for name,value in config.get('environment',{}).items():os.environ[name]=value
        install()
        try:result=run(config,args.target)
        except Exception as exc:
            # Exact safe failure lives in the durable capture. Never let an
            # exception chain print a provider body or credential to job logs.
            print(json.dumps({'status':'FAILED','error_type':type(exc).__name__}))
            return 1
        # Full output already lives in the sealed capture. Do not serialize or
        # expose provider/evidence bodies again during process shutdown.
        print(json.dumps({k:result[k] for k in ('run_id','status','exit_code','exit_reason')}))
        return result['exit_code']
    config=load(args.estate)
    if args.runtime=='local':
        # Same digest and entrypoint in the cloud. Mount only the explicitly selected
        # estate working directory; credential refs stay refs, never shell args.
        root=Path(args.estate).resolve().parent
        names=('DIA_PLATFORM_GATEWAY_POLICY','DIA_CLOUD_SLIM_RECORDING_JSON','DIA_RUNNER_ESTATE_JSON',
               'INVESTIGATOR_STATE_BACKEND','INVESTIGATOR_PG_HOST','INVESTIGATOR_PG_DATABASE','INVESTIGATOR_PG_USER',
               'AZURE_CLIENT_ID','DIA_GATEWAY_HTTP_IDENTITY','DIA_GATEWAY_SQL_IDENTITY','DIA_GATEWAY_MODEL_IDENTITY',
               'DIA_GATEWAY_STATE_IDENTITY','DIA_PLATFORM_CONTROL_RECEIPTS','DIA_GATEWAY_AUDIT_FILE','DIA_LIVE_ACCESS_DISABLED')
        forwarded=[part for name in names if name in os.environ for part in ('--env',name)]
        cmd=['docker','run','--rm','--entrypoint','python','--mount',f'type=bind,source={root},target=/estate',*forwarded,config['image'],'/app/scripts/dia.py','run',args.target,'--estate','/estate/'+Path(args.estate).name,'--runtime','worker']
        return subprocess.run(cmd,check=False).returncode
    # Cloud launches use the same fixed argv and retain job's already installed
    # managed identity/environment. No inline Python or arbitrary command.
    print(json.dumps(azure_launch(config,args.target)));return 0

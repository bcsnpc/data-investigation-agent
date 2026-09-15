"""Run an approved evidence-led session, inspect history or reconcile an interruption."""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess

from investigator.onboarding import ModelStore
from investigator.runtime import Runtime
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.adaptive_planner import azure_plan
from metadata_config import load_config, ROOT
from run_native_diagnostic import transport as native_transport
from run_source_diagnostic import transport as source_transport


@contextmanager
def local_azure_key(settings_path):
    if settings_path is None:
        yield
        return
    settings=json.loads(settings_path.read_text(encoding='utf-8-sig'))
    variables=('AZURE_OPENAI_API_KEY','AZURE_OPENAI_ENDPOINT','AZURE_OPENAI_DEPLOYMENT')
    previous={k:os.environ.get(k) for k in variables}
    try:
        result=subprocess.run([str(ROOT/'.local/azure-cli-env/Scripts/python.exe'),'-m','azure.cli',
            'cognitiveservices','account','keys','list','--subscription',settings['subscription_id'],
            '--resource-group',settings['resource_group'],'--name',settings['account'],'-o','json'],
            capture_output=True,text=True,check=True,timeout=60)
        os.environ.update(AZURE_OPENAI_API_KEY=json.loads(result.stdout)['key1'],
                          AZURE_OPENAI_ENDPOINT=settings['endpoint'],AZURE_OPENAI_DEPLOYMENT=settings['deployment'])
        yield
    finally:
        for key,value in previous.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True);parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--environment',required=True)
    select=parser.add_mutually_exclusive_group(required=True)
    select.add_argument('--envelope',type=Path);select.add_argument('--session-id');select.add_argument('--usage-status',action='store_true')
    parser.add_argument('--request-key');parser.add_argument('--approve',action='store_true')
    parser.add_argument('--status-only',action='store_true');parser.add_argument('--recover',action='store_true')
    parser.add_argument('--usage-policy',type=Path)
    parser.add_argument('--cancel',action='store_true');parser.add_argument('--reconcile-cancelled',action='store_true')
    parser.add_argument('--predecessor');parser.add_argument('--azure-settings',type=Path)
    parser.add_argument('--preview',action='store_true')
    args=parser.parse_args()
    if not (args.status_only or args.usage_status or args.preview) and not args.approve:parser.error('Explicit scope approval required')
    if args.preview and (not args.envelope or args.predecessor):parser.error('Preview requires an envelope')
    if args.envelope and (not (args.request_key or args.preview) or args.status_only or args.recover):parser.error('New envelope needs request key and approval')
    if args.predecessor and not args.envelope:parser.error('Reviewed successor needs a new envelope')
    if args.status_only and args.recover:parser.error('Status and recovery are separate actions')
    if sum(bool(x) for x in (args.status_only,args.recover,args.cancel,args.reconcile_cancelled,args.usage_status,args.preview))>1:parser.error('Choose one control action')
    if (args.cancel or args.reconcile_cancelled) and not args.session_id:parser.error('Cancellation requires session ID')
    config=load_config(args.config);store=ModelStore(args.database,config['storage']['database'],args.environment)
    if args.preview:
        from investigator.adaptive_candidates import catalog
        candidates,gaps=catalog(store,config,json.loads(args.envelope.read_text(encoding='utf-8-sig')))
        print(json.dumps({'candidates':candidates,'gaps':gaps,'cloud_calls':0,'equivalence_verified':False}));return 0
    runtime=Runtime(store,config,lambda p:native_transport(config,p),lambda p:source_transport(config,p))
    settings=json.loads(args.azure_settings.read_text(encoding='utf-8-sig')) if args.azure_settings else {}
    profile={'adapter':'azure','endpoint':settings.get('endpoint',os.environ.get('AZURE_OPENAI_ENDPOINT')),
             'deployment':settings.get('deployment',os.environ.get('AZURE_OPENAI_DEPLOYMENT'))}
    policy=json.loads(args.usage_policy.read_text(encoding='utf-8-sig')) if args.usage_policy else None
    agent=AdaptiveRuntime(runtime,azure_plan,planner_profile=profile,usage_policy=policy);identity=args.session_id
    try:
        if args.envelope:
            envelope=json.loads(args.envelope.read_text(encoding='utf-8-sig'))
            result=agent.revise(args.predecessor,envelope,args.request_key) if args.predecessor else agent.create(envelope,args.request_key)
            identity=result['id']
        if args.usage_status:
            if agent.governor is None:raise ValueError('Usage policy required')
            print(json.dumps(agent.governor.snapshot()));return 0
        if args.status_only:result=agent.get(identity)
        elif args.cancel:result=agent.cancel(identity)
        elif args.reconcile_cancelled:result=agent.reconcile_cancelled(identity)
        else:
            with local_azure_key(args.azure_settings):
                if args.recover:result=agent.recover(identity)
                else:result=agent.run(identity)
        print(json.dumps(result));return 0 if result['status'] in ('COMPLETED','NEEDS_INPUT','CANCELLED') or args.status_only else 1
    except Exception as exc:
        print(json.dumps({'status':'HELD','session_id':identity,'error_type':type(exc).__name__}));return 1


if __name__=='__main__':raise SystemExit(main())

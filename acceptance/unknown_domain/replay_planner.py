"""Offline recorded-session replay or explicit live next-action comparison.

Both modes are known-state evaluation, not frozen acceptance or business grading.
No expected answers or grading labels enter the planner payload.
"""
import argparse
import json
from pathlib import Path
import sys
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from metadata_config import load_config
from investigator.onboarding import ModelStore,encoded,digest
from investigator.runtime import Runtime
from investigator.usage_governance import UsageGovernor
from investigator.adaptive_planner import azure_plan
from investigator.dynamic_reasoning import validate
from investigator.generation_policy import error_summary,failure_usage
from run_adaptive_investigation import local_azure_key


def no_execution(*args):
    raise RuntimeError('Replay evaluation cannot execute data tools')


def main():
    if '--offline-session' in sys.argv:
        return offline_main()
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--folder',type=Path,required=True)
    p.add_argument('--payload',type=Path,required=True)
    p.add_argument('--azure-settings',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--repeats',type=int,default=2)
    p.add_argument('--reasoning-efforts',nargs='+',choices=['none','low','medium','high'],default=['none','medium'])
    p.add_argument('--max-output-tokens',type=int,default=4000)
    args=p.parse_args()
    if not 1<=args.repeats<=3:p.error('One to three repetitions')
    if not 1<=len(args.reasoning_efforts)<=3 or not 500<=args.max_output_tokens<=8000:p.error('Bounded comparison settings required')
    if args.output.exists():p.error('Use a new output path; preserve previous trials')
    payload=json.loads(args.payload.read_text(encoding='utf-8'))
    if 'generation_options' in payload:raise ValueError('Provider settings are evaluator-owned')
    config=load_config(args.folder/'config.json')
    store=ModelStore(args.folder/'catalog.sqlite',config['storage']['database'],'development')
    runtime=Runtime(store,config,no_execution,no_execution)
    governor=UsageGovernor(runtime,json.loads((args.folder/'usage-policy.json').read_text()),time.time)
    identity='planner-replay:'+str(uuid4());rows=[];last=0
    with local_azure_key(args.azure_settings):
        for repeat in range(args.repeats):
            for effort in args.reasoning_efforts:
                delay=65-(time.monotonic()-last)
                while delay>0:
                    time.sleep(min(delay,30));delay=65-(time.monotonic()-last)
                key=str(len(rows));options={'reasoning_effort':effort,'max_output_tokens':args.max_output_tokens,'timeout_seconds':120}
                with runtime.db() as db:
                    db.execute('BEGIN IMMEDIATE')
                    governor.reserve(db,identity,key,'planner',len(encoded(payload)),output_tokens=args.max_output_tokens)
                started=last=time.monotonic();usage=None
                row={'repeat':repeat,'generation_options':options}
                try:
                    from investigator.planner_recording import recording
                    with recording({'session_id':identity,'planner_call':len(rows)+1,
                            'context_version':payload.get('context_version'), 'payload':payload,
                            'budget':governor.snapshot(), 'reservation':{'key':key,
                                'input_characters':len(encoded(payload)),
                                'output_tokens':args.max_output_tokens,'governed':True}}):
                        proposal,metadata=azure_plan({**payload,'generation_options':options})
                    usage=metadata.get('usage')
                    validate(proposal,payload)
                    row.update(status='VALID_PROPOSAL',proposal=proposal,provider=metadata)
                except Exception as exc:
                    usage=failure_usage(exc)
                    row.update(status='FAILED',provider_usage=usage,**error_summary(exc))
                finally:
                    with runtime.db() as db:
                        governor.settle(db,identity,key,usage,uncertain=usage is None)
                row['elapsed_seconds']=round(time.monotonic()-started,3);rows.append(row)
                args.output.write_text(json.dumps({'trial_kind':'KNOWN_STATE_NO_TOOL_EXECUTION',
                    'payload_hash':digest(payload),'reservation_session':identity,'trials':rows,
                    'business_correctness':'NOT_AUTOMATICALLY_GRADED'},indent=2),encoding='utf-8')
                print(json.dumps({k:v for k,v in row.items() if k not in ('proposal','provider')}),flush=True)


def offline_main():
    """Separate offline path: never obtains a cloud key or calls the live adapter."""
    from session_replay import replay
    from run_ledger import append, row, failed
    from investigator.planner_recording import load_session
    p=argparse.ArgumentParser(description='Replay a recorded session offline in an isolated local copy')
    p.add_argument('--offline-session',required=True)
    p.add_argument('--recordings',type=Path,default=ROOT/'.local/planner-recordings')
    p.add_argument('--folder',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--inject-at',type=int)
    p.add_argument('--injection',type=Path)
    p.add_argument('--allow-engine-drift',action='store_true')
    args=p.parse_args()
    destination=args.output.resolve()
    if not destination.is_relative_to((ROOT/'.local').resolve()):
        p.error('Replay output must be a new directory under .local')
    started=time.monotonic()
    try:
        config=load_config(args.folder/'config.json')
        result=replay(args.offline_session,args.recordings,args.folder/'catalog.sqlite',
            config['storage']['database'],config,destination,inject_at=args.inject_at,
            injection=json.loads(args.injection.read_text()) if args.injection else None,
            allow_engine_drift=args.allow_engine_drift)
    except Exception as exc:
        append(ROOT/'docs/runs/ledger.jsonl',failed(type(exc).__name__,round(time.monotonic()-started,3)))
        print(json.dumps({'status':'REPLAY_PREFLIGHT_FAILED','error_type':type(exc).__name__}))
        return 1
    append(ROOT/'docs/runs/ledger.jsonl', row(result, load_session(args.offline_session,args.recordings)))
    print(json.dumps({k:v for k,v in result.items() if k!='session'}))
    return 0 if result['status'] in ('MATCHED','INJECTION_PROBE') else 1


if __name__=='__main__':raise SystemExit(main())

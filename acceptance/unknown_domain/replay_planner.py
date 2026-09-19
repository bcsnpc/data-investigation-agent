"""Budgeted next-action comparison on a saved payload. Never executes proposals.

This is known-state evaluation, not frozen acceptance or end-to-end validation.
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
from investigator.generation_policy import error_summary
from run_adaptive_investigation import local_azure_key


def no_execution(*args):
    raise RuntimeError('Replay evaluation cannot execute data tools')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--folder',type=Path,required=True)
    p.add_argument('--payload',type=Path,required=True)
    p.add_argument('--azure-settings',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--repeats',type=int,default=2)
    args=p.parse_args()
    if not 1<=args.repeats<=3:p.error('One to three repetitions')
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
            for effort in ('none','medium'):
                delay=65-(time.monotonic()-last)
                while delay>0:
                    time.sleep(min(delay,30));delay=65-(time.monotonic()-last)
                key=str(len(rows));options={'reasoning_effort':effort,'max_output_tokens':4000,'timeout_seconds':120}
                with runtime.db() as db:
                    db.execute('BEGIN IMMEDIATE')
                    governor.reserve(db,identity,key,'planner',len(encoded(payload)),output_tokens=4000)
                started=last=time.monotonic();usage=None
                row={'repeat':repeat,'generation_options':options}
                try:
                    proposal,metadata=azure_plan({**payload,'generation_options':options})
                    usage=metadata.get('usage')
                    validate(proposal,payload)
                    row.update(status='VALID_PROPOSAL',proposal=proposal,provider=metadata)
                except Exception as exc:
                    row.update(status='FAILED',**error_summary(exc))
                finally:
                    with runtime.db() as db:
                        governor.settle(db,identity,key,usage,uncertain=usage is None)
                row['elapsed_seconds']=round(time.monotonic()-started,3);rows.append(row)
                args.output.write_text(json.dumps({'trial_kind':'KNOWN_STATE_NO_TOOL_EXECUTION',
                    'payload_hash':digest(payload),'reservation_session':identity,'trials':rows,
                    'business_correctness':'NOT_AUTOMATICALLY_GRADED'},indent=2),encoding='utf-8')
                print(json.dumps({k:v for k,v in row.items() if k not in ('proposal','provider')}),flush=True)


if __name__=='__main__':main()

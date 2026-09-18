"""Run a business ticket through the frozen engine and ordinary discovered catalog.

No evaluator expectations, publisher manifest or native model IDs are loaded here.
The evaluator reviews the LLM scope proposal before launching this acceptance run.
"""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from challenge_freeze import verify
from metadata_config import load_config
from investigator.onboarding import ModelStore
from investigator.runtime import Runtime
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.adaptive_planner import azure_plan
from investigator.question_intake import azure_resolve
from investigator.workspace import Workspace
from run_native_diagnostic import transport as native
from run_source_diagnostic import transport as source
from run_adaptive_investigation import local_azure_key


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--folder',type=Path,required=True)
    p.add_argument('--ticket',type=Path,required=True)
    p.add_argument('--key',required=True)
    p.add_argument('--execute-reviewed-scope',action='store_true')
    p.add_argument('--known-domain-regression',action='store_true',
                   help='Explicitly test changed code against an already known domain; never unknown-domain acceptance')
    p.add_argument('--minimum-llm-interval',type=int,default=0,
                   help='Evaluator-side pacing in seconds; does not retry failed calls or change prompts')
    args=p.parse_args();folder=args.folder
    if not 0<=args.minimum_llm_interval<=120:p.error('LLM interval must be 0–120 seconds')
    freeze=json.loads((folder/'freeze.json').read_text())
    if not args.known_domain_regression:verify(freeze)
    c=load_config(folder/'config.json');store=ModelStore(folder/'catalog.sqlite',c['storage']['database'],'development')
    last_call=[0.0]
    def paced(call,payload):
        remaining=args.minimum_llm_interval-(time.monotonic()-last_call[0])
        while remaining>0:
            time.sleep(min(remaining,30))
            remaining=args.minimum_llm_interval-(time.monotonic()-last_call[0])
        last_call[0]=time.monotonic()
        return call(payload)
    agent=AdaptiveRuntime(Runtime(store,c,lambda r:native(c,r),lambda r:source(c,r)),lambda payload:paced(azure_plan,payload),
          planner_profile={'adapter':'azure','deployment':'investigator-llm'},
          usage_policy=json.loads((folder/'usage-policy.json').read_text()))
    def resolve(payload):
        response=paced(azure_resolve,payload)
        # Evaluator-side observation only; returns the exact unmodified proposal.
        (folder/('intake-proposal-'+args.key+'.json')).write_text(json.dumps(response,indent=2))
        return response
    ws=Workspace(agent,execution_enabled=True,question_resolver=resolve)
    with local_azure_key(ROOT/'infra/llm/development.json'):
        intake=ws.intake.resolve({'text':args.ticket.read_text(encoding='utf-8'),'request_key':args.key,'parent_id':None})
        output={'freeze_commit':None if args.known_domain_regression else freeze['commit'],
                'trial_kind':'KNOWN_DOMAIN_REGRESSION' if args.known_domain_regression else 'FROZEN_UNKNOWN_DOMAIN',
                'minimum_llm_interval':args.minimum_llm_interval,'intake':intake}
        if intake['status']=='PROPOSED':
            proposal=intake['proposal'];request={k:proposal[k] for k in ('model_id','measure_id','filters','dimension_ids')}
            request.update(symptom=intake['text'],predecessor=None,intake_id=intake['id'])
            preview=ws.preview(request);output['preview']=preview
            if args.execute_reviewed_scope:
                state=agent.create(preview['envelope'],'challenge:'+args.key)
                print('SESSION '+state['id'],flush=True)
                output['session']=agent.run(state['id'])
    if not args.known_domain_regression:verify(freeze)
    destination=folder/'runs';destination.mkdir(exist_ok=True)
    # Key is not a path supplied to the investigator.
    if not args.key.replace('-','').replace('_','').isalnum():raise ValueError('Simple output key required')
    (destination/(args.key+'.json')).write_text(json.dumps(output,indent=2),encoding='utf-8')
    result=output.get('session',{})
    print(json.dumps({'intake':intake['status'],'question':intake.get('question'),
        'status':result.get('status'),'classification':result.get('outcome',{}).get('classification'),
        'planner_calls':result.get('planner_calls'),'cloud_calls':result.get('cloud_calls')}))


if __name__=='__main__':main()

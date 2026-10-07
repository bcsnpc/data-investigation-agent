"""Plan or execute a bounded synthetic intake evaluation; no investigation reads."""
import argparse
import json
from pathlib import Path
from uuid import uuid4
from investigator.estate_installation import build
from investigator.estate_manifest import load
from investigator.onboarding import digest
from investigator.model_eval_intake import run_case
from investigator.question_intake import azure_resolve
from run_adaptive_investigation import local_azure_key


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--golden',type=Path,default=Path('acceptance/model_steps/intake.json'))
    p.add_argument('--model-version',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--execute',action='store_true')
    args=p.parse_args();manifest=load(args.manifest)
    if manifest['model']['deployment']!=args.model_version:raise ValueError('Model version differs from declared deployment')
    golden=json.loads(args.golden.read_text(encoding='utf8'))
    if golden['step']!='intake':raise ValueError('Intake golden set required')
    if args.output.exists():raise ValueError('Existing evaluation attempts are immutable; no replacement')
    plan={'kind':'SYNTHETIC_INTAKE_EVALUATION','cases':len(golden['cases']),
          'maximum_model_calls':2*len(golden['cases']),'physical_estate_requests':0,
          'model_version':args.model_version,'golden_hash':digest(golden),'manifest_hash':digest(manifest),
          'budget':'Existing daily model governor; no counter reset or policy increase.',
          'provider_authentication':'Existing local Azure credential mechanism; no secret created.'}
    if not args.execute:print(json.dumps(plan,indent=2));return
    # Build read-only: no transports, code fetch or discovery approval probe.
    manifest,workspace=build(args.manifest,execution_enabled=False)
    agent=workspace.agent;args.output.mkdir(parents=True,exist_ok=False)
    before=agent.governor.snapshot()
    (args.output/'plan.json').write_text(json.dumps({**plan,'usage_before':before},indent=2),encoding='utf8')
    model=manifest['model'];settings={**model['credential'],'endpoint':model['endpoint'],'deployment':model['deployment']}
    records=[];batch=str(uuid4());failure=None
    try:
        with local_azure_key(settings):
            for case in golden['cases']:
                if digest(json.loads(args.golden.read_text(encoding='utf8')))!=plan['golden_hash']:raise ValueError('Golden set changed during evaluation')
                saved=run_case(agent,golden,case,azure_resolve,args.output/(case['id']+'.tape.json'),batch+':'+case['id'])
                row={'case_id':case['id'],'model_version':args.model_version,'intake':saved}
                records.append(row)
                (args.output/(case['id']+'.result.json')).write_text(json.dumps(row,indent=2),encoding='utf8')
                print(json.dumps({'case_id':case['id'],'status':saved['status'],'error':saved.get('error')}),flush=True)
    except BaseException as exc:failure=type(exc).__name__;raise
    finally:
        (args.output/'records.json').write_text(json.dumps(records,indent=2),encoding='utf8')
        (args.output/'usage-after.json').write_text(json.dumps({'snapshot':agent.governor.snapshot(),
            'completed_cases':len(records),'error_type':failure,'physical_estate_requests':0},indent=2),encoding='utf8')


if __name__=='__main__':main()

"""Plan or execute the MODEL-extractor score set without verification or reads."""
import argparse,json
from pathlib import Path
from uuid import uuid4
from investigator.estate_installation import build
from investigator.estate_manifest import load
from investigator.onboarding import digest
from investigator.model_eval_reader import run_case
from investigator.adapters.code_model import azure_propose
from run_adaptive_investigation import local_azure_key


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--golden',type=Path,default=Path('acceptance/model_steps/reader.json'))
    p.add_argument('--model-version',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--execute',action='store_true')
    args=p.parse_args();m=load(args.manifest);g=json.loads(args.golden.read_text(encoding='utf8'))
    if m['model']['deployment']!=args.model_version or g['step']!='reader':raise ValueError('Declared model and reader suite required')
    if args.output.exists():raise ValueError('Existing attempts are immutable; no replacement')
    plan={'kind':'MODEL_EXTRACTOR_EVALUATION','cases':len(g['cases']),'maximum_model_calls':len(g['cases']),
          'golden_hash':digest(g),'manifest_hash':digest(m),'model_version':args.model_version,
          'physical_requests':0,'verification_performed':False,'generation_options':m['model']['generation_options']}
    if not args.execute:print(json.dumps(plan,indent=2));return
    m,w=build(args.manifest,execution_enabled=False);args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'plan.json').write_text(json.dumps({**plan,'usage_before':w.agent.governor.snapshot()},indent=2),encoding='utf8')
    settings={**m['model']['credential'],'endpoint':m['model']['endpoint'],'deployment':m['model']['deployment']}
    records=[];failure=None
    try:
        with local_azure_key(settings):
            for c in g['cases']:
                if digest(json.loads(args.golden.read_text(encoding='utf8')))!=plan['golden_hash']:raise ValueError('Golden changed during evaluation')
                r=run_case(w.agent,g,c,azure_propose,args.output/(c['id']+'.tape.json'),'model-eval-reader:'+str(uuid4()))
                row={'case_id':c['id'],'model_version':args.model_version,**r};records.append(row)
                (args.output/(c['id']+'.result.json')).write_text(json.dumps(row,indent=2),encoding='utf8')
                print(json.dumps({'case_id':c['id'],'proposals':len(r['proposals']),'semantic_refusal':r['semantic_refusal'],
                                  'provider_error':r['provider_error'],'validation_error':r['validation_error']}),flush=True)
                if r.get('budget_hold'):
                    raise RuntimeError('Reader evaluation stopped at budget admission; remaining cases unattempted')
    except BaseException as exc:failure=type(exc).__name__;raise
    finally:
        (args.output/'records.json').write_text(json.dumps(records,indent=2),encoding='utf8')
        (args.output/'usage-after.json').write_text(json.dumps({'snapshot':w.agent.governor.snapshot(),'error_type':failure,
            'completed_cases':len(records),'physical_requests':0},indent=2),encoding='utf8')


if __name__=='__main__':main()

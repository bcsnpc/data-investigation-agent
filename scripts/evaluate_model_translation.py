"""Evaluate first translation proposals on authored local data, not the estate."""
import argparse,json
from pathlib import Path
from uuid import uuid4
from investigator.estate_manifest import load
from investigator.estate_installation import build
from investigator.onboarding import digest
from investigator.model_eval_translation import run_case,azure_propose
from evaluate_model_reader import stop_reason
from run_adaptive_investigation import local_azure_key


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--golden',type=Path,default=Path('acceptance/model_steps/translation.json'))
    p.add_argument('--model-version',required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--execute',action='store_true');a=p.parse_args()
    m=load(a.manifest);g=json.loads(a.golden.read_text(encoding='utf8'))
    if g['step']!='translation' or m['model']['deployment']!=a.model_version:raise ValueError('Declared translation suite and deployment required')
    if a.output.exists():raise ValueError('Recorded attempts are immutable')
    plan={'kind':'TRANSLATION_EVALUATION','cases':len(g['cases']),'model_calls_maximum':len(g['cases']),
        'golden_hash':digest(g),'manifest_hash':digest(m),'estate_physical_requests':0}
    if not a.execute:print(json.dumps(plan,indent=2));return
    m,w=build(a.manifest,execution_enabled=False);a.output.mkdir(parents=True,exist_ok=False)
    (a.output/'plan.json').write_text(json.dumps({**plan,'usage_before':w.agent.governor.snapshot()},indent=2),encoding='utf8')
    settings={**m['model']['credential'],'endpoint':m['model']['endpoint'],'deployment':m['model']['deployment']}
    records=[];failure=None
    try:
        with local_azure_key(settings):
            for c in g['cases']:
                if digest(json.loads(a.golden.read_text(encoding='utf8')))!=plan['golden_hash']:raise ValueError('Golden changed during evaluation')
                r=run_case(w.agent,g,c,azure_propose,a.output/(c['id']+'.tape.json'),'model-eval-translation:'+str(uuid4()))
                row={'case_id':c['id'],'model_version':a.model_version,**r};records.append(row)
                (a.output/(c['id']+'.result.json')).write_text(json.dumps(row,indent=2),encoding='utf8')
                print(json.dumps({'case_id':c['id'],'verdict':(r['evaluation'] or {}).get('verification',{}).get('status'),
                    'provider_error':r['provider_error'],'validation_error':r['validation_error']}),flush=True)
                reason=stop_reason(r)
                if reason:raise RuntimeError('Translation batch stopped at '+reason+'; remaining cases unattempted')
    except BaseException as exc:failure=type(exc).__name__;raise
    finally:
        (a.output/'records.json').write_text(json.dumps(records,indent=2),encoding='utf8')
        (a.output/'usage-after.json').write_text(json.dumps({'snapshot':w.agent.governor.snapshot(),'error_type':failure,'completed_cases':len(records)},indent=2),encoding='utf8')


if __name__=='__main__':main()

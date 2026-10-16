"""Invoke current intake over sealed golden texts; no estate transport is installed."""
import argparse
import base64
import json
import os
import time
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path

from investigator.estate_installation import build
from investigator.model_eval_intake import run_case, ci_agent
from investigator.model_step_scores import score_intake
from investigator.onboarding import digest
from investigator.question_intake import azure_resolve
from investigator.runtime import fingerprint
from run_adaptive_investigation import local_azure_key


def nomination(path):
    """The last recorded wire nomination; never invent a lost held proposal."""
    tape=json.loads(Path(path).read_text(encoding='utf-8'))
    found=None
    for event in tape['events']:
        if event['kind']!='PROVIDER_RESPONSE':continue
        response=json.loads(base64.b64decode(event['body']))
        body=json.loads(base64.b64decode(response['body']))
        for item in body.get('output',[]):
            if item.get('type')=='function_call':
                args=json.loads(item['arguments'])
                found=(args.get('kind') if item.get('name')=='extract_ticket_spans'
                       else (args.get('question_kind') or {}).get('kind'))
    return found


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sources=parser.add_mutually_exclusive_group(required=True)
    sources.add_argument('--manifest',type=Path)
    sources.add_argument('--ci-profile',type=Path)
    parser.add_argument('--golden',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--local-azure-key',action='store_true')
    parser.add_argument('--minimum-full-match',type=float,default=.9)
    parser.add_argument('--pace-seconds',type=float,default=65)
    args=parser.parse_args(argv)
    golden=json.loads(args.golden.read_text(encoding='utf-8'))
    args.output.mkdir(parents=True,exist_ok=True)
    if (args.output/'plan.json').exists():raise FileExistsError('Batch already attempted; preserve it.')
    if args.manifest:
        manifest,owner=build(args.manifest,execution_enabled=False)
        agent=owner.agent;store=owner.store
        model=manifest['model'];start=manifest['budgets']['round']['starts_at_epoch']
    else:
        model=json.loads(args.ci_profile.read_text(encoding='utf-8'))
        agent=ci_agent(args.output/'quality-store',model);store=agent.store;start=time.time()
        if args.local_azure_key:raise ValueError('CI must use its approved model credential, never an estate control profile.')
    engine=fingerprint();rows=[];last=[0.]
    version=model['deployment']
    def pot():
        with store.connect() as db:
            return db.execute("SELECT count(*) FROM adaptive_usage WHERE environment=? AND kind='cloud' AND created>=?",
                              (store.environment,start)).fetchone()[0]
    plan={'created':datetime.now(timezone.utc).isoformat(),'engine_hash':engine,
          'golden_hash':digest(golden),'model_version':version,'cases':len(golden['cases']),
          'physical_estate_requests':0,'pot_before':pot(),'budget_before':agent.governor.snapshot(),
          'basis':'CURRENT_PROMPT_AND_VALIDATOR; no recorded provider answers reused'}
    (args.output/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    def resolver(payload):
        while time.monotonic()-last[0]<args.pace_seconds:
            time.sleep(min(1,args.pace_seconds-(time.monotonic()-last[0])))
        last[0]=time.monotonic()
        return azure_resolve(payload)
    resolver.request_characters=azure_resolve.request_characters
    resolver.request_output_tokens=azure_resolve.request_output_tokens
    settings={**model.get('credential',{}),'endpoint':model.get('endpoint') or os.environ.get('AZURE_OPENAI_ENDPOINT'),'deployment':version}
    os.environ['INVESTIGATOR_RECORD_PLANNER']='1'
    if settings['endpoint']:os.environ['AZURE_OPENAI_ENDPOINT']=settings['endpoint']
    os.environ['AZURE_OPENAI_DEPLOYMENT']=version
    context=local_azure_key(settings) if args.local_azure_key else nullcontext()
    try:
        with context:
            if not os.environ.get('AZURE_OPENAI_API_KEY') or not settings['endpoint']:
                raise RuntimeError('Model provider authentication and endpoint are required; no cached-response fallback.')
            for case in golden['cases']:
                if fingerprint()!=engine:raise RuntimeError('Engine changed during intake evaluation.')
                before=agent.governor.snapshot()
                result=run_case(agent,golden,case,resolver,args.output/(case['id']+'.tape.json'),
                                'round-ten-c-'+args.output.name+'-'+case['id'])
                row={'case_id':case['id'],'model_version':version,'intake':result,
                     'nominated_question_kind':nomination(args.output/(case['id']+'.tape.json'))}
                rows.append(row)
                (args.output/(case['id']+'.result.json')).write_text(json.dumps(row,indent=2),encoding='utf-8')
                (args.output/'records.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
                after=agent.governor.snapshot()
                note={'date':datetime.now(timezone.utc).isoformat(),'experiment':'ROUND_TEN_C_INTAKE_DRY_RUN',
                      'trial_kind':'INTAKE_EVALUATION','family':case['id'],'status':result['status'],
                      'error':result.get('error'),'physical_requests':0,'diagnostic_reads':0,'guard_requests':0,
                      'intake_calls':after['reserved_today']['planner_calls']-before['reserved_today']['planner_calls'],
                      'pot_before':pot(),'pot_after':pot(),'artifact':str(args.output/(case['id']+'.result.json')),
                      'notes_doc':'docs/round-ten-c-intake-audit.md'}
                with Path('docs/runs/ledger.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(note,sort_keys=True)+'\n')
                print(json.dumps({k:note[k] for k in ('family','status','error','intake_calls')}),flush=True)
    finally:
        result=score_intake(golden,rows,version)
        result.update(pot_after=pot(),budget_after=agent.governor.snapshot(),
                      full_matches=sum(all(r['fields'].values()) for r in result['results']))
        result['full_match_rate']=result['full_matches']/len(golden['cases'])
        groups={group:[c['id'] for c in golden['cases'] if c.get('group')==group] for group in ('fifty','nine')}
        matched={r['case_id']:all(r['fields'].values()) for r in result['results']}
        by_id={r['case_id']:r['intake'] for r in rows}
        result['fifty_full_matches']=sum(matched[c] for c in groups['fifty'])
        result['fifty_full_match_rate']=result['fifty_full_matches']/len(groups['fifty']) if groups['fifty'] else None
        result['nine_resolved']=sum(by_id.get(c,{}).get('status')=='PROPOSED' and
            (by_id[c].get('proposal') or {}).get('target_visual',{}).get('resolution')=='RESOLVED' for c in groups['nine'])
        quality=result['fifty_full_match_rate'] if groups['fifty'] else result['full_match_rate']
        result['gate']='PASSED' if result['status']=='COMPLETE' and quality>=args.minimum_full_match and result['nine_resolved']==len(groups['nine']) else 'FAILED'
        (args.output/'score.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return 0 if result['gate']=='PASSED' else 1


if __name__=='__main__':raise SystemExit(main())

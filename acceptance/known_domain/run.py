"""One live known-domain case, selected by its approved fixture-state context.

Expected answers never enter intake, preview, compiler or planner payloads.
An operator establishes fixture state and records approval separately.
"""
import sys,json,time,traceback,os
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from investigator.estate_installation import build
from investigator.acceptance_context import load_case,pin_run_context
from investigator.onboarding import digest
from investigator.process_read_receipts import accounting
from run_adaptive_investigation import local_azure_key

def run_case(manifest_path,case_path,ticket_path,out,*,request_key,experiment,notes_doc):
    root=ROOT;out=Path(out);out.mkdir(parents=True,exist_ok=True)
    case_path=Path(case_path);family=case_path.stem
    os.environ['INVESTIGATOR_RECORD_PLANNER']='1'
    result_path=out/(family+'.json')
    if result_path.exists():raise FileExistsError('One attempt already exists: '+str(result_path))
    case=load_case(case_path)
    ticket=Path(ticket_path).read_text(encoding='utf8')
    if digest(ticket)!=case['ticket_hash']:raise ValueError('Original ticket hash differs')
    manifest,ws=build(manifest_path);agent=ws.agent
    selected=pin_run_context(ws,case_path,fixture=manifest)
    round_start=manifest['budgets']['round']['starts_at_epoch']
    def pot():
     with selected.connect() as db:return db.execute("SELECT count(*) FROM adaptive_usage WHERE environment=? AND kind='cloud' AND created>=?",(selected.environment,round_start)).fetchone()[0]
    def save():result_path.write_text(json.dumps(result,indent=2),encoding='utf8')
    result={'family':family,'trial_kind':'KNOWN_DOMAIN_REGRESSION','manifest_hash':digest(manifest),'fixture_state':selected.acceptance_fixture_state,'started':datetime.now(timezone.utc).isoformat(),'pot_before':pot(),'budget_before':agent.governor.snapshot(),'stage':'INTAKE'};save()
    print(json.dumps({'family':family,'pot_before':result['pot_before'],'rolling_before':result['budget_before']['read_allowance']['ordinary_charged'],'diagnostic_cap':manifest['budgets']['diagnostic_reads_per_run']}),flush=True)
    key=request_key;sid=None
    last=[0.0]
    def paced(call,payload):
     wait=65-(time.monotonic()-last[0])
     while wait>0:
      time.sleep(min(wait,30));wait=65-(time.monotonic()-last[0])
     last[0]=time.monotonic();return call(payload)
    original_planner=agent.planner;agent.planner=lambda p:paced(original_planner,p)
    original_resolver=ws.intake.resolver if hasattr(ws.intake,'resolver') else None
    settings={**manifest['model']['credential'],'endpoint':manifest['model']['endpoint'],'deployment':manifest['model']['deployment']}
    try:
     with local_azure_key(settings):
      intake=ws.intake.resolve({'text':ticket,'request_key':key,'parent_id':None});result['intake']=intake;save()
      if intake['status']=='PROPOSED':
       p=intake['proposal']
       if p['model_id']!=case['model_id']:raise ValueError('Intake selected another model; no investigation read')
       request={k:p[k] for k in ('model_id','measure_id','filters','dimension_ids')};request.update(symptom=intake['text'],predecessor=None,intake_id=intake['id'])
       result['stage']='PREVIEW';preview=ws.preview(request);result['preview']=preview;save()
       result['stage']='CREATE';state=agent.create(preview['envelope'],key);sid=state['id'];result['session_id']=sid;save()
       result['stage']='INVESTIGATION';result['session']=agent.run(sid);save()
       if result['session']['status'] in ('COMPLETED','NEEDS_INPUT','HELD'):
        result['stage']='SYNTHESIS';result['session']=paced(lambda _:agent.synthesize(sid),None)
      result['stage']='FINISHED'
    except BaseException as exc:
     result.update(error_type=type(exc).__name__,error=str(exc));traceback.print_exc()
    finally:
     if sid:result['session']=agent.get(sid)
     tape=agent._run_tapes.get(sid or (result.get('intake') or {}).get('id'))
     if tape:
      result.update(tape_path=str(tape.path),tape_finished=tape.finished)
      try:tape.validate();result['tape_validation']='VALIDATED'
      except Exception as exc:result['tape_validation']=str(exc)
     result.update(pot_after=pot(),budget_after=agent.governor.snapshot(),ended=datetime.now(timezone.utc).isoformat());save()
     state=result.get('session') or {};intake=result.get('intake') or {};syn=state.get('synthesis') or {}
     with selected.connect() as db:
      usage=db.execute('SELECT kind,session_id,actual FROM adaptive_usage WHERE session_id IN (?,?)',(sid or '', 'intake:'+intake.get('id',''))).fetchall()
     row={'date':result['ended'],'experiment':experiment+'_'+family,'family':family,'trial_kind':'KNOWN_DOMAIN_REGRESSION','session_id':sid,'status':'FAILED' if result.get('error') else state.get('status') or intake.get('status') or 'FAILED','outcome':(state.get('assessment') or {}).get('classification'),'error':result.get('error'),'manifest_hash':result['manifest_hash'],'fixture_state':result['fixture_state'],'physical_requests':sum(json.loads(r[2] or '{}').get('cloud_calls',0) for r in usage),'pot_before':result['pot_before'],'pot_after':result['pot_after'],'intake_calls':sum(r[0]=='planner' and r[1].startswith('intake:') for r in usage),'investigation_planner_calls':sum(e['kind']=='PLANNER_RESERVED' for e in state.get('events',[])),'synthesis_calls':syn.get('calls',0),'synthesis_status':syn.get('status'),'tape_validation':result.get('tape_validation'),'notes_doc':notes_doc,**accounting(state)}
     row['physical_requests_charged']=result['pot_after']-result['pot_before']
     with (root/'docs/runs/ledger.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(row,sort_keys=True)+'\n')
     (out/(family+'-inferred-ledger.json')).write_text(json.dumps(row,indent=2),encoding='utf8')
     print(json.dumps({k:row.get(k) for k in ['family','status','outcome','physical_requests_charged','error','tape_validation']}),flush=True)

    return result

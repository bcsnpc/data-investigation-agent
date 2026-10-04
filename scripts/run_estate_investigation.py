"""Investigate a ticket using the estate manifest as the sole configuration source."""
import argparse
import json
import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from investigator.estate_installation import build


def record_attempt(workspace, manifest, result, output, request_key):
    """Append counts from retained receipts, including failed composition."""
    from investigator.process_read_receipts import accounting
    from metadata_config import ROOT
    state=result.get('session') or {};intake=result.get('intake') or {}
    with workspace.agent.store.connect() as db:
        records=db.execute('SELECT kind,session_id,actual FROM adaptive_usage WHERE session_id IN (?,?)',
            (result.get('session_id',''),'intake:'+intake.get('id',''))).fetchall()
    total={}
    for kind,sid,actual in records:
        for key,value in json.loads(actual or '{}').items():total[key]=total.get(key,0)+value
    synthesis=state.get('synthesis') or {}
    row={'date_utc':datetime.now(timezone.utc).isoformat(),'mode':'live',
        'experiment':'MANIFEST_INVESTIGATION','run_key':request_key,'environment':manifest['environment'],
        'session_id':result.get('session_id'),'intake_id':intake.get('id'),
        'status':state.get('status') or intake.get('status') or 'FAILED',
        'stop_reason':state.get('stop_reason') or result.get('error_type'),
        'outcome_label':(state.get('assessment') or {}).get('classification'),
        'planner_calls':state.get('planner_calls',0),'intake_calls':sum(kind=='planner' and sid.startswith('intake:') for kind,sid,_ in records),
        'synthesis_calls':synthesis.get('calls',0),'synthesis_status':synthesis.get('status'),
        'engine_hash':state.get('engine_hash'),'manifest_hash':result['manifest_hash'],
        'diagnostic_read_cap':manifest['budgets']['diagnostic_reads_per_run'],
        'provider_input_tokens':total.get('input_tokens',0),'provider_output_tokens':total.get('output_tokens',0),
        'result_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),**accounting(state)}
    ledger=ROOT/'docs/runs/ledger.jsonl'
    with ledger.open('a',encoding='utf-8',newline='\n') as f:f.write(json.dumps(row,separators=(',',':'))+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,required=True)
    choice=p.add_mutually_exclusive_group(required=True)
    choice.add_argument('--ticket',type=Path)
    choice.add_argument('--preview-envelope',type=Path)
    p.add_argument('--request-key')
    p.add_argument('--output',type=Path)
    p.add_argument('--approve',action='store_true')
    a=p.parse_args()
    if a.preview_envelope:
        from investigator.estate_manifest import load
        from investigator.adapters.estate_installation import configuration
        from investigator.onboarding import ModelStore
        from investigator.adaptive_candidates import catalog
        from metadata_config import ROOT
        installation=load(a.manifest);config=configuration(installation)
        store=ModelStore(ROOT/installation['storage']['catalog'],config['storage']['database'],installation['environment'])
        candidates,gaps=catalog(store,config,json.loads(a.preview_envelope.read_text(encoding='utf-8-sig')))
        print(json.dumps({'candidates':candidates,'gaps':gaps,'cloud_calls':0,'equivalence_verified':False}))
        return 0
    if not a.request_key or not a.output:p.error('Live investigation requires request key and output')
    if not a.approve:p.error('Explicit scope approval required')
    if a.output.exists():p.error('Output exists; preserve the earlier attempt')
    manifest,workspace=build(a.manifest)
    model=manifest['model']
    settings={**model['credential'],'endpoint':model['endpoint'],'deployment':model['deployment']}
    from run_adaptive_investigation import local_azure_key
    from investigator.onboarding import digest
    result={'stage':'INTAKE','manifest_hash':digest(manifest)}
    try:
        with local_azure_key(settings):
            intake=workspace.intake.resolve({'text':a.ticket.read_text(encoding='utf-8'),'request_key':a.request_key,'parent_id':None})
            result['intake']=intake
            if intake['status']=='PROPOSED':
                proposal=intake['proposal']
                request={k:proposal[k] for k in ('model_id','measure_id','filters','dimension_ids')}
                request.update(symptom=intake['text'],predecessor=None,intake_id=intake['id'])
                result['stage']='PREVIEW';preview=workspace.preview(request)
                result['stage']='CREATE';state=workspace.agent.create(preview['envelope'],a.request_key)
                result['session_id']=state['id'];result['stage']='RUN'
                state=workspace.agent.run(state['id'])
                if state['status'] in ('COMPLETED','NEEDS_INPUT','HELD'):
                    result['stage']='SYNTHESIS';state=workspace.agent.synthesize(state['id'])
                result['session']=state
            result['stage']='FINISHED'
    except Exception as exc:
        result.update(error_type=type(exc).__name__,error=str(exc));raise
    finally:
        if result.get('session_id'):result['session']=workspace.agent.get(result['session_id'])
        a.output.write_text(json.dumps(result,indent=2),encoding='utf-8')
        record_attempt(workspace,manifest,result,a.output,a.request_key)
    return 0


if __name__=='__main__':raise SystemExit(main())

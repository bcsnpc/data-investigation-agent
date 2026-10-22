"""Plan, submit/resume, recorded stub and human CSV enrichment commands."""
import argparse
from datetime import datetime,timezone
import json
import hashlib
import os
from pathlib import Path
from investigator.enrichment import task,cache_key,EnrichmentStore,export_csv,import_csv
from investigator.enrichment_job import EnrichmentJob,EnrichmentSpendBudget,ACCOUNT,CEILING
from investigator.shared_state import SharedState,configured_state,encoded,sha


def plan(sources):
    sources=[task(s) for s in sources]
    return {'status':'PLAN_ONLY','tasks':len(sources),'subjects':[s['subject'] for s in sources],
        'task_hashes':[cache_key(s) for s in sources],'model_calls':0,'estate_requests':0,
        'account':ACCOUNT,'ceiling_microdollars':CEILING,'links':'INFERRED_ONLY_QUERY_CHECK_REQUIRED'}


def tasks_from_graph(repository,estate,*,limit=10000,key_tables=(),resolve_definition=None):
    """Operator enrichment enumeration, not ticket verification/intake loading."""
    graph=repository.records(estate,limit=limit)
    if graph['truncated']:raise ValueError('ENRICHMENT_GRAPH_ENUMERATION_TRUNCATED')
    nodes={n['id']:n for n in graph['nodes']};tasks=[]
    kinds={'REPORT','PAGE','VISUAL','MEASURE','CALCULATED_COLUMN','TABLE'}
    for node in graph['nodes']:
        if node['kind'] not in kinds or node['kind']=='TABLE' and node['id'] not in key_tables:continue
        definition=node['properties'].get('definition')
        if isinstance(definition,dict):
            if resolve_definition is None:raise ValueError('ENRICHMENT_DEFINITION_RESOLVER_REQUIRED')
            reference=definition
            raw=resolve_definition(reference)
            if not isinstance(raw,bytes) or len(raw)!=reference.get('bytes') or hashlib.sha256(raw).hexdigest()!=reference.get('sha256'):
                raise ValueError('ENRICHMENT_RETAINED_DEFINITION_HASH_DIFFERS')
            definition=raw.decode('utf8')
        if not isinstance(definition,str) or not definition:raise ValueError('ENRICHMENT_DEFINITION_NOT_RETAINED')
        neighbours=set()
        for edge in graph['edges']:
            if edge['source']==node['id']:neighbours.add(edge['target'])
            if edge['target']==node['id']:neighbours.add(edge['source'])
        values=[{'id':nodes[n]['id'],'kind':nodes[n]['kind'],'label':nodes[n]['label']} for n in sorted(neighbours) if n in nodes]
        tasks.append(task({'estate':estate,'subject':node['id'],'kind':node['kind'],'definition_hash':node['provenance']['definition_hash'],
            'definition':definition,'neighbours':values,'evidence_ids':[node['provenance']['source_id']]}))
    return tasks


def recorded_stub(sources,outputs,*,database,batch_key,at):
    from investigator.adapters.enrichment_stub import RecordedEnrichmentStub
    from investigator.adapters.enrichment_anthropic import price
    state=SharedState.offline(database);state.migrate()
    try:state.snapshot(ACCOUNT)
    except KeyError:
        # Private synthetic ledger only, never the approved live $25 account.
        state.import_accounts('stub-enrichment-account',{'accounts':[{'identity':ACCOUNT,'unit':'MICRODOLLARS',
            'ceiling':str(CEILING),'protected':'0','opening':'0','violated':False}],
            'provenance':{'source':'RECORDED_STUB','owner_approval':'synthetic-only'}})
    provider=RecordedEnrichmentStub(outputs);budget=EnrichmentSpendBudget(state,owner='stub-only',price=price)
    job=EnrichmentJob(state,provider,budget,clock=lambda:at)
    submitted=job.submit(sources,batch_key=batch_key)
    result=job.resume(batch_key) if submitted['status']=='SUBMITTED' else submitted
    simulation_budget=result.pop('budget',None)
    return {**result,'simulation_budget':simulation_budget,'live_enrichment_spend_microdollars':0,'live_model_calls':0,'stub_model_responses':len(sources),
            'examples':[job.store.projection(s['estate'],s['subject'],s['definition_hash']) for s in sources]}


def live_job(config,*,record):
    from investigator.adapters.enrichment_anthropic import BatchClient,price
    state=configured_state()
    if state is None:raise ValueError('ENRICHMENT_LIVE_SHARED_STATE_REQUIRED')
    provider=BatchClient(secret_reference=config['secret_reference'],identity=config['gateway_identity'],record=record,purpose='ENRICHMENT')
    budget=EnrichmentSpendBudget(state,owner=config['worker_identity'],price=price)
    return EnrichmentJob(state,provider,budget,clock=lambda:datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('operation',choices=['plan','stub','submit','resume','export','import'])
    parser.add_argument('--tasks');parser.add_argument('--outputs');parser.add_argument('--config');parser.add_argument('--csv')
    parser.add_argument('--reviewer');parser.add_argument('--batch-key');parser.add_argument('--database')
    parser.add_argument('--recording-dir',default='.local/enrichment-recordings')
    args=parser.parse_args(argv)
    sources=json.loads(Path(args.tasks).read_text(encoding='utf8')) if args.tasks else None
    if args.operation=='plan':result=plan(sources)
    elif args.operation=='stub':
        if not args.database or not args.outputs or not args.batch_key:raise ValueError('STUB_DATABASE_OUTPUTS_BATCH_REQUIRED')
        result=recorded_stub(sources,json.loads(Path(args.outputs).read_text(encoding='utf8')),database=args.database,batch_key=args.batch_key,
            at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
    else:
        if args.operation in ('export','import'):
            state=configured_state()
            if state is None:raise ValueError('ENRICHMENT_SHARED_STATE_REQUIRED')
            store=EnrichmentStore(state)
            if args.operation=='export':
                rows=[store.projection(s['estate'],s['subject'],s['definition_hash']) for s in sources]
                Path(args.csv).write_text(export_csv([r for r in rows if r]),encoding='utf8');result={'status':'EXPORTED','rows':sum(r is not None for r in rows)}
            else:
                results=import_csv(store,Path(args.csv).read_text(encoding='utf8'),at=datetime.now(timezone.utc).isoformat(),reviewer=args.reviewer)
                result={'status':'IMPORTED','rows':len(results)}
        else:
            from investigator.planner_recording import recording
            config=json.loads(Path(args.config).read_text(encoding='utf8'))
            prior=os.environ.get('INVESTIGATOR_RECORD_PLANNER');os.environ['INVESTIGATOR_RECORD_PLANNER']='1'
            counter=[0]
            try:
                with recording({'call_kind':'enrichment_batch','batch_key':args.batch_key,'purpose':'ENRICHMENT_ONLY'},directory=args.recording_dir) as capture:
                    def record(kind,body):
                        counter[0]+=1
                        if not capture.safe_write(str(counter[0])+'-'+kind+'.json',encoded(body).encode()):raise ValueError('ENRICHMENT_CAPTURE_EXCLUDED')
                    job=live_job(config,record=record)
                    result=job.submit(sources,batch_key=args.batch_key) if args.operation=='submit' else job.resume(args.batch_key)
            finally:
                if prior is None:os.environ.pop('INVESTIGATOR_RECORD_PLANNER',None)
                else:os.environ['INVESTIGATOR_RECORD_PLANNER']=prior
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()

"""Cloud approval-time binding controls; caller supplies an active exact capture.

This never publishes READY, changes approval, or invokes a language model.
"""
import argparse
import json
from pathlib import Path
from investigator.onboarding import digest
from investigator.verification_budget import VerificationBudget


def plan(spec):
    proposals=spec['proposals']
    if not proposals:raise ValueError('EMPTY_VERIFICATION_INVENTORY')
    identities=[digest(p) for p in proposals]
    if len(identities)!=len(set(identities)):raise ValueError('DUPLICATE_VERIFICATION_BINDING')
    required={p['target']['table'] for p in proposals}|{s['table'] for p in proposals for s in p['sources']}
    if set(spec['schemas'])!=required:raise ValueError('VERIFICATION_SCHEMA_COVERAGE_DIFFERS')
    targets={p['target']['table'] for p in proposals}
    if set(spec['samples'])!=targets:raise ValueError('VERIFICATION_SAMPLE_COVERAGE_DIFFERS')
    vb=VerificationBudget(spec['budgets'],len(proposals),record=lambda event:None)
    groups={spec['target_databases'][name] for name in targets}
    needed=2*len(proposals)+len(groups)+2
    return {'bindings':len(proposals),'target_catalog_reads':len(groups),
        'verification_reads_needed':needed,'verification_cap':vb.cap,
        'admissible':needed<=vb.cap,'physical_endpoint_requests':0,
        'diagnostic_investigation_reads':0,'model_calls':0,
        'publication':'NOT_PERFORMED','native_direct_route':'TWO_READS_IN_SAME_SESSION'}


def perform(bootstrap, work, budget_catalog=None, live=None):
    """Replay-compatible capture entry point, same inputs under live/replay.

    Cloud storage/budget authority is mandatory live. SQLite remains the private
    replay materialisation only. Failure preserves prior witnesses and stops.
    """
    from investigator import process_tape as tape
    from investigator.onboarding import ModelStore
    from investigator.runtime import Runtime, fingerprint
    from investigator.usage_governance import UsageGovernor
    from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
    from investigator.adapters.code_verification import resolve_objects
    from investigator.adapters.binding_verification import BindingVerificationRoute
    from investigator.adapters.binding_catalog import read_many as target_catalog
    from investigator.adapters.retained_endpoints import read as endpoint
    from investigator.binding_sample import verify
    from investigator.physical_reads import guard_scope
    from fabric_sql_surface import read as sql_read
    journal=tape.ACTIVE.get()
    if journal is None:raise ValueError('EXACT_CAPTURE_REQUIRED')
    i=bootstrap['state']['inputs'];spec=i['verification_spec'];config=bootstrap['config']
    if fingerprint()!=i['engine_fingerprint']:raise ValueError('VERIFIER_ENGINE_DIFFERS')
    planned=plan(spec)
    if not planned['admissible']:raise ValueError('VERIFICATION_CAP_INSUFFICIENT')
    work=Path(work);context=json.loads((work/'context.json').read_bytes())
    model=json.loads((work/'model.json').read_bytes())
    if digest(context)!=i['context_hash'] or model['context_id']!=i['model_context_id']:
        raise ValueError('VERIFIER_CONTEXT_PIN_DIFFERS')
    store=ModelStore(budget_catalog or work/'catalog.sqlite',work/'inventory.sqlite',bootstrap['state']['environment'])
    if store.get(model['id'])!=model:raise ValueError('VERIFIER_MODEL_STATE_DIFFERS')
    runtime=Runtime(store,config,None,None)
    governor=UsageGovernor(runtime,bootstrap['usage_policy'],lambda:tape.clock('cloud-verification-budget'))
    if not journal.replaying and governor.shared is None:raise ValueError('CLOUD_POSTGRES_AUTHORITY_REQUIRED')
    record={'plan':planned,'verification_events':[],'guards':[],'target_catalogs':[],
            'witnesses':[],'profile_published':False,'verification_reads':0}
    vb=VerificationBudget(spec['budgets'],len(spec['proposals']),record=lambda e:record['verification_events'].append(
        tape.bounded_call('binding_verification_admission',e,lambda:e)))
    sequence=0
    def meter(tool,execute):
        nonlocal sequence
        if tape.clock('cloud-verification-deadline')>=i['deadline']:raise ValueError('VERIFICATION_DEADLINE')
        sequence+=1
        return governor.metered_read(i['session_id'],tool+':'+str(sequence),execute)
    def sql(database,request):return sql_read(config,database,request)
    from run_native_diagnostic import transport as native_transport
    process=MicrosoftProcessAdapter(store,config,model,lambda request:native_transport(config,request),None,meter_read=meter,
        lower_surface={'status':'READY'},execute_lower=sql,
        read_endpoint=lambda request:endpoint(config,context,request,receipt_path=work/'endpoints.json'))
    objects,missing=resolve_objects(process,context,spec['schemas'])
    if missing:raise ValueError('VERIFICATION_OBJECT_RESOLUTION_REFUSED')
    try:
        with guard_scope(lambda e:record['guards'].append(e)):
            groups={}
            for name in dict.fromkeys(p['target']['table'] for p in spec['proposals']):
                target=objects[name]
                if spec['target_databases'][name]!=target['database']:raise ValueError('TARGET_DATABASE_PIN_DIFFERS')
                groups.setdefault((target['connection'],target['database']),[]).append(target)
            for targets in groups.values():
                results=target_catalog(config,targets,execute=lambda db,request:vb.read('METADATA',
                    lambda:meter('target-schema',lambda:sql(db,request))))
                for target in targets:
                    columns,proof=results[target['asset_id']]
                    target['catalog']['metadata']['columns']=columns;record['target_catalogs'].append(proof)
            route=BindingVerificationRoute(process,objects=objects,context=model['context_id'],
                string_semantics=spec['string_semantics'])
            for proposal in spec['proposals']:
                witness=verify(proposal,context=model['context_id'],sample=spec['samples'][proposal['target']['table']],
                    profile=route.target_profile(proposal),compiler=route.compile,
                    execute=lambda side,compiled:vb.read(side,lambda:route.execute(side,compiled)))
                record['witnesses'].append(witness)
                if witness['status']!='VERIFIED':break
        if len(record['witnesses'])==len(spec['proposals']) and all(w['status']=='VERIFIED' for w in record['witnesses']):
            # The declared semantic SUM boundary is checked in the same40-probe
            # session; no separate cap or duplicated allowance is created.
            from investigator.process_debugging import vertical
            receipts=[]
            def native_meter(tool,execute):
                if tool not in ('bounded_dax','bounded_fabric_sql'):raise ValueError('NATIVE_ROUTE_UNEXPECTED_READ')
                result=vb.read('TARGET' if tool=='bounded_dax' else 'SOURCE',lambda:meter(tool,execute))
                receipts.append({'receipt_id':result.get('id'),'status':result.get('status'),'tool':tool,'result_hash':digest(result)})
                return result
            process.meter_read=native_meter
            process.max_boundaries=1
            result=vertical(process,spec['native_measure_id'],{'filters':[],'dimension_ids':[]})
            record['native_route']={'id':i['session_id']+':native-route',
                'observations':result['_observations'],'process_read_receipts':receipts,
                'assessment':{k:v for k,v in result.items() if k!='_observations'}}
            comparisons=[o for o in result['_observations'] if o.get('comparison_status')=='CROSS_SURFACE_VERIFIED']
            if len(receipts)!=2 or len(comparisons)!=1 or comparisons[0].get('values_equal') is not True:
                raise ValueError('NATIVE_DECLARED_ROUTE_NOT_VERIFIED')
        record['status']='VERIFIED' if len(record['witnesses'])==len(spec['proposals']) and all(w['status']=='VERIFIED' for w in record['witnesses']) else 'REFUSED'
        return record
    finally:
        record['verification_reads']=vb.count
        # Local capture-side detail retains partial progress even on an error.
        (work/'verification-progress.json').write_text(json.dumps(record,sort_keys=True,indent=2),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(plan(json.loads(args.plan.read_bytes())),indent=2))

if __name__=='__main__':main()

"""Cloud approval-time binding controls; caller supplies an active exact capture.

This never publishes READY, changes approval, or invokes a language model.
"""
import argparse
import json
from pathlib import Path
from investigator.onboarding import digest
from investigator.verification_budget import VerificationBudget


def plan(spec,*,config=None,objects=None):
    proposals=spec['proposals']
    if not proposals:raise ValueError('EMPTY_VERIFICATION_INVENTORY')
    identities=[digest(p) for p in proposals]
    if len(identities)!=len(set(identities)):raise ValueError('DUPLICATE_VERIFICATION_BINDING')
    required={p['target']['table'] for p in proposals}|{s['table'] for p in proposals for s in p['sources']}
    if set(spec['schemas'])!=required:raise ValueError('VERIFICATION_SCHEMA_COVERAGE_DIFFERS')
    targets={p['target']['table'] for p in proposals}
    if set(spec['samples'])!=targets:raise ValueError('VERIFICATION_SAMPLE_COVERAGE_DIFFERS')
    vb=VerificationBudget(spec['budgets'],len(proposals),record=lambda event:None)
    prewarm=spec.get('prewarm')
    if prewarm is not None:
        if (not isinstance(prewarm,dict) or set(prewarm)!={'asset_ids'}
                or not isinstance(prewarm['asset_ids'],list) or not 1<=len(prewarm['asset_ids'])<=32
                or any(not isinstance(a,str) or not a for a in prewarm['asset_ids'])
                or len(set(prewarm['asset_ids']))!=len(prewarm['asset_ids'])):
            raise ValueError('VERIFICATION_PREWARM_DECLARATION')
    groups={spec['target_databases'][name] for name in targets}
    needed=2*len(proposals)+len(groups)+2
    scope_validated=prewarm is None
    if prewarm is not None and config is not None and objects is not None:
        prewarm_assets(spec,config,objects);scope_validated=True
    return {'bindings':len(proposals),'target_catalog_reads':len(groups),
        'verification_reads_needed':needed,'verification_cap':vb.cap,
        'admissible':needed<=vb.cap and scope_validated,'physical_endpoint_requests':0,
        'prewarm_scope_validated':scope_validated,
        'diagnostic_investigation_reads':0,'model_calls':0,
        'publication':'NOT_PERFORMED','native_direct_route':'TWO_READS_IN_SAME_SESSION'}


def prewarm_source(spec,config,objects,governor,inputs,record,*,execute=None,sleep=None):
    """Opt-in source connection control; ordinary pot, no verification probes."""
    declaration=spec.get('prewarm')
    if declaration is None:return
    from investigator import process_tape as tape
    from serverless_control import prewarm
    if tape.ACTIVE.get() is None:raise ValueError('EXACT_CAPTURE_REQUIRED')
    assets=prewarm_assets(spec,config,objects)
    from sql_layer_policy import policy
    timeout=policy(config,{'asset_ids':assets})['worker_timeout_seconds']
    if type(timeout)is not int or not 1<=timeout<=240:
        raise ValueError('VERIFICATION_PREWARM_WORKER_BOUND')
    events=record.setdefault('control_events',[]);sequence=0
    def event(kind,value):
        entry={'class':'CONTROL','kind':kind,'value':value}
        events.append(tape.bounded_call('verification_prewarm_control',entry,lambda:entry))
    def deadline():
        if tape.clock('cloud-verification-prewarm-deadline')>=inputs['deadline']:
            raise ValueError('VERIFICATION_DEADLINE')
    def admit(kind,call):
        nonlocal sequence
        # Never admit a worker whose existing timeout reaches beyond the
        # verification job deadline. The configured timeout is not increased.
        if tape.clock('cloud-verification-prewarm-admission')+timeout>=inputs['deadline']:
            raise ValueError('VERIFICATION_DEADLINE')
        sequence+=1
        event(kind,{'asset_ids':assets,'attempt':sequence,'status':'ADMITTED'})
        return governor.metered_read(inputs['session_id']+':prewarm-controls',kind+':'+str(sequence),call)
    options={}
    if execute is not None:options['execute']=execute
    if sleep is not None:options['sleep']=sleep
    result=prewarm(config,assets,admit_control=admit,record_control=event,**options)
    deadline()
    if result.get('error') or result.get('status')!='CONNECTED':raise ValueError('VERIFICATION_PREWARM_FAILED')


def prewarm_assets(spec,config,objects):
    """Same source restriction for offline admission and actual controls."""
    declaration=spec.get('prewarm')
    if declaration is None:return []
    assets=declaration['asset_ids']
    sources={objects[s['table']]['asset_id']for p in spec['proposals']for s in p['sources']}
    layers={l['asset_id']:l for l in config.get('_estate',{}).get('layers',[])}
    if not set(assets)<=sources or any(layers.get(a,{}).get('serverless')is not True for a in assets):
        raise ValueError('VERIFICATION_PREWARM_SOURCE_NOT_DECLARED')
    return list(assets)


def preflight(spec,config,context,*,receipt_path,manifest_budgets):
    """Pure retained-input admission; no transport, PG, model or budget seam."""
    # The probe cap alone is insufficient: a stale round, rolling allowance,
    # reserve or daily policy must refuse before publishing a model candidate.
    if spec.get('budgets')!=manifest_budgets:raise ValueError('VERIFICATION_BUDGET_DIFFERS')
    from types import SimpleNamespace
    from investigator.adapters.code_verification import resolve_objects
    from investigator.adapters.retained_endpoints import read
    plan(spec) # shape and conservation validation before retained resolution
    process=SimpleNamespace(config=config,read_endpoint=lambda request:read(config,context,request,receipt_path=receipt_path))
    objects,missing=resolve_objects(process,context,spec['schemas'])
    if missing:raise ValueError('VERIFICATION_PREFLIGHT_OBJECT_RESOLUTION_REFUSED')
    result=plan(spec,config=config,objects=objects)
    assets=prewarm_assets(spec,config,objects)
    return {**result,'budget_match_validated':True,'prewarm_scope_validated':True,'prewarm_asset_ids':assets,
        'resolved_source_asset_ids':sorted({objects[s['table']]['asset_id']for p in spec['proposals']for s in p['sources']})}


def validate_native_window(window):
    if (not isinstance(window,dict) or set(window)!={'seconds','finalization_seconds','demo_seconds'}
            or any(type(v)is not int for v in window.values())
            or not 1<=window['seconds']<=900 or not 30<=window['finalization_seconds']<=600
            or not 0<=window['demo_seconds']<=900):
        raise ValueError('VERIFICATION_NATIVE_WINDOW_BOUND')


def native_inputs(inputs):
    """Start only inside captured execution, after durable pre-read retention.

    Legacy sealed inputs keep their absolute deadline and emit no new event.
    Never mutate the sealed bootstrap; the effective deadline is a local view.
    """
    if 'native_window' not in inputs:return inputs
    from investigator import process_tape as tape
    window=inputs['native_window'];validate_native_window(window)
    started=tape.clock('cloud-verification-native-window-start')
    deadline=min(started+window['seconds'],inputs['deadline']-window['finalization_seconds']-window['demo_seconds'])
    # Leave enough room to start one ordinary bounded request, not merely a
    # positive fraction of a second. Specific pre-warm bounds remain stricter.
    if started+60>deadline:raise ValueError('VERIFICATION_DEADLINE_NO_NATIVE_WINDOW')
    return {**inputs,'deadline':deadline}


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
    i=native_inputs(bootstrap['state']['inputs']);spec=i['verification_spec'];config=bootstrap['config']
    if fingerprint()!=i['engine_fingerprint']:raise ValueError('VERIFIER_ENGINE_DIFFERS')
    planned=plan(spec)
    if planned['verification_reads_needed']>planned['verification_cap']:raise ValueError('VERIFICATION_CAP_INSUFFICIENT')
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
    planned=plan(spec,config=config,objects=objects);record['plan']=planned
    if not planned['admissible']:raise ValueError('VERIFICATION_CAP_INSUFFICIENT')
    try:
        with guard_scope(lambda e:record['guards'].append(e)):
            prewarm_source(spec,config,objects,governor,i,record)
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
    for key in ('manifest','context','endpoints'):parser.add_argument('--'+key,type=Path)
    args=parser.parse_args()
    spec=json.loads(args.plan.read_bytes())
    if spec.get('prewarm') is not None and not all((args.manifest,args.context,args.endpoints)):
        raise ValueError('VERIFICATION_PREWARM_PREFLIGHT_INPUTS_REQUIRED')
    if any((args.manifest,args.context,args.endpoints)):
        if not all((args.manifest,args.context,args.endpoints)):raise ValueError('VERIFICATION_PREFLIGHT_INPUTS_REQUIRED')
        from investigator.estate_manifest import load
        from investigator.adapters.estate_installation import configuration
        manifest=load(args.manifest)
        result=preflight(spec,configuration(manifest),json.loads(args.context.read_bytes()),receipt_path=args.endpoints,
            manifest_budgets=manifest['budgets'])
    else:result=plan(spec)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()

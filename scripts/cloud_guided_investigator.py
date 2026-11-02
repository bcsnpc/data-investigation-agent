"""Installed cloud entry point for IntakeRequest/1 and AI-authored queries."""
import json
import time
from pathlib import Path
from datetime import datetime,timezone
from cloud_investigator import reference,PathCollector


def intake_question_outcome(text, mapped, *, resolution, step_costs, cost,physical_requests=0):
    """Keep the original text bound even when no intake has been admitted."""
    business=mapped.get('question','A named choice is needed before investigation.')
    return {'status':'NEEDS_INPUT','ticket':{'text':text},'business':business,
            'outputs':{'business':business,'technical':json.dumps(mapped)},
            'intake':mapped,'intake_resolution':resolution,'ai_step_costs':step_costs,
            'cost':cost,'physical_requests':physical_requests}


def metadata_tokens(configuration):
    """Use the full installed auth declaration, never its display profile."""
    from investigator.adapters.vault_user_cache import credential,provider
    return provider(credential(configuration['fabric']['auth']))


def specification(options):
    if not isinstance(options,dict) or not {'spec'}<=set(options)<={'spec','ticket'}:
        raise ValueError('GUIDED_RUNNER_OPTIONS')
    value=json.loads(reference(options['spec'],maximum=500000).read_bytes())
    required={'version','ticket','assets','graph','reasoning','max_requests'}
    if not isinstance(value,dict) or not required<=set(value)<=required|{'collector','screenshots','diagnostic_budget','diagnostic_prompt_cache','ai_routing','intake_cascade','investigator_cascade'} or value['version']!='guided-investigation/1':
        raise ValueError('GUIDED_RUNNER_SPECIFICATION')
    if 'intake_cascade' in value and type(value['intake_cascade'])is not bool:raise ValueError('INTAKE_CASCADE_BOOLEAN_REQUIRED')
    if 'investigator_cascade' in value and type(value['investigator_cascade'])is not bool:raise ValueError('INVESTIGATOR_CASCADE_BOOLEAN_REQUIRED')
    if type(value['max_requests']) is not int or not 1<=value['max_requests']<=100:
        raise ValueError('GUIDED_PHYSICAL_REQUEST_BOUND')
    graph=value['graph']
    if set(graph)!={'estate','identity','allowed_objects'} or not isinstance(graph['allowed_objects'],list):
        raise ValueError('GUIDED_GRAPH_SCOPE')
    reason=value['reasoning']
    from investigator.adapters.provider_runtime import validate
    validate(reason)
    if 'diagnostic_budget' in value and value['diagnostic_budget']!={'label':'UNSCORED_STATIC_DIAGNOSTIC','actual_usage_limit_microdollars':3000000}:
        raise ValueError('GUIDED_OWNER_DIAGNOSTIC_BUDGET_REQUIRED')
    if 'diagnostic_prompt_cache'in value and value['diagnostic_prompt_cache']is not True:
        raise ValueError('GUIDED_OWNER_DIAGNOSTIC_CACHE_REQUIRED')
    if 'ticket' in options:value['ticket']=options['ticket']
    return value


def execute(plan,context):
    from investigator.normal_audit import normal_context
    from investigator.build_phase import operating_mode
    from investigator.run_timing import GuidedTiming
    with operating_mode(category='INVESTIGATION'),normal_context(context,plan.get('run_id','guided')) as audit:
        timed=GuidedTiming(audit)
        return timed.finish(run(plan,timed))


def run(plan,context):
    from investigator.shared_state import configured_state
    from investigator.estate_manifest import load
    from investigator.adapters.estate_installation import configuration
    from investigator.estate_graph_api import GraphAPI
    from investigator.estate_graph_repository import GraphRepository
    from investigator.live_gateway import current
    from investigator.facts_ledger import FactLedger
    from investigator.physical_reads import guard_scope,scope
    from investigator.guided_cases import Cases
    from investigator.guided_intake import Catalog
    from investigator.guided_text_resolver import Resolver
    from investigator.guided_investigator_installation import Factory
    from investigator.guided_live_facts import PathFacts
    from investigator.adapters.ai_native_catalog import NativeCatalog
    from investigator.adapters.investigative_native import NativeQueries
    from investigator.adapters.provider_runtime import client as provider_client
    from investigator.reasoning_budget import RateCard,TicketBudget
    from scan_estate_graph import Meter
    from investigator.usage_governance import UsageHold
    from investigator.round23_calendar import require_live_window
    require_live_window()
    started=time.monotonic();phases=[]
    spec=specification(plan['options']);manifest=load(plan['manifest'])
    config=configuration(manifest)
    state=configured_state()
    if state is None or state.backend!='postgresql':raise ValueError('GUIDED_SHARED_STATE_REQUIRED')
    if manifest.get('recording',{}).get('tape_class','EXACT')!='EXACT':
        raise ValueError('GUIDED_PROJECTED_STORAGE_NOT_INSTALLED_NO_RAW_FALLBACK')
    root=Path(context.root);root.mkdir(parents=True,exist_ok=True)
    ai_usage=[]
    def record(value):
        if value.get('event')=='AI_NORMALIZED_USAGE':ai_usage.append(value)
        return context.record('guided-case-event',value)
    from investigator.ai_cost_report import summarize as step_costs
    intake_resolution=None
    graph_spec=spec['graph']
    graph=GraphAPI(GraphRepository(state),current(),identity=graph_spec['identity'],estate=graph_spec['estate'],
                   allowed_objects=graph_spec['allowed_objects'],max_nodes=200,max_edges=500,max_bytes=256000)
    from investigator.slim_recording import CONFIG_ENV,validate
    import os
    storage=validate(json.loads(Path(os.environ[CONFIG_ENV]).read_bytes()))
    from investigator.adapters.blob_artifacts import recording_stores
    from investigator.graph_definitions import DefinitionSink
    files,_=recording_stores(storage)
    graph.definition_reader=DefinitionSink(files,storage['account_url']+'/snapshots',recording_class='EXACT',scratch=root).read
    submitted=json.loads(reference(spec['ticket'],maximum=250000).read_bytes())
    retained=json.loads(reference(spec['assets'],maximum=64*1024*1024).read_bytes())
    assets=retained['assets'] if isinstance(retained,dict) else retained
    if isinstance(retained,dict):assets=[*assets,*retained.get('native_relation_witnesses',[])]
    if isinstance(retained,dict) and retained.get('graph'):
        from investigator.adapters.estate_graph_static import retained_native_relation_assets
        extra=retained_native_relation_assets(retained,observed_at=retained.get('created'))
        known={a['id'] for a in assets};assets=[*assets,*[a for a in extra if a['id'] not in known]]
    catalog=Catalog.from_graph(graph)
    # Only names/containment cross the catalog boundary. Raw definitions are
    # obtained for the actual selected path, not the historical catalog.
    collector=None;collector_config=None
    if 'collector' in spec:
        collector_config=json.loads(reference(spec['collector'],maximum=500000).read_bytes())
        collector=PathCollector(collector_config,state,
                                graph_spec['allowed_objects'],record)
    def ai_configuration(step):
        if 'ai_routing' not in spec:return spec['reasoning']
        from investigator.adapters.provider_runtime import select
        return select(spec['ai_routing'],tenant=graph_spec['estate'],step=step)
    investigator_configuration = ai_configuration('INVESTIGATOR')
    rate=RateCard(model=investigator_configuration['model'],**investigator_configuration['rate_card'])
    budgets={}
    def budget(case_id,step='INVESTIGATOR'):
        selected=ai_configuration(step)
        key=(case_id,step,selected.get('provider','anthropic'),selected['model'])
        if key not in budgets:
            budgets[key]=TicketBudget(state,case_id=case_id,owner=selected['worker_identity'],
                rate=RateCard(model=selected['model'],**selected['rate_card']),
                provider=selected.get('provider','anthropic'),purpose=step,
                actual_usage_limit=spec.get('diagnostic_budget',{}).get('actual_usage_limit_microdollars',3000000))
        return budgets[key]
    def model(case_id,step='INVESTIGATOR'):
        return provider_client(ai_configuration(step),budget=budget(case_id,step),record=record,
                      diagnostic_prompt_cache=spec.get('diagnostic_prompt_cache',True))
    request_key=plan.get('run_id',getattr(context,'run_id',root.name))
    from investigator.estate_graph_contract import digest
    case_id='guided:'+digest([graph_spec['estate'],request_key])
    pending_intake = None
    initial_intake_queries=[]
    candidate_binding=None
    operational_admission = None
    if set(submitted)=={'text'}:
        from investigator.operational_intake import admit as admit_operational
        admission = admit_operational(submitted, {'candidates': list(catalog.nodes.values())})
        if admission['status'] == 'READY':operational_admission = admission
    if set(submitted)=={'text'} and operational_admission is None:
        if spec.get('intake_cascade'):
            from investigator.intake_cascade import Cascade
            mapped=Cascade(catalog=catalog,first_model=model(case_id,'INTAKE'),
                fallback_model=lambda:model(case_id,'INTAKE_FALLBACK'),record=record).resolve(submitted['text'])
        else:mapped=Resolver(catalog=catalog,model=model(case_id,'INTAKE'),record=record).resolve(submitted['text'])
        intake_resolution=mapped.get('intake_cascade')
        record({'event':'GUIDED_INTAKE_ADMISSION','status':mapped['status'],
                'resolution':intake_resolution,'confidence':mapped.get('resolution_confidence')})
        if mapped['status']!='READY':
            from investigator.guided_intake_candidates import inventory as candidate_inventory
            if not candidate_inventory(submitted['text'],mapped,catalog):
                return intake_question_outcome(submitted['text'],mapped,resolution=intake_resolution,
                    step_costs=step_costs(ai_usage),cost=budget(case_id).status())
            pending_intake=mapped
        else:submitted={'intake':mapped['intake'],'source':mapped['source']}
    if pending_intake is None and operational_admission is None and (not isinstance(submitted,dict) or not {'intake'}<=set(submitted)<={'intake','source'}):
        raise ValueError('GUIDED_TICKET_ENVELOPE')
    meter=Meter(state,{'environment':manifest['environment']},spec['max_requests'],reporting_mirror=False,enforce_limit=True)
    def physical(kind,call):
        if meter.used>=spec['max_requests']:raise UsageHold('GUIDED_PHYSICAL_CAP_REACHED')
        return meter(call)
    def metered(call):
        with scope(physical):return physical('guided-native',call)
    def sql_read(settings,database,request):
        from fabric_sql_surface import read
        return metered(lambda:read(settings,database,request))
    from metadata_auth import MetadataHttp
    http=MetadataHttp(metadata_tokens(config),meter=metered)
    endpoint_cache={}
    def endpoint(container):
        if container['id'] not in endpoint_cache:
            workspace,item=container['id'].removeprefix('fabric://').split('/')
            plural='lakehouses' if container['kind']=='Lakehouse' else 'warehouses'
            response=http('workspaces/'+workspace+'/'+plural+'/'+item)
            if response['status_code']!=200:raise ValueError('NATIVE_ENDPOINT_METADATA_UNAVAILABLE')
            endpoint_cache[container['id']]=response['text']
            record({'event':'NATIVE_ENDPOINT_METADATA','asset_id':container['id'],'response':response})
        return endpoint_cache[container['id']]
    from run_source_diagnostic import transport as source_transport
    native_catalog=NativeCatalog.from_graph(graph,assets=assets,configuration=config,
                                  endpoint=endpoint,sql_read=sql_read,record=record,
                                  source_read=lambda settings,q:metered(lambda:source_transport(settings,q)))
    native=NativeQueries(native_catalog.routes)
    from investigator.adapters.guided_security import Security
    security=Security(assets=assets,nodes=list(native_catalog.graph_nodes.values()),http=http)
    def execute_native(layer,bound,**kwargs):return metered(lambda:native(layer,bound,**kwargs))
    # Factory updates this installed registry after a native schema lookup.
    execute_native.routes=native.routes
    ledger=FactLedger(state);fact_ports={}
    def triage(path,identity):
        port=PathFacts(ledger=ledger,estate=graph_spec['estate'],path=path,
            collector=history_reader.top_up if history_reader else collector,save=record)
        fact_ports[identity]=port
        return port
    history_reader=None
    if collector_config:
        from investigator.guided_runtime_reads import SubjectHistory
        from investigator.adapters.scanner_refresh import RefreshHttp
        retained_history=DefinitionSink(files,storage['account_url']+'/snapshots',recording_class='EXACT',scratch=root)
        def history_sql(route,request):
            settings=collector_config.get('sql_configs',{}).get(route.get('reader'))
            if settings is None:raise ValueError('FACT_DECLARED_SQL_READER_ABSENT')
            if settings['fabric']['sql_reader']['server']!=route['connection']:raise ValueError('FACT_SQL_DECLARED_CONNECTION_DIFFERS')
            return sql_read(settings,route['database'],request)
        refresh_http=(RefreshHttp(collector_config['refresh_authentication'],collector_config['subjects'],meter=metered)
            if 'refresh_authentication' in collector_config else None)
        history_reader=SubjectHistory(subjects=collector_config['subjects'],allowed=graph.allowed,
            http=http,retain=retained_history,sql=history_sql,refresh_http=refresh_http,
            now=lambda:datetime.now(timezone.utc).isoformat(),ledger=ledger,estate=graph_spec['estate'])
    def history(node,kinds):
        if history_reader:return history_reader(node,kinds)
        return next(iter(fact_ports.values())).history(node,kinds)
    if operational_admission is not None:
        from investigator.operational_fastpath import run as operational_run
        def operational_history(node, kinds):
            if history_reader:return history_reader(node, kinds)
            return {'status': 'UNAVAILABLE', 'reason': 'Native subject history is not configured.', 'facts': []}
        try:
            result = operational_run(operational_admission, operational_history, record=record,
                history_for_selector=(lambda node,kinds,selector,text:history_reader(node,kinds,selector=selector,text=text))if history_reader else None)
            result.update(ticket=submitted, physical_requests=meter.used,
                          timing={'wall_seconds':time.monotonic()-started},
                          outputs={'business':result['business'],'technical':json.dumps(result.get('technical',result.get('history',{})))})
            context.record('guided-investigator-result',result)
            return result
        finally:meter.close()
    def screenshot_reader(case_id,checksum):
        if checksum not in spec.get('screenshots',{}):raise ValueError('SCREENSHOT_ATTACHMENT_NOT_INSTALLED')
        image=reference(spec['screenshots'][checksum],maximum=1024*1024).read_bytes()
        if __import__('hashlib').sha256(image).hexdigest()!=checksum:raise ValueError('SCREENSHOT_ATTACHMENT_HASH_DIFFERS')
        return image
    def check_candidate_origin(origin,intake,actual_catalog):
        from investigator.guided_intake_candidates import check_origin
        return check_origin(origin,intake,actual_catalog,candidate_binding)
    factory=Factory(state=state,graph=graph,routes=native_catalog.routes,native=execute_native,
        intake_queries=lambda case:initial_intake_queries if candidate_binding and case['intake'].get('measure')==candidate_binding['intake']['measure']else[],
        intake_origin_checker=check_candidate_origin,
        context_for=native_catalog.context,triage_for=triage,model_for=model,
        model_for_step=model,
        investigator_cascade=spec.get('investigator_cascade',False),
        prepare_route=native_catalog.prepare,begin_case=native_catalog.opened.clear,candidate_details=native_catalog.candidate_details,
        screenshot_reader=screenshot_reader,
        security_definitions=security,
        declared_continuations=native_catalog.declared_continuations,
        associated_nodes=native_catalog.associated_nodes,
        definition_for=native_catalog.definition,
        reserve=lambda *_:None,persist=lambda _,event:record(event),
        job_runs=lambda node:history(node,{'JOB_RUN','RUN_HISTORY','SCHEDULE','TABLE_LOAD'}),
        refresh_history=lambda node:history(node,{'REFRESH_RUN','REFRESH_STATE','SCHEDULE','RUN_HISTORY'}))
    if pending_intake is not None:
        from investigator.guided_intake_candidates import resolve as resolve_candidates
        from investigator.investigative_queries import Queries
        from investigator.model_spend import SpendHold
        from investigator.live_gateway import GatewayDenied
        from investigator.planner_recording import _safe
        from investigator.guided_intake_candidates import probe_measure
        def probe_candidate(measure,proposal):
            return probe_measure(factory,catalog,measure,proposal,execute_native,record,initial_intake_queries)
        try:
            with guard_scope(record):mapped=resolve_candidates(submitted['text'],pending_intake,catalog,probe_candidate,record=record)
        except BaseException:
            meter.close();raise
        if mapped['status']!='READY':
            try:return intake_question_outcome(submitted['text'],mapped,resolution=intake_resolution,
                step_costs=step_costs(ai_usage),cost=budget(case_id).status(),physical_requests=meter.used)
            finally:meter.close()
        candidate_binding=mapped
        submitted={'intake':mapped['intake'],'source':mapped['source']}
    phases.append({'phase':'startup-and-intake','seconds':time.monotonic()-started})
    try:
        with guard_scope(record):
            cases=Cases(state=state,graph=graph,estate=graph_spec['estate'],engine_factory=factory)
            queued=cases.submit({'request_key':request_key,**submitted})
            investigated=time.monotonic();result=cases.run(queued['id'])
            phases.append({'phase':'triage-and-investigation','seconds':time.monotonic()-investigated})
        outcome=result['outcome']
        if candidate_binding and isinstance(outcome.get('business'),str):
            outcome['business']='Assumption: '+candidate_binding['resolution_assumption']+' '+outcome['business']
        output={**outcome,'ticket':submitted['intake'],'case_id':queued['id'],
                'intake_resolution':intake_resolution,'ai_step_costs':step_costs(ai_usage),
                'physical_requests':meter.used,'budget_before':meter.before,'budget_after':meter.usage.snapshot(),
                'cost':budget(case_id).status(),'timing':{**outcome.get('timing',{}),'wall_seconds':time.monotonic()-started,'phases':phases},
                'outputs':{'business':outcome['business'],'technical':json.dumps(outcome.get('technical',outcome.get('handoff',{})),ensure_ascii=False)}}
        context.record('guided-investigator-result',output)
        return output
    finally:meter.close()

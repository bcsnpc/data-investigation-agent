"""Installed cloud entry point for IntakeRequest/1 and AI-authored queries."""
import json
import time
from pathlib import Path
from datetime import datetime,timezone
from cloud_investigator import reference,PathCollector


def metadata_tokens(configuration):
    """Use the full installed auth declaration, never its display profile."""
    from investigator.adapters.vault_user_cache import credential,provider
    return provider(credential(configuration['fabric']['auth']))


def specification(options):
    if not isinstance(options,dict) or not {'spec'}<=set(options)<={'spec','ticket'}:
        raise ValueError('GUIDED_RUNNER_OPTIONS')
    value=json.loads(reference(options['spec'],maximum=500000).read_bytes())
    required={'version','ticket','assets','graph','reasoning','max_requests'}
    if not isinstance(value,dict) or not required<=set(value)<=required|{'collector','screenshots'} or value['version']!='guided-investigation/1':
        raise ValueError('GUIDED_RUNNER_SPECIFICATION')
    if type(value['max_requests']) is not int or not 1<=value['max_requests']<=100:
        raise ValueError('GUIDED_PHYSICAL_REQUEST_BOUND')
    graph=value['graph']
    if set(graph)!={'estate','identity','allowed_objects'} or not isinstance(graph['allowed_objects'],list):
        raise ValueError('GUIDED_GRAPH_SCOPE')
    reason=value['reasoning']
    if set(reason)!={'model','rate_card','secret_reference','gateway_identity','worker_identity'}:
        raise ValueError('GUIDED_REASONING_CONFIGURATION')
    if 'ticket' in options:value['ticket']=options['ticket']
    return value


def execute(plan,context):
    from investigator.normal_audit import normal_context
    from investigator.build_phase import operating_mode
    with operating_mode(category='INVESTIGATION'),normal_context(context,plan.get('run_id','guided')) as audit:
        return run(plan,audit)


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
    from investigator.adapters.reasoning_anthropic import Client
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
    def record(value):return context.record('guided-case-event',value)
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
        extra=retained_native_relation_assets(retained,observed_at=retained['created'])
        known={a['id'] for a in assets};assets=[*assets,*[a for a in extra if a['id'] not in known]]
    catalog=Catalog.from_graph(graph)
    # Only names/containment cross the catalog boundary. Raw definitions are
    # obtained for the actual selected path, not the historical catalog.
    metadata=graph.intake_catalog()
    collector=None
    if 'collector' in spec:
        collector=PathCollector(json.loads(reference(spec['collector'],maximum=500000).read_bytes()),state,
                                graph_spec['allowed_objects'],record)
    rate=RateCard(model=spec['reasoning']['model'],**spec['reasoning']['rate_card'])
    budgets={}
    def budget(case_id):
        if case_id not in budgets:
            budgets[case_id]=TicketBudget(state,case_id=case_id,owner=spec['reasoning']['worker_identity'],rate=rate)
        return budgets[case_id]
    def model(case_id):
        return Client(model=rate.model,budget=budget(case_id),identity=spec['reasoning']['gateway_identity'],
                      secret_reference=spec['reasoning']['secret_reference'],record=record)
    request_key=plan.get('run_id',getattr(context,'run_id',root.name))
    from investigator.estate_graph_contract import digest
    case_id='guided:'+digest([graph_spec['estate'],request_key])
    if set(submitted)=={'text'}:
        mapped=Resolver(catalog=catalog,model=model(case_id),record=record).resolve(submitted['text'])
        if mapped['status']!='READY':
            business=mapped.get('question','A named choice is needed before investigation.')
            return {'status':'NEEDS_INPUT','business':business,'outputs':{'business':business,'technical':json.dumps(mapped)},
                    'intake':mapped,'cost':budget(case_id).status(),'physical_requests':0}
        submitted={'intake':mapped['intake'],'source':mapped['source']}
    if not isinstance(submitted,dict) or not {'intake'}<=set(submitted)<={'intake','source'}:
        raise ValueError('GUIDED_TICKET_ENVELOPE')
    meter=Meter(state,{'environment':manifest['environment']},spec['max_requests'],reporting_mirror=False)
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
    native_catalog=NativeCatalog(assets=assets,graph_nodes=metadata['nodes'],configuration=config,
                                  endpoint=endpoint,sql_read=sql_read,record=record,
                                  source_read=lambda settings,q:metered(lambda:source_transport(settings,q)))
    native=NativeQueries(native_catalog.routes)
    from investigator.adapters.guided_security import Security
    security=Security(assets=assets,nodes=metadata['nodes'],http=http)
    def execute_native(layer,bound,**kwargs):return metered(lambda:native(layer,bound,**kwargs))
    # Factory updates this installed registry after a native schema lookup.
    execute_native.routes=native.routes
    ledger=FactLedger(state);fact_ports={}
    def triage(path,identity):
        port=PathFacts(ledger=ledger,estate=graph_spec['estate'],path=path,collector=collector,save=record)
        fact_ports[identity]=port
        return port
    def history(node,kinds):
        return next(iter(fact_ports.values())).history(node,kinds)
    def screenshot_reader(case_id,checksum):
        if checksum not in spec.get('screenshots',{}):raise ValueError('SCREENSHOT_ATTACHMENT_NOT_INSTALLED')
        image=reference(spec['screenshots'][checksum],maximum=1024*1024).read_bytes()
        if __import__('hashlib').sha256(image).hexdigest()!=checksum:raise ValueError('SCREENSHOT_ATTACHMENT_HASH_DIFFERS')
        return image
    factory=Factory(state=state,graph=graph,routes=native_catalog.routes,native=execute_native,
        context_for=native_catalog.context,triage_for=triage,model_for=model,
        prepare_route=native_catalog.prepare,begin_case=native_catalog.opened.clear,candidate_details=native_catalog.candidate_details,
        screenshot_reader=screenshot_reader,
        security_definitions=security,
        declared_continuations=native_catalog.declared_continuations,
        reserve=lambda *_:None,persist=lambda _,event:record(event),
        job_runs=lambda node:history(node,{'JOB_RUN','RUN_HISTORY','SCHEDULE','TABLE_LOAD'}),
        refresh_history=lambda node:history(node,{'REFRESH_RUN','REFRESH_STATE','SCHEDULE','RUN_HISTORY'}))
    phases.append({'phase':'startup-and-intake','seconds':time.monotonic()-started})
    try:
        with guard_scope(record):
            cases=Cases(state=state,graph=graph,estate=graph_spec['estate'],engine_factory=factory)
            queued=cases.submit({'request_key':request_key,**submitted})
            investigated=time.monotonic();result=cases.run(queued['id'])
            phases.append({'phase':'triage-and-investigation','seconds':time.monotonic()-investigated})
        outcome=result['outcome']
        output={**outcome,'ticket':submitted['intake'],'case_id':queued['id'],
                'physical_requests':meter.used,'budget_before':meter.before,'budget_after':meter.usage.snapshot(),
                'cost':budget(case_id).status(),'timing':{'wall_seconds':time.monotonic()-started,'phases':phases},
                'outputs':{'business':outcome['business'],'technical':json.dumps(outcome.get('technical',outcome.get('handoff',{})),ensure_ascii=False)}}
        context.record('guided-investigator-result',output)
        return output
    finally:meter.close()

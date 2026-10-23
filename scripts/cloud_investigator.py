"""Trusted cloud adapter for the single ledger investigator; no dynamic imports."""
import json
import hashlib
import shutil
import time
import os
from pathlib import Path
from investigator.ledger_investigator_tools import Tools
from investigator.ledger_investigator import Investigator


def run(plan,context,*,graph,ledger,value_reader,decide,admit,collector=None,checks=None,now,recording_class='EXACT'):
    """Root's registry supplies installed guarded ports, never the ticket/model.

    No refresh/run/write handler exists. In particular, value_reader must be a
    compiler-backed gateway read using the admitted graph identifiers.
    """
    options=plan['options'];ticket=json.loads(Path(options['ticket']).read_bytes())
    def persist(value):
        reference=context.record('investigator-event',value)
        return reference['key']
    tools=Tools(graph,ledger,visual=ticket.get('visual') or ticket['request']['subject'],key=ticket.get('key'),context=ticket.get('filters',{}),
        comparison=ticket.get('comparison'),persist=persist,now=now,value_reader=value_reader,collector=collector,checks=checks,request_kind=ticket.get('request',{}).get('kind','COMPARE'),recording_class=recording_class)
    tools.estate=plan.get('estate')
    from investigator.process_tape import utc_now
    tools.availability_clock=utc_now
    engine=Investigator(tools,decide=decide,persist=persist,admit=admit,step_cap=options.get('step_cap',12),wall_seconds=options.get('wall_seconds',900),
        progress=lambda value:context.progress(value)if hasattr(context,'progress')else context.record('progress',value))
    invoke=lambda:engine.run(ticket,warnings=options.get('warnings',[]))
    result=context.step('investigation',invoke)if hasattr(context,'step')else invoke()
    # JSON run bundle is persisted through the normal outer capture before return.
    context.record('investigator-bundle',result)
    return result


def reference(value,*,maximum=1_500_000_000):
    """Hash pinned inputs as streams; never read a historical database in RAM."""
    if not isinstance(value,dict) or set(value)!={'path','sha256'}:raise ValueError('INVESTIGATOR_INPUT_REFERENCE')
    path=Path(value['path'])
    if not path.is_file() or path.is_symlink() or path.stat().st_size>maximum:raise ValueError('INVESTIGATOR_INPUT_BOUND')
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
    if digest.hexdigest()!=value['sha256']:raise ValueError('INVESTIGATOR_INPUT_HASH_DIFFERS')
    return path


def specification(options):
    if not {'spec'}<=set(options)<={'spec','ticket'}:raise ValueError('INVESTIGATOR_RUNNER_OPTIONS')
    spec=json.loads(reference(options['spec'],maximum=250000).read_bytes())
    if 'ticket'in options:
        reference(options['ticket'],maximum=250000)
        spec['ticket']=dict(options['ticket'])
    required={'ticket','graph','budget','max_requests','model_enabled','generation_options','step_cap','wall_seconds','warnings'}
    if not isinstance(spec,dict) or not required<=set(spec)<=required|{'native','collector','retained_continuation','recording_mode'}:raise ValueError('INVESTIGATOR_SPEC_FIELDS')
    from investigator.normal_audit import mode
    mode(spec.get('recording_mode','NORMAL'))
    if 'retained_continuation' in spec and 'native' not in spec:raise ValueError('RETAINED_CONTINUATION_NATIVE_REQUIRED')
    graph=spec['graph']
    if (not isinstance(graph,dict) or set(graph)!={'estate','identity','allowed_objects'}
            or not isinstance(graph['allowed_objects'],list) or not 1<=len(graph['allowed_objects'])<=200
            or len(set(graph['allowed_objects']))!=len(graph['allowed_objects'])):raise ValueError('INVESTIGATOR_GRAPH_SCOPE')
    if type(spec['model_enabled'])is not bool or type(spec['max_requests'])is not int or not 1<=spec['max_requests']<=100:
        raise ValueError('INVESTIGATOR_REQUEST_ALLOWANCE')
    if type(spec['step_cap'])is not int or not 1<=spec['step_cap']<=25 or type(spec['wall_seconds'])is not int or not 1<=spec['wall_seconds']<=3600:
        raise ValueError('INVESTIGATOR_STEP_OR_DEADLINE_BOUND')
    from investigator.generation_policy import validate
    validate(spec['generation_options'])
    if not isinstance(spec['warnings'],list) or any(not isinstance(v,str) for v in spec['warnings']):raise ValueError('INVESTIGATOR_WARNING_LABELS')
    return spec


def retained_view(current,process,spec,*,context,visual,measure_id):
    """Trusted opt-in, separate from current graph discovery and its refusals."""
    if 'retained_continuation' not in spec:return current,[]
    from investigator.adapters.retained_graph_continuation import RetainedApprovedContinuation
    view=RetainedApprovedContinuation(current,process,context=context,pin=spec['retained_continuation'],
                                      visual=visual,measure_id=measure_id)
    return view,list(view.warning_labels)


def compiled_values(process,path,*,visual,measure_id,retain):
    """A named unavailable definition is a retained gap, not a lost run.

    An invalid target/measure binding still refuses. Only the graph consumer's
    recorded unavailable-owner state can explain why its path omits the measure.
    No replacement node or native read is selected in that case.
    """
    from investigator.adapters.ledger_investigator_ports import ProcessValues,ProcessChecks
    try:
        values=ProcessValues(process,graph_slice=path,visual=visual,measure_id=measure_id,retain=retain)
    except ValueError as error:
        if str(error)!='EXACT_MEASURE_GRAPH_BINDING_REQUIRED' or not path.get('unavailable_owners'):raise
        gap={'reason':'CURRENT_GRAPH_DEFINITION_OWNER_UNAVAILABLE','stops':path.get('stops',[]),
             'owners':sorted(path['unavailable_owners']),'native_value_queries':0}
        retain({'event':'INVESTIGATOR_NATIVE_PATH_UNAVAILABLE',**gap})
        def unavailable(*args):raise ValueError(gap['reason'])
        return unavailable,None
    return values,ProcessChecks(values)


class JournalGraph:
    """Retain each bounded graph/fact response; replay never queries its source."""
    METHODS=frozenset({'_slice','path_to_source','node_facts','definition_of','freshness','visual_context','filters_on','table_columns','definition_diff','refresh_facts'})
    def __init__(self,graph,*,at=None):self.graph,self.at=graph,at
    def as_of(self,at):return JournalGraph(self.graph,at=at)
    def refresh_facts(self,path,collector,**kwargs):
        from investigator.process_tape import bounded_call
        def live():
            if self.graph is None:raise AssertionError('INVESTIGATOR_REPLAY_GRAPH_IO_FORBIDDEN')
            return self.graph.refresh_facts(path,collector,**kwargs)
        # A trusted producer is a runtime port, never serializable ticket data.
        return bounded_call('ledger-investigator-graph:refresh_facts',{'at':self.at,'path':path,'kwargs':kwargs},live)
    def __getattr__(self,name):
        if name not in self.METHODS:raise AttributeError(name)
        def call(*args,**kwargs):
            from investigator.process_tape import bounded_call
            def live():
                if self.graph is None:raise AssertionError('INVESTIGATOR_REPLAY_GRAPH_IO_FORBIDDEN')
                source=self.graph.as_of(self.at) if self.at else self.graph
                return getattr(source,name)(*args,**kwargs)
            return bounded_call('ledger-investigator-graph:'+name,{'at':self.at,'args':list(args),'kwargs':kwargs},live)
        return call


class PathCollector:
    """Installed metadata top-up restricted to this admitted ticket's subjects."""
    def __init__(self,config,state,allowed,retain):
        from cloud_facts_collector import validate
        self.config=validate(config);self.state=state;self.allowed=frozenset(allowed);self.retain=retain
    def run(self,estate,subjects,*,now,force=False):
        if estate!=self.config['estate'] or not set(subjects)<=self.allowed:raise ValueError('INVESTIGATOR_COLLECTOR_OUTSIDE_PATH')
        selected=sorted(set(subjects)&set(self.config['subjects']))
        missing=sorted(set(subjects)-set(selected))
        if not selected:return {'status':'UNAVAILABLE','subjects':[],'unsupported_subjects':missing,'facts':[]}
        import copy
        from cloud_facts_collector import collect
        from investigator.build_phase import operating_mode
        config=copy.deepcopy(self.config);config['subjects']={key:config['subjects'][key] for key in selected}
        config['key_tables']=[key for key in config.get('key_tables',[]) if key in selected]
        config['max_subjects_per_wake']=len(selected)
        if force:config['list_interval_seconds']=1
        with operating_mode(category='SCAN'):
            result=collect(config,state=self.state,clock=lambda:now,force=force)
        self.retain({'event':'INVESTIGATOR_PATH_FACT_TOP_UP','result':result,'unsupported_subjects':missing})
        return {**result['collection'],'unsupported_subjects':missing,'purpose':'SCAN','physical_requests':result['physical_requests']}


def execute(plan,context):
    from investigator.normal_audit import mode,normal_context
    chosen=mode(specification(plan['options']).get('recording_mode','NORMAL'))
    if chosen=='TEST':return _execute(plan,context)
    with normal_context(context,plan.get('run_id','investigation'))as audit:
        return _execute(plan,audit)


def _execute(plan,context):
    """Installed cloud assembly. No ticket-supplied module, query or identity."""
    from investigator.shared_state import configured_state
    from investigator.estate_manifest import load
    from investigator.adapters.estate_installation import configuration
    from investigator.estate_graph_repository import GraphRepository
    from investigator.estate_graph_api import GraphAPI
    from investigator.facts_ledger import FactLedger
    from investigator.live_gateway import current
    from investigator.adapters.managed_identity import model_session
    from investigator.adapters.ledger_investigator_ports import installed_process,ProcessValues,ProcessChecks,AzureDecision
    from investigator.onboarding import ModelStore,digest
    from investigator.physical_reads import guard_scope,scope
    from investigator import process_tape as journal
    from investigator.runtime import fingerprint
    from investigator.source_revision import committed_revision
    from cloud_graph_interpreter import runtime_governor
    from scan_estate_graph import Meter
    from contextlib import nullcontext
    started=time.monotonic();phases=[]
    spec=specification(plan['options'])
    recording_mode=spec.get('recording_mode','NORMAL')
    if hasattr(context,'progress'):context.progress({'stage':'ACKNOWLEDGED','message':'Investigation received; checking the declared path and current ledger facts.'})
    ticket_path=reference(spec['ticket'],maximum=250000);ticket=json.loads(ticket_path.read_bytes())
    request_kind=ticket.get('request',{}).get('kind','COMPARE')
    if request_kind not in ('FACT','COMPARE','DEFINITION'):raise ValueError('INVESTIGATOR_REQUEST_KIND')
    if request_kind=='COMPARE' and 'native' not in spec:raise ValueError('INVESTIGATOR_NATIVE_INPUT_REQUIRED')
    manifest=load(plan['manifest'])
    if manifest.get('recording',{}).get('tape_class','EXACT')!='EXACT':
        from investigator.privacy_projection import ProjectionError
        raise ProjectionError('LEDGER_INVESTIGATOR_PROJECTED_CAPTURE_NOT_INSTALLED')
    config=configuration(manifest)
    if spec['budget']['environment']!=manifest['environment']:raise ValueError('INVESTIGATOR_BUDGET_ENVIRONMENT_DIFFERS')
    state=configured_state()
    if state is None or state.backend!='postgresql':raise ValueError('INVESTIGATOR_SHARED_POSTGRES_REQUIRED')
    root=Path(context.root);work=root/'ledger-investigator';work.mkdir(parents=True,exist_ok=True)
    governor=runtime_governor(state,manifest['environment'],work)
    graph_spec=spec['graph'];repository=GraphRepository(state)
    graph_live=GraphAPI(repository,current(),identity=graph_spec['identity'],estate=graph_spec['estate'],
                        allowed_objects=graph_spec['allowed_objects'],max_nodes=200,max_edges=500,max_bytes=256000)
    session='ledger-investigator:'+str(journal.uuid4())
    now=journal.utc_now();deadline=time.monotonic()+spec['wall_seconds']
    bootstrap={'entry_point':'ledger_investigator','context_identity':graph_spec['estate']+':'+str(ticket.get('visual') or ticket['request']['subject']),
        'config':config,'profile':{},'usage_policy':governor.policy,'engine_hash':fingerprint(),
        'state':{'engine_revision':committed_revision(),'spec':spec,'session':session,'observed_at':now}}
    tape=journal.Tape(work/'investigator-tape.json',bootstrap=bootstrap)if recording_mode=='TEST' else None
    def retain(value):return context.record('investigator-native',value)
    from investigator.build_phase import operating_mode
    with operating_mode(category='INVESTIGATION'):
        meter=Meter(state,spec['budget'],spec['max_requests'])
    prior_record=os.environ.get('INVESTIGATOR_RECORD_PLANNER');os.environ['INVESTIGATOR_RECORD_PLANNER']='1'if recording_mode=='TEST'else '0'
    try:
        with journal.active(tape),guard_scope(lambda value:context.record('investigator-guard',value)):
            graph=JournalGraph(graph_live);decision=None;values=None;checks=None;collector=None;retained_labels=[]
            def admit(kind,step):
                if time.monotonic()>=deadline:
                    from investigator.usage_governance import UsageHold
                    raise UsageHold('INVESTIGATOR_RUN_DEADLINE')
            if spec['model_enabled'] and request_kind!='FACT':
                decision=AzureDecision(governor,session=session,directory=work/'planner-recordings',retain=retain,options=spec['generation_options'],recording_mode=recording_mode)
            if 'collector' in spec:
                collector=PathCollector(json.loads(reference(spec['collector'],maximum=250000).read_bytes()),state,
                                        graph_spec['allowed_objects'],retain)
            if 'native' in spec:
                native=spec['native']
                if set(native)!={'model','context','catalog','inventory','endpoints','measure_id'}:raise ValueError('INVESTIGATOR_NATIVE_INPUT_FIELDS')
                paths={name:reference(native[name]) for name in ('model','context','catalog','inventory','endpoints')}
                model=json.loads(paths['model'].read_bytes());retained_context=json.loads(paths['context'].read_bytes())
                catalog=work/'catalog.sqlite'
                # Private materialization, with shared accounting still owned by
                # the governor/meter. No copied budget becomes an authority.
                from investigator.ticket_catalog import materialize
                store,catalog_summary=materialize(paths['catalog'],catalog,model=model,context=retained_context,
                    inventory=paths['inventory'],environment=manifest['environment'])
                context.record('ticket-catalog',catalog_summary)
                retained=store.get(model['id'])
                if retained['context_id']!=model['context_id'] or digest(retained['context'])!=digest(model['context']):raise ValueError('INVESTIGATOR_CATALOG_PIN_DIFFERS')
                from investigator.context_search import latest
                if digest(latest(store))!=digest(retained_context):raise ValueError('INVESTIGATOR_ENTERPRISE_CONTEXT_PIN_DIFFERS')
                def physical(kind,call):
                    admit('TOOL',0)
                    if meter.used>=spec['max_requests']:
                        from investigator.usage_governance import UsageHold
                        raise UsageHold('INVESTIGATOR_PHYSICAL_CAP_REACHED')
                    return meter(call)
                def metered(tool,call):
                    admit('TOOL',0)
                    # Logical diagnostics and every actual worker/metadata
                    # request use the same existing physical request authority.
                    with scope(physical):return physical(tool,call)
                from investigator.adapters.retained_endpoints import read as endpoint
                process=installed_process(store,config,model,meter_read=metered,max_boundaries=32,
                    read_endpoint=lambda request:endpoint(config,retained_context,request,receipt_path=paths['endpoints']),
                    judge_definition=decision.judge_definition if decision else None)
                visual=ticket.get('visual') or ticket['request']['subject']
                view,retained_labels=retained_view(graph_live,process,spec,context=retained_context,
                    visual=visual,measure_id=native['measure_id'])
                if view is not graph_live:graph=JournalGraph(view)
                values,checks=compiled_values(process,graph.path_to_source(visual),visual=visual,
                                              measure_id=native['measure_id'],retain=retain)
            phases.append({'phase':'admission_and_path_materialization','wall_seconds':max(0,time.monotonic()-started)})
            investigation_started=time.monotonic()
            call_plan={'estate':graph_spec['estate'],'options':{'ticket':str(ticket_path),'step_cap':spec['step_cap'],'wall_seconds':spec['wall_seconds'],'warnings':[*spec['warnings'],*retained_labels]}}
            settings={**manifest['model']['credential'],'endpoint':manifest['model']['endpoint'],'deployment':manifest['model']['deployment']}
            with model_session(settings) if decision else nullcontext():
                result=run(call_plan,context,graph=graph,ledger=FactLedger(state),value_reader=values,
                           decide=decision,admit=admit,checks=checks,collector=collector,now=now)
            result.update(physical_requests=meter.used,before=meter.before,after=meter.usage.snapshot(),
                          model_calls=decision.calls if decision else 0)
            phases.append({'phase':'investigation','wall_seconds':max(0,time.monotonic()-investigation_started)})
            if recording_mode=='NORMAL':result.setdefault('timing',{})['phases']=phases
            else:context.record('observational-phase-timing',{'not_part_of_semantic_tape':True,'phases':phases})
            result['recording']={'mode':recording_mode,'byte_exact_replay':recording_mode=='TEST'}
            if tape is not None:tape.finish(result)
        if tape is not None:
            from investigator.slim_recording import stores,validate,CONFIG_ENV
            _,files=stores(validate(json.loads(Path(os.environ[CONFIG_ENV]).read_bytes())))
            artifacts={name:files.capture(path) for name,path in [('tape',tape.path),('events',tape.journal_path)] if path.exists()}
            context.record('investigator-tape',{'artifacts':artifacts,'entry_point':'ledger_investigator',
                           'engine_revision':committed_revision(),'original_inputs_unchanged':True})
        if hasattr(context,'progress'):context.progress({'stage':'ANSWER','message':'Investigation finished.','verdict':result.get('verdict'),'status':result.get('status')})
        return result
    finally:
        meter.close()
        if prior_record is None:os.environ.pop('INVESTIGATOR_RECORD_PLANNER',None)
        else:os.environ['INVESTIGATOR_RECORD_PLANNER']=prior_record

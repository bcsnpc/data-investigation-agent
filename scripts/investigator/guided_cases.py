"""Submit/poll for guided cases over existing shared application storage.

An installed engine factory supplies transports/validators; neither tickets nor
HTTP callers can select a Python module, identity or connection. CAS claiming
prevents two workers from executing the same queued case.
"""
from copy import deepcopy
from datetime import datetime,timezone
from .estate_graph_contract import digest
from .guided_intake import Catalog,admit
from .shared_state import StateConflict


class Cases:
    namespace='guided_investigation_cases_v1'

    def __init__(self,*,state,graph,estate,engine_factory,recording_class='EXACT'):
        if recording_class!='EXACT':
            raise ValueError('GUIDED_PROJECTED_STORAGE_NOT_INSTALLED_NO_RAW_FALLBACK')
        if not callable(engine_factory):raise ValueError('INSTALLED_ENGINE_FACTORY_REQUIRED')
        self.state,self.graph,self.estate,self.engine_factory=state,graph,estate,engine_factory

    def submit(self,body):
        if (not isinstance(body,dict) or not {'request_key','intake'}<=set(body)<={'request_key','intake','source'}
                or not isinstance(body['request_key'],str) or not body['request_key']):
            raise ValueError('GUIDED_REQUEST_KEY_AND_INTAKE_REQUIRED')
        catalog=Catalog.from_graph(self.graph)
        admission_error=None
        origin=body.get('source')
        if origin is not None:
            if not isinstance(origin,dict) or set(origin)!={'kind','text','provenance','figure_mentions'} or origin['kind']!='MAPPED_TEXT':
                raise ValueError('MAPPED_TEXT_SOURCE_REQUIRED')
            from .guided_text_resolver import Resolver
            checked=Resolver(catalog=catalog,model=None,record=lambda _:None).check(origin['text'],
                {'proposal':body['intake'],'provenance':origin['provenance'],'figure_mentions':origin['figure_mentions']})
            if checked['status']!='READY':return checked
            resolved=checked
        else:
            try:resolved=admit(body['intake'],catalog)
            except ValueError as error:
                if str(error) not in ('UNKNOWN_REPORT','UNKNOWN_PAGE','PAGE_OUTSIDE_REPORT','VISUAL_OUTSIDE_PAGE','VISUAL_REQUIRES_PAGE'):raise
                admission_error=str(error);resolved=deepcopy(body['intake'])
        identity='guided:'+digest([self.estate,body['request_key']]);fingerprint=digest([body['intake'],origin])
        try:prior=self.state.get(self.namespace,identity)
        except KeyError:prior=None
        if prior:
            if prior['body']['intake_hash']!=fingerprint:raise StateConflict('REQUEST_KEY_DIFFERENT_INTAKE')
            return self.poll(identity)
        value={'id':identity,'estate':self.estate,'intake_hash':fingerprint,'intake':resolved,
               'source':deepcopy(origin) if origin else {'kind':'FORM'},
               'status':'QUEUED','outcome':None,'created_at':datetime.now(timezone.utc).isoformat()}
        if admission_error:
            choices=catalog.reports()
            question={'question':'Which report should I check?','choices':choices,'reason':admission_error}
            outcome={'status':'NEEDS_INPUT','business':question['question'],'question':question,
                'stop':admission_error,'handoff':{'intake':deepcopy(body['intake']),'queries':[],
                    'stopping_point':admission_error,'next_checks':['Resolve the selected target from the catalog choices.'],
                    'catalog_choices':choices,'ruled_out':[]}}
            value.update(status='NEEDS_INPUT',outcome=outcome)
        try:self.state.put(self.namespace,identity,value)
        except StateConflict:
            prior=self.state.get(self.namespace,identity)['body']
            if prior['intake_hash']!=fingerprint:raise
        return self.poll(identity)

    def poll(self,identity):
        saved=self.state.get(self.namespace,identity)
        value=saved['body']
        if value['estate']!=self.estate:raise PermissionError('CASE_OUTSIDE_ESTATE')
        return deepcopy(value)

    def run(self,identity):
        if self.state.mode=='live':
            from .round23_calendar import require_live_window
            require_live_window()
        saved=self.state.get(self.namespace,identity);case=saved['body']
        if case['estate']!=self.estate:raise PermissionError('CASE_OUTSIDE_ESTATE')
        if case['status']!='QUEUED':return self.poll(identity)
        claimed={**case,'status':'RUNNING'}
        try:claim=self.state.put(self.namespace,identity,claimed,revision=saved['revision'])
        except StateConflict:return self.poll(identity)
        engine=None
        try:
            engine=self.engine_factory(deepcopy(claimed))
            outcome=engine.run()
            if not isinstance(outcome,dict) or not outcome.get('status') or not outcome.get('business'):
                raise ValueError('ENGINE_MUST_DELIVER_BUSINESS_OUTCOME')
            finished={**claimed,'status':outcome['status'],'outcome':outcome}
        except Exception as error:
            # Private checkpoints retain precise native/model diagnostics.
            # This lifecycle row does not echo arbitrary exception payloads.
            from .planner_recording import _safe
            message=str(error)
            try:_safe(message.encode())
            except ValueError:message='Details withheld by secret protection'
            handoff={'intake':deepcopy(claimed['intake']),'queries':[],
                'query_history_status':'NOT_ESTABLISHED_BEFORE_ENGINE_INITIALIZATION',
                'lineage_status':'NOT_ESTABLISHED_BEFORE_ENGINE_INITIALIZATION',
                'ruled_out':[],'stopping_point':type(error).__name__+': '+message,
                'next_checks':['Inspect the retained initialization error and native control receipts in this run capture.']}
            if engine is not None:
                context=getattr(engine,'context',None)
                queries=getattr(getattr(engine,'queries',None),'records',None)
                if isinstance(context,dict):handoff.update(context=deepcopy(context),lineage_status='RETAINED_ENGINE_CONTEXT')
                if isinstance(queries,list):handoff.update(queries=deepcopy(queries),query_history_status='RETAINED_ENGINE_QUERY_RECORDS')
            finished={**claimed,'status':'INTERRUPTED','error_type':type(error).__name__,
                      'outcome':{'status':'INTERRUPTED','business':'The investigation did not establish completion; partial case evidence is retained.',
                                 'stop':type(error).__name__+': '+message,'handoff':handoff}}
        self.state.put(self.namespace,identity,finished,revision=claim['revision'])
        return deepcopy(finished)


def install(workspace,*,graph,state,estate,engine_factory,recording_class='EXACT'):
    workspace.guided_graph=graph
    workspace.guided_cases=Cases(state=state,graph=graph,estate=estate,
        engine_factory=engine_factory,recording_class=recording_class)
    return workspace.guided_cases

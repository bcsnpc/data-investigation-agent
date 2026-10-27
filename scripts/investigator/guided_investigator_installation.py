"""Assemble guided cases from trusted installed ports, never ticket callbacks.

The installation owns graph-to-native route bindings, schemas, model/key/budget
factories and read-only collectors. A case only contributes IntakeRequest/1.
"""
from copy import deepcopy
from .ai_investigation import Investigator
from .investigative_queries import Queries
from .investigation_read_tools import ReadTools
from .investigator_checkpoint import SharedStore
from .planner_recording import _safe
from .estate_graph_contract import canonical,digest


class Factory:
    def __init__(self,*,state,graph,routes,native,context_for,triage_for,model_for,
                 reserve,persist,job_runs,refresh_history,security_definitions=None,
                 checkpoint_for=None):
        self.state,self.graph,self.routes=state,graph,deepcopy(routes)
        self.native,self.context_for,self.triage_for,self.model_for=native,context_for,triage_for,model_for
        self.reserve,self.persist=reserve,persist
        self.job_runs,self.refresh_history,self.security=job_runs,refresh_history,security_definitions
        self.checkpoint_for=checkpoint_for or (lambda case_id:SharedStore(state,'ai-query:'+case_id,resume=True))
        for route in self.routes.values():
            if not route.get('path_nodes') or not set(route['path_nodes'])<=graph.allowed:
                raise ValueError('NATIVE_ROUTE_BINDING_OUTSIDE_ADMITTED_GRAPH')

    def __call__(self,case):
        intake=deepcopy(case['intake'])
        root=intake.get('visual') or intake.get('page') or intake['report']
        path=self.graph.path_to_source(root)
        nodes={n['id'] for n in path['nodes']}
        routes={i:r for i,r in self.routes.items() if nodes.intersection(r['path_nodes'])}
        available={i:{'dialect':r['dialect'],'objects':deepcopy(r['objects']),'label':r['label']} for i,r in self.routes.items()}
        layers={i:available[i] for i in routes}
        context=deepcopy(self.context_for(path,intake))
        # A context builder cannot replace the selected target/path/intake.
        context.update(intake=intake,path=deepcopy(path),layers=deepcopy(layers))
        context['route_registry_hash']=digest(self.routes)
        from .facts_ledger import FactLedger
        scope={k:intake[k] for k in ('report','page','visual','details') if k in intake}
        context['engineer_scope']=scope
        context['engineer_replies']=FactLedger(self.state).engineer_replies_for_path(case['estate'],sorted(nodes),scope)
        _safe(canonical(context).encode())
        save=lambda event:self.persist(case['id'],event)
        queries=Queries(layers,execute=self.native,reserve=lambda layer,key:self.reserve(case['id'],layer,key),save=save,
                        available_layers=available)
        def expand(extra):
            ids={n['id'] for n in extra['nodes']}
            return queries.activate([i for i,r in self.routes.items() if ids.intersection(r['path_nodes'])])
        read_tools=ReadTools(graph=self.graph,path=path,queries=queries,intake=intake,
                            job_runs=self.job_runs,refresh_history=self.refresh_history,security_definitions=self.security,
                            candidates=self.graph.intake_catalog(),expand=expand)
        triage=self.triage_for(path,case['id']).run()
        return Investigator(queries=queries,model=self.model_for(case['id']),read_tools=read_tools.registry,
            checkpoint=self.checkpoint_for(case['id']),case_id=case['id'],context=context,triage=triage)

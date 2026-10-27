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
                 checkpoint_for=None,prepare_route=None,begin_case=None,candidate_details=None,screenshot_reader=None,declared_continuations=None):
        self.state,self.graph,self.routes=state,graph,deepcopy(routes)
        self.native,self.context_for,self.triage_for,self.model_for=native,context_for,triage_for,model_for
        self.reserve,self.persist=reserve,persist
        self.prepare_route=prepare_route;self.begin_case=begin_case;self.candidate_details=candidate_details
        self.registry=deepcopy(routes)
        self.screenshot_reader=screenshot_reader
        self.declared_continuations=declared_continuations
        self.job_runs,self.refresh_history,self.security=job_runs,refresh_history,security_definitions
        self.checkpoint_for=checkpoint_for or (lambda case_id:SharedStore(state,'ai-query:'+case_id,resume=True))
        for route in self.routes.values():
            if not route.get('path_nodes') or not set(route['path_nodes'])<=graph.allowed:
                raise ValueError('NATIVE_ROUTE_BINDING_OUTSIDE_ADMITTED_GRAPH')

    def prepare(self, identity, nodes=None):
        if self.prepare_route:
            route=self.prepare_route(identity,nodes)
            if route['path_nodes']!=self.routes[identity]['path_nodes'] or set(route['asset_ids'])!=set(self.routes[identity]['asset_ids']):
                raise ValueError('NATIVE_SCHEMA_PREPARATION_CHANGED_BINDING')
            self.routes[identity]=deepcopy(route)
            if hasattr(self.native,'routes'):self.native.routes[identity]=deepcopy(route)
        return self.routes[identity]

    def target_path(self, intake):
        catalog=self.graph.intake_catalog()
        def associated(path):
            owners={n.get('owner') for n in path['nodes'] if n.get('owner')}
            present={n['id'] for n in path['nodes']}
            additions=[n for n in catalog['nodes'] if n['kind']=='MODEL' and n['id'] not in present
                       and (n.get('owner') in owners or n.get('properties',{}).get('asset_id') in owners)]
            return {**path,'nodes':[*path['nodes'],*additions]}
        if intake.get('visual'):return associated(self.graph.path_to_source(intake['visual']))
        # A record ticket can explicitly name a physical object without
        # naming a visual. Resolve that literal against installed routes;
        # do not expand every visual in its report or silently choose one.
        # Identical qualified names on multiple layers remain candidates.
        import re
        words=canonical({'description':intake.get('description',''),'details':intake.get('details',{})})
        roots=set()
        for route in self.routes.values():
            for obj in route['objects']:
                metadata=obj.get('metadata',{});name=metadata.get('name');schema=metadata.get('schema_name')
                if not name or not schema:continue
                literal=schema+'.'+name
                if not re.search(r'(?<![\w.])'+re.escape(literal)+r'(?![\w.])',words,re.I):continue
                roots.update(n['id'] for n in catalog['nodes']
                    if n.get('kind') in ('TABLE','VIEW') and n.get('properties',{}).get('asset_id')==obj['id'])
        if roots:
            selected={intake['report'],intake.get('page')}
            nodes={n['id']:n for n in catalog['nodes'] if n['id'] in selected};edges={};stops=[];unavailable={};truncated=False
            for root in sorted(roots):
                part=self.graph.path_to_source(root)
                nodes.update({n['id']:n for n in part['nodes']})
                edges.update({e.get('id') or digest(e):e for e in part['edges']})
                stops.extend(part.get('stops',[]));unavailable.update(part.get('unavailable_owners',{}))
                truncated=truncated or part.get('truncated',False)
            return associated({'nodes':list(nodes.values()),'edges':list(edges.values()),'stops':stops,
                'unavailable_owners':unavailable,'truncated':truncated,
                'target_selection':'Explicit qualified objects named by the ticket, matched to installed catalog routes. All matching candidates retained; no visual selected.'})
        from .guided_intake import Catalog
        choices=Catalog(catalog)
        pages=[{'id':intake['page']}] if intake.get('page') else choices.pages(intake['report'])
        visuals=[v for page in pages for v in choices.visuals(intake['report'],page['id'])]
        nodes={n['id']:deepcopy(n) for n in catalog['nodes'] if n['id'] in {intake['report'],*[p['id'] for p in pages]}}
        edges={};stops=[];unavailable={};truncated=False
        for visual in visuals:
            part=self.graph.path_to_source(visual['id'])
            nodes.update({n['id']:n for n in part['nodes']})
            for edge in part['edges']:edges[edge.get('id') or digest(edge)]=edge
            stops.extend(part.get('stops',[]));unavailable.update(part.get('unavailable_owners',{}))
            truncated=truncated or part.get('truncated',False)
        for edge in catalog['edges']:
            if edge['source'] in nodes and edge['target'] in nodes:edges[edge.get('id') or digest(edge)]=edge
        return associated({'nodes':list(nodes.values()),'edges':list(edges.values()),'stops':stops,
                'unavailable_owners':unavailable,'truncated':truncated,
                'target_selection':'Report/page resolved; visual remains optional. Candidate measures are not a selected replacement visual.'})

    def __call__(self,case):
        if self.begin_case:self.begin_case()
        self.routes=deepcopy(self.registry)
        intake=deepcopy(case['intake'])
        root=intake.get('visual') or intake.get('page') or intake['report']
        path=self.target_path(intake)
        # Catalog containment projections need not carry persisted edge IDs.
        # Give those edges a local identity without rewriting retained graph
        # records or losing them from later case-file/handoff composition.
        path={**path,'edges':[deepcopy(e) if e.get('id') else
            {**deepcopy(e),'id':'derived:'+digest(e),'id_basis':'DERIVED_PROJECTED_EDGE_CONTENT'} for e in path['edges']]}
        if self.declared_continuations:
            bridges=self.declared_continuations(path)
            nodes={n['id']:n for n in path['nodes']};edges={e['id']:e for e in path['edges']}
            catalog_nodes={n['id']:n for n in self.graph.intake_catalog()['nodes']}
            for bridge in bridges:
                for root in bridge['graph_nodes']:
                    kind=catalog_nodes.get(root,{}).get('kind')
                    extra=(self.graph.calculation_path(root) if kind in ('PIPELINE','COPY_ACTIVITY','NOTEBOOK','QUERY_STEP')
                        else self.graph.path_to_source(root))
                    nodes.update({n['id']:n for n in extra['nodes']});edges.update({e['id']:e for e in extra['edges']})
            path={**path,'nodes':list(nodes.values()),'edges':list(edges.values()),'declared_route_bridges':bridges}
        nodes={n['id'] for n in path['nodes']}
        routes={i:r for i,r in self.routes.items() if nodes.intersection(r['path_nodes'])}
        for identity in routes:self.prepare(identity,nodes)
        available={i:{'dialect':r['dialect'],'objects':deepcopy(r['objects']),'label':r['label'],
                      **({'endpoint_evidence':deepcopy(r['endpoint_evidence'])} if r.get('endpoint_evidence') else {})}
                   for i,r in self.routes.items()}
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
            selected=[i for i,r in self.routes.items() if ids.intersection(r['path_nodes'])]
            for identity in selected:
                prepared=self.prepare(identity,ids)
                queries.available_layers[identity]={'dialect':prepared['dialect'],'objects':deepcopy(prepared['objects']),'label':prepared['label'],
                    **({'endpoint_evidence':deepcopy(prepared['endpoint_evidence'])} if prepared.get('endpoint_evidence') else {})}
                if identity in queries.layers:queries.layers[identity]=deepcopy(queries.available_layers[identity])
            return queries.activate(selected)
        read_tools=ReadTools(graph=self.graph,path=path,queries=queries,intake=intake,
                            job_runs=self.job_runs,refresh_history=self.refresh_history,security_definitions=self.security,
                            candidates=(self.candidate_details(self.graph.intake_catalog()) if self.candidate_details else self.graph.intake_catalog()),expand=expand)
        triage=self.triage_for(path,case['id']).run()
        model=self.model_for(case['id'])
        def registry():
            tools=read_tools.registry()
            if intake.get('screenshot') and self.screenshot_reader:
                from .screenshot_record_lookup import ScreenshotLookup
                from .adapters.screenshot_assistance import Assistance
                from .guided_intake import Catalog
                from .ai_investigation import schema
                assistance=Assistance(model,lambda:{**context,'layers':deepcopy(queries.layers)})
                lookup=ScreenshotLookup(catalog=Catalog.from_graph(self.graph),queries=queries,
                    extract=assistance.extract,plan=assistance.plan,audit=save)
                def resolve(_):
                    image=self.screenshot_reader(case['id'],intake['screenshot']['sha256'])
                    if __import__('hashlib').sha256(image).hexdigest()!=intake['screenshot']['sha256']:
                        raise ValueError('SCREENSHOT_ATTACHMENT_HASH_DIFFERS')
                    return lookup.resolve(image,intake)
                tools['lookup_screenshot']={'description':'Resolve the attached screenshot to an actual native key; image stays within this case. Queries and vision share this case budget.',
                                            'schema':schema({}),'run':resolve}
            return tools
        return Investigator(queries=queries,model=model,read_tools=registry,
            checkpoint=self.checkpoint_for(case['id']),case_id=case['id'],context=context,triage=triage)

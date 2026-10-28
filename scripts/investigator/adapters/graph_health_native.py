"""Offline health of the production route builder using retained native addresses."""
from copy import deepcopy
from collections import defaultdict,deque
from ..estate_graph_contract import digest
from .ai_native_catalog import NativeCatalog
from .estate_installation import configuration
from ..guided_investigator_installation import Factory
from ..graph_health import analyze


def effective(snapshot,assets,manifest):
    nodes={n['id']:deepcopy(n)for n in snapshot['nodes']};edges={e.get('id')or digest(e):deepcopy(e)for e in snapshot['edges']}
    byasset=defaultdict(list)
    for n in nodes.values():byasset[n.get('properties',{}).get('asset_id')].append(n['id'])
    def link(source,target,proof):
        for a in byasset[source]:
            for b in byasset[target]:
                key=digest([a,b,proof]);edges[key]={'id':key,'source':a,'target':b,'kind':'COMPUTED_FROM','confidence':'DECLARED','provenance':proof}
    known={a['id']:a for a in assets}
    for a in assets:
        parent=known.get(a.get('parent_id'),{})
        if a['kind']in ('SemanticColumn','SqlColumn','LakehouseColumn','WarehouseColumn')and parent.get('kind')in ('SemanticTable','SqlObject','LakehouseTable','WarehouseTable'):
            link(a['id'],parent['id'],{'basis':'EXACT_NATIVE_PARENT_ADDRESS','asset_id':a['id'],'content_hash':a.get('content_hash')})
    class Snapshot:
        allowed=set(nodes)
        def intake_catalog(self):return {'nodes':list(nodes.values()),'edges':list(edges.values())}
        def path_to_source(self,root):
            seen=set();queue=deque([root]);selected={}
            while queue:
                current=queue.popleft()
                if current in seen:continue
                if current not in nodes:continue
                seen.add(current)
                for key,e in list(edges.items()):
                    if e['source']==current and e['kind']not in ('CONTAINS','INTERACTS_WITH'):
                        selected[key]=e;queue.append(e['target'])
            return {'nodes':[nodes[k]for k in seen],'edges':list(selected.values()),'stops':[]}
        calculation_path=path_to_source
    graph=Snapshot()
    def forbidden(*a,**k):raise AssertionError('GRAPH_HEALTH_IS_OFFLINE_NO_NATIVE_READ')
    native=NativeCatalog(assets=assets,graph_nodes=list(nodes.values()),configuration=configuration(manifest),endpoint=forbidden,sql_read=forbidden,record=forbidden)
    factory=Factory.__new__(Factory);factory.graph=graph;factory.associated_nodes=native.associated_nodes;factory.declared_continuations=native.declared_continuations
    def declared_links(bridge):
        proof={'basis':'PRODUCTION_DECLARED_ROUTE_BRIDGE','declaration':deepcopy(bridge)}
        if 'semantic_table'in bridge:
            link(bridge['semantic_table'],bridge['physical_table'],proof)
            for binding in bridge.get('column_bindings',[]):link(binding['semantic_column'],binding['physical_column'],proof)
        elif 'source_asset'in bridge:
            link(bridge['delivery_asset'],bridge['source_asset'],proof)
            for producer in bridge.get('producers',[]):link(bridge['delivery_asset'],producer['producer_asset_id'],proof)
    for visual in [n for n in nodes.values()if n['kind']=='VISUAL']:
        path=factory.resolve_path(graph.path_to_source(visual['id']))
        for bridge in path.get('declared_route_bridges',[]):declared_links(bridge)
    queryable=set()
    for route in native.routes.values():
        queryable.update(route['asset_ids'])
        if route['kind']=='SOURCE_SQL':
            for obj in route['objects']:
                if obj['metadata'].get('type_desc')=='USER_TABLE':
                    for ident in byasset[obj['id']]:nodes[ident].setdefault('properties',{})['source_system_object']=True
    result={'nodes':list(nodes.values()),'edges':list(edges.values()),'queryable_assets':sorted(queryable)}
    return result

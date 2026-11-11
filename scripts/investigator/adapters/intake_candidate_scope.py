"""Compile candidate quantities from retained native definitions, never values.

Reuses the declared-context compiler, including page, visual and saved slicer
restrictions. Unknown interactive state or an unaddressed matrix is not an
unfiltered fallback.
"""
from copy import deepcopy
import json
import re
from urllib.parse import unquote
from ..estate_graph_contract import digest


def compile_scope(model, measure_id, target_id, filters=(), *, total=False):
    from . import report_predicates as predicates
    from .report_cells import roles, addresses
    from ..declared_reproduction import compose
    report=next((r for r in model['context']['reports']
                 if any(p['id']==target_id for p in r['report_definitions'])),None)
    if report is None:raise ValueError('CANDIDATE_VISUAL_DEFINITION_ABSENT')
    declaration=predicates._extract(model,measure_id,{'report_binding':{'report_id':report['report']['id']}},target_id)
    if any(e['disposition']=='UNSUPPORTED'for e in declaration['inventory']['entries']):
        raise ValueError('CANDIDATE_DECLARED_SCOPE_UNSUPPORTED')
    restrictions=compose([*declaration['restrictions'],*filters])
    document=predicates._document(model,target_id)
    columns,_=roles(model,document)
    mode='TOTAL'if columns and total else'KEYED'if columns else'UNGROUPED'
    scope={'target_visual':{'target_id':target_id,'measure_id':measure_id,'mode':mode},
           'filters':[{'column_id':r['field_id'],'operator':'in','values':r['values']}for r in restrictions]}
    cells=addresses(model,document,target_id,measure_id,scope)
    if len(cells)!=1:raise ValueError('CANDIDATE_CELL_NOT_UNIQUE')
    return {'query':predicates.quantity_query(model,measure_id,restrictions),
            'scope_evidence':{'kind':'RETAINED_DECLARED_CONTEXT_NOT_INTERACTIVE_STATE',
                 'inventory':declaration['inventory'],'restrictions':restrictions,
                 'cell':cells[0],'definition_evidence':declaration['evidence']}}


def plan(native,catalog,target,proposal):
    """Resolve native addresses and compile exactly one candidate context."""
    from .estate_graph_static import StaticGraph
    from types import SimpleNamespace
    node=catalog.nodes[target];kind=node['kind'];details=proposal.get('details')or{}
    if any(details.get(k)for k in ('date_range','approximate_date','record','users','roles')):
        raise ValueError('CANDIDATE_STATED_SCOPE_NOT_COMPILED')
    if re.search(r'\b(?:clicked|bookmark|highlighted|selected row|yesterday|last week|last month|this month)\b',proposal.get('description',''),re.I):
        raise ValueError('CANDIDATE_INTERACTIVE_OR_RELATIVE_SCOPE_UNESTABLISHED')
    reports=catalog.reports_for(target)
    if kind=='REPORT':reports=[{'id':target}]
    if len(reports)!=1:raise ValueError('CANDIDATE_REPORT_PARENT_NOT_UNIQUE')
    report_node=reports[0]['id'];report_id=catalog.nodes[report_node].get('properties',{}).get('asset_id')
    if report_id not in native.assets:raise ValueError('CANDIDATE_NATIVE_REPORT_ABSENT')
    model_id=StaticGraph.model_for_report(SimpleNamespace(assets=native.assets),report_id)
    if not model_id:raise ValueError('CANDIDATE_EXPLICIT_MODEL_BINDING_ABSENT')
    routes=[k for k,r in native.routes.items()if r['dialect']=='DAX'and r['container']==model_id]
    if len(routes)!=1:raise ValueError('CANDIDATE_MODEL_ROUTE_NOT_UNIQUE')
    pages=([{'id':target}]if kind=='PAGE'else
           [{'id':proposal['page']}]if proposal.get('page')else catalog.pages(report_node))
    if kind=='VISUAL':
        pages=[p for p in catalog.pages(report_node)if any(v['id']==target for v in catalog.visuals(report_node,p['id']))]
    visuals=[(p['id'],v)for p in pages for v in catalog.visuals(report_node,p['id'])if kind!='VISUAL'or v['id']==target]
    named=details.get('measure')or proposal.get('measure')
    if named in catalog.nodes:named=catalog.nodes[named]['label']
    metrics={r['id']for r in catalog.measure_matches(proposal.get('description',''))}
    possibilities=[(p,v,m)for p,v in visuals for m in v.get('measures',[])
                   if m['id']in metrics and (not named or m['name'].casefold()==str(named).casefold())]
    if len(possibilities)!=1:raise ValueError('CANDIDATE_VISUAL_CALCULATION_NOT_UNIQUE')
    page,visual,measure=possibilities[0]
    measure_id=catalog.nodes[measure['id']].get('properties',{}).get('asset_id')
    visual_asset=catalog.nodes[visual['id']].get('properties',{}).get('asset_id','')
    if '/visual/'not in visual_asset:raise ValueError('CANDIDATE_NATIVE_VISUAL_ADDRESS_ABSENT')
    path=unquote(visual_asset.split('/visual/',1)[1])
    parts=[a for a in native.assets.values()if a['kind']=='DefinitionPart'and a['parent_id']==report_id]
    targets=[a for a in parts if a['name']==path]
    if len(targets)!=1:raise ValueError('CANDIDATE_EXACT_DEFINITION_PART_ABSENT')
    selected={model_id}
    while True:
        children={a['id']for a in native.assets.values()if a['parent_id']in selected}
        if children<=selected:break
        selected|=children
    assets=[native.assets[i]for i in sorted(selected)]
    context={'model_assets':assets,'reports':[{'report':native.assets[report_id],'model_id':model_id,
        'binding_status':'RESOLVED_EXPLICIT_ID','gaps':[],'report_definitions':parts}]}
    context_id=digest(context);context['id']=context_id
    workspace,model=model_id.removeprefix('fabric://').split('/')
    pinned={'id':model_id,'workspace':workspace,'native_id':model,'revision':0,'context_id':context_id,'context':context}
    filters=[]
    for f in details.get('filters',[]):
        column=catalog.nodes.get(f['field'],{}).get('properties',{}).get('asset_id',f['field'])
        if not any(a['id']==column and a['kind']=='SemanticColumn'for a in assets):
            raise ValueError('CANDIDATE_FILTER_COLUMN_NOT_BOUND')
        filters.append({'field_id':column,'operator':'IN','values':f['value']if isinstance(f['value'],list)else[f['value']]})
    compiled=compile_scope(pinned,measure_id,targets[0]['id'],filters,
                           total=bool(re.search(r'\b(?:grand total|total row|total cell|matrix total)\b',proposal.get('description',''),re.I)))
    # Route preparation needs the compiled measure and predicate members, not
    # the visual's graph ID. Bind against the same model, then expose only
    # graph nodes belonging to those exact native references.
    from ..query_dax import compile_query
    bound=compile_query(compiled['query'],native.routes[routes[0]]['objects'],max_rows=250)
    reference_nodes=sorted({n for asset in bound['asset_ids'] for n in native.object_nodes(asset)})
    if not reference_nodes:raise ValueError('CANDIDATE_COMPILED_REFERENCES_NOT_IN_GRAPH')
    intake={k:deepcopy(v)for k,v in proposal.items()if k not in ('table','measure','report','page','visual')}
    intake.update(report=report_node,page=page,visual=visual['id'])
    return {**compiled,'layer':routes[0],'reference_nodes':reference_nodes,'intake':intake,
            'scope':'EXACT_RETAINED_REPORT_PAGE_VISUAL_SLICER_AND_STATED_FILTERS'}

"""Metadata-derived tests inside an explicitly reviewed diagnostic envelope."""
from .onboarding import fields, text, digest, Conflict
from . import native_diagnostics, source_diagnostics

CONTEXT_CHANGERS={'FILTERED_MEASURE','TIME_SHIFT','RELATIONSHIP_SWITCH','CONDITIONAL'}


def catalog(store,config,envelope):
    fields(envelope,['model_id','revision','context_id','measure_id','filters','dimension_ids','source_tests','symptom','limits']+
           (['source_selection'] if 'source_selection' in envelope else []))
    if 'source_selection' in envelope and (envelope['source_selection']!='reviewed_mappings' or envelope['source_tests']!=[]):
        raise ValueError('Reviewed discovery requires an empty manual source-test list')
    text(envelope['symptom'],2000)
    limits=envelope['limits'];fields(limits,['cloud_calls','planner_calls','wall_seconds','input_characters','max_depth'])
    for name,low,high in [('cloud_calls',1,10),('planner_calls',1,6),('wall_seconds',60,1800),('input_characters',1000,80000),('max_depth',0,4)]:
        if type(limits[name]) is not int or not low<=limits[name]<=high:raise ValueError('Invalid budget')
    model=store.get(envelope['model_id'])
    dimensions=envelope['dimension_ids']; sources=envelope['source_tests']
    if not isinstance(dimensions,list) or len(dimensions)>4 or any(not isinstance(x,str) for x in dimensions) or len(set(dimensions))!=len(dimensions):
        raise ValueError('Invalid dimension envelope')
    if not isinstance(sources,list) or len(sources)>8:raise ValueError('Invalid source envelope')
    graph=model['context'].get('semantic_graph',{}).get('measures',{}) if model['context'] else {}
    pending=[(envelope['measure_id'],0,None)]; visited=set(); candidates=[]; gaps=[]
    while pending:
        measure,depth,parent=pending.pop(0)
        if measure in visited:continue
        visited.add(measure)
        if len(visited)>24:raise ValueError('Dependency candidate limit exceeded')
        plan={k:envelope[k] for k in ('model_id','revision','context_id','filters')}
        plan.update(measure_ids=[measure],dimension_id=None,include_dependencies=False)
        native_diagnostics.build(model,plan)
        def add(tool,plan,dimension=None):
            identity=digest({'tool':tool,'plan':plan})
            if any(c['id']==identity for c in candidates):return
            candidates.append({'id':identity,'tool':tool,'plan':plan,'measure_id':measure,
                               'dimension_id':dimension,'depth':depth,'parent':parent})
        add('native',plan)
        for dimension in dimensions:
            sliced=dict(plan,dimension_id=dimension);native_diagnostics.build(model,sliced);add('native',sliced,dimension)
        node=graph.get(measure)
        if not node or node.get('dependency_state')!='SUPPORTED':
            gaps.append({'measure_id':measure,'reason':'DEPENDENCY_ANALYSIS_PARTIAL'});continue
        if set(node['operations']) & CONTEXT_CHANGERS:
            if node['dependencies']:gaps.append({'measure_id':measure,'reason':'CHILD_CONTEXT_UNCERTIFIED'})
            continue
        if node['dependencies'] and depth>=limits['max_depth']:
            gaps.append({'measure_id':measure,'reason':'DEPTH_LIMIT'});continue
        pending.extend((child,depth+1,measure) for child in node['dependencies'])
    if envelope.get('source_selection')=='reviewed_mappings':
        from .source_bindings import resolve
        sources,source_gaps=resolve(store,config,envelope,visited);gaps.extend(source_gaps)
    for source in sources:
        fields(source,['measure_id','plan'])
        if source['measure_id'] not in visited:raise ValueError('Source test is outside reachable measure scope')
        plan=source['plan']
        if any(plan.get(k)!=envelope[k] for k in ('model_id','revision','context_id')):raise Conflict('Source scope is stale')
        compiled=source_diagnostics.build(store,plan,config)
        identity=digest({'tool':'source','plan':plan})
        if any(c['id']==identity for c in candidates):raise ValueError('Duplicate source test')
        candidates.append({'id':identity,'tool':'source','plan':plan,'measure_id':source['measure_id'],
                           'dimension_id':None,'depth':0,'parent':None,
                           'reviewed_mapping':compiled.get('reviewed_mapping')})
    if len(candidates)>100:raise ValueError('Candidate catalog too large')
    return candidates,gaps


def available(candidates,observations,attempted):
    scalars={o['measure_id'] for o in observations if o['tool']=='native' and o['dimension_id'] is None and o['status']=='COMPLETED'}
    return [c for c in candidates if c['id'] not in attempted
            and (c['parent'] is None or c['parent'] in scalars)
            and (c['dimension_id'] is None or c['measure_id'] in scalars)]


def observation(candidate,child):
    receipt=child['steps'][0]['result']
    if not receipt:return None
    data=receipt.get('result') or {}
    return {'id':receipt['id'],'candidate_id':candidate['id'],'run_id':child['id'],
            'tool':candidate['tool'],'measure_id':candidate['measure_id'],'dimension_id':candidate['dimension_id'],
            'status':receipt['status'],'values':(data.get('rows',[]) if candidate['tool']=='native' else [data.get('value')]) if receipt['status']=='COMPLETED' else [],
            'completeness':data.get('completeness','SOURCE_AGGREGATE'),
            'request_hash':receipt['request_hash'],'proof_eligible':False,
            'source_operation':candidate['plan'].get('operation'),
            'reviewed_mapping':candidate.get('reviewed_mapping'),
            'freshness':data.get('freshness')}


def diagnostic_pairs(observations):
    """Differences of operator-associated observations, never equivalence or cause."""
    from decimal import Decimal, InvalidOperation
    pairs=[]
    for native in observations:
        if native['tool']!='native' or native['dimension_id'] is not None or native['status']!='COMPLETED':continue
        for source in observations:
            if source['tool']!='source' or source['status']!='COMPLETED' or source['measure_id']!=native['measure_id']:continue
            if source.get('source_operation') == 'watermark_age_microseconds':continue
            left=native['values'][0].get('[m0]');right=source['values'][0]
            pair={'native_observation_id':native['id'],'source_observation_id':source['id'],
                  'association':'OPERATOR_DECLARED_ONLY','comparable':False,'difference':None}
            if left and right and left['type']=='decimal' and right['type']=='decimal':
                try:
                    a,b=Decimal(left['value']),Decimal(right['value'])
                    if a.is_finite() and b.is_finite():pair['difference']=str(a-b)
                except InvalidOperation:pass
            pairs.append(pair)
    return pairs

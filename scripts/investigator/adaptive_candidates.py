"""Metadata-derived tests inside an explicitly reviewed diagnostic envelope."""
from .onboarding import fields, text, digest, Conflict
from . import native_diagnostics, source_diagnostics

CONTEXT_CHANGERS={'FILTERED_MEASURE','TIME_SHIFT','RELATIONSHIP_SWITCH','CONDITIONAL'}


def catalog(store,config,envelope):
    fields(envelope,['model_id','revision','context_id','measure_id','filters','dimension_ids','source_tests','symptom','limits']+
           [k for k in ('source_selection','record_tests','record_pairs','record_selection') if k in envelope])
    if 'source_selection' in envelope and (envelope['source_selection']!='reviewed_mappings' or envelope['source_tests']!=[]):
        raise ValueError('Reviewed discovery requires an empty manual source-test list')
    if 'record_selection' in envelope and (envelope['record_selection']!='reviewed_mappings' or envelope.get('record_tests',[]) or envelope.get('record_pairs',[])):
        raise ValueError('Reviewed record discovery cannot mix manual tests or pairs')
    text(envelope['symptom'],2000)
    limits=envelope['limits'];fields(limits,['cloud_calls','planner_calls','wall_seconds','input_characters','max_depth'])
    for name,low,high in [('cloud_calls',1,10),('planner_calls',1,6),('wall_seconds',60,1800),('input_characters',1000,80000),('max_depth',0,4)]:
        if type(limits[name]) is not int or not low<=limits[name]<=high:raise ValueError('Invalid budget')
    model=store.get(envelope['model_id'])
    reader=config.get('fabric',{}).get('native_reader')
    if reader is not None:
        from .native_identity import profile
        profile(reader)
        if model['workspace'] != config['fabric']['workspace_id'] or model['native_id'] not in reader['model_ids']:
            raise Conflict('Model is outside the configured native reader scope')
    dimensions=envelope['dimension_ids']; sources=envelope['source_tests']
    if not isinstance(dimensions,list) or len(dimensions)>4 or any(not isinstance(x,str) for x in dimensions) or len(set(dimensions))!=len(dimensions):
        raise ValueError('Invalid dimension envelope')
    if not isinstance(sources,list) or len(sources)>8:raise ValueError('Invalid source envelope')
    graph=model['context'].get('semantic_graph',{}).get('measures',{}) if model['context'] else {}
    pending=[(envelope['measure_id'],0,None,[envelope['measure_id']],False,None)]
    visited=set(); seen_contexts=set(); candidates=[]; gaps=[]
    while pending:
        measure,depth,parent,path,transformed,parent_candidate=pending.pop(0)
        visit=(measure,tuple(path) if transformed else None)
        if visit in seen_contexts:continue
        seen_contexts.add(visit)
        if not transformed:visited.add(measure)
        if len(seen_contexts)>24:raise ValueError('Dependency candidate limit exceeded')
        plan={k:envelope[k] for k in ('model_id','revision','context_id','filters')}
        plan.update(measure_ids=[measure],dimension_id=None,include_dependencies=False)
        if transformed:plan['context_path']=path
        compiled_native=native_diagnostics.build(model,plan)
        def add(tool,plan,dimension=None,scalar_candidate=None):
            identity=digest({'tool':tool,'plan':plan})
            if any(c['id']==identity for c in candidates):return identity
            candidates.append({'id':identity,'tool':tool,'plan':plan,'measure_id':measure,
                               'dimension_id':dimension,'depth':depth,'parent':parent,
                               **({'parent_candidate_id':parent_candidate,'scalar_candidate_id':scalar_candidate,
                                   'dependency_context':compiled_native['dependency_context']} if transformed else {})})
            return identity
        scalar_id=add('native',plan)
        for dimension in dimensions:
            sliced=dict(plan,dimension_id=dimension);native_diagnostics.build(model,sliced);add('native',sliced,dimension,scalar_id)
        node=graph.get(measure)
        from .dependency_context import edges, Unsupported
        try:context_edges=edges(model,measure)
        except Unsupported:context_edges=None
        if context_edges is None:
            if not node or node.get('dependency_state')!='SUPPORTED':
                gaps.append({'measure_id':measure,'reason':'DEPENDENCY_ANALYSIS_PARTIAL'});continue
            if set(node['operations']) & CONTEXT_CHANGERS:
                if node['dependencies']:gaps.append({'measure_id':measure,'reason':'CHILD_CONTEXT_UNCERTIFIED'})
                continue
            # Legacy retained contexts without expressions preserve their old diagnostic path.
            # A transformed path cannot extend through an unrecognized expression.
            if transformed and node['dependencies']:
                gaps.append({'measure_id':measure,'reason':'CHILD_CONTEXT_UNCERTIFIED'});continue
            context_edges=[{'child_id':child,'filters':[]} for child in node['dependencies']]
        if transformed:
            gaps.append({'measure_id':measure,'reason':'CONTEXTUAL_SOURCE_COMPARISON_UNSUPPORTED','context_path':path})
        if context_edges and depth>=limits['max_depth']:
            gaps.append({'measure_id':measure,'reason':'DEPTH_LIMIT'});continue
        for edge in context_edges:
            child=edge['child_id']
            if child in path:
                gaps.append({'measure_id':measure,'reason':'CYCLIC_CONTEXT_PATH'});continue
            next_transformed=transformed or bool(edge['filters'])
            if next_transformed:
                from .dependency_context import compile_path
                try:compile_path(model,path+[child],child)
                except Unsupported:
                    gaps.append({'measure_id':measure,'reason':'CHILD_CONTEXT_UNCERTIFIED'});continue
            pending.append((child,depth+1,measure,path+[child],next_transformed,scalar_id))
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
    record_tests=envelope.get('record_tests',[])
    if envelope.get('record_selection')=='reviewed_mappings':
        from .record_bindings import resolve as resolve_records
        record_tests,record_gaps=resolve_records(store,config,envelope,visited);gaps.extend(record_gaps)
    if not isinstance(record_tests,list) or len(record_tests)>4:raise ValueError('Record candidate budget exceeded')
    from . import record_readback
    for test in record_tests:
        fields(test,['measure_id','tool','plan'])
        if test['measure_id'] not in visited or test['tool'] not in ('native_records','source_records'):raise ValueError('Record test outside admitted scope')
        plan=test['plan']
        if any(plan.get(k)!=envelope[k] for k in ('model_id','revision','context_id')):raise Conflict('Record scope is stale')
        if test['tool']=='native_records' and plan['filters']!=envelope['filters']:raise ValueError('Native readback must retain full native scope')
        compiled=record_readback.build(store,plan,config,test['tool'])
        identity=digest({'tool':test['tool'],'plan':plan})
        if any(c['id']==identity for c in candidates):raise ValueError('Duplicate record candidate')
        candidates.append({'id':identity,'tool':test['tool'],'plan':plan,'measure_id':test['measure_id'],
                           'dimension_id':None,'depth':0,'parent':test['measure_id'],
                           'record_mapping':compiled.get('reviewed_mapping')})
    pairs=envelope.get('record_pairs',[])
    if not isinstance(pairs,list) or len(pairs)>2:raise ValueError('Record pair budget exceeded')
    from .record_comparison import validate_projection
    for pair in pairs:
        fields(pair,['native_test','source_test','column_bindings','filter_bindings'])
        for key,tool in [('native_test','native_records'),('source_test','source_records')]:
            index=pair[key]
            if type(index) is not int or not 0<=index<len(record_tests) or record_tests[index]['tool']!=tool:raise ValueError('Record pair needs approved typed tests')
        left=record_tests[pair['native_test']];right=record_tests[pair['source_test']]
        if left['measure_id']!=right['measure_id']:raise ValueError('Record pair crosses measure scope')
        validate_projection(left['plan'],right['plan'],pair['column_bindings'],pair['filter_bindings'])
    if len(candidates)>100:raise ValueError('Candidate catalog too large')
    return candidates,gaps


def available(candidates,observations,attempted):
    captured=[o for o in observations if o['tool']=='native' and o['dimension_id'] is None and o['status']=='COMPLETED']
    scalars={o['measure_id'] for o in captured if not o.get('dependency_context')}
    scalar_candidates={o['candidate_id'] for o in captured if o.get('candidate_id')}
    return [c for c in candidates if c['id'] not in attempted
            and ((c['parent_candidate_id'] in scalar_candidates) if c.get('dependency_context') else (c['parent'] is None or c['parent'] in scalars))
            and (c['dimension_id'] is None or (c['scalar_candidate_id'] in scalar_candidates if c.get('dependency_context') else c['measure_id'] in scalars))]


def observation(candidate,child):
    receipt=child['steps'][0]['result']
    if not receipt:return None
    data=receipt.get('result') or {}
    return {**({'execution_identity':data['execution_identity']} if data.get('execution_identity') else {}),
            **({'dependency_context':candidate['dependency_context']} if candidate.get('dependency_context') else {}),
            'id':receipt['id'],'candidate_id':candidate['id'],'run_id':child['id'],
            'tool':candidate['tool'],'measure_id':candidate['measure_id'],'dimension_id':candidate['dimension_id'],
            'status':receipt['status'],'values':(data.get('rows',[]) if candidate['tool'] in ('native','native_records','source_records') else [data.get('value')]) if receipt['status']=='COMPLETED' else [],
            'completeness':data.get('completeness','SOURCE_AGGREGATE'),
            'request_hash':receipt['request_hash'],'proof_eligible':False,
            'source_operation':candidate['plan'].get('operation'),
            'reviewed_mapping':candidate.get('reviewed_mapping'),
            'record_mapping':candidate.get('record_mapping'),
            'freshness':data.get('freshness'),
            'record_readback':dict({k:data.get(k) for k in ('column_ids','key_column_ids','types','record_hash','observed_row_count')},
                                   filters=candidate['plan']['filters'],context_hash=child.get('context_hash')) if candidate['tool'] in ('native_records','source_records') else None}


def record_pairs(envelope,observations):
    """Deterministic local evidence from approved pairs; no additional data call."""
    from .record_comparison import compare
    results=[]
    for pair in envelope.get('record_pairs',[]):
        receipts=[]
        for key in ('native_test','source_test'):
            test=envelope['record_tests'][pair[key]]
            identity=digest({'tool':test['tool'],'plan':test['plan']})
            observed=next((o for o in observations if o['candidate_id']==identity),None)
            if not observed:break
            info=observed['record_readback']
            receipts.append({'id':observed['id'],'status':observed['status'],'local_context_current':True,
                             'request':{**info,'backend':observed['tool'],'plan':{'filters':info['filters']}},
                             'result':{'rows':observed['values'],'completeness':observed['completeness']}})
        if len(receipts)==2:
            # Failed reads carry no shape. Keep their unavailable evidence explicit.
            if any(r['status']!='COMPLETED' for r in receipts):
                results.append({'status':'NOT_ASSESSED','gaps':['READBACK_UNAVAILABLE'],'root_cause_verified':False})
            else:results.append(compare(*receipts,pair['column_bindings'],pair['filter_bindings']))
    grouped={}
    for observed in observations:
        review=observed.get('record_mapping')
        if not review:continue
        key=(review['id'],review['hash'],observed['measure_id'])
        grouped.setdefault(key,[]).append(observed)
    for group in grouped.values():
        if len(group)!=2 or {o['tool'] for o in group}!={'native_records','source_records'}:continue
        group.sort(key=lambda o:o['tool'])
        review=group[0]['record_mapping'];receipts=[]
        for o in group:
            info=o['record_readback']
            receipts.append({'id':o['id'],'status':o['status'],'local_context_current':True,
                             'request':{**info,'backend':o['tool'],'plan':{'filters':info['filters']}},
                             'result':{'rows':o['values'],'completeness':o['completeness']}})
        if any(o['status']!='COMPLETED' for o in group):
            result={'status':'NOT_ASSESSED','gaps':['READBACK_UNAVAILABLE'],'root_cause_verified':False}
        else:result=compare(*receipts,review['column_bindings'],review['filter_bindings'])
        results.append(dict(result,reviewed_mapping=review))
    return results


def diagnostic_pairs(observations):
    """Differences of operator-associated observations, never equivalence or cause."""
    from decimal import Decimal, InvalidOperation
    pairs=[]
    for native in observations:
        if native['tool']!='native' or native['dimension_id'] is not None or native['status']!='COMPLETED':continue
        if native.get('dependency_context'):continue
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

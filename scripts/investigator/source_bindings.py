"""Derive reviewed source tests from ticket filters, without per-ticket SQL plans."""
from . import comparisons, native_diagnostics
from .onboarding import Conflict
from .source_scope import kind


def validate_plan(store, plan, columns=None):
    review=comparisons.mapping(store,plan['model_id'],plan['comparison_mapping_id'])
    body=review['body']
    if review['revocation'] is not None:raise Conflict('Source mapping revoked')
    if (body['revision']!=plan['revision'] or body['context_id']!=plan['context_id'] or
        body['source_object_id']!=plan['object_id'] or body['source_operation']!=plan['operation'] or
        body['source_column_id']!=plan['column_id']):raise Conflict('Source plan does not match reviewed mapping')
    bindings={b['source_column_id']:b['native_column_id'] for b in body['filter_bindings']}
    if set(bindings)!={f['column_id'] for f in plan['filters']}:raise Conflict('Mapping does not cover the complete filter scope')
    model=store.get(plan['model_id'])
    native_filters=[dict(f,column_id=bindings[f['column_id']]) for f in plan['filters']]
    native_plan={k:plan[k] for k in ('model_id','revision','context_id')}
    native_plan.update(measure_ids=[body['measure_id']],filters=native_filters,dimension_id=None,include_dependencies=False)
    native_diagnostics.build(model,native_plan)
    if columns is not None:
        native={a['id']:a['metadata'] for a in model['context']['reports'][0]['model_assets'] if a['kind']=='SemanticColumn'}
        for source_id,native_id in bindings.items():
            if source_id not in columns or kind(columns[source_id]['metadata'])!=native[native_id].get('dataType'):
                raise Conflict('Mapped filter types differ')
    return {'id':review['id'],'hash':review['hash'],'authority':'TEAM_CONFIRMED_INTENT','equivalence_verified':False}


def resolve(store, config, envelope, reachable):
    """Only a unique current mapping covering the whole scope becomes a test."""
    from .source_diagnostics import build
    reviews=comparisons.list_mappings(store,envelope['model_id'])
    sources=[];gaps=[]
    for measure in sorted(reachable):
        selected=[r for r in reviews if r['body']['measure_id']==measure and r['revocation'] is None
                  and r['body']['revision']==envelope['revision'] and r['body']['context_id']==envelope['context_id']]
        if len(selected)!=1:
            gaps.append({'measure_id':measure,'reason':'SOURCE_MAPPING_AMBIGUOUS' if selected else 'CURRENT_SOURCE_MAPPING_MISSING'})
            continue
        review=selected[0];body=review['body']
        bindings={b['native_column_id']:b['source_column_id'] for b in body['filter_bindings']}
        if set(bindings)!={f['column_id'] for f in envelope['filters']}:
            gaps.append({'measure_id':measure,'mapping_id':review['id'],'reason':'SOURCE_MAPPING_FILTER_COVERAGE_GAP'})
            continue
        plan={k:envelope[k] for k in ('model_id','revision','context_id')}
        plan.update(object_id=body['source_object_id'],operation=body['source_operation'],column_id=body['source_column_id'],
                    filters=[dict(f,column_id=bindings[f['column_id']]) for f in envelope['filters']],
                    comparison_mapping_id=review['id'])
        try:build(store,plan,config)
        except (ValueError,KeyError):
            gaps.append({'measure_id':measure,'mapping_id':review['id'],'reason':'SOURCE_MAPPING_NOT_EXECUTABLE'})
            continue
        sources.append({'measure_id':measure,'plan':plan})
    if len(sources)>8:raise ValueError('Reviewed source test budget exceeded')
    return sources,gaps

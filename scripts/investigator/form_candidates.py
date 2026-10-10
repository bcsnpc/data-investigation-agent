"""Value-based form resolution from an exhaustive, receipted candidate set.

The observer is a trusted reader port, never an oracle or model response.
No observation is also no authority: failed/missing probes cannot be omitted.
"""
import copy
from .onboarding import digest, Conflict
from . import form_intake, reported_figure


class NotMeasurable(Conflict):pass


def candidates(request,models):
    result=[]
    for model in models:
        for visual in model.get('visuals',[]):
            if visual['report_id']!=request['report_id'] or visual.get('page_id')!=request['page_id']:continue
            for measure in visual['measure_ids']:
                if request.get('measure_id') and request['measure_id']!=measure:continue
                mode=request['cell_mode'] or ('UNGROUPED' if not visual['grouping_columns'] else None)
                if mode is None:raise NotMeasurable('Candidate cell mode is unresolved; no total substituted')
                if bool(visual['grouping_columns'])!=(mode!='UNGROUPED'):continue
                picked={**request,'target_id':visual['target_id'],'cell_mode':mode,'measure_id':measure}
                bound=form_intake.resolve(picked,models,None)
                declaration=visual.get('declared_scopes',{}).get(measure)
                if bound['status']!='BOUND' or not declaration or declaration.get('state')!='COMPLETE':
                    raise NotMeasurable('Candidate definition/scope unavailable: '+visual['target_id'])
                scope=bound['scope'];semantic={'measure_id':measure,'restrictions':declaration['restrictions'],
                    'keys':scope['filters'],'context_id':declaration['context_id'],'context_hash':declaration['context_hash']}
                result.append({'model_id':model['id'],'target_id':visual['target_id'],'measure_id':measure,
                    'mode':mode,'scope_hash':digest(semantic),'scope':scope,'declaration':copy.deepcopy(declaration)})
    if not result:raise NotMeasurable('No executable candidates for the selected page and cell')
    return sorted(result,key=lambda c:(c['target_id'],c['measure_id']))


def observe(request,models,reader):
    if request['target_id'] is not None or request['value_seen'] is None:
        raise ValueError('Value resolution requires a skipped visual and supplied value')
    if reader is None:raise NotMeasurable('Candidate value reader unavailable; no values inferred')
    entries=[]
    for candidate in candidates(request,models):
        probe=reader(copy.deepcopy(candidate))
        if not isinstance(probe,dict) or probe.get('status')!='OBSERVED' or probe.get('complete') is not True:
            raise NotMeasurable('Candidate probe unavailable: '+candidate['target_id'])
        if not all(probe.get(k) for k in ('receipt_id','query_hash','execution_surface','attestation')):
            raise NotMeasurable('Candidate probe lacks receipt or attestation')
        if probe['attestation'].get('consistency')!='MATCHED':raise NotMeasurable('Candidate surface did not attest')
        reported_figure.label(candidate['scope']['reported_figure'],probe['value'])
        entries.append({'target_id':candidate['target_id'],'measure_id':candidate['measure_id'],
                        'scope_hash':candidate['scope_hash'],'probe':copy.deepcopy(probe)})
    binding={'request_hash':digest(request),'catalog_hash':digest(models),'entries':entries}
    return binding,matching(request,models,binding)


def matching(request,models,binding):
    if binding['request_hash']!=digest(request) or binding['catalog_hash']!=digest(models):
        raise Conflict('Candidate evidence belongs to changed inputs or metadata')
    current=candidates(request,models);entries=binding['entries']
    for e in entries:
        p=e['probe']
        if p.get('status')!='OBSERVED' or p.get('complete') is not True or not all(p.get(k) for k in ('receipt_id','query_hash','execution_surface','attestation')) or p['attestation'].get('consistency')!='MATCHED':
            raise NotMeasurable('Retained candidate probe is incomplete or unattested')
    if [(e['target_id'],e['measure_id'],e['scope_hash']) for e in entries]!=[
            (c['target_id'],c['measure_id'],c['scope_hash']) for c in current]:
        raise Conflict('Candidate evidence is not exhaustive for current definitions')
    matches=[c for c,e in zip(current,entries) if reported_figure.label(c['scope']['reported_figure'],e['probe']['value'])=='REPRODUCED']
    if not matches:
        return {'status':'NEEDS_INPUT','questions':[{'field':'NUMBER',
            'reason':'VALUE_NOT_FOUND','candidate_target_ids':sorted({c['target_id'] for c in current})}]}
    if len({c['scope_hash'] for c in matches})!=1:
        return {'status':'NEEDS_INPUT','questions':[{'field':'NUMBER','candidate_target_ids':[c['target_id'] for c in matches]}]}
    return {'status':'BOUND','scope':matches[0]['scope'],'authority':'RECEIPTED_VALUE_MATCH',
            'equivalent_target_ids':[c['target_id'] for c in matches]}

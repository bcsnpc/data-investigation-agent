"""Evaluation-only form construction from sealed truth and retained definitions.

This module is not called by intake. Every selection carries its derivation;
unknown truth stays unknown. Expected values never enter a reader port.
"""
import copy
from . import form_intake
from .onboarding import digest


def construct(oracle,models,base):
    request=copy.deepcopy(base);steps=[];gaps=[]
    target=oracle['true_target_and_cell'];report=oracle['true_report_and_page']
    if report['state']=='DETERMINED':
        request.update({k:report['value'].get(k) for k in ('report_id','page_id')})
        steps.append({'field':'report/page','source':'sealed oracle container','basis':report.get('basis')})
    else:gaps.append('Report/page '+report['state'])
    if target['state']=='DETERMINED':
        truth=target['value']
        if truth.get('kind')=='MEASURE_AT_SCOPE':
            review=oracle.get('scope_equivalence_review',{})
            if review.get('status')!='VERIFIED_EQUIVALENT_DECLARED_SCOPE':gaps.append('R1 review is not complete')
            else:
                choices=[]
                for m in models:
                    for v in m.get('visuals',[]):
                        declared=v.get('declared_scopes',{}).get(truth['measure_id'],{})
                        if v['target_id'] in review['candidate_ids'] and v['report_id']==request['report_id'] and v.get('page_id')==request['page_id'] and declared.get('state')=='COMPLETE' and declared.get('restrictions')==[]:
                            choices.append((bool(v['grouping_columns']),v['target_id'],v))
                if not choices:gaps.append('No retained visual satisfies reviewed R1 scope')
                else:
                    v=sorted(choices,key=lambda x:x[:2])[0][2]
                    request.update(target_id=v['target_id'],measure_id=truth['measure_id'],cell_mode='TOTAL' if v['grouping_columns'] else 'UNGROUPED')
                    steps.append({'field':'visual/measure/cell','source':'sealed R1 equivalence review plus complete retained declarations','candidate_ids':review['candidate_ids'],'chosen':v['target_id']})
        else:
            request.update(target_id=truth['target_id'],cell_mode=truth['mode'])
            if truth.get('cell_keys'):request['cell_keys']=copy.deepcopy(truth['cell_keys'])
            measure=truth.get('measure_id')
            if measure:request['measure_id']=measure
            steps.append({'field':'visual/cell','source':'sealed resolved target (including reviewed inherited variant targets)','basis':target.get('basis')})
    else:gaps.append('Target '+target['state']+'; no visual invented')
    route=oracle['true_comparison_route']
    if route['state']=='NOT_APPLICABLE':request['comparison']=form_intake.SUBJECT_ROUTE
    elif route['state']=='DETERMINED' and route['value'] in form_intake.SCHEMA['properties']['comparison']['enum']:request['comparison']=route['value']
    else:gaps.append('Comparison unknown or unimplemented: '+str(route.get('value',route['state'])))
    steps.append({'field':'comparison','source':'sealed route/declared subject','route':request['comparison']})
    figure=oracle['true_reported_figure']
    if figure['state']=='DETERMINED':
        v=figure['value']
        if v['state']=='EMPTY':request['value_seen']='empty'
        elif v['state']=='NUMBER':
            if v['precision']['state']=='EXACT':request['value_seen']=v['value']
            elif v.get('source'):request['value_seen']=v['source']['quote']
            else:gaps.append('No authored wording for reduced precision')
        else:gaps.append('Reported figure '+v['state']+'; not selected')
    elif figure['state']=='UNDETERMINED':gaps.append('Reported figure undetermined')
    steps.append({'field':'value','source':'sealed reported figure, original precision preserved','state':figure['state']})
    return {'form':request,'construction':steps,'cannot_complete':gaps,'complete':not gaps,
            'oracle_record_hash':digest(oracle),'definition_catalog_hash':digest(models)}

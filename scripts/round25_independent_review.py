"""Independent saved-capture adjudication tooling; never an investigation route."""
from copy import deepcopy
from hashlib import sha256
import json
from investigator.adapters.evaluation_anthropic import guided_grader_schema
FIELDS=('verdict_match','layer_match','cause_match','harmful','handoff_quality','partial','failing_step')
def differs(primary,secondary):
    return any(primary.get(k)!=secondary.get(k)for k in FIELDS)
def packet(*,ticket,answer,evidence,expectation,primary,secondary):
    return deepcopy({'ticket':ticket,'DIA_saved_answer':answer,'saved_evidence':evidence,
       'sealed_expectation':expectation,'graders':{'primary':primary,'secondary':secondary}})
def schema():
    value=guided_grader_schema()
    value['properties']['winner']={'enum':['primary','secondary','both','neither']}
    value['required'].append('winner')
    return value
def exact_deduplicate(value):
    """Retain every row and literal; exact duplicate values become references."""
    pool=[];seen={}
    canonical=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)
    def visit(v):
        raw=canonical(v)
        if isinstance(v,(dict,list,str))and len(raw)>120:
            if raw in seen:return {'verbatim_pool_ref':seen[raw]}
            index=len(pool);seen[raw]=index;pool.append(None);pool[index]=contents(v)
            return {'verbatim_pool_ref':index}
        return contents(v)
    def contents(v):
        if isinstance(v,dict):return {k:visit(x)for k,x in v.items()}
        if isinstance(v,list):return [visit(x)for x in v]
        return v
    root=visit(value)
    packed={'encoding':'verbatim_pool_ref indexes exact JSON values; expand recursively. No rows or fields omitted.','root':root,'verbatim_pool':pool}
    def restore(v):
        if isinstance(v,dict)and set(v)=={'verbatim_pool_ref'}:return restore(pool[v['verbatim_pool_ref']])
        if isinstance(v,dict):return {k:restore(x)for k,x in v.items()}
        if isinstance(v,list):return [restore(x)for x in v]
        return v
    assert restore(root)==value
    return packed
SYSTEM='''You are a fresh independent reviewer of two graders, not an investigator. You have only this ticket, DIA saved answer and evidence, sealed expectation and both graders assessments. Decide which grader is right by examining the full saved evidence. Do not request tools or new reads. Preserve the original all-three scoring rule: correct verdict AND layer/split AND named cause; partial is zero. Distinguish honest uncertainty from confident unsupported or wrong claims. Judge substance rather than labels. Return your own verdict_match,layer_match,cause_match,harmful,handoff_quality,partial,failing_step and reason, plus winner primary/secondary/both/neither. Explain exactly what the raw capture establishes and why each disputed judgment is right or wrong. Operator judgments and prior outcomes are not supplied. Return only through resolve_intake. The verbatim pool is lossless; use all relevant rows, not merely the grader samples.'''

def metric_winner(decision,primary,secondary):
    # Only adapt the existing report vocabulary; never change reviewer grades.
    winner=decision['winner']
    if winner=='both':return 'mixed'
    if winner in ('primary','secondary'):
        selected=primary if winner=='primary'else secondary
        if differs(decision,selected):return 'mixed'
    return winner

def saved_evidence(wrapped):
    answer=wrapped.get('result',wrapped);case=answer.get('case')or{}
    result={k:deepcopy(case.get(k))for k in ('queries','triage','evidence')}
    result['intake']=deepcopy(case['intake']if 'intake'in case else answer.get('intake'))
    return result

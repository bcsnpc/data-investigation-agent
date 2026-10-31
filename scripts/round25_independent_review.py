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

def pack_embedded_json(value):
    """Intern JSON embedded in strings only when its original bytes reconstruct."""
    pool=[];seen={}
    canonical=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)
    def ordered(v):
        if isinstance(v,dict):return {'ordered_json_object':[list(v),[ordered(x)for x in v.values()]]}
        if isinstance(v,list):return [ordered(x)for x in v]
        return v
    def visit(v):
        key=canonical(v)
        if isinstance(v,(dict,list,str)) and len(key)>120:
            if key in seen:return {'verbatim_pool_ref':seen[key]}
            i=len(pool);seen[key]=i;pool.append(None);pool[i]=contents(v)
            return {'verbatim_pool_ref':i}
        return contents(v)
    def contents(v):
        if isinstance(v,str) and len(v)>2000:
            try:parsed=json.loads(v)
            except (ValueError,RecursionError):parsed=None
            if isinstance(parsed,(dict,list)):
                for ascii_value in (False,True):
                    for sort in (False,True):
                        for separators in ((',',':'),(', ',': ')):
                            options={'ensure_ascii':ascii_value,'sort_keys':sort,'separators':separators}
                            if json.dumps(parsed,**options)==v:
                                return {'exact_json_string':visit(ordered(parsed)),'json_options':options}
        if isinstance(v,dict):return {k:visit(x)for k,x in v.items()}
        if isinstance(v,list):return [visit(x)for x in v]
        return v
    root=visit(value)
    packed={'encoding':'Lossless: verbatim_pool_ref expands an exact JSON value. ordered_json_object is [keys,values] reconstructing an object in the listed key order. exact_json_string expands its value, then JSON serializes using json_options (separators pair, ensure_ascii, sort_keys). No evidence omitted.','root':root,'verbatim_pool':pool}
    def restore(v):
        if isinstance(v,dict)and set(v)=={'verbatim_pool_ref'}:return restore(pool[v['verbatim_pool_ref']])
        if isinstance(v,dict)and set(v)=={'ordered_json_object'}:
            keys,values=restore(v['ordered_json_object']);return dict(zip(keys,values))
        if isinstance(v,dict)and set(v)=={'exact_json_string','json_options'}:return json.dumps(restore(v['exact_json_string']),**v['json_options'])
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

def compact_capture_packet(value):
    """Column-key dictionaries and repeated values, including nested JSON text."""
    from collections import Counter
    counts=Counter();parsed_strings={};key_sets=[];key_ids={};pool=[];seen={}
    raw=lambda x:json.dumps(x,ensure_ascii=False,separators=(',',':'))
    def parse(s):
        if len(s)<2000:return None
        if s in parsed_strings:return parsed_strings[s]
        try:v=json.loads(s)
        except (ValueError,RecursionError):return None
        if not isinstance(v,(dict,list)):return None
        for ascii_value in (False,True):
            for sort in (False,True):
                for compact in (True,False):
                    options={'ensure_ascii':ascii_value,'sort_keys':sort,'separators':(',',':')if compact else(', ',': ')}
                    if json.dumps(v,**options)==s:
                        parsed_strings[s]=(v,options);return v,options
        return None
    def count(x):
        if isinstance(x,(dict,list,str)):
            key=raw(x)
            if len(key)>100:counts[key]+=1
        if isinstance(x,str):
            p=parse(x)
            if p:count(p[0])
        elif isinstance(x,dict):
            for v in x.values():count(v)
        elif isinstance(x,list):
            for v in x:count(v)
    count(value)
    def node(x):
        if isinstance(x,(dict,list,str)):
            key=raw(x)
            if counts[key]>1:
                if key not in seen:
                    i=len(pool);seen[key]=i;pool.append(None);pool[i]=contents(x)
                return {'r':seen[key]}
        return contents(x)
    def contents(x):
        if isinstance(x,str):
            p=parse(x)
            return {'j':[node(p[0]),p[1]]}if p else x
        if isinstance(x,dict):
            keys=tuple(x)
            if keys not in key_ids:key_ids[keys]=len(key_sets);key_sets.append(list(keys))
            return {'o':[key_ids[keys],[node(v)for v in x.values()]]}
        if isinstance(x,list):return [node(v)for v in x]
        return x
    root=node(value)
    result={'encoding':'Lossless capture: {r:i} expands pool[i]; {o:[i,values]} zips key_sets[i] with expanded values in order; {j:[value,options]} JSON serializes expanded value with exact options. Other arrays/scalars are literal. All rows, fields and original string bytes retained.','root':root,'pool':pool,'key_sets':key_sets}
    def restore(x):
        if isinstance(x,dict)and set(x)=={'r'}:return restore(pool[x['r']])
        if isinstance(x,dict)and set(x)=={'o'}:
            k,v=x['o'];return dict(zip(key_sets[k],[restore(a)for a in v]))
        if isinstance(x,dict)and set(x)=={'j'}:
            v,options=x['j'];return json.dumps(restore(v),**options)
        if isinstance(x,list):return [restore(a)for a in x]
        return x
    assert restore(root)==value
    return result

def review_resume_response(events):
    responses=[x['body']for x in events if x.get('event')=='REASONING_RESPONSE']
    if len(responses)==1:return responses[0]
    if events and all(x.get('event')=='REASONING_TOKEN_COUNT'for x in events):return None
    raise RuntimeError('INDEPENDENT_REVIEW_UNCERTAIN_DO_NOT_DUPLICATE')

def review_budget(state,case_id,rate):
    from investigator.reasoning_budget import TicketBudget
    return TicketBudget(state,case_id=case_id,owner='round25-independent-reviewer',rate=rate,purpose='GRADING',actual_usage_limit=3_000_000)

"""Post-grade diagnostics from saved outcomes; no provider or estate access."""
from collections import Counter
from hashlib import sha256
import random

STEPS={'intake':'intake','target':'target','triage':'triage','query validation':'query','query error':'query','wrong evidence':'reading results','wrong conclusion':'conclusion','asked the user':'intake'}


def sample_ids(ids,pass_id,*,final=False):
    ids=sorted(ids)
    if final:return ids
    rng=random.Random(sha256(pass_id.encode()).digest());rng.shuffle(ids)
    return sorted(ids[:max(1,(len(ids)+3)//4)]) if ids else []


def report(cases,*,pass_id):
    rows=[];correct={key:0 for key in ('verdict_match','layer_match','cause_match')};score=0;harmful=0
    for case in cases:
        grade=case['grade'];out=case['outcome']
        for key in correct:correct[key]+=bool(grade[key])
        harmful+=bool(grade['harmful'])
        passed=all(grade[k]for k in correct);score+=passed
        if passed:continue
        step=STEPS.get(grade.get('failing_step'))
        stop=str(out.get('stop',out.get('handoff',{})))
        if step is None:
            if 'BUDGET' in stop.upper()or 'MODEL_EXHAUSTED'in stop.upper():step='budget stop'
            elif out.get('status')in ('HELD','CLARIFYING'):step='intake'
            else:step='conclusion' if not grade['cause_match']else 'write-up'
        queries=out.get('case',{}).get('queries',[])
        errors=[{'id':q.get('id'),'error':q.get('error'),'query':q.get('text')}for q in queries if q.get('status')=='ERROR']
        rows.append({'ticket':case['id'],'first_wrong_step':step,'reason':grade['reason'],
           'saved_trace':case.get('saved_trace',{}),
           'basis':'Independent grader first-step assessment plus retained terminal status. Earlier corrected query errors alone are not classified as the first causal failure.',
           'retained_query_errors':errors,'correct_action':{'target':'Open the named native target and its exact declared upstream routes.', 'query':'Use the returned native error and schema to correct this read before concluding.', 'triage':'Read and act on the current path run or freshness fact first.', 'budget stop':'Report the furthest evidenced boundary; do not turn the missing read into a finding.', 'reading results':'Interpret the saved result with its actual scope and native semantics.', 'intake':'Resolve only the missing user fact using the admitted catalog.', 'conclusion':'Restrict the cause to what the cited native evidence establishes.', 'write-up':'State the supported verdict, boundary and cause explicitly.'}.get(step,'Choose the tool that checks the unmet hypothesis.')})
    walkthroughs=[]
    for row in rows:
        if row['first_wrong_step']not in {r['first_wrong_step']for r in walkthroughs}:walkthroughs.append(row)
        if len(walkthroughs)==3:break
    for row in rows:
        if len(walkthroughs)>=3:break
        if row not in walkthroughs:walkthroughs.append(row)
    return {'pass':pass_id,'graded':len(cases),'score':score,'correctness':correct,'harmful':harmful,
        'zero_groups':dict(Counter(r['first_wrong_step']for r in rows)),'zeros':rows,'walkthroughs':walkthroughs,
        'estate_reads':0,'model_calls':0,'scores_or_expectations_changed':False}


def markdown(value):
    lines=['## '+value['pass']+' automatic backtrack','',str({k:value[k]for k in ('graded','score','harmful','correctness','zero_groups')}),'','| Ticket | First wrong step | Reason and correct action |','|---|---|---|']
    for row in value['zeros']:lines.append('| '+row['ticket']+' | '+row['first_wrong_step']+' | '+(row['reason']+' '+row['correct_action']).replace('|','/').replace('\n',' ')+' |')
    import json
    for row in value['walkthroughs']:
        lines+=['','### '+row['ticket'],row['reason']+' '+row['correct_action']]
        trace=row.get('saved_trace',{})
        if trace:
            for label in ('intake','target','triage','tool_decisions','queries','final_answer','sealed_expected'):
                if label in trace:lines+=['',label.replace('_',' ').capitalize()+':','```json',json.dumps(trace[label],ensure_ascii=False,indent=2,default=str),'```']
            if trace.get('checkpoint_sha256'):lines+=['','Saved checkpoint SHA-256: '+trace['checkpoint_sha256']+'. Only recorded tool choices are shown; no new queries or model calls.']
        else:lines+=['','Saved query errors: '+str(row['retained_query_errors'])]
    return '\n'.join(lines)+'\n'

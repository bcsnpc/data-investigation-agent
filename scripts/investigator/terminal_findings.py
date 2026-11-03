"""Render observed partial work even when a run cannot establish a cause.

This never upgrades an unresolved/safety result to a successful investigation.
No new queries or model calls: every value below is already in the case file.
"""
from copy import deepcopy
import json
import re


def report(*,outcome,queries=(),context=None,candidates=()):
    context=context or {};layers=context.get('layers',{})
    findings=[]
    for identity in dict.fromkeys([*layers,*[q['layer'] for q in queries]]):
        observations=[]
        for q in queries:
            if q['layer']!=identity:continue
            if q['status']=='SUCCEEDED':
                rows=q['result']['rows']
                observations.append({'evidence_id':q['id'],'purpose':q['purpose'],'status':'OBSERVED',
                    'row_count':q['row_count'],'rows_sample':deepcopy(rows[:3]),
                    'sample_only':len(rows)>3,'truncated':bool(q.get('truncated')),
                    **({'metadata_scope':deepcopy(q['metadata_scope'])}if q.get('metadata_scope')else{})})
            else:observations.append({'evidence_id':q['id'],'purpose':q['purpose'],'status':'READ_FAILED',
                                      'reason':q.get('error','Native result not established')})
        findings.append({'layer':identity,'name':layers.get(identity,{}).get('label',context.get('candidate_layer_labels',{}).get(identity,identity)),
                         'status':'CHECKED'if observations else'NOT_CHECKED','observations':observations})
    for check in candidates:
        findings.append({'layer':check.get('candidate',check.get('measure')),'name':check.get('name','Candidate'),
                         'status':'CANDIDATE_CHECK','observations':[deepcopy(check)]})
    technical=outcome.get('technical',{})
    fact=technical.get('operational_fact')if isinstance(technical,dict)else None
    if isinstance(fact,dict)and isinstance(fact.get('value'),dict):
        subject=fact.get('subject','Native job')
        findings.append({'layer':subject,'name':context.get('operational_name','Native job'),
            'status':'CHECKED','observations':[{'evidence_id':fact.get('id','Retained native run fact'),
                'purpose':'native_run_history','status':'OBSERVED','row_count':1,'rows_sample':[deepcopy(fact['value'])],
                'sample_only':False,'truncated':False}]})
    calculations=[]
    intake=context.get('intake',{})
    selected=intake.get('measure')or intake.get('details',{}).get('measure')
    path=context.get('path',{})
    path_nodes=path.get('nodes',[])if isinstance(path,dict)else[]
    path_assets={n.get('properties',{}).get('asset_id')for n in path_nodes if n.get('kind')=='MEASURE'}
    for layer in layers.values():
        for obj in layer.get('objects',[]):
            if obj.get('kind')!='Measure':continue
            if obj['id']not in path_assets and selected not in (obj['id'],obj['name']):continue
            expression=obj.get('metadata',{}).get('expression')
            if isinstance(expression,list):expression='\n'.join(expression)
            if isinstance(expression,str) and expression:
                calculations.append({'name':obj['name'],'expression':expression,'source':'RETAINED_DEFINITION','asset_id':obj['id']})
    for q in queries:
        if q['status']=='SUCCEEDED'and q['purpose']=='recreate'and not q.get('metadata_scope'):
            calculations.append({'name':'Native recreation','expression':q['text'],'source':'EXECUTED_QUERY','evidence_id':q['id']})
    retention=[]
    for q in queries:
        if q['status']!='SUCCEEDED' or q.get('purpose')!='history':continue
        history_limit=q.get('metadata_scope',{}).get('history_limit')
        rows=q['result']['rows']
        if history_limit and len(rows)<history_limit and not q.get('truncated'):
            for field in ('version','timestamp'):
                values=[v for row in rows if isinstance(row,dict)for k,v in row.items()if k.casefold()==field and v is not None]
                if values:
                    try:earliest=min(values,key=float)if field=='version'else min(values,key=str)
                    except (ValueError,TypeError):continue
                    retention.append({'evidence_id':q['id'],'field':'earliest_available_'+field,'value':deepcopy(earliest),
                        'qualification':'Earliest entry in the complete returned native Delta history, not a latest-N sample or a reconstructed earlier state.'})
        from sqlglot import parse_one,exp
        try:
            tree=parse_one(q['text'],read='tsql')
            full_history=any(v.args.get('kind')=='ALL'for v in tree.find_all(exp.Version))
            minimum=bool(list(tree.find_all(exp.Min)))
            min_fields={e.alias_or_name.casefold()for e in tree.expressions if isinstance(e.this if isinstance(e,exp.Alias)else e,exp.Min)}
        except Exception:full_history=minimum=False
        if not(full_history and minimum):continue
        # Do not mislabel the oldest row in a truncated latest-N sample as the
        # beginning of retention. Prefer an explicit earliest/MIN aggregate.
        for row in q['result']['rows']:
            if not isinstance(row,dict):continue
            for key,value in row.items():
                if value is not None and key.casefold()in min_fields and re.search(r'(?:earliest|retention_start|oldest_available)',key,re.I):
                    retention.append({'evidence_id':q['id'],'field':key,'value':deepcopy(value),
                        'qualification':'Earliest retained time/version in the queried native ALL-history scope; not a reconstructed earlier value or a global retention guarantee.'})
    limitations=[]
    if outcome.get('status')!='ANSWERED':
        limitations.append(str(outcome.get('stop')or'No unique admitted target or validated cause was established.'))
    if any(f['status']=='NOT_CHECKED'for f in findings):limitations.append('Unmeasured layers remain unmeasured; no whole-chain conclusion is established.')
    if context.get('operational_status_only'):
        calculations=[{'name':'Request scope','expression':'Run status only; no quantity calculation was requested or claimed.','source':'ADMITTED_REQUEST_KIND'}]
    if not calculations:limitations.append('The calculation definition was not established in this run.')
    if not findings:limitations.append('No layer was admitted or read; no data finding is claimed.')
    question=outcome.get('question',{})
    business=((isinstance(question,dict)and question.get('reason')=='BUSINESS_POLICY')or outcome.get('question_reason')=='BUSINESS_POLICY'
              or isinstance(technical,dict)and technical.get('routing')=='BUSINESS_OWNER')
    routing={'to':'BUSINESS_OWNER'if business else'ENGINEER',
             'reason':'A business rule or intended meaning needs an owner decision.'if business else'Use the saved queries, scope and unresolved checks for the next technical step.'}
    return {'verdict':outcome.get('verdict')or(technical.get('verdict')if isinstance(technical,dict)else None)or'not established','findings_per_layer':findings,
            'calculation':calculations,'limitations':limitations,'routing':routing,'retention_limits':retention}


def text(value):
    parts=['Verdict: '+value['verdict'],'Findings per layer:']
    for layer in value['findings_per_layer']:
        observations=[]
        for row in layer['observations']:
            if row.get('status')=='OBSERVED':
                observations.append(row['evidence_id']+': '+json.dumps(row['rows_sample'],ensure_ascii=False,default=str)
                    +(' (sample only)'if row['sample_only']else'')+(' (truncated)'if row['truncated']else''))
            elif row.get('status')=='READ_FAILED':observations.append(row['evidence_id']+': read failed: '+row['reason'])
            else:observations.append(json.dumps({k:v for k,v in row.items()if k in ('status','value','scope','error','error_type')},ensure_ascii=False,default=str))
        parts.append(layer['name']+': '+('; '.join(observations)if observations else'not checked'))
    if not value['findings_per_layer']:parts.append('No layer was admitted or read; no data finding is claimed.')
    parts.append('Calculation: '+('; '.join(c['name']+' = '+c['expression'] for c in value['calculation'])or'not established from a retained definition.'))
    if value['retention_limits']:
        parts.append('Retention limit: '+'; '.join(str(r['field'])+' = '+str(r['value'])+' ('+r['evidence_id']+')' for r in value['retention_limits'])+'. Earlier values cannot be reconstructed from evidence that is unavailable; an empty history result is not proof of an earlier zero.')
    parts.append('Could not decide: '+('; '.join(value['limitations'])or'No additional limitation recorded; the cited finding remains scoped to these checks.'))
    parts.append('Routing: '+value['routing']['to'].replace('_',' ').lower()+'. '+value['routing']['reason'])
    return '\n'.join(parts)


def attach(outcome,*,queries=(),context=None,candidates=()):
    value=deepcopy(outcome);summary=report(outcome=value,queries=queries,context=context,candidates=candidates)
    value['investigation_report']=summary
    if isinstance(value.get('technical'),dict):value['technical']['investigation_report']=deepcopy(summary)
    body=text(summary)
    if isinstance(value.get('business'),dict):
        value['business']['text']=str(value['business'].get('text',''))+'\n\n'+body
    else:value['business']=str(value.get('business',''))+'\n\n'+body
    return value

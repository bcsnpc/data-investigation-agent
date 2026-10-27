"""Cited native values and engine-rendered questions at the user boundary.

These checks bind references and literal values. They do not pretend to prove
the semantic equivalence of arbitrary model-written calculations; independent
grading evaluates verdict, layer and causal interpretation.
"""
from copy import deepcopy
from decimal import Decimal,InvalidOperation
from .clarification_grounding import QUESTIONS,label


def leaves(value):
    if isinstance(value,dict):
        for child in value.values():yield from leaves(child)
    elif isinstance(value,list):
        for child in value:yield from leaves(child)
    else:yield value


def number(value):
    if value is None:return ('BLANK',None)
    if isinstance(value,bool):return ('OTHER',value)
    try:
        result=Decimal(str(value))
        if result.is_finite():return ('NUMBER',result)
    except InvalidOperation:pass
    return ('TEXT',str(value))


def cited(args,case):
    queries={q['id']:q for q in case['queries']}
    found=[]
    def native_query(record):
        if record['status']=='SUCCEEDED':
            return {'query_id':record['id'],'subject':record['layer'],'observed_at':record['time'],
                    'native_result':deepcopy(record['result']),'asset_ids':record.get('asset_ids',[])}
        if args.get('verdict','').casefold() in ('not found','unresolved','blocked'):
            return {'query_id':record['id'],'subject':record['layer'],'error':record.get('error')}
        raise ValueError('FAILED_QUERY_DOES_NOT_SUPPORT_TECHNICAL_FINDING')
    for identity in args['evidence_ids']:
        if identity in queries:
            found.append(native_query(queries[identity]));continue
        record=case['evidence'].get(identity)
        if record is None:raise ValueError('UNKNOWN_SUPPORT:'+identity)
        if record.get('kind')=='MODEL_RESPONSE' or record.get('rejected_tool'):
            raise ValueError('MODEL_OUTPUT_IS_NOT_NATIVE_SUPPORT')
        if record.get('kind')=='TRIAGE':
            facts=record.get('facts',{})
            rows=facts.get('facts',[]) if isinstance(facts,dict) else facts
            current=[f for f in rows if f.get('state') in ('OBSERVED','OBSERVED_NEGATIVE') and f.get('source') and f.get('observed_at')]
            if current:found.append({'facts':current})
        elif record.get('tool') in ('run_sql','run_dax'):
            value=record['result'];value=value.get('record',value)
            if value.get('id') not in queries:raise ValueError('QUERY_SUPPORT_NOT_RETAINED')
            found.append(native_query(queries[value['id']]))
        elif record.get('tool') in ('record_trace','list_candidates'):
            value=record['result']
            for check in value.get('layers',value.get('checks',[])):
                if check.get('query_id') in queries:found.append(native_query(queries[check['query_id']]))
        elif record.get('tool')=='get_evidence':
            value=record['result']
            if value.get('id') in queries:found.append(native_query(queries[value['id']]))
            else:raise ValueError('CITE_ORIGINAL_NATIVE_EVIDENCE_NOT_A_FETCH_WRAPPER')
        elif record.get('tool')=='get_definition':
            value=record['result']
            if value.get('content') and value.get('provenance'):found.append(value)
        elif record.get('tool') in ('get_job_runs','get_refresh_history','get_security_definitions'):
            value=record['result']
            if value.get('source') and value.get('observed_at') and value.get('status') not in ('UNAVAILABLE','BLOCKED_PENDING_OWNER'):
                found.append(value)
    if not found:raise ValueError('NO_NATIVE_OR_LEDGER_SUPPORT')
    return found


def finding(args,case):
    support=cited(args,case)
    if not args['verdict'].strip() or not args['cause'].strip():raise ValueError('VERDICT_AND_CAUSE_REQUIRED')
    source_consistency=args['verdict'].casefold().replace('_',' ').replace('-',' ') in ('as designed','consistent to source')
    if source_consistency:
        declaration=case['context'].get('system_of_record',{})
        source=declaration.get('layer')
        if declaration.get('declared') is not True or declaration.get('reachable') is not True or not source:
            raise ValueError('SOURCE_CONSISTENCY_UNESTABLISHED: no reachable declared system of record; report only the reached boundary or observed value')
        source_asset=declaration.get('asset_id')
        if source_asset and not any(item.get('subject')==source and source_asset in item.get('asset_ids',[]) for item in support):
            raise ValueError('SOURCE_CONSISTENCY_UNESTABLISHED: declared source object was not queried')
        compared={}
        for item in support:
            rows=item.get('native_result',{}).get('rows',[])
            if len(rows)==1 and isinstance(rows[0],dict) and len(rows[0])==1:
                compared.setdefault(item['subject'],set()).add(number(next(iter(rows[0].values()))))
        required=set(case['context'].get('layers',{}))|{source}
        record_consistency=False
        if case['intake'].get('issue_type') in ('RECORD_MISSING','EXTRA_OR_DUPLICATE_RECORD'):
            for identity in args['evidence_ids']:
                record=case['evidence'].get(identity,{})
                if record.get('tool')!='record_trace':continue
                trace=record.get('result',{});rows=trace.get('layers',[])
                established={row['layer']:(row['presence'],row.get('matching_rows')) for row in rows
                    if row.get('presence') in ('PRESENT','ABSENT') and not row.get('truncated')}
                if required<=established.keys() and len({established[layer] for layer in required})==1:
                    record_consistency=True;break
        if not record_consistency:
            if not required<=compared.keys():
                raise ValueError('SOURCE_CONSISTENCY_UNESTABLISHED: unread layers '+', '.join(sorted(required-compared.keys())))
            values=set().union(*(compared[layer] for layer in required))
            if len(values)!=1:raise ValueError('SOURCE_CONSISTENCY_UNESTABLISHED: compared native values differ')
        if not any(item.get('content') and item.get('provenance') for item in support):
            raise ValueError('AS_DESIGNED_NEEDS_RETAINED_DEFINITION: native equality alone does not explain the definition')
    # A response already supplied in the form is a reported value, never an
    # observed query value. Preserve its provenance in the technical output.
    actual={number(v) for record in support for v in leaves(record)}
    reported=case['intake'].get('reported_figure')
    if reported:
        actual.add(number(None if reported['state']=='EMPTY' else reported['value']))
    for value in args['numbers']:
        if isinstance(value,(dict,list)) or number(value) not in actual:
            raise ValueError('NUMBER_NOT_IN_CITED_RESULTS_OR_REPORTED_INPUT:'+str(value))
    path=case['context'].get('path',{})
    nodes=path.get('nodes',[]) if isinstance(path,dict) else []
    names={n['id']:n['label'] for n in nodes}
    names.update({i:l.get('label',i) for i,l in case['context'].get('layers',{}).items()})
    measured={q['layer'] for q in case['queries']}
    def subjects(value):
        if isinstance(value,dict):
            for key,child in value.items():
                if key in ('subject','node') and isinstance(child,str):yield child
                else:yield from subjects(child)
        elif isinstance(value,list):
            for child in value:yield from subjects(child)
    for record in support:measured.update(subjects(record))
    checked=[]
    for item in args['checked']:
        if item not in measured:raise ValueError('CHECKED_OBJECT_NOT_READ:'+item)
        checked.append(label([names.get(item,item)]))
    # No action/recommended-fix slot is rendered. Cause interpretation belongs
    # to the AI, must cite these native records and remains independently graded.
    displayed=['BLANK' if v is None else str(v) for v in args['numbers']]
    operational=[]
    business=args['verdict']+'. '+args['cause']
    if displayed:business+='\nNumbers: '+', '.join(displayed)+'.'
    if checked:business+='\nChecked: '+', '.join(checked)+'.'
    if args['verdict'] in ('failed job','waiting on job','latency'):
        # Reuse the existing renderer, using only the cited path observations.
        # No new reads, guessed run identity or model-authored operational data.
        facts=[]
        def collect(value):
            if isinstance(value,list):
                for item in value:collect(item)
            elif isinstance(value,dict):
                if {'subject','kind','state','value','observed_at'}<=set(value):facts.append(value)
                elif 'value' in value:collect(value['value'])
        for item in support:
            if 'facts' in item:collect(item['facts'])
        node_map={n['id']:n for n in nodes}
        eligible=[f for f in facts if f['subject'] in node_map and node_map[f['subject']]['kind'] in ('PIPELINE','COPY_ACTIVITY','NOTEBOOK')
            and f['state'] in ('OBSERVED','OBSERVED_NEGATIVE')]
        states={'failed job':{'FAILED'},'waiting on job':{'QUEUED','RUNNING'},'latency':set()}
        jobs=[f for f in eligible if f['kind']=='JOB_RUN' and f['value'].get('status') in states[args['verdict']]]
        if args['verdict']=='latency':jobs=[f for f in eligible if f['kind']=='SCHEDULE']
        from .operational_delivery import details
        rendered=[]
        for fact in jobs:
            schedule=next((f for f in eligible if f['kind']=='SCHEDULE' and f['subject']==fact['subject']),None)
            value=details({'verdict':args['verdict'],'operational_fact':fact,'operational_schedule':schedule},node_map)
            if value not in rendered:rendered.append(value)
        if not rendered:rendered=[details({'verdict':args['verdict']},node_map)]
        operational=rendered
        business+='\n'+'\n'.join(rendered)
    qualifications=[]
    if source_consistency:
        qualifications.append('The values were observed at their recorded query times; no common query-bound snapshot is claimed.')
        if record_consistency:
            qualifications.append('For this record, the source comparison covers key presence and matching row count; it does not establish equality of every field.')
    if reported and reported['state']=='NUMBER' and reported['precision']!='EXACT':
        qualifications.append('Comparison at the ticket’s stated digit precision '+str(reported['precision'])+
                              ' is weaker than an exact match; no tolerance was inferred.')
    qualifications.extend(case['context'].get('warnings',[]))
    for record in support:
        qualifications.extend(record.get('native_result',{}).get('warnings',[]))
    qualifications=list(dict.fromkeys(qualifications))
    if qualifications:business+='\n'+'\n'.join(qualifications)
    classification=args.get('classified_issue_type',case['intake'].get('classified_issue_type'))
    return {'business':business,'technical':{'verdict':args['verdict'],'cause':args['cause'],
        **({'operational_details':operational} if operational else {}),
        **({'original_issue_type':'SOMETHING_ELSE','classified_issue_type':classification}
           if case['intake'].get('issue_type')=='SOMETHING_ELSE' else {}),
        'numbers':deepcopy(args['numbers']),'checked':checked,'evidence_ids':args['evidence_ids'],
        'reported_input':deepcopy(reported),'queries':deepcopy(case['queries']),'qualifications':qualifications,
        'validation_scope':'CITED_RECORDS_AND_LITERAL_VALUES; causal interpretation is independently graded'}}


def question(args,case):
    cited(args,case)
    field=args.get('field') or ('BUSINESS_INTENT' if args['reason']=='BUSINESS_POLICY' else 'COMPARISON')
    if field not in QUESTIONS:raise ValueError('UNKNOWN_QUESTION_FIELD')
    picked={'REPORT':'report','PAGE':'page','VISUAL':'visual'}
    if field in picked and case['intake'].get(picked[field]):raise ValueError('QUESTION_REASKS_PICKED_FIELD')
    graph=case['context'].get('path',{})
    names={n['label'] for n in graph.get('nodes',[])} if isinstance(graph,dict) else set()
    names.update(case['context'].get('catalog_choice_names',[]))
    names.update({'A spreadsheet','My own count','Another source','I do not know',
                  'What the current rule does','Whether the business policy is intended'})
    choices=[]
    for choice in args['choices']:
        if choice not in names:raise ValueError('CHOICE_HAS_NO_CATALOG_OR_USER_FACT_TYPE')
        choices.append(label([choice]))
    if len(set(choices))!=len(choices):raise ValueError('CHOICES_NOT_DISTINGUISHABLE')
    # Discard model-authored premises. No invented duplicate count or internal
    # ID can enter this fixed question through a model-provided sentence.
    return {'question':QUESTIONS[field],'choices':choices,'checked_evidence':list(args['evidence_ids'])}

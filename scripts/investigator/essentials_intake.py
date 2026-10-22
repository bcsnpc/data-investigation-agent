"""Small, deterministic report/number intake; no values or causes are invented.

This additive contract is the Round 21 investigator's entry point. Historical
forms and model-only tickets keep their original interpretation and replay.
"""
from copy import deepcopy
import json
import re
import unicodedata

from jsonschema import Draft202012Validator
from .onboarding import digest
from .clarification_grounding import label

VERSION = 'investigator-essentials-v1'
TEXT = {'type':'string', 'minLength':1, 'maxLength':2000}
GOALS = ('COMPARE', 'FRESHNESS', 'DEFINITION')
COMPARISON = {'type':'object', 'additionalProperties':False,
              'properties':{'kind':{'enum':['REPORT','PAGE','SOURCE','SPREADSHEET','OWN_COUNT','EARLIER_VALUE']},
                            'reference':TEXT,'value':TEXT}, 'required':['kind','reference']}
SCHEMA = {'type':'object', 'additionalProperties':False,
          'properties':{'version':{'const':VERSION}, 'request_key':{**TEXT,'maxLength':100},
                        'report':TEXT, 'page':TEXT, 'number':TEXT, 'goal':{'enum':list(GOALS)},
                        'comparison':{'anyOf':[COMPARISON,{'type':'null'}]}, 'value':TEXT,
                        'description':{'type':'string','maxLength':16000},
                        'date':TEXT, 'filters':{'type':'array','maxItems':20,'items':{'type':'object'}},
                        'screenshot':TEXT},
          'required':['version','request_key','report','number','goal','comparison'],
          'allOf':[{'if':{'properties':{'goal':{'const':'COMPARE'}}},
                    'then':{'properties':{'comparison':COMPARISON}}}]}


def normalize(value):
    return ' '.join(re.findall(r'\w+',unicodedata.normalize('NFKC',value).casefold()))


def nodes(catalog):
    """Project retained definitions only; never select a convenient default visual."""
    result=[];seen=set()
    for model in catalog['models']:
        for report in model.get('reports',[]):
            result.append({'id':report['id'],'kind':'REPORT','names':[report['name']],
                           'model_id':model['id'],'report_id':report['id']})
        for visual in model.get('visuals',[]):
            key=(visual['report_id'],visual.get('page_id'))
            if visual.get('page_id') and key not in seen:
                seen.add(key)
                result.append({'id':visual['page_id'],'kind':'PAGE','names':visual.get('page_names',[]),
                               'model_id':model['id'],'report_id':visual['report_id'],'page_id':visual['page_id']})
            # A page name in visual.names is not a visual title. Retained collectors
            # historically include both. Strip only the exact page-name aliases.
            titles=[n for n in visual.get('names',[]) if n not in visual.get('page_names',[])]
            result.append({'id':visual['target_id'],'kind':'VISUAL','names':titles,
                           'model_id':model['id'],'report_id':visual['report_id'],
                           'page_id':visual.get('page_id'),'page_names':visual.get('page_names',[]),
                           'measure_ids':visual.get('measure_ids',[]),
                           'unsupported':visual.get('unsupported')})
        for measure in model.get('measures',[]):
            for report in model.get('reports',[]):
                visuals=[v for v in model.get('visuals',[]) if v['report_id']==report['id'] and measure['id'] in v.get('measure_ids',[])]
                if visuals:
                    result.append({'id':measure['id'],'kind':'MEASURE','names':[measure['name'],*measure.get('aliases',[])],
                                   'model_id':model['id'],'report_id':report['id'],
                                   'page_ids':sorted({v['page_id'] for v in visuals if v.get('page_id')})})
    return result


def rank(phrase, candidates, enrichment=()):
    """Confidence is a transparent lexical score, not a model probability."""
    wanted=normalize(phrase);rows=[]
    by_subject={}
    for row in enrichment:
        if (row.get('status') not in ('INFERRED','HUMAN_CONFIRMED')
                or row.get('stale_definition') is True or row.get('recording_class')=='RECORDED_STUB'):
            continue
        by_subject.setdefault(row['subject'],[]).append(row)
    for candidate in candidates:
        scores=[]
        if phrase==candidate['id']:scores.append((1.0,'EXPLICIT_SELECTED_ID',None))
        for name in candidate['names']:
            actual=normalize(name)
            if not actual:continue
            if actual==wanted:scores.append((1.0,'RETAINED_NAME',name))
            else:
                a,b=set(actual.split()),set(wanted.split())
                overlap=len(a&b)/len(a|b) if a|b else 0
                if overlap>=.5:scores.append((round(.5+.3*overlap,6),'PARTIAL_RETAINED_NAME',name))
        for entry in by_subject.get(candidate['id'],[]):
            for synonym in entry.get('synonyms',[]):
                if normalize(synonym)==wanted:
                    scores.append((.95 if entry['status']=='HUMAN_CONFIRMED' else .9,
                                   'ENRICHMENT_'+entry['status'],synonym))
        if not scores:continue
        score,source,matched=max(scores,key=lambda x:x[0])
        rows.append({**deepcopy(candidate),'confidence':score,'match_source':source,'matched_name':matched})
    return sorted(rows,key=lambda r:(-r['confidence'],r['id'],r.get('report_id','')))


def _hold(reason, **extra):
    return {'version':VERSION,'status':'HELD','reason':reason,'questions':[],
            'question_count':0,'investigation_executed':False,**extra}


def _pick(phrase, candidates, enrichment, field, questions_asked, catalog_hash):
    ranked=rank(phrase,candidates,enrichment)
    if not ranked or ranked[0]['confidence']<.8:
        return None,_hold(field.upper()+'_UNRESOLVED',candidates=ranked)
    tied=[r for r in ranked if r['confidence']==ranked[0]['confidence']]
    if len(tied)==1:return tied[0],None
    if questions_asked>=1:return None,_hold('AMBIGUITY_AFTER_ONE_QUESTION',field=field,candidates=ranked)
    try:
        choices=[]
        for row in tied:
            name=label(row['names'])
            if sum(label(other['names'])==name for other in tied)>1 and row['kind'] in ('VISUAL','MEASURE'):
                name += ' (visual on '+label(row['page_names'])+')' if row['kind']=='VISUAL' and row.get('page_names') else ' ('+row['kind'].lower()+')'
            choice={'key':digest({'field':field,'id':row['id'],'report':row.get('report_id')}),
                    'label':name,'node_id':row['id'],'kind':row['kind'],'catalog_hash':catalog_hash}
            if not any(c['key']==choice['key'] for c in choices):choices.append(choice)
        if len({c['label'] for c in choices})!=len(choices):
            return None,_hold('CANDIDATE_NAMES_NOT_DISTINGUISHABLE',field=field,candidates=ranked)
    except Exception as exc:
        return None,_hold('CANDIDATE_DISPLAY_NAME_UNAVAILABLE',field=field,error_type=type(exc).__name__)
    # The entire question, including its premise and choices, is code-rendered
    # from equal-ranked actual catalog nodes. No model-authored premise crosses.
    return None,{'version':VERSION,'status':'CLARIFYING','reason':'TIED_CATALOG_CANDIDATES',
                 'question_count':1,'investigation_executed':False,
                 'questions':[{'field':field,'text':'Which '+field+' do you mean?',
                               'choices':choices,'catalog_hash':catalog_hash}], 'candidates':ranked}


def admit(request, catalog, *, enrichment=(), questions_asked=0):
    """Return an admission or explicit held state. Never execute a query/model."""
    try:
        errors=sorted(Draft202012Validator(SCHEMA).iter_errors(request),key=lambda e:list(map(str,e.path)))
        if errors:
            return _hold('ESSENTIALS_INVALID_OR_MISSING',validation_errors=[{'path':list(e.path),'reason':e.message} for e in errors])
        if re.search(r'\b(intended value|business correctness|business rule decision|(?:should|ought to) (?:we |it )?(?:count|include))\b',request.get('description',''),re.I):
            return _hold('BUSINESS_INTENT_REQUIRES_OWNER')
        if type(questions_asked) is not int or questions_asked not in (0,1):
            return _hold('QUESTION_BUDGET_INVALID')
        projected=nodes(catalog);catalog_hash=digest(catalog)
        report,result=_pick(request['report'],[n for n in projected if n['kind']=='REPORT'],enrichment,'report',questions_asked,catalog_hash)
        if result:return result
        eligible=[n for n in projected if n.get('report_id')==report['id']]
        page=None
        if request.get('page'):
            page,result=_pick(request['page'],[n for n in eligible if n['kind']=='PAGE'],enrichment,'page',questions_asked,catalog_hash)
            if result:return result
            eligible=[n for n in eligible if n.get('page_id')==page['id'] or page['id'] in n.get('page_ids',[])]
        number,result=_pick(request['number'],[n for n in eligible if n['kind'] in ('VISUAL','MEASURE')],enrichment,'number',questions_asked,catalog_hash)
        if result:return result
        if number.get('unsupported') or number['kind']=='VISUAL' and not number.get('measure_ids'):
            return _hold('TARGET_NOT_EXECUTABLE',target=number)
        # A named measure is a measure anchor. Do not replace it with a visual,
        # infer TOTAL, create a cell address, or choose a saved filter context.
        figure={'state':'UNSPECIFIED'}
        if request.get('value'):
            from . import reported_figure
            from .intake_statement_registry import empty_matches
            text=request['value'];source={'start':0,'end':len(text),'quote':text}
            if empty_matches(text):
                if re.search(r'\d',text):return _hold('REPORTED_EMPTY_AND_NUMBER_CONFLICT')
                figure={'state':'EMPTY','source':source}
            else:
                value,precision=reported_figure.stated(text)
                figure={'state':'NUMBER','value':value,'precision':precision,'source':source}
            reported_figure.validate(figure,text)
        supplied_filters=deepcopy(request.get('filters',[]))
        model=next(m for m in catalog['models'] if m['id']==report['model_id'])
        columns={c['column_id']:c for c in model.get('columns',[])}
        from .filter_scope import compile_filter
        for spec in supplied_filters:
            column=columns.get(spec.get('column_id'))
            if column is None:
                return _hold('FILTER_COLUMN_UNRESOLVED',supplied_filters=supplied_filters)
            try:
                compile_filter(spec,{'dataType':column['data_type']},'validated_reference')
            except (ValueError,TypeError,KeyError) as exc:
                return _hold('FILTER_RESTRICTION_INVALID',cause={'type':type(exc).__name__,'message':str(exc)})
        return {'version':VERSION,'status':'READY','question_count':0,'questions':[],
                'reason':'ESSENTIALS_BOUND','investigation_executed':False,
                'catalog_hash':catalog_hash,'request_hash':digest(request),'goal':request['goal'],
                'scope':{'model_id':report['model_id'],'report_id':report['id'],
                         'page_id':page['id'] if page else None,'node_id':number['id'],
                         'node_kind':number['kind'],'target_id':number['id'] if number['kind']=='VISUAL' else None,
                         'measure_ids':number.get('measure_ids',[number['id']])},
                'reported_figure':figure,'comparison':deepcopy(request['comparison']),
                'filters':supplied_filters,'filters_authority':'USER_SUPPLIED_NOT_LOWER_PATH_ATTESTATION',
                'selected_number':number,'date':request.get('date'),'screenshot':request.get('screenshot'),
                'description':request.get('description','')}
    except Exception as exc:
        # Preserve the submitted ticket and exact code cause in the API record;
        # never turn an internal exception into a user ambiguity or lost ticket.
        return _hold('INTAKE_INTERNAL_ERROR',cause={'type':type(exc).__name__,'message':str(exc)})


def goal_from_text(text):
    lowered=text.casefold()
    if re.search(r'\b(refresh|refreshed|current|latest|up to date)\b',lowered):return 'FRESHNESS'
    if re.search(r'\b(definition|included|calculated|represent|meaning|what.*counts)\b',lowered):return 'DEFINITION'
    return 'COMPARE'


def _named_span(text, candidates):
    matches=[]
    for candidate in candidates:
        for name in candidate['names']:
            found=re.search(r'(?<!\w)'+re.escape(name)+r'(?!\w)',text,re.I)
            if found:matches.append((len(name),found.start(),found.group()))
    return max(matches,key=lambda x:(x[0],-x[1]))[2] if matches else None


def retained_text(text, catalog, *, request_key):
    """Offline compatibility adapter: exact named spans only, no made-up picks.

    Historical free-text tickets are not magically complete new forms. Missing
    essentials remain missing; definition/freshness have no numeric comparator.
    """
    goal=goal_from_text(text)
    if goal=='COMPARE':return _hold('MISSING_COMPARISON',goal=goal)
    try:
        projected=nodes(catalog)
        report=_named_span(text,[n for n in projected if n['kind']=='REPORT'])
        if report is None:return _hold('MISSING_REPORT',goal=goal)
        report_candidates=rank(report,[n for n in projected if n['kind']=='REPORT'])
        # A tied report remains a genuine candidate question; never choose an
        # estate solely because the scorer knows which one a ticket meant.
        scope_ids={r['id'] for r in report_candidates if r['confidence']==report_candidates[0]['confidence']}
        scoped=[n for n in projected if n.get('report_id') in scope_ids]
        number=_named_span(text,[n for n in scoped if n['kind'] in ('VISUAL','MEASURE')])
        if number is None:return _hold('MISSING_NUMBER',goal=goal)
        page=_named_span(text,[n for n in scoped if n['kind']=='PAGE'])
        request={'version':VERSION,'request_key':request_key,'report':report,'number':number,
                 'goal':goal,'comparison':None,'description':text}
        if page:request['page']=page
        result=admit(request,catalog)
        result['submitted_essentials']=request
        return result
    except Exception as exc:
        return _hold('INTAKE_INTERNAL_ERROR',cause={'type':type(exc).__name__,'message':str(exc)})


def submit(workspace, request):
    """Durable API boundary: retain every input/result, including internal holds."""
    if workspace.agent.config.get('_estate',{}).get('recording',{}).get('tape_class')=='PRIVACY_PROJECTED':
        return _hold('ESSENTIALS_PROJECTED_PERSISTENCE_UNAVAILABLE')
    try:
        from .question_intake import snapshot
        catalog=snapshot(workspace)
        entries=getattr(workspace,'enrichment_entries',lambda:[])()
        result=admit(request,catalog,enrichment=entries)
    except Exception as exc:
        result=_hold('INTAKE_INTERNAL_ERROR',cause={'type':type(exc).__name__,'message':str(exc)})
    from .onboarding import encoded
    record={'request':deepcopy(request),'result':result}
    with workspace.store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS workspace_essentials (identity TEXT PRIMARY KEY, body TEXT NOT NULL, body_hash TEXT NOT NULL)')
        identity=digest(request)
        result['intake_id']=identity
        prior=db.execute('SELECT body,body_hash FROM workspace_essentials WHERE identity=?',(identity,)).fetchone()
        if prior is not None:
            prior_body=json.loads(prior[0])
            if digest(prior_body)!=prior[1]:raise ValueError('ESSENTIALS_RECORD_HASH_DIFFERS')
            return prior_body['result']
        db.execute('INSERT INTO workspace_essentials VALUES(?,?,?)',(identity,encoded(record),digest(record)))
    return result


def reply(workspace, identity, request):
    """One catalog-grounded choice, with the original question/input retained."""
    from .onboarding import encoded, Conflict
    if not isinstance(request,dict) or set(request)!={'choice_key','request_key'}:
        return _hold('CLARIFICATION_REPLY_INVALID')
    with workspace.store.connect() as db:
        saved=db.execute('SELECT body,body_hash FROM workspace_essentials WHERE identity=?',(identity,)).fetchone()
    if saved is None:return _hold('INTAKE_NOT_FOUND')
    record=json.loads(saved[0])
    if digest(record)!=saved[1]:raise ValueError('ESSENTIALS_RECORD_HASH_DIFFERS')
    if record.get('reply'):
        return record['result'] if record['reply']==request else _hold('CLARIFICATION_ALREADY_USED')
    old=record['result'];questions=old.get('questions',[])
    if old['status']!='CLARIFYING' or len(questions)!=1:
        return _hold('NO_OPEN_CLARIFICATION')
    question=questions[0]
    choices=[c for c in question['choices'] if c['key']==request['choice_key']]
    if len(choices)!=1:return _hold('CLARIFICATION_CHOICE_NOT_OFFERED')
    try:
        from .question_intake import snapshot
        catalog=snapshot(workspace)
        if digest(catalog)!=question['catalog_hash']:
            result=_hold('CATALOG_CHANGED_DURING_CLARIFICATION')
        else:
            bound=deepcopy(record['request']);bound[question['field']]=choices[0]['node_id']
            result=admit(bound,catalog,enrichment=getattr(workspace,'enrichment_entries',lambda:[])(),questions_asked=1)
    except Exception as exc:
        result=_hold('INTAKE_INTERNAL_ERROR',cause={'type':type(exc).__name__,'message':str(exc)})
    result.update(intake_id=identity,questions_asked_total=1)
    updated={**record,'original_question':question,'reply':deepcopy(request),'result':result}
    with workspace.store.connect() as db:
        current=db.execute('SELECT body_hash FROM workspace_essentials WHERE identity=?',(identity,)).fetchone()
        if current is None or current[0]!=saved[1]:raise Conflict('Essentials intake changed; reload before replying')
        db.execute('UPDATE workspace_essentials SET body=?,body_hash=? WHERE identity=?',(encoded(updated),digest(updated),identity))
    return result

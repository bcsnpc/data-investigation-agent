"""Consequential claim questions and interpretation, rendered from actual facts."""
import re
from .onboarding import digest
from .clarification_grounding import label


def catalog_projection(catalog):
    result={'hash':digest(catalog),'models':catalog['models'],'reports':[],'pages':[],'visuals':[],'metrics':[]}
    seen=set()
    for model in catalog['models']:
        for m in model.get('measures',[]):result['metrics'].append({'id':m['id'],'model_id':model['id'],'label':label([m['name']])})
        for report in model.get('reports',[]):result['reports'].append({'id':report['id'],'model_id':model['id'],'label':label([report['name']])})
        for v in model.get('visuals',[]):
            page=v.get('page_id');key=(v['report_id'],page)
            if page and key not in seen:
                result['pages'].append({'id':page,'report_id':v['report_id'],'model_id':model['id'],'label':label(v.get('page_names',[]))});seen.add(key)
            result['visuals'].append({'id':v['target_id'],'model_id':model['id'],'report_id':v['report_id'],'page_id':page,
                'label':label(v.get('names',[])),'measure_ids':v['measure_ids']})
    return result


def scope_columns(scope,catalog,binding=None):
    """Only a uniquely retained column in the selected model is executable."""
    entries=binding.get('bindings',[])if binding and binding.get('kind')=='MULTIPLE'else[binding]if binding else[]
    model_ids={item['model_id']for item in entries}
    if scope.get('model_id'):model_ids.add(scope['model_id'])
    if not model_ids and scope.get('report_id'):
        model_ids={model['id']for model in catalog['models']if any(r['id']==scope['report_id']for r in model.get('reports',[]))}
    result={}
    for field in ('field_id','dimension_id'):
        if field not in scope:continue
        if not isinstance(scope[field],str)or not scope[field]:raise ValueError('Claim column identity must be a nonempty string')
        columns=[(model,column)for model in catalog['models']for column in model.get('columns',[])if column.get('column_id')==scope[field]]
        if len(columns)!=1 or model_ids and columns[0][0]['id']not in model_ids:
            raise ValueError('Claim column is unknown or outside the selected model')
        result[field]=label([columns[0][1]['name']])
    return result


def resolve_scope(fact,catalog,context=None):
    """Resolve only actual visible names inside the user's extracted scope span."""
    value=dict(context or {},**fact['value']);phrase=value.get('phrase','')
    if not phrase:return None
    projection=catalog_projection(catalog)
    def matches(name):return re.search(r'(?<!\w)'+re.escape(name)+r'(?!\w)',phrase,re.I)is not None
    reports=[r for r in projection['reports']if (r['label'].casefold()==value['report_phrase'].casefold()if value.get('report_phrase')else matches(r['label']))]
    selected=value.get('report_id')or(reports[0]['id']if len(reports)==1 else None)
    pages=[p for p in projection['pages']if matches(p['label'])and(not selected or p['report_id']==selected)]
    page=value.get('page_id')or(pages[0]['id']if len(pages)==1 else None)
    visuals=[v for v in projection['visuals']if matches(v['label'])and(not selected or v['report_id']==selected)and(not page or v['page_id']==page)]
    resolved={'kind':value['kind']}
    if selected:resolved['report_id']=selected
    if page:resolved['page_id']=page
    if visuals and value['kind']=='VISUALS':resolved['visual_ids']=[v['id']for v in visuals]
    if len(resolved)==1:return None
    from .claim_facts import fact as make
    return make('scope',resolved,{'kind':'CATALOG_NAME_RESOLUTION','catalog_hash':digest(catalog),'source_fact_id':fact['id']},authority=fact['authority'])


def candidates(settled,catalog,glossary=None):
    scope=settled.get('scope')or{};phrases=[m['phrase']for m in settled.get('metric',[])]
    result=[];glossary_phrases=set()
    if glossary:
        for phrase in phrases:
            resolved=glossary.resolve(phrase,catalog['models'])
            if resolved:glossary_phrases.add(phrase)
            for candidate in resolved:
                if scope.get('model_id')and candidate['model_id']!=scope['model_id']:continue
                model=next((m for m in catalog['models']if m['id']==candidate['model_id']),None)
                if model is None:continue
                vs=[v for v in model.get('visuals',[])if candidate.get('measure_id')in v['measure_ids']and(not candidate.get('report_id')or v['report_id']==candidate['report_id'])and(not candidate.get('page_id')or v.get('page_id')==candidate['page_id'])and(not candidate.get('target_ids')or v['target_id']in candidate['target_ids'])and(not scope.get('report_id')or v['report_id']==scope['report_id'])and(not scope.get('page_id')or v.get('page_id')==scope['page_id'])and(not scope.get('visual_ids')or v['target_id']in scope['visual_ids'])]
                if (scope.get('report_id')or scope.get('page_id')or scope.get('visual_ids'))and not vs:continue
                candidate=dict(candidate,metric_phrase=phrase,report_id=scope.get('report_id',candidate.get('report_id')),page_id=scope.get('page_id',candidate.get('page_id')),target_ids=[v['target_id']for v in vs]);result.append(candidate)
    for model in catalog['models']:
        if scope.get('model_id')and model['id']!=scope['model_id']:continue
        visuals=[v for v in model.get('visuals',[]) if
            (not scope.get('report_id')or v['report_id']==scope['report_id'])and
            (not scope.get('page_id')or v.get('page_id')==scope['page_id'])and
            (not scope.get('visual_ids')or v['target_id']in scope['visual_ids'])]
        eligible={i for v in visuals for i in v['measure_ids']}if scope.get('report_id')or scope.get('page_id')else None
        for measure in model.get('measures',[]):
            names=[measure['name'],*measure.get('aliases',[])]
            matched=any(re.sub(r'\W+',' ',phrase).strip().casefold()in
                [re.sub(r'\W+',' ',n).strip().casefold()for n in names]for phrase in phrases if phrase not in glossary_phrases)
            if matched and(eligible is None or measure['id']in eligible):
                targets=[v for v in visuals if measure['id']in v['measure_ids']]
                result.append({'model_id':model['id'],'measure_id':measure['id'],
                    'report_id':scope.get('report_id'),'page_id':scope.get('page_id'),
                    'target_ids':[v['target_id']for v in targets],'label':label([measure['name']]),
                    'evidence_ids':['catalog:'+digest(catalog)],'status':'INFERRED','metric_phrase':next(phrase for phrase in phrases if phrase not in glossary_phrases and re.sub(r'\W+',' ',phrase).strip().casefold()in[re.sub(r'\W+',' ',n).strip().casefold()for n in names])})
    unique={}
    for c in result:
        key=digest({k:c.get(k)for k in('model_id','measure_id','report_id','page_id','target_ids')})
        if key not in unique or c.get('status')=='CONFIRMED':unique[key]=c
    return list(unique.values())


def question(field,text,choices,catalog_hash,fact_ids):
    # Value semantics remain private; only retained visible names cross display.
    labels=[c[0]for c in choices]
    if any(label([n])!=n for n in labels):raise ValueError('Claim choice is not a retained visible name')
    if len(set(labels))!=len(labels):raise ValueError('Claim choice labels are not distinguishable')
    q={'field':field,'question':text,'choices':[{'id':digest(value),'label':name}for name,value in choices],
        'grounding':{'catalog_hash':catalog_hash,'fact_ids':fact_ids}}
    q['id']=digest(q)
    return q,{digest(value):value for _,value in choices}


def plan(claim,catalog):
    s=claim['settled'];facts=[f['id']for f in claim['facts']];scope=s.get('scope')or{};direction=s.get('direction')
    is_page=scope.get('kind')in('PAGE','REPORT','VISUALS')
    conflicts=claim['conflicts']
    if conflicts:return question(conflicts[0],'Which description should we use for this investigation?',[],digest(catalog),facts)
    binding=claim.get('selected_binding');rows=claim['candidate_bindings']
    if not binding and not(direction=='STALE'and scope.get('kind')in('PAGE','REPORT')):
        if len(rows)==1:binding=rows[0]
        elif len(s.get('metric',[]))>1 and scope.get('kind')in('VISUALS','PAGE','REPORT'):
            selected=[]
            for metric in s['metric']:
                matches=[r for r in rows if r.get('metric_phrase')==metric['phrase']]
                if len(matches)!=1:break
                selected.append(matches[0])
            if len(selected)==len(s['metric']):
                binding={'kind':'MULTIPLE','bindings':selected,'target_ids':list(dict.fromkeys(t for r in selected for t in r.get('target_ids',[]))),'label':', '.join(r['label']for r in selected)}
            else:
                return question('binding','Which retained definitions should represent the metrics you named?',[(r['label'],{'binding':r})for r in rows],digest(catalog),facts)
        else:
            choices=[(r['label'],{'binding':r})for r in rows]
            return question('binding'if s.get('metric')else'metric','Which retained definition should represent the metric you named?'if s.get('metric')else'Which business metric do you mean?',choices,digest(catalog),facts)
    if not s.get('comparator')and direction not in('STALE','DEFINITION'):
        return question('comparator','What are you comparing against?',[
            ('My own count',{'comparator':'OWN_COUNT'}),('The source application',{'comparator':'APPLICATION'}),
            ('Another report',{'comparator':'OTHER_REPORT'}),('No other comparison',{'comparator':'NONE'})],digest(catalog),facts)
    if not scope or scope.get('kind')=='UNKNOWN':
        return question('scope','Does the issue concern records, particular visuals, the page, or the report?',[
            ('Particular records',{'scope':{'kind':'RECORDS'}}),('One or more visuals',{'scope':{'kind':'VISUALS'}}),
            ('The page',{'scope':{'kind':'PAGE'}}),('The report',{'scope':{'kind':'REPORT'}})],digest(catalog),facts)
    if is_page and not scope.get('report_id'):
        visible=catalog_projection(catalog)
        return question('report_binding'if scope.get('report_phrase')else'report',('Which retained report matches the report you named?'if scope.get('report_phrase')else'Which report is this about?'),[(r['label'],{'report_id':r['id']})for r in visible['reports']],digest(catalog),facts)
    if scope.get('kind')in('PAGE','VISUALS')and not scope.get('page_id'):
        visible=catalog_projection(catalog)
        pages=[p for p in visible['pages']if p['report_id']==scope.get('report_id')]
        return question('page_binding'if scope.get('page_phrase')else'page',('Which retained page matches the page you named?'if scope.get('page_phrase')else'Which page is this about?'),[(p['label'],{'page_id':p['id']})for p in pages],digest(catalog),facts)
    if scope.get('kind')=='VISUALS'and not scope.get('visual_ids')and binding and len(binding.get('target_ids',[]))>1:
        visible=catalog_projection(catalog);targets=[v for v in visible['visuals']if v['id']in binding['target_ids']]
        choices=[(v['label'],{'scope':{'kind':'VISUALS','visual_ids':[v['id']]}})for v in targets]
        if scope.get('page_id'):choices.append(('All matching visuals on this page',{'scope':{'kind':'VISUALS','visual_ids':[v['id']for v in targets]}}))
        return question('targets','Which visible objects are included in this claim?',choices,digest(catalog),facts)
    if scope.get('kind')=='RECORDS'and not s.get('examples')and direction not in ('MORE','WRONG_BREAKDOWN'):
        return question('examples','Can you give one missing, extra, or wrong record as an example?',[],digest(catalog),facts)
    # A freshness/page complaint never needs a single displayed figure. Values
    # already supplied remain facts, but do not manufacture a reproduction.
    if direction is None:
        return question('direction','Is it less, more, different, stale, or a definition question?',[
            ('Less or missing',{'direction':'LESS'}),('More or extra',{'direction':'MORE'}),
            ('Different',{'direction':'DIFFERENT'}),('Stale or not up to date',{'direction':'STALE'}),
            ('A definition question',{'direction':'DEFINITION'})],digest(catalog),facts)
    return None,binding


def interpretation(claim,catalog):
    s=claim['settled'];binding=claim.get('selected_binding')or{}
    phrases=[m['phrase']for m in s.get('metric',[])];name=binding.get('label')or', '.join(phrases)or'this page'
    parts=['You are asking about '+name+'.']
    if binding and phrases:parts.append("By '"+"', '".join(phrases)+"', you mean "+name+'.')
    for value in s.get('observation',[]):
        if value['role']=='CONTEXT':continue
        f=value['figure'];number='an empty result'if f['state']=='EMPTY'else f.get('source',{}).get('quote',f.get('value','not stated'))
        parts.append(('You observed 'if value['role']=='OBSERVED'else'You expected ')+str(number)+'.')
    scope=s.get('scope')or{};projection=catalog_projection(catalog)
    if scope.get('model_id'):
        models=[m for m in catalog['models']if m['id']==scope['model_id']]
        if len(models)!=1:raise ValueError('Interpretation names an unknown model')
        parts.append('Using '+label([models[0].get('name','Selected semantic model')])+'.')
    for field,name in scope_columns(scope,catalog,binding).items():
        parts.append(('Field to trace: 'if field=='field_id'else'Breakdown by: ')+name+'.')
    for field,rows in(('report_id',projection['reports']),('page_id',projection['pages'])):
        if scope.get(field):
            matches=[r for r in rows if r['id']==scope[field]]
            if len(matches)!=1:raise ValueError('Interpretation names an unknown or ambiguous container')
            parts.append('On '+matches[0]['label']+'.')
    targets=scope.get('visual_ids')or binding.get('target_ids',[])
    if scope.get('kind')=='VISUALS'and targets:
        names=[v['label']for v in projection['visuals']if v['id']in targets]
        if len(names)!=len(set(targets)):raise ValueError('Interpretation cannot render unknown targets')
        parts.append('Visible objects: '+', '.join(names)+'.')
        if len(targets)>1:parts.append('The scope includes all '+str(len(targets))+' selected visuals.')
    if s.get('direction')=='STALE':parts.append('The question is whether it is up to date, not whether a single figure reproduces.')
    direction_labels={'LESS':'less or missing','MORE':'more or extra','DIFFERENT':'different','STALE':'stale','DEFINITION':'a definition question','WRONG_BREAKDOWN':'a wrong breakdown','CONTEXT':'filter or security context','FIELD_WRONG':'a record with a wrong field','UNKNOWN':'not yet specified'}
    comparator_labels={'OWN_COUNT':'your own count','APPLICATION':'the source application','OTHER_REPORT':'another report','SPREADSHEET':'a spreadsheet','FINANCE':'a finance figure','NONE':'no other comparison','UNKNOWN':'not yet specified'}
    def display(value):
        if isinstance(value,list):return '; '.join(display(item)for item in value)
        if isinstance(value,dict):
            if 'column_id'in value:
                names=[c['name']for m in catalog['models']for c in m.get('columns',[])if c.get('column_id')==value['column_id']]
                if len(set(names))!=1:raise ValueError('Cannot render unknown filter column')
                if set(value)-{'column_id','operator','value'}:raise ValueError('Cannot render unsupported filter fields')
                operators={'EQ':'equals','IN':'is one of','NE':'does not equal','GT':'is greater than','LT':'is less than','GE':'is at least','LE':'is at most'}
                if value.get('operator')not in operators:raise ValueError('Cannot render unknown filter operation')
                return names[0]+' '+operators[value['operator']]+' '+display(value.get('value'))
            if set(value)=={'phrase'}:return str(value['phrase'])
            raise ValueError('Structured context has no visible-label renderer')
        return str(value)
    if s.get('direction'):parts.append('Direction: '+direction_labels[s['direction']]+'.')
    if s.get('comparator'):parts.append('Compared with '+comparator_labels[s['comparator']]+'.')
    for field,title in(('time','Time'),('filters','Visible filters'),('examples','Example records'),('guessed_cause','Your suggested cause, not an established finding'),('when_last_right','When last correct')):
        if field in s:parts.append(title+': '+display(s[field])+'.')
    scope_labels={'RECORDS':'particular records','VISUALS':'the selected visuals','PAGE':'the page','REPORT':'the report','UNKNOWN':'not yet specified'}
    parts.append('Scope: '+scope_labels[scope.get('kind','UNKNOWN')]+'.')
    parts.append('Is this interpretation correct?')
    return {'text':' '.join(parts),'fact_ids':[f['id']for f in claim['facts']]}


def validate_question(claim,q):
    """A consequential question must not request a fact already established."""
    field=q['field'];s=claim['settled'];scope=s.get('scope')or{}
    if field in claim['conflicts']or field in('binding','report_binding','page_binding','current_target','correction'):return
    if field=='report'and(scope.get('report_id')or scope.get('report_phrase'))or field=='page'and(scope.get('page_id')or scope.get('page_phrase')):
        raise ValueError('CLAIM_QUESTION_REASKS_SETTLED_FACT')
    if field in s and s[field]not in(None,[],'UNKNOWN'):
        raise ValueError('CLAIM_QUESTION_REASKS_SETTLED_FACT')

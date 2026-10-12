"""Additive claim-first controller; confirmation creates a plan, never a finding."""
import copy,json
from .onboarding import digest,encoded,Conflict
from .process_tape import event,uuid4
from .run_recording import operation
from . import claim_facts as facts,claim_clarification as policy

class ClaimIntake:
    def __init__(self,workspace):
        self.workspace=workspace;self.store=workspace.store
        with self.store.connect()as db:
            db.execute('CREATE TABLE IF NOT EXISTS claim_intakes(id TEXT PRIMARY KEY,request_key TEXT UNIQUE,request_hash TEXT,revision INTEGER,body TEXT,body_hash TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS claim_revisions(id TEXT,revision INTEGER,body TEXT,body_hash TEXT,PRIMARY KEY(id,revision))')

    def _guard(self):
        if self.workspace.agent.config.get('_estate',{}).get('recording',{}).get('tape_class')=='PRIVACY_PROJECTED':
            raise Conflict('CLAIM_PROJECTED_CAPTURE_UNAVAILABLE: no raw fallback is permitted')

    def _catalog(self):
        from .question_intake import snapshot
        return snapshot(self.workspace)

    def catalog(self):return policy.catalog_projection(self._catalog())

    def _load(self,db,id):
        row=db.execute('SELECT revision,body,body_hash FROM claim_intakes WHERE id=?',(id,)).fetchone()
        if row is None:raise KeyError('Claim not found')
        body=json.loads(row[1])
        if digest(body)!=row[2]or body['id']!=id:raise Conflict('Claim state integrity differs')
        return row[0],body

    def _public(self,body):
        result={k:copy.deepcopy(body[k])for k in ('id','revision','status','claim','questions','interpretation','engine_admission','history')}
        from .agent_handoff import settings
        if settings(self.workspace)['enabled']:
            from .claim_handoff import ClaimHandoff
            handoff=ClaimHandoff(self.workspace).get(body['id'])
            if handoff is not None:result['automatic_handoff']=handoff
        return result

    def _after_pipeline(self,body,result=None):
        from .claim_handoff import maybe
        handoff=maybe(self.workspace,body,result)
        if handoff is not None:
            with self.store.connect()as db:_,body=self._load(db,body['id'])
        return self._public(body)

    def get(self,id):
        with self.store.connect()as db:_,body=self._load(db,id)
        return self._public(body)

    def _persist(self,db,body):
        event('CONFIGURATION',{'claim_intake':'REVISION','id':body['id'],'revision':body['revision'],'body':body})
        db.execute('UPDATE claim_intakes SET revision=?,body=?,body_hash=? WHERE id=?',(body['revision'],encoded(body),digest(body),body['id']))
        db.execute('INSERT INTO claim_revisions VALUES(?,?,?,?)',(body['id'],body['revision'],encoded(body),digest(body)))

    def _plan(self,body,catalog):
        claim=body['claim']
        for original in list(claim['facts']):
            if original['field']=='scope'and not original.get('superseded_by'):
                derived=facts.resolve_native_scope(original,catalog)
                if derived is not None:
                    original['superseded_by']=derived['id']
                    claim['facts']=facts.merge(claim['facts'],[derived])
        texts={d['hash']:d.get('request',{}).get('text','')for d in body.get('documents',[])}
        for original in list(claim['facts']):
            if original.get('superseded_by'):continue
            source=original['source'];document=source.get('document_id')
            text=texts.get(document,'')
            derived=facts.location_fact(original,text)
            if derived is not None:
                original['superseded_by']=derived['id'];claim['facts']=facts.merge(claim['facts'],[derived])
        for _ in range(2):
            established=facts.settled(claim['facts'])[0]
            context=dict(established.get('location')or{},**(established.get('scope')or{}))
            resolved=[policy.resolve_scope(f,catalog,context)for f in claim['facts']if f['field']in('scope','location')and not f.get('superseded_by')]
            claim['facts']=facts.merge(claim['facts'],[f for f in resolved if f])
        claim['settled'],claim['conflicts']=facts.settled(claim['facts'])
        settled=claim['settled'];scope=policy.merge_location_scope(settled)
        projected=policy.catalog_projection(catalog)
        if scope.get('model_id')and not any(m['id']==scope['model_id']for m in catalog['models']):raise ValueError('Claim names an unknown model')
        if scope.get('model_id')and scope.get('report_id')and not any(r['id']==scope['report_id']and r['model_id']==scope['model_id']for r in projected['reports']):raise ValueError('Claim report is outside selected model')
        for key,rows in (('report_id',projected['reports']),('page_id',projected['pages'])):
            if scope.get(key)and not any(r['id']==scope[key]for r in rows):raise ValueError('Claim names an unknown '+key)
        if scope.get('page_id')and scope.get('report_id')and not any(p['id']==scope['page_id']and p['report_id']==scope['report_id']for p in projected['pages']):raise ValueError('Claim page is outside selected report')
        for target in scope.get('visual_ids',[]):
            if not any(v['id']==target and(not scope.get('report_id')or v['report_id']==scope['report_id'])and(not scope.get('page_id')or v['page_id']==scope['page_id'])for v in projected['visuals']):raise ValueError('Claim visual is outside selected page')
        selected=claim.get('selected_binding')
        for selected in (selected.get('bindings',[])if selected and selected.get('kind')=='MULTIPLE'else[selected]if selected else[]):
            model=next((m for m in catalog['models']if m['id']==selected['model_id']),None)
            if model is None or selected.get('measure_id')and not any(m['id']==selected['measure_id']for m in model.get('measures',[]))or any(t not in {v['target_id']for v in (model or {}).get('visuals',[])}for t in selected.get('target_ids',[])):
                raise ValueError('The retained definition target is no longer available')
        glossary=getattr(self.workspace,'claim_glossary',None)
        if glossary:glossary.seed_catalog(catalog['models'])
        claim['candidate_bindings']=policy.candidates(claim['settled'],catalog,glossary)+claim.get('screenshot_candidates',[])
        # Exact candidate addresses can establish location without selecting a
        # visual. Distinct pages/reports remain an actual location question.
        rows=claim['candidate_bindings']
        scope=policy.candidate_location(scope,catalog,rows)
        if scope:settled['scope']=scope
        groups=[]
        for phrase in settled.get('metric',[]):
            matches=[r for r in rows if r.get('metric_phrase')==phrase['phrase']]
            if len(matches)==1:groups.append(copy.deepcopy(matches[0]))
        numeric=[copy.deepcopy(f)for f in claim['facts']if f['field']=='observation'and not f.get('superseded_by')and f['value'].get('role')=='OBSERVED'and
            (f['value']['figure']['state']in('NUMBER','EMPTY')or f['value'].get('quantity_structure',{}).get('kind')=='MULTIPLE_QUANTITIES')]
        if(scope.get('kind')=='METRIC'or scope.get('kind')=='VISUALS'and not scope.get('visual_ids'))and groups and all(g.get('target_ids')for g in groups)and len(groups)==len(settled.get('metric',[])):
            body['planning_request']={'kind':'METRIC_VISUAL_CHECKS','catalog_hash':digest(catalog),
                'groups':groups,'reported_observations':numeric,'purpose':'CONSISTENCY_AND_FIGURE_ATTRIBUTION',
                'status':'AWAITING_CONFIRMED_CANDIDATE_CHECKS'}
        elif numeric and scope.get('report_id')and scope.get('page_id'):
            matching_groups=copy.deepcopy(rows)
            if not rows:
                # A stated figure with an established location may be matched
                # against the actual retained visual inventory. This lists
                # candidates; it does not guess the user's metric.
                for model in catalog['models']:
                    if scope.get('model_id')and model['id']!=scope['model_id']:continue
                    for measure in model.get('measures',[]):
                        target_ids=[v['target_id']for v in model.get('visuals',[])if v['report_id']==scope['report_id']and v.get('page_id')==scope['page_id']and measure['id']in v['measure_ids']]
                        if target_ids:
                            matching_groups.append({'model_id':model['id'],'measure_id':measure['id'],'report_id':scope['report_id'],
                                'page_id':scope['page_id'],'target_ids':target_ids,'label':measure['name'],
                                'status':'INFERRED','evidence_ids':['catalog:'+digest(catalog)]})
            body['planning_request']={'kind':'FIGURE_VISUAL_MATCH','catalog_hash':digest(catalog),
                'groups':matching_groups,'reported_observations':numeric,
                'purpose':'FIGURE_ATTRIBUTION_BEFORE_QUESTION','status':'AWAITING_CANDIDATE_CHECKS'}
        else:body.pop('planning_request',None)
        check=getattr(self.workspace,'claim_candidate_checks',None)
        validator=getattr(self.workspace,'validate_claim_candidate_checks',None)
        if body.get('planning_request')and callable(check):
            if not callable(validator):raise ValueError('Claim candidate result validation is required')
            checked=check(body,catalog);validator(checked,body,catalog)
            body['candidate_checks']=copy.deepcopy(checked)
            if checked.get('candidate_bindings'):
                claim['candidate_bindings']=copy.deepcopy(checked['candidate_bindings'])
        question,binding=policy.plan(claim,catalog)
        resolved_binding=binding if isinstance(binding,dict)and ('model_id'in binding or binding.get('kind')=='MULTIPLE')else claim.get('selected_binding')
        policy.scope_columns(scope,catalog,resolved_binding)
        body['catalog_hash']=digest(catalog);body['engine_admission']=None
        if question:
            policy.validate_question(claim,question)
            body['status']='CLARIFYING';body['questions']=[question];body['_choices']=binding;body['interpretation']=None
            if not any(h.get('kind')=='QUESTION_PLANNED'and h.get('question_id')==question['id']for h in body['history']):
                body['history'].append({'kind':'QUESTION_PLANNED','question_id':question['id'],'field':question['field']})
        else:
            claim['selected_binding']=binding;body['status']='AWAITING_CONFIRMATION';body['questions']=[];body['_choices']={};body['interpretation']=policy.interpretation(claim,catalog)
        return body

    @operation('claim_submit')
    def submit(self,request):
        self._guard()
        if not isinstance(request,dict)or set(request)-{'text','request_key','claim','screenshot_evidence'}:raise ValueError('Unknown claim request field')
        text=request.get('text','');key=request.get('request_key')
        if not isinstance(text,str)or len(text)>16000:raise ValueError('Claim text exceeds bound')
        if not isinstance(key,str)or not 1<=len(key)<=100:raise ValueError('Claim request key required')
        if not text.strip()and not request.get('claim')and not request.get('screenshot_evidence'):raise ValueError('Claim requires an actual user source')
        hash=digest(request)
        with self.store.connect()as db:
            prior=db.execute('SELECT id,request_hash FROM claim_intakes WHERE request_key=?',(key,)).fetchone()
            if prior:
                if prior[1]!=hash:raise Conflict('Claim key reused with different input')
                return self._public(self._load(db,prior[0])[1])
        id=str(uuid4());new=facts.merge(facts.submitted(request.get('claim',{}),hash),facts.merge(facts.labelled_text(text,hash),facts.linked_text(text,hash)));screenshot_candidates=[];captured_context=None
        if request.get('screenshot_evidence'):
            ref=request['screenshot_evidence']
            if not isinstance(ref,dict)or set(ref)!={'review_id'}:raise ValueError('Screenshot requires retained review ID')
            review=self.workspace.claim_screenshots.load(ref['review_id'],self._catalog())
            for f in review['facts']:
                if f['authority']!='SCREENSHOT_REVIEW' or f['source'].get('review_id')!=review['id']or f['source'].get('review_hash')!=review['hash']:raise ValueError('Screenshot fact lacks retained review provenance')
            new=facts.merge(new,review['facts']);screenshot_candidates=review.get('candidate_bindings',[])
            captured_context={'review_id':review['id'],'review_hash':review['hash'],
                'visible_filter_scope':copy.deepcopy(review.get('visible_filter_scope')),
                'limitations':copy.deepcopy(review.get('limitations',[]))}
        audit={'calls':0,'rejections':[]}
        refusal=None
        if text.strip():
            from .claim_provider import extract
            try:
                extracted,audit=extract(self.workspace,text,hash,id);new=facts.merge(new,extracted)
            except ValueError as exc:
                refusal={'reason':'CLAIM_EXTRACTION_UNAVAILABLE','message':str(exc)}
        body={'id':id,'revision':0,'status':'NEW','claim':{'version':facts.VERSION,'facts':new,'settled':{},'conflicts':[],'candidate_bindings':[],'screenshot_candidates':screenshot_candidates,'selected_binding':None},'questions':[],'interpretation':None,'engine_admission':None,'history':[{'kind':'SUBMITTED','request_hash':hash,'model':audit}], '_choices':{},'documents':[{ 'hash':hash,'request':copy.deepcopy(request)}]}
        if captured_context is not None:body['captured_context']=captured_context
        if refusal:body['status']='HELD';body['history'].append(refusal)
        else:body=self._plan(body,self._catalog())
        with self.store.connect()as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('INSERT INTO claim_intakes VALUES(?,?,?,?,?,?)',(id,key,hash,0,encoded(body),digest(body)))
            event('CONFIGURATION',{'claim_intake':'SUBMIT','request':request,'body':body})
            db.execute('INSERT INTO claim_revisions VALUES(?,?,?,?)',(id,0,encoded(body),digest(body)))
        return self._after_pipeline(body)

    @operation('claim_reply')
    def reply(self,request):
        self._guard()
        if set(request)-{'id','revision','request_key','answers','claim','text','question_id','choice_id'}:raise ValueError('Unknown claim reply field')
        with self.store.connect()as db:revision,body=self._load(db,request['id'])
        if request.get('revision')!=revision:raise Conflict('Claim changed; read current question')
        if body['status']!='CLARIFYING':raise Conflict('Claim is not awaiting a question reply')
        answers=request.get('answers')or[{'question_id':request.get('question_id'),'choice_id':request.get('choice_id'),'text':request.get('text')}]
        if len(answers)!=1:raise ValueError('Reply must answer the one current question')
        answer=answers[0];question=body['questions'][0]
        if answer.get('question_id')!=question['id']:raise Conflict('Claim question is stale')
        patch=copy.deepcopy(request.get('claim',{}));sourcehash=digest(request)
        choice=answer.get('choice_id')
        if choice:
            if choice not in body['_choices']:raise ValueError('Choice is not in retained question')
            value=body['_choices'][choice]
            if 'binding'in value:body['claim']['selected_binding']=copy.deepcopy(value['binding'])
            else:
                for k,v in value.items():
                    if k in('report_id','page_id'):patch.setdefault('scope',{})[k]=v
                    else:patch[k]=v
                if 'scope'in patch:patch['scope'].setdefault('kind',(body['claim']['settled'].get('scope')or{}).get('kind','UNKNOWN'))
        new=facts.submitted(patch,sourcehash)
        text=answer.get('text')or''
        if text:
            from .claim_provider import extract
            extra,audit=extract(self.workspace,text,sourcehash,body['id']);new=facts.merge(new,extra)
        from .agent_handoff import settings
        if not choice and not new and not settings(self.workspace)['enabled']:raise ValueError('Claim reply supplied no usable fact')
        if question['field']=='correction'or question['field']in body['claim'].get('conflicts',[]):
            replacements={f['field']:[n['id']for n in new if n['field']==f['field']]for f in new}
            for old in body['claim']['facts']:
                if old['field']in replacements and not old.get('superseded_by'):old['superseded_by']=replacements[old['field']]
            body['history'].append({'kind':'USER_CORRECTION','superseded_fields':list(replacements),'request_hash':sourcehash})
        if text:body['history'].append({'kind':'REPLY_EXTRACTION','model':audit})
        expected_fields={'binding':{'metric','scope','location'},'report_binding':{'scope','location'},
            'page_binding':{'scope','location'},'report':{'scope','location'},'page':{'scope','location'},
            'targets':{'scope'},'current_target':{'metric','scope','location'},
            'correction':set(f['field']for f in new)}.get(question['field'],{question['field']})
        actual_fields=sorted({f['field']for f in new})
        body['history'].append({'kind':'REPLY_TYPE_MATCH','question_id':question['id'],
            'expected_fields':sorted(expected_fields),'actual_fields':actual_fields,
            'status':'MATCHED'if choice or set(actual_fields)&expected_fields else'NO_EXPECTED_TYPE',
            'request_hash':sourcehash})
        body['claim']['facts']=facts.merge(body['claim']['facts'],new)
        body['revision']+=1;body['history'].append({'kind':'REPLIED','request_hash':sourcehash,'question_id':question['id']});body['documents'].append({'hash':sourcehash,'request':copy.deepcopy(request)})
        body=self._plan(body,self._catalog())
        with self.store.connect()as db:
            db.execute('BEGIN IMMEDIATE')
            if self._load(db,body['id'])[0]!=revision:raise Conflict('Concurrent claim reply')
            self._persist(db,body)
        return self._after_pipeline(body)

    @operation('claim_confirm')
    def confirm(self,request):
        self._guard()
        if set(request)-{'id','revision','request_key','accepted'}or type(request.get('accepted'))is not bool:raise ValueError('Explicit interpretation decision required')
        with self.store.connect()as db:revision,body=self._load(db,request['id'])
        if revision!=request.get('revision')or body['status']!='AWAITING_CONFIRMATION':raise Conflict('Read current interpretation before confirming')
        catalog=self._catalog()
        if digest(catalog)!=body['catalog_hash']:
            old=body['catalog_hash'];oldinterpretation=copy.deepcopy(body['interpretation']);oldbinding=copy.deepcopy(body['claim'].get('selected_binding'))
            body.setdefault('catalog_history',[]).append({'previous_hash':old,'previous_binding':oldbinding})
            try:
                body=self._plan(body,catalog)
                binding=body['claim'].get('selected_binding')
                def identity(value):
                    if value and value.get('kind')=='MULTIPLE':return {'kind':'MULTIPLE','bindings':[identity(v)for v in value['bindings']]}
                    return {k:value.get(k)for k in('model_id','measure_id','report_id','page_id','target_ids')}if value else None
                if identity(binding)!=identity(oldbinding):raise ValueError('The retained definition target changed')
            except ValueError as exc:
                q,choices=policy.question('current_target','Which current definition should we use for this claim?',[],digest(catalog),[f['id']for f in body['claim']['facts']])
                body['status']='CLARIFYING';body['questions']=[q];body['_choices']=choices;body['interpretation']=None;body['engine_admission']=None
                body['history'].append({'kind':'CATALOG_REVALIDATION','status':'TARGET_UNRESOLVED','message':str(exc)})
                body['revision']+=1
                with self.store.connect()as db:
                    db.execute('BEGIN IMMEDIATE');self._persist(db,body)
                return self._public(body)
            body['history'].append({'kind':'CATALOG_REVALIDATION','status':'SAME_STABLE_OBJECTS','old_hash':old,'new_hash':digest(catalog)})
            if body['interpretation']!=oldinterpretation:
                body['revision']+=1;body['history'].append({'kind':'INTERPRETATION_CHANGED','requires_fresh_user_confirmation':True})
                with self.store.connect()as db:
                    db.execute('BEGIN IMMEDIATE');self._persist(db,body)
                return self._public(body)
        body['revision']+=1
        if request['accepted']:
            body['status']='CONFIRMED';body['confirmation']={'authority':'USER_CONFIRMED','request_hash':digest(request),'interpretation_hash':digest(body['interpretation']),'fact_ids':body['interpretation']['fact_ids'],'catalog_hash':body['catalog_hash'],'actor':{'kind':'USER','id':'local-operator@'+str(getattr(self.workspace,'owner','local'))}}
            direction=body['claim']['settled'].get('direction');scope=body['claim']['settled'].get('scope',{})
            route='FRESHNESS'if direction=='STALE'else 'DEFINITION'if direction=='DEFINITION'else 'RECORD_COMPARISON'if scope.get('kind')=='RECORDS'else 'CLAIM_COMPARISON'
            body['engine_admission']={'kind':'PLAN_ONLY','route':route,'claim_hash':digest(body['claim']),'confirmation_hash':digest(body['confirmation']),'executed':False}
        else:
            q,choices=policy.question('correction','What should we correct in this interpretation?',[],body['catalog_hash'],body['interpretation']['fact_ids']);body['status']='CLARIFYING';body['questions']=[q];body['_choices']=choices
        body['documents'].append({'hash':digest(request),'request':copy.deepcopy(request)})
        body['history'].append({'kind':'CONFIRMATION','accepted':request['accepted'],'request_hash':digest(request)})
        with self.store.connect()as db:
            db.execute('BEGIN IMMEDIATE')
            if self._load(db,body['id'])[0]!=revision:raise Conflict('Concurrent claim confirmation')
            self._persist(db,body)
        if request['accepted']and getattr(self.workspace,'claim_glossary',None):
            from .claim_glossary_evidence import record_confirmation
            record_confirmation(self.workspace.claim_glossary,self.store,body['id'],catalog)
        return self._public(body)

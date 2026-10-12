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
        return {k:copy.deepcopy(body[k])for k in ('id','revision','status','claim','questions','interpretation','engine_admission','history')}

    def get(self,id):
        with self.store.connect()as db:_,body=self._load(db,id)
        return self._public(body)

    def _persist(self,db,body):
        event('CONFIGURATION',{'claim_intake':'REVISION','id':body['id'],'revision':body['revision'],'body':body})
        db.execute('UPDATE claim_intakes SET revision=?,body=?,body_hash=? WHERE id=?',(body['revision'],encoded(body),digest(body),body['id']))
        db.execute('INSERT INTO claim_revisions VALUES(?,?,?,?)',(body['id'],body['revision'],encoded(body),digest(body)))

    def _plan(self,body,catalog):
        claim=body['claim']
        for _ in range(2):
            context=(facts.settled(claim['facts'])[0].get('scope')or{})
            resolved=[policy.resolve_scope(f,catalog,context)for f in claim['facts']if f['field']=='scope']
            claim['facts']=facts.merge(claim['facts'],[f for f in resolved if f])
        claim['settled'],claim['conflicts']=facts.settled(claim['facts'])
        scope=claim['settled'].get('scope')or{}
        projected=policy.catalog_projection(catalog)
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
        question,binding=policy.plan(claim,catalog)
        body['catalog_hash']=digest(catalog);body['engine_admission']=None
        if question:
            policy.validate_question(claim,question)
            body['status']='CLARIFYING';body['questions']=[question];body['_choices']=binding;body['interpretation']=None
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
        return self._public(body)

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
        if not choice and not new:raise ValueError('Claim reply supplied no usable fact')
        if question['field']=='correction'or question['field']in body['claim'].get('conflicts',[]):
            replacements={f['field']:[n['id']for n in new if n['field']==f['field']]for f in new}
            for old in body['claim']['facts']:
                if old['field']in replacements and not old.get('superseded_by'):old['superseded_by']=replacements[old['field']]
            body['history'].append({'kind':'USER_CORRECTION','superseded_fields':list(replacements),'request_hash':sourcehash})
        if text:body['history'].append({'kind':'REPLY_EXTRACTION','model':audit})
        body['claim']['facts']=facts.merge(body['claim']['facts'],new)
        body['revision']+=1;body['history'].append({'kind':'REPLIED','request_hash':sourcehash,'question_id':question['id']});body['documents'].append({'hash':sourcehash,'request':copy.deepcopy(request)})
        body=self._plan(body,self._catalog())
        with self.store.connect()as db:
            db.execute('BEGIN IMMEDIATE')
            if self._load(db,body['id'])[0]!=revision:raise Conflict('Concurrent claim reply')
            self._persist(db,body)
        return self._public(body)

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

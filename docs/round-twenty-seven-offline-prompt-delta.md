# Round 27 offline follow-up: prompt and tool-builder delta

Source f0d14fcd. Baseline audit/export remains in prompts.md. These verbatim current builders capture the offline follow-up changes: role-specific identifiers and references to native definitions already retained in the case. No ticket, catalog, secret or evidence value was rendered for this export. This is source inspection only, with zero model or estate calls.

Routing remains Opus intake/investigation/evaluator, Nova primary grading, Sol secondary and Nova Lite disagreement review. No Anthropic grading. Current live pass 1 retains its recorded image split; these builders are candidates for the later pass, not retroactive changes to saved outcomes.

## scripts/investigator/investigation_read_tools.py:179 (registry)

UTF-8 source-segment SHA-256: `65c6d41753d10e8500adebe23ed2dfe575343fda3c58da86fa5c681ef304defa`

```python
def registry(self):
        ids=sorted(self.visible)
        def entry(description,properties,run,required=None):
            return {'description':description,'schema':schema(properties,required),'run':run}
        node={'enum':ids,'description':'A graph node ID from this exact enum. Do not pass a native query-layer ID, inventory asset address or evidence ID.'}
        registry={
            'get_definition':entry('Read the retained DAX, SQL, notebook or view definition for an admitted path object.',{'node':node},self.definitions),
            'get_lineage':entry('Read upstream lineage within the admitted estate and activate its known native query routes. Use a list_candidates result to open an upstream object not active yet; no unrelated catalog dump.',{'node':node,'operation':{'enum':['PATH','SEARCH','NEIGHBOURS','PRODUCERS','CONSUMERS','CANDIDATE_BINDINGS']},'words':{'type':'string','maxLength':256}},self.lineage,[]),
            'get_job_runs':entry('Read native job runs and load accounting. Audit source is preferred when declared.',{'node':{'enum':[i for i,n in self.nodes.items() if i in self.visible and n['kind'] in ('PIPELINE','COPY_ACTIVITY','NOTEBOOK')]}},lambda a:self.job_runs(a['node'])),
            'get_refresh_history':entry('Read the admitted model refresh facts and schedule; automatic-update setting availability is stated separately, never inferred.',{'node':{'enum':[i for i,n in self.nodes.items() if i in self.visible and n['kind']=='MODEL']}},lambda a:self.refresh_history(a['node'])),
            'get_security_definitions':entry('Read RLS/OLS roles, memberships, mapping, SQL policies, user-sensitive views, report access and connection mode where the existing reader can. Never impersonate or grant.',{'node':node},self.security_definitions)}
        check=schema({'candidate':{'type':'string'},'layer':{'enum':list(self.queries.layers)},
                      'kind':{'enum':['sql','dax']},'query':{'type':'string'}})
        registry['list_candidates']=entry('Rank named objects using path proximity, names, synonyms, workspace, ownership and activity. Supply your own cheap queries to check up to five candidates against the stated figure.',
            {'words':{'type':'string'},'workspace':{'type':'string'},'owner':{'type':'string'},
             'checks':{'type':'array','maxItems':5,'items':check}},self.candidates,['words'])
        record_query=schema({'layer':{'enum':list(self.queries.layers)},'kind':{'enum':['sql','dax']},
                             'query':{'type':'string'},'key_field':{'type':'string'}})
        analysis_query=schema({'layer':{'enum':list(self.queries.layers)},'kind':{'enum':['sql','dax']},
                               'query':{'type':'string','minLength':1}})
        fields={'type':'array','minItems':1,'maxItems':3,'uniqueItems':True,'items':{'type':'string','minLength':1}}
        registry['contribution_analysis']=entry(
            'Compare two bounded GROUP BY results. You write both read-only queries using the retained calculation and scopes. Rank slices by signed/absolute share of the observed difference; this is contribution, not causal proof. Truncation is explicit.',
            {'left':analysis_query,'right':analysis_query,'dimensions':fields,'value_field':{'type':'string','minLength':1}},
            lambda a:self.analyze(a,'contribution'))
        registry['row_layer_diff']=entry(
            'Compare two different layers by their business keys using your two bounded read-only queries. Return missing/extra/changed counts and samples within those query scopes. Duplicated keys are rejected; truncated samples never prove missing records.',
            {'left':analysis_query,'right':analysis_query,'keys':fields,
             'compare_fields':{'type':'array','minItems':1,'maxItems':20,'uniqueItems':True,'items':{'type':'string','minLength':1}}},
            lambda a:self.analyze(a,'row_diff'))
        if getattr(self,'target_inventory',None):
            identities=[candidate['id']for candidate in self.target_inventory['candidates']]
            registry['get_target_candidates']=entry(
                'Read the bounded plausible targets with their exact retained report/page/visual filters. None is selected. Preserve explicit choices; investigate each candidate before asking.',
                {},lambda _:deepcopy(self.target_inventory))
            registry['check_target_candidates']=entry(
                'Supply one read-only scalar query per candidate using its own retained filters and calculation. Code compares the actual results at stated precision; no unique target is selected unless all candidates were measured successfully and only one matches.',
                {'checks':{'type':'array','minItems':1,'maxItems':5,'items':schema({
                    'candidate':{'enum':identities},'layer':{'enum':list(self.queries.layers)},
                    'kind':{'enum':['sql','dax']},'query':{'type':'string','minLength':1}})}},self.check_targets)
        registry['record_trace']=entry('Run your key lookup queries in source-to-model order. Distinguish presence, duplicates, absence, truncation and failed reads. Then inspect definitions/jobs for the cause.',
            {'key':{'type':'string'},'queries':{'type':'array','minItems':1,'maxItems':5,'items':record_query}},self.record_trace)
        # Empty enum tools are unavailable on this path, not invented scopes.
        return {name:value for name,value in registry.items()
                if all(prop.get('enum')!=[] for prop in value['schema']['properties'].values())}
```

## scripts/investigator/ai_investigation.py:409 (run)

UTF-8 source-segment SHA-256: `d48165157614bc52ee8c00d4e7d5197a01a14d54df18d6c358ab917193996783`

```python
def run(self):
        started=self.clock();self._started=started;pins=digest([self.case_id,self.context,self.triage])
        saved=self.checkpoint.load()
        if saved:
            if saved.get('pins')!=pins:raise ValueError('CASE_CHECKPOINT_BINDING_CHANGED')
            self.state=deepcopy(saved)
            self._elapsed_before=self.state.get('elapsed_seconds',0)
            self.queries.activate(self.state.get('active_layers',[]))
            self.queries.records=deepcopy(self.state.get('queries',[]))
            self.queries.cache={q['signature']:deepcopy(q) for q in self.queries.records if q['status']=='SUCCEEDED'}
            self.queries.attempts={}
            for q in self.queries.records:
                if q['status']=='ERROR':
                    key=(q['layer'],q['purpose']);self.queries.attempts[key]=self.queries.attempts.get(key,0)+1
            if self.state['outcome']:return self.finish()
            # Never silently re-issue a request whose completion is unknown.
            if self.state['pending']:
                self.state['outcome']={'status':'UNESTABLISHED','business':'The last request has no established completion.',
                                       'stop':deepcopy(self.state['pending'])}
                return self.finish()
        else:
            self.state={'version':'ai-investigation-v1','case_id':self.case_id,'pins':pins,'messages':[],
                        'evidence':{},'cache':{},'tools_used':self.initial_tools_used,'model_calls':0,'candidate_checks':False,
                        'pending':None,'outcome':None,'elapsed_seconds':0}
            self._elapsed_before=0
            self.evidence({'kind':'TRIAGE','facts':self.triage})
            from .retained_definition_evidence import references
            definitions=[{'evidence_id':self.evidence(reference),**reference}
                         for reference in references(self.context)]
            if definitions:
                self.state['messages'].append({'role':'user','content':canonical({
                    'retained_definition_references':definitions,
                    'instruction':'The native content is already in the admitted context. Cite these IDs for its retained definition; get_evidence returns full details. These references do not prove current values or deployment freshness.'})})
        try:
            if not saved:
                self.prime_access_definitions()
                self.prime_operational_run()
            while self.state['tools_used']<self.tool_limit and self.state['model_calls']<self.tool_limit+3:
                if self._elapsed_before+self.clock()-started>=self.deadline_seconds:break
                recitation={'case_id':self.case_id,'tools_used':self.state['tools_used'],
                            'evidence_ids':list(self.state['evidence']),
                            'query_ids':[q['id'] for q in self.queries.records],
                            'instruction':'Choose the next useful check, or submit a supported finding.'}
                if self.state.get('physical_reads_closed'):
                    recitation['instruction']='The physical read allowance is exhausted. No more estate calls are allowed. Submit only a finding supported by saved evidence, with unchecked parts stated, or ask a validated question. You may inspect saved evidence locally.'
                if self.closing_action_reserved():
                    recitation['instruction']='The last action is reserved for delivery. Submit the finding supported by the saved evidence, including its limits, or ask a validated last-resort question. No additional investigation read is available. A supported partial finding is preferable to silently dropping established evidence.'
                if not self.state.get('turn'):
                    self.refresh_tools()
                    self.state['messages'].append({'role':'user','content':canonical({'current_state':recitation})})
                    self.state['pending']={'kind':'MODEL','step':self.state['model_calls']+1};self.save()
                    model_started=self.clock()
                    try:response=self.presentation.complete(self.model,system=self.stable,messages=self.state['messages'],tools=self.tools)
                    finally:self.model_seconds+=max(0,self.clock()-model_started)
                    self.state['model_calls']+=1;self.state['pending']=None
                    self.evidence({'kind':'MODEL_RESPONSE','response':response})
                    content=response.get('content',[])
                    if not isinstance(content,list):content=[]
                    calls=[b for b in content if isinstance(b,dict) and b.get('type')=='tool_use']
                    if not calls or any(not isinstance(b.get('id'),str) or not b.get('id') for b in calls):
                        self.state['messages'].append({'role':'user','content':'Format warning: use the supplied tools; your response is retained but no unchecked finding is delivered.'})
                        self.save();continue
                    self.state['messages'].append({'role':'assistant','content':content})
                    self.state['turn']={'calls':calls,'results':[]}
                    self.save()
                turn=self.state['turn'];results=turn['results']
                calls=turn['calls'][len(results):]
                parallel=self.parallel_queries(calls)
                for call in calls:
                    if self.state['tools_used']>=self.tool_limit:break
                    name,args=call.get('name'),call.get('input');key=digest([name,args])
                    if self.state.get('physical_reads_closed') and name not in ('submit_finding','ask_user_choice','get_evidence'):
                        results.append({'type':'tool_result','tool_use_id':call['id'],'content':canonical({'rejected_tool':name,'reason':'PHYSICAL_READS_CLOSED_USE_SAVED_EVIDENCE','available':['submit_finding','ask_user_choice','get_evidence']}),'is_error':True})
                        self.save();continue
                    if self.closing_action_reserved() and name not in ('submit_finding','ask_user_choice'):
                        # Reject without a read or consuming the delivery slot. The
                        # unchanged model-call, time and dollar caps still apply.
                        results.append({'type':'tool_result','tool_use_id':call['id'],
                            'content':canonical({'rejected_tool':name,'reason':'FINAL_ACTION_RESERVED_FOR_VALIDATED_DELIVERY','available':['submit_finding','ask_user_choice']}),'is_error':True})
                        self.save();continue
                    self.state['tools_used']+=1
                    self.state['pending']={'kind':'TOOL','name':name,'signature':key};self.save()
                    try:
                        if key in self.state['cache']:
                            previous=self.state['cache'][key]
                            result={'already_have':previous['evidence_id'],'note':'Already have this as evidence '+previous['evidence_id']+'. Use get_evidence if full details are needed.'}
                        else:
                            if key in parallel:
                                success,result=parallel[key]
                                if not success:raise result
                            else:result=self.dispatch(name,args)
                            evidence_id=self.evidence({'tool':name,'arguments':args,'result':result})
                            result={'evidence_id':evidence_id,'result':result}
                            failed=isinstance(result['result'],dict) and result['result'].get('status')=='ERROR'
                            if name not in ('submit_finding','ask_user_choice') and not failed:
                                self.state['cache'][key]=deepcopy(result)
                        is_error=(isinstance(result.get('result'),dict) and result['result'].get('status')=='ERROR')
                    except UsageHold as error:
                        if str(error)!='GUIDED_PHYSICAL_CAP_REACHED' or not any(q['status']=='SUCCEEDED'for q in self.queries.records):raise
                        # Close physical work permanently for this case. Model/delivery
                        # can use saved evidence only, within their unchanged budgets.
                        self.state['physical_reads_closed']=True
                        result={'rejected_tool':name,'reason':'PHYSICAL_READS_CLOSED_USE_SAVED_EVIDENCE','available':['submit_finding','ask_user_choice','get_evidence']}
                        self.evidence(result);is_error=True
                    except (SpendHold,GatewayDenied):raise
                    except Exception as error:
                        from .planner_recording import _safe
                        message=str(error)
                        try:_safe(message.encode())
                        except ValueError:message=type(error).__name__
                        result={'rejected_tool':name,'reason':message,'error_type':type(error).__name__}
                        self.evidence(result);is_error=True
                    self.state['pending']=None
                    results.append({'type':'tool_result','tool_use_id':call['id'],
                                    'content':canonical(result),'is_error':is_error})
                    self.save()
                    if self.state['outcome']:break
                self.state['messages'].append({'role':'user','content':deepcopy(results)})
                self.state['turn']=None;self.save()
                if self.state['outcome']:break
        except (SpendHold,UsageHold,GatewayDenied) as error:
            self.state['outcome']={'status':'BLOCKED','business':'The investigation stopped at a safety or budget boundary.',
                                   'stop':type(error).__name__+': '+str(error)}
        if not self.state['outcome']:
            self.state['outcome']={'status':'UNRESOLVED','business':'The checks did not establish a cause within this ticket’s limits.',
                                   'stop':'TOOL_OR_TIME_LIMIT'}
        return self.finish()
```

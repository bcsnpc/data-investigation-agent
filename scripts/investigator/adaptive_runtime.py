"""Durable evidence-led sessions over the existing receipt-fenced diagnostic runtime.

Planner suggestions are unverified. This module owns scope, budgets, facts and stops.
"""
from .process_tape import utc_now
from .model_context import assets as model_assets
from .evidence_prose import diagnostic_detail
from datetime import datetime, timezone
import json
import time
from .process_tape import uuid4
from .run_recording import operation
from .process_tape import clock as tape_clock, event as tape_event

from .onboarding import digest, encoded, text, Conflict
from .runtime import fingerprint
from .adaptive_candidates import catalog, available, observation, diagnostic_pairs, record_pairs
from .adaptive_planner import validate, VERSION
from .usage_governance import UsageGovernor,UsageHold
from .record_aggregate import derive as reconcile_aggregates


def now():
    return utc_now()


def outcome(state):
    reason=state.get('stop_reason')
    classification='UNRESOLVED' if reason in ('BUDGET_LIMIT','DEADLINE','PLANNER_FAILED','TOOL_UNAVAILABLE','PROCESS_FAILED','PLANNER_COMPLETION_UNCERTAIN','REMOTE_COMPLETION_UNCERTAIN','USAGE_LIMIT','NO_PROGRESS','USER_CANCELLED') else 'INSUFFICIENT_EVIDENCE'
    result={'classification':classification,'stop_reason':reason,
            'record_comparisons':state.get('record_comparisons',[]),
            'aggregate_reconciliations':state.get('aggregate_reconciliations',[]),
            'scoped_conditions':[{'observation_id':o['id'], **o['freshness']} for o in state['observations']
                                 if o.get('freshness')],
            'facts':state['observations'],'diagnostic_pairs':diagnostic_pairs(state['observations']),'hypotheses':[{**h,'verified':False} for h in state['hypotheses']],
            'gaps':state['gaps']+[{'reason':'MAPPING_CONTEXT_VERSION_AND_CAUSAL_PROOF_NOT_VERIFIED'}],
            'cause_verified':False,'delivery_eligible':False}
    if state['envelope'].get('strategy'):
        from .dynamic_reasoning import outcome as dynamic_outcome
        return dynamic_outcome(state,result)
    return result


class AdaptiveRuntime:
    def __init__(self,runtime,planner,clock=time.time,planner_profile=None,usage_policy=None,process_judge=None,
                 process_lineage=None):
        self.runtime=runtime;self.store=runtime.store;self.config=runtime.config
        self.planner=planner;self.clock=lambda:tape_clock('agent',clock);self.process_judge=process_judge
        self.process_lineage=process_lineage
        self.planner_profile=planner_profile or {"adapter":"injected"}
        self.process_max_boundaries=self.planner_profile.get('process_max_boundaries',1)
        if type(self.process_max_boundaries) is not int or not 0<=self.process_max_boundaries<=32:
            raise ValueError('Process boundary ceiling must be 0 through 32')
        from .generation_policy import validate as generation_policy
        self.generation_options=generation_policy(self.planner_profile.get('generation_options'))
        self.max_planner_recoveries=self.planner_profile.get('max_planner_recoveries',0)
        if type(self.max_planner_recoveries) is not int or self.max_planner_recoveries not in (0,1):
            raise ValueError('At most one explicit planner recovery is supported')
        self.governor=UsageGovernor(runtime,usage_policy,self.clock) if usage_policy is not None else None
        with runtime.db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS adaptive_sessions(
              id TEXT PRIMARY KEY,model_id TEXT,request_key TEXT,request_hash TEXT,
              state TEXT,state_hash TEXT,UNIQUE(model_id,request_key));
            CREATE TABLE IF NOT EXISTS adaptive_events(
              id INTEGER PRIMARY KEY,session_id TEXT,kind TEXT,detail TEXT,created TEXT);
            """)

    def save(self,db,state,kind,detail=None):
        if kind=='CREATED' or ('previous_runs' in state and state['status'] not in ('READY','PLANNING','EXECUTING')):
            from .run_history import capture
            state['previous_runs']=capture(db,state)
        if kind.endswith('RESERVED') or kind.startswith('SQL_GUARD_'):
            tape_event('BUDGET',{'kind':kind,'detail':detail,'session_id':state['id']})
        db.execute('UPDATE adaptive_sessions SET state=?,state_hash=? WHERE id=?',
                   (encoded(state),digest(state),state['id']))
        db.execute('INSERT INTO adaptive_events(session_id,kind,detail,created) VALUES(?,?,?,?)',
                   (state['id'],kind,encoded(detail or {}),now()))

    def load(self,db,identity):
        row=db.execute('SELECT state,state_hash,model_id FROM adaptive_sessions WHERE id=?',(identity,)).fetchone()
        if row is None:raise KeyError('Session not found')
        state=json.loads(row['state'])
        if digest(state)!=row['state_hash']:raise ValueError('Session integrity differs')
        self.store.get(row['model_id'])
        if state['model_id']!=row['model_id']:raise ValueError('Session model differs')
        return state

    def admit(self,state):
        if state.get('usage_policy_hash')!=(self.governor.hash if self.governor else None):raise Conflict('Usage policy changed')
        if state['engine_hash']!=fingerprint() or state['config_hash']!=digest(self.config) or state['planner_profile_hash']!=digest(self.planner_profile):raise Conflict('Engine or connection changed')
        model=self.store.get(state['model_id'])
        if digest(model['context'])!=state['context_hash']:raise Conflict('Context changed')
        if state['envelope'].get('strategy'):
            from .context_search import latest
            current=latest(self.store)
            if not current or current['version']!=state['discovery_version']:raise Conflict('Environment context changed')
        try:candidates,gaps=catalog(self.store,self.config,state['envelope'])
        except (ValueError,KeyError) as exc:raise Conflict('Candidate metadata or review is no longer admissible') from exc
        if digest(candidates)!=state['catalog_hash']:raise Conflict('Candidate admission changed')
        return candidates

    @operation('create')
    def create(self,envelope,key,*,predecessor=None):
        if self.planner_profile.get('adapter')=='azure' and self.governor is None:raise ValueError('Live Azure sessions require an explicit usage policy')
        text(key,100);candidates,gaps=catalog(self.store,self.config,envelope)
        model=self.store.get(envelope['model_id']);identity=str(uuid4())
        state={'id':identity,'model_id':model['id'],'envelope':envelope,'scope_hash':digest(envelope),
               'engine_hash':fingerprint(),'config_hash':digest(self.config),'context_hash':digest(model['context']),
               'catalog_hash':digest(candidates),'planner_profile_hash':digest(self.planner_profile),'planner_version':VERSION,'status':'READY','token':None,
               'deadline':self.clock()+envelope['limits']['wall_seconds'],'planner_calls':0,'cloud_calls':0,
               'usage_policy_hash':self.governor.hash if self.governor else None,'no_progress':0,
                'input_characters':0,'attempted':[],'observations':[],'record_comparisons':[],'hypotheses':[],'decisions':[],
               'question':None,'stop_reason':None,'pending':None,'predecessor':predecessor,'gaps':gaps}
        state['measure_display_name']=next((a.get('name') for a in model_assets(model['context']) if a['id']==envelope['measure_id']),None)
        if envelope.get('strategy'):
            from .context_search import latest
            context=latest(self.store)
            if context is None:raise Conflict('Dynamic investigation needs discovered context')
            state['discovery_version']=context['version']
            state['action_budget_version']=1
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT id,request_hash FROM adaptive_sessions WHERE model_id=? AND request_key=?',
                           (model['id'],key)).fetchone()
            if row:
                if row['request_hash']!=digest({'envelope':envelope,'predecessor':predecessor}):raise Conflict('Idempotency key has another scope')
                return self.get(row['id'])
            db.execute('INSERT INTO adaptive_sessions VALUES(?,?,?,?,?,?)',
                       (identity,model['id'],key,digest({'envelope':envelope,'predecessor':predecessor}),encoded(state),digest(state)))
            self.save(db,state,'CREATED',{'scope_hash':state['scope_hash'],'predecessor':predecessor})
        return self.get(identity)

    def get(self,identity):
        with self.runtime.db() as db:
            state=self.load(db,identity)
            from .evidence_synthesis import read as read_synthesis
            synthesis=read_synthesis(db,identity)
            events=[{'kind':r['kind'],'detail':json.loads(r['detail']),'created':r['created']} for r in
                    db.execute('SELECT kind,detail,created FROM adaptive_events WHERE session_id=? ORDER BY id',(identity,))]
        state.pop('token');state['outcome']=outcome(state);state['events']=events
        if synthesis:
            state['synthesis']=synthesis
            if synthesis['status']=='COMPLETED':
                state['investigation_outcome']=state['outcome']
                assessment=synthesis['assessment']
                if assessment is not None:
                    state['outcome']={**state['outcome'],'classification':assessment['classification'],
                                      'assessment':assessment,'assessment_phase':'SYNTHESIS'}
                if 'outputs' in synthesis:state['outcome']['synthesis_outputs']=synthesis['outputs']
        from .action_budget import summary,allocation
        state['trajectory_metrics']=summary(state)
        if state.get('action_budget_version')==1:state['action_budget']=allocation(state)
        return state

    def payload(self,state,candidates):
        model=self.store.get(state['model_id'])
        assets=model_assets(model['context'])
        names={a['id']:a.get('name',a['id']) for a in assets}
        choices=[{'id':c['id'],'tool':c['tool'],'measure_id':c['measure_id'],
                  'measure_name':names.get(c['measure_id'],c['measure_id']),
                  'dimension_id':c['dimension_id'],'depth':c['depth'],
                  'operations':model['context'].get('semantic_graph',{}).get('measures',{}).get(c['measure_id'],{}).get('operations',[]),
                  'source_binding':c.get('reviewed_mapping') or ('OPERATOR_SELECTED_NOT_EQUIVALENCE_PROOF' if c['tool']=='source' else None),
                  'source_operation':c['plan'].get('operation'), 'approved_filters':c['plan'].get('filters',[]),
                  'projected_columns':c['plan'].get('column_ids'),'record_limit':c['plan'].get('limit'),
                  'captures_aggregate_with_records':'aggregate_measure_id' in c['plan'],
                  **({'dependency_context':c['dependency_context']} if c.get('dependency_context') else {})} for c in candidates]
        observations=[]
        for o in state['observations']:
            sampled=[];size=0
            for value in o['values'][:20]:
                size+=len(encoded(value))
                if size>6000:break
                sampled.append(value)
            # The planner needs values, not the operator's account identifiers.
            observations.append({**{k:v for k,v in o.items() if k!='execution_identity'},
                                 'values':sampled,'planner_sample_truncated':len(sampled)<len(o['values'])})
        result={'symptom':state['envelope']['symptom'],'scope_hash':state['scope_hash'],
                'filters':state['envelope']['filters'],'candidates':choices,
                'observations':observations,'diagnostic_pairs':diagnostic_pairs(state['observations']),
                'record_comparisons':[{**p,'differences':p.get('differences',[])[:3],
                                       'planner_examples_truncated':len(p.get('differences',[]))>3} for p in state.get('record_comparisons',[])],
                'aggregate_reconciliations':state.get('aggregate_reconciliations',[]),
                'hypotheses':state['hypotheses'],'gaps':state['gaps'],
                'remaining_cloud_calls':state['envelope']['limits']['cloud_calls']-state['cloud_calls'],
                'remaining_wall_seconds':max(0,int(state['deadline']-self.clock())),
                'limitation':'All observations are diagnostic only; no semantic equivalence or causal proof.'}
        if state['envelope'].get('strategy'):
            from .dynamic_reasoning import enrich
            from .flexible_tools import capabilities
            result['tool_capabilities']=capabilities(self.store,model,self.config)
            from .action_budget import allocation
            if state.get('action_budget_version')==1:result['action_budget']=allocation(state)
            return enrich(self.store,state,result)
        return result

    def stop(self,db,state,reason,status='COMPLETED'):
        from .process_debugging import VERSION as process_version
        if status in ('HELD','NEEDS_INPUT') and state['envelope'].get('strategy')==process_version:
            from .process_receipts import refusal
            from .refusal_synthesis import earliest
            if earliest(state) is None:
                state['observations'].append(refusal('WALK_REFUSED',reason,
                    'process-refused-'+str(len(state['observations']))))
        state.update(status=status,token=None,stop_reason=reason)
        self.save(db,state,'STOPPED',{'reason':reason})

    def step(self,identity):
        token=str(uuid4())
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');state=self.load(db,identity)
            if state['status'] in ('COMPLETED','NEEDS_INPUT','HELD','CANCELLED'):return self.get(identity)
            if state['status']!='READY':raise Conflict('Session has an active or interrupted turn')
            try:candidates=self.admit(state)
            except Conflict:
                self.stop(db,state,'ADMISSION_CHANGED','HELD');return self.project_after_commit(db,state)
            dynamic=bool(state['envelope'].get('strategy'))
            choices=([c for c in candidates if c['id'] not in state['attempted']] if dynamic else available(candidates,state['observations'],state['attempted']));limits=state['envelope']['limits']
            reason=None
            if self.clock()+self.generation_options['timeout_seconds']>state['deadline']:reason='DEADLINE'
            elif state['planner_calls']>=limits['planner_calls'] or state['cloud_calls']>=limits['cloud_calls']:reason='BUDGET_LIMIT'
            elif state.get('no_progress',0)>=(self.governor.policy['no_progress_limit'] if self.governor else 2):reason='NO_PROGRESS'
            elif not choices and not dynamic:reason='NO_ADMITTED_TEST'
            payload=self.payload(state,choices)
            if dynamic:
                from .planner_projection import fit
                payload=fit(payload,self.generation_options['max_payload_characters'])
                from .connection_registry import attach
                payload=attach(payload,self.config,min(self.generation_options['max_payload_characters'],
                    limits['input_characters']-state['input_characters']))
            size=len(encoded(payload))
            if size>self.generation_options['max_payload_characters'] or state['input_characters']+size>limits['input_characters']:reason='BUDGET_LIMIT'
            if reason:
                self.stop(db,state,reason);return self.project_after_commit(db,state)
            if self.governor:
                try:self.governor.reserve(db,identity,'planner:'+str(state['planner_calls']+1),'planner',size,
                                         output_tokens=self.generation_options['max_output_tokens'])
                except UsageHold:
                    self.stop(db,state,'USAGE_LIMIT','HELD');return self.project_after_commit(db,state)
            state.update(status='PLANNING',token=token)
            state['planner_calls']+=1;state['input_characters']+=size
            self.save(db,state,'PLANNER_RESERVED',{'payload_hash':digest(payload),'input_characters':size})
        proposal_received=False
        repairs=[]
        if self.planner_profile.get('adapter')=='azure':payload['generation_options']=self.generation_options
        try:
            from .planner_recording import recording
            with recording(lambda: {'session_id':identity,'planner_call':state['planner_calls'],
                    'environment':self.store.environment,'planner_profile':self.planner_profile,
                    'usage_policy':self.governor.policy if self.governor else None,
                    'context_version':state.get('discovery_version',state['context_hash']),
                    'state':{k:v for k,v in state.items() if k!='token'},'payload':payload,
                    'reservation':{'key':'planner:'+str(state['planner_calls']),
                        'input_characters':size,'output_tokens':self.generation_options['max_output_tokens'],
                        'governed':self.governor is not None},
                    'budget':self.governor.snapshot() if self.governor else {'limits':limits}}) as record:
                try:proposal,usage=self.planner(payload)
                finally:
                    if record:record.safe_write('runtime-return.json',encoded({'clock':self.clock()}).encode('utf-8'))
            proposal_received=True
            if dynamic:
                from .proposal_repairs import repair
                proposal,repairs=repair(proposal)
                from .dynamic_reasoning import validate as validate_dynamic
                decision=validate_dynamic(proposal,payload)
            else:decision=validate(proposal,payload)
        except Exception as exc:
            from .generation_policy import failure_usage
            failed_usage=usage.get('usage') if proposal_received and isinstance(usage,dict) else failure_usage(exc)
            with self.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE');state=self.load(db,identity)
                if self.governor:self.governor.settle(db,identity,'planner:'+str(state['planner_calls']),
                    failed_usage,uncertain=not proposal_received and failed_usage is None)
                if state['token']==token:
                    for detail in repairs:self.save(db,state,'PROPOSAL_REPAIRED',detail)
                    if dynamic and proposal_received and isinstance(exc,ValueError):
                        item={'id':str(uuid4()),'tool':'context','status':'REJECTED','completeness':'UNAVAILABLE','values':[],
                              'metadata':{'reason':'Decision contract rejected: '+diagnostic_detail(exc,400)},'measure_id':None,'dimension_id':None}
                        from .action_budget import RetrievalBudgetExceeded
                        if isinstance(exc,RetrievalBudgetExceeded):
                            item['metadata']['reason_code']='RETRIEVAL_BUDGET_EXHAUSTED'
                            self.save(db,state,'RETRIEVAL_BUDGET_REJECTED',{'observation_id':item['id']})
                        state['observations'].append(item);state.update(status='READY',token=None,no_progress=state.get('no_progress',0)+1)
                        self.save(db,state,'PROPOSAL_REJECTED',{'observation_id':item['id']})
                    else:
                        from .generation_policy import error_summary
                        detail=error_summary(exc)
                        recover=(not proposal_received and detail['error_type'] in ('APITimeoutError','APIConnectionError')
                                 and state.get('planner_recoveries',0)<self.max_planner_recoveries)
                        if recover:
                            state.update(status='READY',token=None,planner_recoveries=state.get('planner_recoveries',0)+1)
                        else:self.stop(db,state,'PLANNER_FAILED','HELD')
                        self.save(db,state,'PLANNER_ERROR',{**detail,'recovery_scheduled':recover})
            return self.get(identity)
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');state=self.load(db,identity)
            if self.governor:self.governor.settle(db,identity,'planner:'+str(state['planner_calls']),usage.get('usage') if isinstance(usage,dict) else None)
            if state['token']!=token or state['status']!='PLANNING':raise Conflict('Planner is fenced')
            for detail in repairs:self.save(db,state,'PROPOSAL_REPAIRED',detail)
            try:self.admit(state)
            except Conflict:
                self.stop(db,state,'ADMISSION_CHANGED','HELD');return self.project_after_commit(db,state)
            if self.clock()>state['deadline']:
                self.stop(db,state,'DEADLINE');return self.project_after_commit(db,state)
            hypotheses={h['id']:h for h in state['hypotheses']}
            hypotheses.update({h['id']:h for h in decision['hypotheses']});state['hypotheses']=list(hypotheses.values())
            # Only safe scalar usage counts are retained, never provider payloads/secrets.
            counts=usage.get('usage',{}) if isinstance(usage,dict) else {}
            counts={k:v for k,v in (counts or {}).items() if k in ('input_tokens','output_tokens','total_tokens') and type(v) is int and v>=0}
            state['decisions'].append({'decision':decision,'usage':counts,'payload_hash':digest(payload)})
            if decision['action']=='ASK':
                state['question']=decision['question'];self.stop(db,state,'CLARIFICATION_REQUIRED','NEEDS_INPUT')
            elif decision['action']=='STOP':
                if dynamic:state['assessment']=decision['assessment']
                self.stop(db,state,decision['stop_reason'])
            elif decision['action']=='LOOKUP':
                from .dynamic_reasoning import lookup
                try:item=lookup(self.store,decision['lookup'],self.store.get(state['model_id']))
                except (ValueError,KeyError):
                    item={'id':str(uuid4()),'tool':'context','status':'REJECTED','completeness':'UNAVAILABLE',
                          'values':[],'metadata':{'reason':'Context lookup unavailable or outside scope'},'measure_id':None,'dimension_id':None}
                duplicate=next((o for o in state['observations'] if o['tool']=='context' and o['status']=='COMPLETED'
                                and o.get('lookup')==item.get('lookup') and
                                o.get('metadata',{}).get('context_version')==item.get('metadata',{}).get('context_version')),None) if item['status']=='COMPLETED' else None
                if duplicate:
                    item['duplicate_of']=duplicate['id']
                    item['metadata']['progress_notice']='This request already returned the same context version. Reuse that evidence or choose a different definition, content range or diagnostic.'
                state['observations'].append(item);state.update(status='READY',token=None)
                state['no_progress']=state.get('no_progress',0)+1 if item['status']=='REJECTED' or duplicate else 0
                self.save(db,state,'CONTEXT_OBSERVED',{'observation_id':item['id']})
            else:
                if decision['action']=='QUERY':
                    from .dynamic_reasoning import MissingSourceContext
                    from .proposal_repairs import candidate_with_schema
                    def schema_observed(item):
                        self.save(db,state,'PROPOSAL_REPAIRED',{'repair_kind':'schema_prefetch',
                                  'observation_id':item['id'],'status':item['status']})
                    try:candidate=candidate_with_schema(self.store,self.config,state,decision['query'],schema_observed)
                    except (ValueError,KeyError) as exc:
                        from .read_redundancy import RedundantRead
                        item={'id':str(uuid4()),'tool':'context','status':'REJECTED','completeness':'UNAVAILABLE','values':[],
                              'metadata':{'reason':diagnostic_detail(exc,500),'proposed_tool':decision['query']['tool']},'measure_id':None,'dimension_id':None}
                        if isinstance(exc,MissingSourceContext):item['metadata']['recovery_assets']=exc.recovery_assets
                        from .query_sql import QueryRejection
                        if isinstance(exc,QueryRejection):item['metadata'].update(exc.feedback)
                        if isinstance(exc,RedundantRead):
                            prior=exc.observation
                            item.update(duplicate_of=prior['id'],values=prior['values'])
                            item['metadata'].update(reason_code='READ_ALREADY_OBSERVED',prior_tool=prior['tool'],
                                context_version=state.get('discovery_version'),result_is_reused=True,
                                prior_completeness=prior['completeness'])
                            self.save(db,state,'READ_REDUNDANT',{'prior_observation_id':prior['id'],'observation_id':item['id']})
                        state['observations'].append(item);state.update(status='READY',token=None,no_progress=state.get('no_progress',0)+1)
                        self.save(db,state,'PROPOSAL_REJECTED',{'observation_id':item['id']})
                        return self.project_after_commit(db,state)
                else:candidate=next(c for c in choices if c['id']==decision['candidate_id'])
                seconds=300 if candidate['tool'] in ('source','source_records','bounded_sql') else 120
                if self.clock()+seconds>state['deadline']:self.stop(db,state,'DEADLINE')
                else:
                    if self.governor:
                        try:self.governor.reserve(db,identity,'tool:'+str(state['cloud_calls']+1),'cloud')
                        except UsageHold:
                            self.stop(db,state,'USAGE_LIMIT','HELD');return self.project_after_commit(db,state)
                    state['cloud_calls']+=1;state['physical_calls']=state.get('physical_calls',state['cloud_calls']-1)+1;state['read_accounting_version']='diagnostic-operations-v1';state['attempted'].append(candidate['id'])
                    state.update(status='EXECUTING',pending={'candidate':candidate,'key':identity+':'+str(state['cloud_calls']),'run_id':None,'reservation_key':'tool:'+str(state['cloud_calls'])})
                    self.save(db,state,'TOOL_RESERVED',{'candidate_id':candidate['id'],'cloud_calls':state['cloud_calls']})
        if self.get(identity)['status']=='EXECUTING':return self.dispatch(identity,token)
        return self.get(identity)

    def project_after_commit(self,db,state):
        # Return only after durable writes, including early stop paths.
        db.commit()
        return self.get(state['id'])

    def dispatch(self,identity,token):
        # Creating the child and linking it are separate DB transactions. Its stable
        # request key closes this crash window; recovery finds the same child.
        with self.runtime.db() as db:
            state=self.load(db,identity)
            if state['token']!=token or state['status']!='EXECUTING':raise Conflict('Dispatcher fenced')
            self.admit(state);pending=state['pending'];candidate=pending['candidate']
            if self.clock()+(300 if candidate['tool'] in ('source','source_records','bounded_sql') else 120)>state['deadline']:
                self.stop(db,state,'DEADLINE','HELD');return self.project_after_commit(db,state)
        child=self.runtime.create({'model_id':state['model_id'],'call_budget':1,
                                  'actions':[{'tool':candidate['tool'],'input':candidate['plan']}]},pending['key'])
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');state=self.load(db,identity)
            if state['status']=='CANCELLED':
                self.runtime.cancel_in_transaction(db,child['id']);db.commit();return self.get(identity)
            if state['token']!=token or state['status']!='EXECUTING':raise Conflict('Dispatcher fenced')
            state['pending']['run_id']=child['id'];self.save(db,state,'CHILD_LINKED',{'run_id':child['id']})
        def additional_read(tool,execute):
            with self.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE');current=self.load(db,identity);self.admit(current)
                if current['status']!='EXECUTING' or current['token']!=token: raise Conflict('Dispatcher fenced')
                if current['status']!='EXECUTING' or self.clock()>=current['deadline']:raise UsageHold('Read cancelled or deadline exhausted')
                number=current.get('physical_calls',current['cloud_calls'])+1;key='physical:'+str(number)
                if self.governor:self.governor.reserve(db,identity,key,'cloud')
                current['physical_calls']=number;self.save(db,current,'PHYSICAL_READ_RESERVED',{'tool':tool,'number':number})
            result=None;error=None
            try:
                result=execute();return result
            except Exception as exc:
                error=type(exc).__name__;raise
            finally:
                from .process_read_receipts import receipt
                entry=receipt(number,tool,result,error)
                with self.runtime.db() as db:
                    db.execute('BEGIN IMMEDIATE');current=self.load(db,identity)
                    current.setdefault('physical_read_receipts',[]).append(entry)
                    self.save(db,current,'PHYSICAL_READ_RECORDED',entry)
                    if self.governor:self.governor.settle(db,identity,key,uncertain=error is not None)
        result=None;physical=None;dispatch_error=None
        try:
            from .physical_reads import scope
            with scope(additional_read) as physical:result=self.runtime.execute(child['id'])
        except Conflict:
            dispatch_error='Conflict'
            if self.get(identity)['status']=='CANCELLED':return self.get(identity)
            raise
        finally:
            from .process_read_receipts import receipt
            first=physical.get('first_report') if physical else None
            number=state.get('physical_calls',state['cloud_calls'])
            body=first or ({'status':result['status']} if result else None)
            entry=receipt(number,first['request_kind'] if first else candidate['tool'],body,dispatch_error)
            if first:entry['logical_tool']=candidate['tool']
            with self.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE');current=self.load(db,identity)
                entries=current.setdefault('physical_read_receipts',[])
                if not any(e['sequence']==number for e in entries):
                    entries.append(entry);self.save(db,current,'PHYSICAL_READ_RECORDED',entry)
        return self.consume(identity,token,result)

    def consume(self,identity,token,child):
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');state=self.load(db,identity)
            if state['status']=='CANCELLED':return self.get(identity)
            if state['token']!=token or state['status']!='EXECUTING':raise Conflict('Receipt consumer fenced')
            if child['id']!=state['pending']['run_id']:raise Conflict('Child run differs')
            item=observation(state['pending']['candidate'],child)
            if item and item['id'] not in {o['id'] for o in state['observations']}:state['observations'].append(item)
            state['record_comparisons']=record_pairs(state['envelope'],state['observations'])
            state['aggregate_reconciliations']=reconcile_aggregates(self.store,state['model_id'],state['observations'])
            if self.governor:self.governor.settle(db,identity,state['pending'].get('reservation_key','tool:'+str(state['cloud_calls'])),uncertain=child['status'] not in ('COMPLETED','CANCELLED') and not any(s['status']=='FAILED' for s in child['steps']))
            if child['status']!='COMPLETED':self.stop(db,state,'TOOL_UNAVAILABLE','HELD')
            else:
                try:self.admit(state)
                except Conflict:self.stop(db,state,'ADMISSION_CHANGED','HELD')
                else:
                    from .progress_policy import informative
                    state['no_progress']=0 if informative(item) else state.get('no_progress',0)+1
                    state.update(status='READY',token=None,pending=None)
                    self.save(db,state,'OBSERVED',{'run_id':child['id'],'observation_id':item['id']})
        return self.get(identity)

    @operation('run')
    def run(self,identity):
        from .physical_reads import guard_scope
        def record_guard(event):
            with self.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE');state=self.load(db,identity);self.admit(state)
                state.setdefault('guard_evidence',[]).append(event)
                self.save(db,state,'SQL_GUARD_'+event['status'],event)
        with guard_scope(record_guard):
            return self._run(identity)

    def _run(self,identity):
        with self.runtime.db() as db:
            state=self.load(db,identity)
        from .process_debugging import VERSION as process_version
        if state['envelope'].get('strategy')==process_version and not state.get('process_started'):
            return self.run_process(identity)
        return self.run_open(identity)

    def run_open(self,identity):
        while True:
            result=self.step(identity)
            if result['status']!='READY':return result

    def run_process(self,identity):
        """Execute the deterministic vertical strategy; open planning is fallback only."""
        from .adapters.microsoft_process import MicrosoftProcessAdapter
        from .process_debugging import vertical
        from .assessment_support import validate as validate_support
        with self.runtime.db() as db:
            state=self.load(db,identity);self.admit(state)
            if state['status']!='READY':return self.get(identity)
        model=self.store.get(state['model_id'])

        def meter_read(tool,execute,physical_only=False):
            with self.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE');current=self.load(db,identity);self.admit(current)
                if current['status']!='EXECUTING' or self.clock()>=current['deadline']:raise UsageHold('Read cancelled or deadline exhausted')
                if not physical_only and current['cloud_calls']>=current['envelope']['limits']['cloud_calls']:
                    raise UsageHold('Investigation diagnostic-read limit')
                from . import process_budget
                if not physical_only:process_budget.admit(current,tool)
                number=current.get('physical_calls',current['cloud_calls'])+1;key='tool:process:'+str(number)
                if self.governor:self.governor.reserve(db,identity,key,'cloud')
                current['physical_calls']=number
                if not physical_only:
                    current['cloud_calls']+=1
                    process_budget.charge(current)
                current['read_accounting_version']='diagnostic-operations-v1'
                self.save(db,current,'PROCESS_READ_RESERVED',{'tool':tool,'physical_calls':number,'diagnostic_reads':current['cloud_calls'],'physical_only':physical_only})
            uncertain=False;result=None;error_type=None;physical=None
            try:
                from .physical_reads import scope
                with scope(lambda kind,call:meter_read(kind,call,True)) as physical: result=execute()
                return result
            except Exception as exc:
                uncertain=True;error_type=type(exc).__name__;raise
            finally:
                # Persist the read independently of interpretation and support validation.
                from .process_read_receipts import receipt
                first=physical.get('first_report') if physical else None
                entry=receipt(number,first['request_kind'] if first else tool,first or result,
                              error_type if not first or first['status']=='UNCERTAIN' else None)
                if first:
                    entry['logical_tool']=tool
                    entry['logical_receipt']=receipt(number,tool,result,error_type)
                with self.runtime.db() as db:
                    db.execute('BEGIN IMMEDIATE');current=self.load(db,identity)
                    current.setdefault('process_read_receipts',[]).append(entry)
                    self.save(db,current,'PROCESS_READ_RECORDED',entry)
                    if self.governor:self.governor.settle(db,identity,key,uncertain=uncertain)

        provider=self.process_judge
        if provider is None and self.planner_profile.get('adapter')=='azure':
            from .transformation_judgment import azure_judge
            provider=azure_judge

        from .evidence_prose import IncompleteProse

        def judgment_event(kind,detail):
            with self.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE');current=self.load(db,identity)
                self.save(db,current,kind,detail)

        def judge_once(payload,attempt):
            size=len(encoded(payload))
            with self.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE');current=self.load(db,identity);self.admit(current)
                if current['status']!='EXECUTING' or self.clock()+self.generation_options['timeout_seconds']>current['deadline']:
                    return {'status':'UNAVAILABLE','explains':None,'reason':'Judgment cancelled or deadline exhausted.'}
                if current['planner_calls']>=current['envelope']['limits']['planner_calls']:
                    return {'status':'UNAVAILABLE','explains':None,'reason':'Investigation planner-call limit reached.'}
                if current['input_characters']+size>current['envelope']['limits']['input_characters']:
                    return {'status':'UNAVAILABLE','explains':None,'reason':'Investigation input-character limit reached.'}
                number=current['planner_calls']+1;key='process-judgment:'+str(number)
                output=self.generation_options['max_output_tokens']
                if self.governor:self.governor.reserve(db,identity,key,'planner',size,output_tokens=output)
                current['planner_calls']=number;current['input_characters']+=size
                self.save(db,current,'PROCESS_JUDGMENT_RESERVED',{'planner_calls':number,'input_characters':size,'attempt':attempt})
            metadata=None;received=False
            try:
                from .planner_recording import recording
                with recording({'session_id':identity,'phase':'PROCESS_JUDGMENT','planner_call':number,
                    'attempt':attempt,'retry_reason':'INCOMPLETE_PROSE' if attempt==2 else None,
                    'context_version':current.get('discovery_version'),'payload':payload,
                    'planner_profile':self.planner_profile,'usage_policy':self.governor.policy if self.governor else None,
                    'reservation':{'key':key,'input_characters':size,'output_tokens':output}}):
                    result,metadata=provider(payload,dict(self.generation_options));received=True
                judgment_event('PROCESS_JUDGMENT_COMPLETED',{'planner_call':number,'attempt':attempt,'retried':attempt==2})
                return result
            except IncompleteProse as exc:
                metadata=getattr(exc,'provider_metadata',None);received=True
                judgment_event('PROCESS_JUDGMENT_REJECTED',{'planner_call':number,'attempt':attempt,'reason_code':'INCOMPLETE_PROSE'})
                raise
            except Exception as exc:
                # Composition/provider failures are not absent estate capabilities.
                # The process failure recorder retains the safe diagnostic.
                raise
            finally:
                if self.governor:
                    usage=metadata.get('usage') if isinstance(metadata,dict) else None
                    with self.runtime.db() as db:
                        db.execute('BEGIN IMMEDIATE')
                        self.governor.settle(db,identity,key,usage,uncertain=not received and not usage)

        def judge(payload):
            for attempt in (1,2):
                try:
                    result=judge_once(payload,attempt)
                    if attempt==2 and result.get('status')=='UNAVAILABLE':
                        raise RuntimeError('Judgment retry unavailable')
                    return result
                except IncompleteProse:
                    if attempt==2:
                        judgment_event('PROCESS_JUDGMENT_RETRY_EXHAUSTED',{'attempts':2,'reason_code':'INCOMPLETE_PROSE'})
                        raise
                    judgment_event('PROCESS_JUDGMENT_RETRY',{'previous_attempt':1,'next_attempt':2,'reason_code':'INCOMPLETE_PROSE'})
                except Exception:
                    if attempt==2:judgment_event('PROCESS_JUDGMENT_RETRY_EXHAUSTED',{'attempts':2,'reason_code':'RETRY_UNAVAILABLE'})
                    raise

        def read_ingestion(request):
            def execute():
                import subprocess
                from metadata_config import ROOT
                from .physical_reads import run as physical_run
                completed=physical_run([self.config['fabric']['auth']['python'],
                    str(ROOT/'scripts/read_onelake_commit.py')],input=encoded(request),capture_output=True,
                    text=True,encoding='utf-8',timeout=90)
                try:result=json.loads(completed.stdout)
                except (ValueError,TypeError):return {'status':'UNAVAILABLE','error_type':'InvalidResponse'}
                return result if not completed.returncode else {'status':'UNAVAILABLE','error_type':result.get('error_type','TransportError')}
            return meter_read('onelake_commit',execute)

        def read_failure_detail(request):
            def execute():
                import subprocess
                from metadata_config import ROOT
                fabric=self.config['fabric']
                payload=dict(request,tenant=fabric['auth']['tenant_id'],account=fabric['native_reader']['account'],
                             library=fabric['xmla_client']['library'])
                from .tape_worker import run as worker_run
                completed=worker_run([fabric['auth']['python'],str(ROOT/'scripts/read_xmla_failure.py')],
                    input=encoded(payload),capture_output=True,text=True,encoding='utf-8',timeout=180)
                try:return json.loads(completed.stdout)
                except (ValueError,TypeError):return {'status':'UNAVAILABLE','error_type':'InvalidResponse','codes':[]}
            return meter_read('xmla_failure_detail',execute,True)

        def read_endpoint(request):
            def execute():
                import subprocess
                from metadata_config import ROOT
                from uuid import UUID
                if request['workspace']!=self.config['fabric']['workspace_id']:
                    raise ValueError('Endpoint lookup leaves approved workspace')
                workspace=str(UUID(request['workspace']))
                kind='warehouses' if 'warehouse' in request else 'lakehouses'
                container=str(UUID(request['warehouse'] if kind=='warehouses' else request['lakehouse']))
                endpoint=f'workspaces/{workspace}/{kind}/{container}'
                try:
                    payload={'operation':'request','endpoint':endpoint,'method':'get','audience':'fabric',
                             'tenant':self.config['fabric']['auth']['tenant_id']}
                    from .tape_worker import run as worker_run
                    result=worker_run([self.config['fabric']['auth']['python'],str(ROOT/'scripts/metadata_worker.py')],
                        input=encoded(payload),capture_output=True,text=True,encoding='utf-8',timeout=90)
                    response=json.loads(result.stdout)
                    if response.get('status_code')!=200:return {'status':'UNAVAILABLE','http_status':response.get('status_code')}
                    body=response['text']
                    if kind=='warehouses':
                        return {'id':body['id'],'properties':{
                            'connectionString':body.get('properties',{}).get('connectionString')}}
                    properties=body.get('properties',{}).get('sqlEndpointProperties',{})
                    return {'id':body['id'],'properties':{'sqlEndpointProperties':{
                        k:properties[k] for k in ('id','connectionString') if k in properties}}}
                except (ValueError,KeyError,subprocess.TimeoutExpired):return {'status':'UNAVAILABLE'}
            return meter_read('fabric_endpoint_metadata',execute)

        # The independent lower surface: declared only when the reader's own
        # session is present (a local check, no token request).
        lower_surface=None;execute_lower=None
        reader_config=self.config['fabric']
        sql_reader=reader_config.get('sql_reader')
        if sql_reader:
            from fabric_sql_auth import session_status
            from fabric_sql_surface import read as read_lower
            lower_surface=session_status(self.config['fabric']['auth']['tenant_id'],sql_reader['account'],sql_reader['profile'])
            execute_lower=lambda database,request:read_lower(self.config,database,request)
        def read_refresh_timing():
            from refresh_timing_reader import read
            from .process_tape import bounded_call
            return meter_read('optional_refresh_timing',lambda:bounded_call('optional_refresh_timing',
                {'model':model['native_id'],'profile':reader_config['refresh_timing_reader']},
                lambda:read(self.config,model)))
        def read_snapshot_identity(probe,workspace_name):
            from snapshot_identity_reader import read
            from .process_tape import bounded_call
            return meter_read('optional_snapshot_identity',lambda:bounded_call('optional_snapshot_identity',
                {'model':model['native_id'],'profile':reader_config['snapshot_identity_reader'],
                 'probe':probe.evidence,'workspace_name':workspace_name},
                lambda:read(self.config,model,probe,workspace_name)))
        def remaining_diagnostic_reads():
            with self.runtime.db() as db:
                current=self.load(db,identity)
            from .process_budget import remaining
            return remaining(current)
        adapter=MicrosoftProcessAdapter(self.store,self.config,model,
            self.runtime.native_transport,self.runtime.source_transport,
            judge_definition=judge if provider is not None else None,meter_read=meter_read,
            remaining_diagnostic_reads=remaining_diagnostic_reads,
            read_ingestion=read_ingestion,
            read_failure_detail=read_failure_detail if self.config['fabric'].get('xmla_client') else None,
            lower_surface=lower_surface,execute_lower=execute_lower,
            max_boundaries=self.process_max_boundaries,read_endpoint=read_endpoint,
            read_refresh_timing=read_refresh_timing if self.config['fabric'].get('refresh_timing_reader') else None,
            read_snapshot_identity=read_snapshot_identity if self.config['fabric'].get('snapshot_identity_reader') else None)
        def stage_event(kind, detail):
            with self.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE');current=self.load(db,identity)
                self.save(db,current,kind,detail)
        from .process_stages import Adapter as StageAdapter
        adapter=StageAdapter(adapter,stage_event)
        from .context_search import MeasurePathLimit
        try:
            path=adapter.resolve_path(state['envelope']['measure_id'])
        except MeasurePathLimit as exc:
            with self.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE');current=self.load(db,identity);self.admit(current)
                if current['status']!='READY':return self.project_after_commit(db,current)
                self.stop(db,current,'PATH_CONTEXT_LIMIT','HELD')
                current['process_error']='PATH_CONTEXT_LIMIT'
                self.save(db,current,'PROCESS_PATH_REFUSED',{'reason':'PATH_CONTEXT_LIMIT',
                    'characters':exc.characters,'limit':exc.limit,
                    'limitation':'The complete measure path exceeds the context bound; no evidence was truncated and no data read was attempted.'})
                return self.project_after_commit(db,current)
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');state=self.load(db,identity);self.admit(state)
            if state['status']!='READY':return self.project_after_commit(db,state)
            state['process_started']=True;state['status']='EXECUTING'
            self.save(db,state,'PROCESS_STARTED',{'procedure':'VERTICAL','reserved_reads':0})
        from . import observation_journal
        error=None;budget_error=None;assessment=None;observations=[];journal=observation_journal.Journal()
        try:
            from .definition_target import procedure_scope
            with observation_journal.scope(journal):
                if self.process_lineage is not None:
                    stage_event('PROCESS_STAGE_STARTED',{'stage':'context','operation':'qualify_lineage'})
                    lineage_error=None
                    try:path=self.process_lineage(adapter,path,state['envelope'],meter_read)
                    except BaseException as exc:
                        lineage_error=type(exc).__name__;raise
                    finally:stage_event('PROCESS_STAGE_FINISHED',{'stage':'context','operation':'qualify_lineage','error_type':lineage_error})
                    adapter.resolve_path=lambda measure:path
                assessment=vertical(adapter,state['envelope']['measure_id'],procedure_scope(state['envelope']))
            observations=assessment.pop('_observations',None)
            if observations is None:
                observations=getattr(adapter,'observations',None)
            if observations is None:
                # Internal technical output alone is insufficient for validation.
                raise ValueError('Process procedure did not return its evidence chain')
            validate_support(assessment,{o['id']:o for o in observations})
        except UsageHold as exc:
            budget_error=str(exc)
            observations=list({o['id']:o for o in journal if o.get('id')}.values())
        except Exception as exc:
            from .process_failure import capture
            error=capture(exc)
            observations=list({o['id']:o for o in journal if o.get('id')}.values())
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');state=self.load(db,identity)
            if budget_error:
                state['observations'].extend(observations)
                from .process_receipts import refusal
                used=state['cloud_calls'];limit=state['envelope']['limits']['cloud_calls']
                reason=f'Read budget stopped after {used} of {limit} diagnostic reads; the next requested check did not run.'
                from . import process_budget
                receipt=refusal('BUDGET_STOP',reason,'budget-stop-'+str(len(state['observations'])),budget=dict(diagnostic_reads=used,diagnostic_limit=limit,
                    phase_counts=state.get('diagnostic_phase_counts',{'WALK':0,'REPRODUCTION':0}),
                    phase_limits=process_budget.allocation(limit,state['envelope']),
                    admission_reason=budget_error,not_run_probes=list(journal.pending_probes)))
                state['observations'].append(receipt)
                self.stop(db,state,'BUDGET_LIMIT','HELD')
                self.save(db,state,'PROCESS_BUDGET_STOPPED',{'diagnostic_reads':used,'diagnostic_limit':limit,
                    'admission_reason':budget_error,'not_run_probes':receipt['not_run_probes']})
                return self.project_after_commit(db,state)
            if error:
                state['observations'].extend(observations or [])
                from .process_receipts import refusal
                state['observations'].append(refusal('PROCESS_FAILED',error['message'],
                    'process-failed-'+str(len(state['observations'])),failure=error))
                self.stop(db,state,'PROCESS_FAILED','HELD')
                state['process_error']=error;self.save(db,state,'PROCESS_FAILED',error)
                return self.project_after_commit(db,state)
            state['observations'].extend(observations);state['assessment']=assessment
            state.update(status='COMPLETED',stop_reason='ENOUGH_DIAGNOSTICS',token=None,pending=None)
            self.save(db,state,'PROCESS_STOPPED',{'classification':assessment['classification'],
                'terminating_step':assessment['terminating_step']})
            return self.project_after_commit(db,state)

    @operation('synthesize')
    def synthesize(self,identity,provider=None):
        from .evidence_synthesis import run,azure_synthesize
        run(self,identity,provider or azure_synthesize)
        return self.get(identity)

    def recover(self,identity):
        token=str(uuid4())
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');state=self.load(db,identity)
            if state['status'] not in ('PLANNING','EXECUTING','HELD'):raise Conflict('No interrupted work')
            # No planner call is silently replayed, including unknown provider completion.
            if state['status']=='PLANNING':
                if self.governor:self.governor.settle(db,identity,'planner:'+str(state['planner_calls']),uncertain=True)
                self.stop(db,state,'PLANNER_COMPLETION_UNCERTAIN','HELD');return self.project_after_commit(db,state)
            if not state['pending']:raise Conflict('Held session requires a reviewed new scope/session')
            state.update(status='EXECUTING',token=token);self.save(db,state,'RECOVERY_CLAIMED')
            pending=state['pending']
        with self.runtime.db() as db:
            row=db.execute('SELECT id FROM v2_runs WHERE model_id=? AND request_key=?',(state['model_id'],pending['key'])).fetchone()
        if row is None:
            # No child exists: new dispatch still passes all original admission gates.
            return self.dispatch(identity,token)
        child=self.runtime.get(row['id'])
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');state=self.load(db,identity)
            if state['token']!=token:raise Conflict('Recovery fenced')
            state['pending']['run_id']=child['id'];self.save(db,state,'CHILD_RECOVERED',{'run_id':child['id']})
        if child['status']=='HELD' and any(step['status']=='FAILED' for step in child['steps']):
            return self.consume(identity,token,child)
        if child['status'] in ('RUNNING','HELD'):
            try:child=self.runtime.reconcile(child['id'])
            except Conflict:
                with self.runtime.db() as db:
                    db.execute('BEGIN IMMEDIATE');state=self.load(db,identity)
                    if state['token']==token:self.stop(db,state,'REMOTE_COMPLETION_UNCERTAIN','HELD')
                return self.get(identity)
        if child['status']=='READY':
            with self.runtime.db() as db:
                state=self.load(db,identity);self.admit(state)
                if self.clock()+(300 if pending['candidate']['tool'] in ('source','source_records','bounded_sql') else 120)>state['deadline']:
                    self.stop(db,state,'DEADLINE','HELD');return self.project_after_commit(db,state)
            return self.dispatch(identity,token)
        return self.consume(identity,token,child)

    def revise(self,identity,envelope,key):
        previous=self.get(identity)
        if previous['status']!='NEEDS_INPUT':raise Conflict('Only clarification creates a scope successor')
        if previous['model_id']!=envelope['model_id']:raise Conflict('Cannot move scope to another model')
        # A separate explicitly approved session: no old observations become eligible.
        return self.create(envelope,key,predecessor={'session_id':identity,'scope_hash':previous['scope_hash']})

    def cancel(self,identity):
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');state=self.load(db,identity)
            from .evidence_synthesis import cancel as cancel_synthesis
            if cancel_synthesis(self,db,identity):return self.project_after_commit(db,state)
            if state['status'] in ('COMPLETED','CANCELLED'):return self.get(identity)
            pending=state['pending']
            if pending:
                child=db.execute('SELECT id FROM v2_runs WHERE model_id=? AND request_key=?',(state['model_id'],pending['key'])).fetchone()
                if child:self.runtime.cancel_in_transaction(db,child['id'])
                if self.governor:self.governor.settle(db,identity,state['pending'].get('reservation_key','tool:'+str(state['cloud_calls'])),uncertain=bool(child))
            elif state['status']=='PLANNING' and self.governor:
                self.governor.settle(db,identity,'planner:'+str(state['planner_calls']),uncertain=True)
            if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='adaptive_usage'").fetchone():
                db.execute("UPDATE adaptive_usage SET status='UNCERTAIN',actual='{}' WHERE session_id=? AND status='RESERVED'",(identity,))
            self.stop(db,state,'USER_CANCELLED','CANCELLED')
        return self.get(identity)

    def reconcile_cancelled(self,identity):
        state=self.get(identity)
        if state['status']!='CANCELLED':raise Conflict('Expected cancelled session')
        if not state['pending']:return state
        with self.runtime.db() as db:
            row=db.execute('SELECT id FROM v2_runs WHERE model_id=? AND request_key=?',(state['model_id'],state['pending']['key'])).fetchone()
        if row is None:return state
        self.runtime.cancel(row['id'])
        child=self.runtime.reconcile(row['id']) if any(s['status']=='DISPATCHED' for s in self.runtime.get(row['id'])['steps']) else self.runtime.get(row['id'])
        item=observation(state['pending']['candidate'],child)
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');current=self.load(db,identity)
            if current['status']!='CANCELLED':raise Conflict('Cancellation state differs')
            if item and item['id'] not in {o['id'] for o in current['observations']}:
                current['observations'].append(item)
                current['record_comparisons']=record_pairs(current['envelope'],current['observations'])
                current['aggregate_reconciliations']=reconcile_aggregates(self.store,current['model_id'],current['observations'])
                self.save(db,current,'CANCELLED_RECEIPT_ADOPTED',{'observation_id':item['id']})
        return self.get(identity)

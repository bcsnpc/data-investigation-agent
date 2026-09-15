"""Durable evidence-led sessions over the existing receipt-fenced diagnostic runtime.

Planner suggestions are unverified. This module owns scope, budgets, facts and stops.
"""
from datetime import datetime, timezone
import json
import time
from uuid import uuid4

from .onboarding import digest, encoded, text, Conflict
from .runtime import fingerprint
from .adaptive_candidates import catalog, available, observation, diagnostic_pairs, record_pairs
from .adaptive_planner import validate, VERSION
from .usage_governance import UsageGovernor,UsageHold


def now():
    return datetime.now(timezone.utc).isoformat()


def outcome(state):
    reason=state.get('stop_reason')
    classification='UNRESOLVED' if reason in ('BUDGET_LIMIT','DEADLINE','PLANNER_FAILED','TOOL_UNAVAILABLE','PLANNER_COMPLETION_UNCERTAIN','REMOTE_COMPLETION_UNCERTAIN','USAGE_LIMIT','NO_PROGRESS','USER_CANCELLED') else 'INSUFFICIENT_EVIDENCE'
    return {'classification':classification,'stop_reason':reason,
            'record_comparisons':state.get('record_comparisons',[]),
            'scoped_conditions':[{'observation_id':o['id'], **o['freshness']} for o in state['observations']
                                 if o.get('freshness')],
            'facts':state['observations'],'diagnostic_pairs':diagnostic_pairs(state['observations']),'hypotheses':[{**h,'verified':False} for h in state['hypotheses']],
            'gaps':state['gaps']+[{'reason':'MAPPING_CONTEXT_VERSION_AND_CAUSAL_PROOF_NOT_VERIFIED'}],
            'cause_verified':False,'delivery_eligible':False}


class AdaptiveRuntime:
    def __init__(self,runtime,planner,clock=time.time,planner_profile=None,usage_policy=None):
        self.runtime=runtime;self.store=runtime.store;self.config=runtime.config
        self.planner=planner;self.clock=clock
        self.planner_profile=planner_profile or {"adapter":"injected"}
        self.governor=UsageGovernor(runtime,usage_policy,clock) if usage_policy is not None else None
        with runtime.db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS adaptive_sessions(
              id TEXT PRIMARY KEY,model_id TEXT,request_key TEXT,request_hash TEXT,
              state TEXT,state_hash TEXT,UNIQUE(model_id,request_key));
            CREATE TABLE IF NOT EXISTS adaptive_events(
              id INTEGER PRIMARY KEY,session_id TEXT,kind TEXT,detail TEXT,created TEXT);
            """)

    def save(self,db,state,kind,detail=None):
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
        try:candidates,gaps=catalog(self.store,self.config,state['envelope'])
        except (ValueError,KeyError) as exc:raise Conflict('Candidate metadata or review is no longer admissible') from exc
        if digest(candidates)!=state['catalog_hash']:raise Conflict('Candidate admission changed')
        return candidates

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
            events=[{'kind':r['kind'],'detail':json.loads(r['detail']),'created':r['created']} for r in
                    db.execute('SELECT kind,detail,created FROM adaptive_events WHERE session_id=? ORDER BY id',(identity,))]
        state.pop('token');state['outcome']=outcome(state);state['events']=events
        return state

    def payload(self,state,candidates):
        model=self.store.get(state['model_id'])
        assets=model['context']['reports'][0]['model_assets']
        names={a['id']:a.get('name',a['id']) for a in assets}
        choices=[{'id':c['id'],'tool':c['tool'],'measure_id':c['measure_id'],
                  'measure_name':names.get(c['measure_id'],c['measure_id']),
                  'dimension_id':c['dimension_id'],'depth':c['depth'],
                  'operations':model['context'].get('semantic_graph',{}).get('measures',{}).get(c['measure_id'],{}).get('operations',[]),
                  'source_binding':c.get('reviewed_mapping') or ('OPERATOR_SELECTED_NOT_EQUIVALENCE_PROOF' if c['tool']=='source' else None),
                  'source_operation':c['plan'].get('operation'), 'approved_filters':c['plan']['filters'],
                  'projected_columns':c['plan'].get('column_ids'),'record_limit':c['plan'].get('limit')} for c in candidates]
        observations=[]
        for o in state['observations']:
            sampled=[];size=0
            for value in o['values'][:20]:
                size+=len(encoded(value))
                if size>6000:break
                sampled.append(value)
            observations.append({**o,'values':sampled,'planner_sample_truncated':len(sampled)<len(o['values'])})
        return {'symptom':state['envelope']['symptom'],'scope_hash':state['scope_hash'],
                'filters':state['envelope']['filters'],'candidates':choices,
                'observations':observations,'diagnostic_pairs':diagnostic_pairs(state['observations']),
                'record_comparisons':[{**p,'differences':p.get('differences',[])[:3],
                                       'planner_examples_truncated':len(p.get('differences',[]))>3} for p in state.get('record_comparisons',[])],
                'hypotheses':state['hypotheses'],'gaps':state['gaps'],
                'remaining_cloud_calls':state['envelope']['limits']['cloud_calls']-state['cloud_calls'],
                'limitation':'All observations are diagnostic only; no semantic equivalence or causal proof.'}

    def stop(self,db,state,reason,status='COMPLETED'):
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
            choices=available(candidates,state['observations'],state['attempted']);limits=state['envelope']['limits']
            reason=None
            if self.clock()+45>state['deadline']:reason='DEADLINE'
            elif state['planner_calls']>=limits['planner_calls'] or state['cloud_calls']>=limits['cloud_calls']:reason='BUDGET_LIMIT'
            elif state.get('no_progress',0)>=(self.governor.policy['no_progress_limit'] if self.governor else 2):reason='NO_PROGRESS'
            elif not choices:reason='NO_ADMITTED_TEST'
            payload=self.payload(state,choices);size=len(encoded(payload))
            if size>32000 or state['input_characters']+size>limits['input_characters']:reason='BUDGET_LIMIT'
            if reason:
                self.stop(db,state,reason);return self.project_after_commit(db,state)
            if self.governor:
                try:self.governor.reserve(db,identity,'planner:'+str(state['planner_calls']+1),'planner',size)
                except UsageHold:
                    self.stop(db,state,'USAGE_LIMIT','HELD');return self.project_after_commit(db,state)
            state.update(status='PLANNING',token=token)
            state['planner_calls']+=1;state['input_characters']+=size
            self.save(db,state,'PLANNER_RESERVED',{'payload_hash':digest(payload),'input_characters':size})
        try:
            proposal,usage=self.planner(payload)
            decision=validate(proposal,payload)
        except Exception as exc:
            with self.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE');state=self.load(db,identity)
                if self.governor:self.governor.settle(db,identity,'planner:'+str(state['planner_calls']),uncertain=True)
                if state['token']==token:
                    self.stop(db,state,'PLANNER_FAILED','HELD')
                    self.save(db,state,'PLANNER_ERROR',{'error_type':type(exc).__name__})
            return self.get(identity)
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');state=self.load(db,identity)
            if self.governor:self.governor.settle(db,identity,'planner:'+str(state['planner_calls']),usage.get('usage') if isinstance(usage,dict) else None)
            if state['token']!=token or state['status']!='PLANNING':raise Conflict('Planner is fenced')
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
            elif decision['action']=='STOP':self.stop(db,state,decision['stop_reason'])
            else:
                candidate=next(c for c in choices if c['id']==decision['candidate_id'])
                seconds=300 if candidate['tool'] in ('source','source_records') else 120
                if self.clock()+seconds>state['deadline']:self.stop(db,state,'DEADLINE')
                else:
                    if self.governor:
                        try:self.governor.reserve(db,identity,'tool:'+str(state['cloud_calls']+1),'cloud')
                        except UsageHold:
                            self.stop(db,state,'USAGE_LIMIT','HELD');return self.project_after_commit(db,state)
                    state['cloud_calls']+=1;state['attempted'].append(candidate['id'])
                    state.update(status='EXECUTING',pending={'candidate':candidate,'key':identity+':'+str(state['cloud_calls']),'run_id':None})
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
            if self.clock()+(300 if candidate['tool'] in ('source','source_records') else 120)>state['deadline']:
                self.stop(db,state,'DEADLINE','HELD');return self.project_after_commit(db,state)
        child=self.runtime.create({'model_id':state['model_id'],'call_budget':1,
                                  'actions':[{'tool':candidate['tool'],'input':candidate['plan']}]},pending['key'])
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');state=self.load(db,identity)
            if state['status']=='CANCELLED':
                self.runtime.cancel_in_transaction(db,child['id']);db.commit();return self.get(identity)
            if state['token']!=token or state['status']!='EXECUTING':raise Conflict('Dispatcher fenced')
            state['pending']['run_id']=child['id'];self.save(db,state,'CHILD_LINKED',{'run_id':child['id']})
        try:result=self.runtime.execute(child['id'])
        except Conflict:
            if self.get(identity)['status']=='CANCELLED':return self.get(identity)
            raise
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
            if self.governor:self.governor.settle(db,identity,'tool:'+str(state['cloud_calls']),uncertain=child['status'] not in ('COMPLETED','CANCELLED') and not any(s['status']=='FAILED' for s in child['steps']))
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

    def run(self,identity):
        while True:
            result=self.step(identity)
            if result['status']!='READY':return result

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
                if self.clock()+(300 if pending['candidate']['tool'] in ('source','source_records') else 120)>state['deadline']:
                    self.stop(db,state,'DEADLINE','HELD');return self.project_after_commit(db,state)
            child=self.runtime.execute(child['id'])
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
            if state['status'] in ('COMPLETED','CANCELLED'):return self.get(identity)
            pending=state['pending']
            if pending:
                child=db.execute('SELECT id FROM v2_runs WHERE model_id=? AND request_key=?',(state['model_id'],pending['key'])).fetchone()
                if child:self.runtime.cancel_in_transaction(db,child['id'])
                if self.governor:self.governor.settle(db,identity,'tool:'+str(state['cloud_calls']),uncertain=bool(child))
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
                self.save(db,current,'CANCELLED_RECEIPT_ADOPTED',{'observation_id':item['id']})
        return self.get(identity)

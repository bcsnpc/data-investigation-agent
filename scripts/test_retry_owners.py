import json,unittest,copy
from types import SimpleNamespace
from unittest.mock import patch
from test_model_transport_retry import RetryTests,retry,Throttle,no_sidecar
from investigator.onboarding import digest
from investigator.usage_governance import UsageHold

class OwnerTests(RetryTests):
    def setUp(self):
        super().setUp()
        self.state={'status':'PLANNING','deadline':2000,'planner_calls':1,'input_characters':100,
            'envelope':{'limits':{'planner_calls':2,'input_characters':1000}}}
        with self.runtime.db() as db:
            db.execute('CREATE TABLE own_state(body TEXT)');db.execute('INSERT INTO own_state VALUES(?)',(json.dumps(self.state),))
        def load(db,identity):return json.loads(db.execute('SELECT body FROM own_state').fetchone()[0])
        def save(db,state,*args):db.execute('UPDATE own_state SET body=?',(json.dumps(state),))
        self.agent=SimpleNamespace(runtime=self.runtime,governor=self.governor,clock=lambda:1000,load=load,save=save,
            admit=lambda state,db:None,generation_options={'max_output_tokens':8000})
    def perform(self,scope):
        seen=[]
        def send(body):
            seen.append(copy.deepcopy(body))
            if len(seen)==1:raise Throttle('capacity')
            return SimpleNamespace(usage={'input_tokens':2,'output_tokens':3})
        with scope,patch('investigator.planner_recording.recording',no_sidecar),patch.object(retry.time,'sleep',lambda n:None):
            retry.dispatch(self.body,send)
        self.assertEqual(len(seen),2)
    def test_adaptive_and_judge_retries_charge_local_counters_before_send(self):
        for phase in ('PLANNING','EXECUTING'):
            with self.runtime.db() as db:
                state=copy.deepcopy(self.state);state['status']=phase;self.agent.save(db,state)
            self.perform(retry.adaptive_scope(self.agent,'session','initial',100,8000,phase))
            with self.runtime.db() as db:current=self.agent.load(db,'session')
            self.assertEqual(current['transport_planner_calls'],1);self.assertEqual(current['input_characters'],200)
            calls=[]
            with retry.adaptive_scope(self.agent,'session','initial',100,8000,phase),patch.object(retry.time,'sleep',lambda n:None),self.assertRaises(UsageHold):
                retry.dispatch(self.body,lambda body:(calls.append(1),(_ for _ in ()).throw(Throttle('capacity')))[1])
            self.assertEqual(calls,[1])
    def test_intake_retry_preserves_logical_record_and_records_physical_attempt(self):
        body={'id':'owned','status':'RESOLVING','expires':2000,'catalog_hash':digest([]),
            'engine_hash':'revision','config_hash':digest({}),'planner_hash':digest({})}
        self.agent.config={};self.agent.planner_profile={}
        def resolver(payload):pass
        resolver.request_characters=lambda payload:100;resolver.request_output_tokens=lambda payload:8000
        def save(db,current):db.execute('UPDATE workspace_intakes SET body=?,hash=? WHERE id=?',(json.dumps(current),digest(current),current['id']))
        workspace=SimpleNamespace(agent=self.agent,clock=lambda:1000,dynamic_input_limit=1000)
        intake=SimpleNamespace(workspace=workspace,resolver=resolver,save=save)
        with self.runtime.db() as db:
            db.execute('CREATE TABLE workspace_intakes(id TEXT,body TEXT,hash TEXT)')
            db.execute('INSERT INTO workspace_intakes VALUES(?,?,?)',(body['id'],json.dumps(body),digest(body)))
            self.governor.reserve(db,'intake:owned','resolve','planner',100,output_tokens=8000)
        with patch('investigator.question_intake.snapshot',return_value=[]),patch('investigator.question_intake.fingerprint',return_value='revision'):
            self.perform(retry.intake_scope(intake,body,{},'resolve'))
        self.assertEqual(body['id'],'owned');self.assertEqual(len(body['transport_attempts']),1)
        with self.runtime.db() as db:current=json.loads(db.execute('SELECT body FROM workspace_intakes').fetchone()[0])
        self.assertEqual(current['transport_attempts'],body['transport_attempts'])
    def test_synthesis_retry_preserves_frozen_investigation_and_counts_attempt(self):
        from investigator.evidence_synthesis import read,save
        with self.runtime.db() as db:
            db.execute('CREATE TABLE adaptive_syntheses(session_id TEXT PRIMARY KEY,body TEXT,hash TEXT)')
            save(db,'session',{'status':'RUNNING','deadline':2000,'source_hash':digest(self.state)})
        self.perform(retry.synthesis_scope(self.agent,'session','initial',100,2000))
        with self.runtime.db() as db:
            current=read(db,'session',full=True);source=self.agent.load(db,'session')
        self.assertEqual(source,self.state);self.assertEqual(current['transport_calls'],1)
    def test_old_tape_scope_does_not_change_events_or_settlement(self):
        old=SimpleNamespace(replaying=True,bootstrap={'state':{}})
        with patch.object(retry.journal,'ACTIVE',SimpleNamespace(get=lambda:old)):
            with self.scope() as owner:self.assertIsNone(owner)

if __name__=='__main__':unittest.main()

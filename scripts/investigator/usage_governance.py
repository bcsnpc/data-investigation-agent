"""Durable daily reservations shared by adaptive sessions in one catalog/estate."""
from datetime import datetime,timezone
import json
from .onboarding import fields,digest,encoded,Conflict

KEYS=('planner_calls','cloud_calls','input_characters','output_tokens')


class UsageHold(Conflict):pass


class UsageGovernor:
    def __init__(self,runtime,policy,clock):
        fields(policy,['environment','daily_limits','max_inflight_planners','no_progress_limit'])
        if not isinstance(policy['environment'],str) or policy['environment']!=runtime.store.environment:
            raise ValueError('Policy must match configured environment')
        fields(policy['daily_limits'],KEYS)
        for value in policy['daily_limits'].values():
            if type(value) is not int or not 1<=value<=10000000:raise ValueError('Invalid daily limit')
        for key,maximum in [('max_inflight_planners',4),('no_progress_limit',4)]:
            if type(policy[key]) is not int or not 1<=policy[key]<=maximum:raise ValueError('Invalid policy limit')
        self.runtime=runtime;self.policy=json.loads(encoded(policy));self.clock=clock
        self.environment=policy['environment'];self.hash=digest(policy)
        with runtime.db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS adaptive_usage(
              environment TEXT,session_id TEXT,reservation_key TEXT,day TEXT,kind TEXT,
              reserved TEXT,actual TEXT,status TEXT,policy_hash TEXT,created REAL,
              PRIMARY KEY(environment,session_id,reservation_key));
            """)

    def day(self):return datetime.fromtimestamp(self.clock(),timezone.utc).date().isoformat()

    def reserve(self,db,session_id,key,kind,characters=0,*,output_tokens=1500):
        # Caller holds BEGIN IMMEDIATE; budget and session transition commit together.
        if kind not in ('planner','cloud'):raise ValueError('Unknown usage kind')
        amount=dict.fromkeys(KEYS,0)
        if type(output_tokens) is not int or not 500<=output_tokens<=8000:raise ValueError('Invalid output reservation')
        if kind=='planner':amount.update(planner_calls=1,input_characters=characters,output_tokens=output_tokens)
        else:amount['cloud_calls']=1
        prior=db.execute('SELECT reserved,kind FROM adaptive_usage WHERE environment=? AND session_id=? AND reservation_key=?',
                         (self.environment,session_id,key)).fetchone()
        if prior:
            if json.loads(prior['reserved'])!=amount or prior['kind']!=kind:raise UsageHold('Reservation key differs')
            return
        if kind=='planner':
            active=db.execute("SELECT count(*) FROM adaptive_usage WHERE environment=? AND kind='planner' AND status='RESERVED'",(self.environment,)).fetchone()[0]
            if active>=self.policy['max_inflight_planners']:raise UsageHold('Planner concurrency limit')
        total=dict.fromkeys(KEYS,0)
        for row in db.execute('SELECT reserved FROM adaptive_usage WHERE environment=? AND day=?',(self.environment,self.day())):
            for k,v in json.loads(row[0]).items():total[k]+=v
        if any(total[k]+amount[k]>self.policy['daily_limits'][k] for k in KEYS):raise UsageHold('Daily usage limit')
        if db.execute("SELECT 1 FROM adaptive_usage WHERE environment=? AND day=? AND status='VIOLATION' LIMIT 1",(self.environment,self.day())).fetchone():
            raise UsageHold('Provider usage exceeded reservation')
        db.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,NULL,?,?,?)',
                   (self.environment,session_id,key,self.day(),kind,encoded(amount),'RESERVED',self.hash,self.clock()))

    def settle(self,db,session_id,key,usage=None,uncertain=False):
        row=db.execute('SELECT status,reserved FROM adaptive_usage WHERE environment=? AND session_id=? AND reservation_key=?',
                       (self.environment,session_id,key)).fetchone()
        if row is None:raise UsageHold('Missing usage reservation')
        if row['status']!='RESERVED':return
        actual={k:v for k,v in (usage if isinstance(usage,dict) else {}).items() if k in ('input_tokens','output_tokens','total_tokens') and type(v) is int and v>=0}
        status='UNCERTAIN' if uncertain else 'SETTLED'
        if actual.get('output_tokens',0)>json.loads(row['reserved'])['output_tokens'] and json.loads(row['reserved'])['planner_calls']:
            status='VIOLATION'
        db.execute('UPDATE adaptive_usage SET actual=?,status=? WHERE environment=? AND session_id=? AND reservation_key=?',
                   (encoded(actual),status,self.environment,session_id,key))
        # Conservative reservations are never refunded. Missing usage remains explicit.

    def snapshot(self):
        with self.runtime.db() as db:
            rows=db.execute('SELECT day,kind,reserved,actual,status FROM adaptive_usage WHERE environment=? ORDER BY created',
                            (self.environment,)).fetchall()
        total=dict.fromkeys(KEYS,0);states={}
        for r in rows:
            if r['day']==self.day():
                for k,v in json.loads(r['reserved']).items():total[k]+=v
            states[r['status']]=states.get(r['status'],0)+1
        return {'environment':self.environment,'day':self.day(),'policy_hash':self.hash,
                'limits':self.policy['daily_limits'],'reserved_today':total,'reservation_states':states,
                'billing_cap_verified':False,'limitation':'Initiated UTC-day reservations in this catalog only; no provider spend or SQL compute guarantee.'}

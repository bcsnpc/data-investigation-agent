"""Durable planner-day and rolling read reservations shared by adaptive sessions in one catalog/estate."""
from datetime import datetime,timezone
import json
from .onboarding import fields,digest,encoded,Conflict
from .generation_policy import MAX_OUTPUT_TOKENS
from . import read_allowance
from .tape_budget import decision

KEYS=('planner_calls','cloud_calls','input_characters','output_tokens')


def charged(row):
    """Keep immutable reservations; release unused output only with usage evidence."""
    amount=json.loads(row['reserved'])
    from .process_tape import ACTIVE
    tape=ACTIVE.get()
    if tape is not None and tape.replaying and getattr(tape,'accounting_version',1)<3:
        return amount
    actual=json.loads(row['actual']) if row['actual'] else {}
    if row['status']!='RESERVED' and type(actual.get('output_tokens')) is int:
        amount['output_tokens']=actual['output_tokens']
    return amount


class UsageHold(Conflict):pass


class UsageGovernor:
    def __init__(self,runtime,policy,clock):
        fields(policy,['environment','daily_limits','max_inflight_planners','no_progress_limit'])
        if not isinstance(policy['environment'],str) or policy['environment']!=runtime.store.environment:
            raise ValueError('Policy must match configured environment')
        fields(policy['daily_limits'],KEYS)
        from .usage_limits import DAILY_MAXIMUM
        for key,value in policy['daily_limits'].items():
            if type(value) is not int or not 1<=value<=DAILY_MAXIMUM[key]:raise ValueError('Invalid daily limit')
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

            read_allowance.initialize(db)
            db.execute('''CREATE TABLE IF NOT EXISTS usage_violation_acknowledgments(
                environment TEXT, session_id TEXT, reservation_key TEXT,
                violation_hash TEXT, approval TEXT, created REAL,
                PRIMARY KEY(environment,session_id,reservation_key))''')

    def acknowledge_violation(self, session_id, key, approval):
        """Operator-only, explicit owner decision; charges and violation stay intact."""
        fields(approval,['owner','approved_at','reason','corrected_output_tokens'])
        if any(not isinstance(approval[k],str) or not approval[k].strip()
               for k in ('owner','approved_at','reason')):
            raise ValueError('Dated owner approval required')
        if type(approval['corrected_output_tokens']) is not int or not 500<=approval['corrected_output_tokens']<=MAX_OUTPUT_TOKENS:
            raise ValueError('Invalid corrected output bound')
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT * FROM adaptive_usage WHERE environment=? AND session_id=? AND reservation_key=?',
                           (self.environment,session_id,key)).fetchone()
            if row is None or row['status']!='VIOLATION':raise UsageHold('Named violation required')
            if approval['corrected_output_tokens']<json.loads(row['actual']).get('output_tokens',0):
                raise ValueError('Corrected bound does not cover retained usage')
            record={'violation_hash':digest(dict(row)),'approval':approval}
            prior=db.execute('SELECT violation_hash,approval FROM usage_violation_acknowledgments WHERE environment=? AND session_id=? AND reservation_key=?',
                             (self.environment,session_id,key)).fetchone()
            if prior:
                if prior['violation_hash']!=record['violation_hash'] or json.loads(prior['approval'])!=approval:
                    raise UsageHold('Acknowledgment is immutable')
                return record
            db.execute('INSERT INTO usage_violation_acknowledgments VALUES(?,?,?,?,?,?)',
                       (self.environment,session_id,key,record['violation_hash'],encoded(approval),self.clock()))
            return record

    def grant_batch(self, approval):
        with self.runtime.db() as db:
            db.execute("BEGIN IMMEDIATE")
            read_allowance.grant(db,self.environment,approval,self.clock())

    def restoration_read(self,session_id,key,execute):
        return self.metered_read(session_id,key,execute,purpose='RESTORATION')

    def metered_read(self,session_id,key,execute,*,purpose='INVESTIGATION'):
        """Operator read/verification; restoration requires preassigned earmarked credits.

        execute is a trusted single-read transport, not model-supplied code.
        This does not authorize mutation. Failed or uncertain work stays charged.
        """
        def metered(slot,call):
            with self.runtime.db() as db:
                db.execute('BEGIN IMMEDIATE')
                if db.execute('SELECT 1 FROM adaptive_usage WHERE environment=? AND session_id=? AND reservation_key=?',
                              (self.environment,session_id,slot)).fetchone():
                    raise UsageHold('Operator request already admitted; never replay')
                self.reserve(db,session_id,slot,'cloud',purpose=purpose)
            uncertain=True
            try:
                result=call();uncertain=False;return result
            finally:
                with self.runtime.db() as db:
                    db.execute('BEGIN IMMEDIATE');self.settle(db,session_id,slot,uncertain=uncertain)
        number=0
        def extra(tool,call):
            nonlocal number
            number+=1
            return metered(key+':physical:'+str(number),call)
        from .physical_reads import scope
        with scope(extra):return metered(key,execute)

    def day(self):return datetime.fromtimestamp(self.clock(),timezone.utc).date().isoformat()

    @decision
    def reserve(self,db,session_id,key,kind,characters=0,*,output_tokens=1500,purpose="INVESTIGATION"):
        # Caller holds BEGIN IMMEDIATE; budget and session transition commit together.
        if kind not in ('planner','cloud'):raise ValueError('Unknown usage kind')
        if kind=='planner' and purpose!='INVESTIGATION':raise ValueError('Restoration credits are read-only')
        amount=dict.fromkeys(KEYS,0)
        if type(output_tokens) is not int or not 500<=output_tokens<=MAX_OUTPUT_TOKENS:raise ValueError('Invalid output reservation')
        if kind=='planner':amount.update(planner_calls=1,input_characters=characters,output_tokens=output_tokens)
        else:amount['cloud_calls']=1
        prior=db.execute('SELECT reserved,kind FROM adaptive_usage WHERE environment=? AND session_id=? AND reservation_key=?',
                         (self.environment,session_id,key)).fetchone()
        if prior:
            if kind=='cloud':
                allocation=db.execute('SELECT purpose FROM read_allocations WHERE environment=? AND session_id=? AND reservation_key=?', (self.environment,session_id,key)).fetchone()
                if allocation and allocation['purpose']!=purpose:raise UsageHold('Reservation purpose differs')
            if json.loads(prior['reserved'])!=amount or prior['kind']!=kind:raise UsageHold('Reservation key differs')
            return
        if kind=='planner':
            active=db.execute("SELECT count(*) FROM adaptive_usage WHERE environment=? AND kind='planner' AND status='RESERVED'",(self.environment,)).fetchone()[0]
            if active>=self.policy['max_inflight_planners']:raise UsageHold('Planner concurrency limit')
        total=dict.fromkeys(KEYS,0)
        for row in db.execute('SELECT reserved,actual,status FROM adaptive_usage WHERE environment=? AND day=?',(self.environment,self.day())):
            for k,v in charged(row).items():total[k]+=v
        if any(amount[k] and total[k]+amount[k]>self.policy['daily_limits'][k] for k in KEYS if k!='cloud_calls'):raise UsageHold('Daily usage limit')
        violations=db.execute("SELECT * FROM adaptive_usage WHERE environment=? AND day=? AND status='VIOLATION'",(self.environment,self.day())).fetchall()
        if purpose!='RESTORATION' and any(not db.execute('''SELECT 1 FROM usage_violation_acknowledgments
                WHERE environment=? AND session_id=? AND reservation_key=? AND violation_hash=?''',
                (self.environment,r['session_id'],r['reservation_key'],digest(dict(r)))).fetchone() for r in violations):
            raise UsageHold('Provider usage exceeded reservation')
        if kind=='cloud':
            round_policy=self.runtime.config.get('_estate',{}).get('round')
            if round_policy:
                used=db.execute("SELECT count(*) FROM adaptive_usage WHERE environment=? AND kind='cloud' AND created>=?",
                    (self.environment,round_policy['starts_at_epoch'])).fetchone()[0]
                restored=db.execute('''SELECT count(*) FROM adaptive_usage u JOIN read_allocations a
                    ON a.environment=u.environment AND a.session_id=u.session_id AND a.reservation_key=u.reservation_key
                    WHERE u.environment=? AND u.kind='cloud' AND u.created>=? AND a.purpose='RESTORATION' ''',
                    (self.environment,round_policy['starts_at_epoch'])).fetchone()[0]
                reserve=0 if purpose=='RESTORATION' else max(0,round_policy['restoration_reserved']-restored)
                if used+1+reserve>round_policy['physical_requests']:
                    raise UsageHold('Estate manifest round physical allowance exhausted; restoration capacity reserved')
            read_allowance.allocate(db,self.environment,session_id,key,self.clock(),
                self.policy['daily_limits']['cloud_calls'],purpose,UsageHold)
        db.execute('INSERT INTO adaptive_usage VALUES(?,?,?,?,?,?,NULL,?,?,?)',
                   (self.environment,session_id,key,self.day(),kind,encoded(amount),'RESERVED',self.hash,self.clock()))

    @decision
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
        # The original reservation stays immutable. Admission charges known
        # actual output after settlement; missing usage retains the full bound.

    def snapshot(self):
        with self.runtime.db() as db:
            reads=read_allowance.snapshot(db,self.environment,self.clock(),self.policy['daily_limits']['cloud_calls'])
            rows=db.execute('SELECT day,kind,reserved,actual,status FROM adaptive_usage WHERE environment=? ORDER BY created',
                            (self.environment,)).fetchall()
        total=dict.fromkeys(KEYS,0);used=dict.fromkeys(KEYS,0);active=dict.fromkeys(KEYS,0);states={}
        unknown_output=0
        for r in rows:
            if r['day']==self.day():
                for k,v in json.loads(r['reserved']).items():total[k]+=v
                for k,v in charged(r).items():used[k]+=v
                if r['status']=='RESERVED':
                    for k,v in json.loads(r['reserved']).items():active[k]+=v
                elif r['kind']=='planner' and 'output_tokens' not in json.loads(r['actual'] or '{}'):
                    unknown_output+=json.loads(r['reserved'])['output_tokens']
            states[r['status']]=states.get(r['status'],0)+1
        return {'environment':self.environment,'day':self.day(),'policy_hash':self.hash,
                'limits':self.policy['daily_limits'],'reserved_today':total,'charged_today':used,
                'active_reservations':active,'unknown_output_charged':unknown_output,'reservation_states':states,
                'read_allowance':reads,'billing_cap_verified':False,
                'limitation':'Planner reservations use UTC days; ordinary reads use rolling 24 hours, with separate expiring run credits. Initiated requests in this catalog only, not provider spend or SQL compute.'}

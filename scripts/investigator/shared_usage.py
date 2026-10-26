"""Transactional PostgreSQL authority for existing usage-governor decisions.

The local connection is only a per-job replay mirror. A shared reservation is
committed before local state; interruption can strand a reservation (charged),
never issue uncharged work. A worker cannot settle another worker's reservation.
"""
from datetime import datetime,timezone
import json
import math
import os
from .onboarding import fields,text,digest,encoded
from .generation_policy import MAX_OUTPUT_TOKENS
from .shared_state import StateConflict,sha
from .read_allowance import WINDOW_SECONDS

KEYS=('planner_calls','cloud_calls','input_characters','output_tokens')
TABLES={
    'adaptive_usage':('state_usage',('environment','session_id','reservation_key','day','kind','reserved','actual','status','policy_hash','created')),
    'read_batches':('state_read_batches',('environment','batch_id','approval','issued','expires')),
    'read_batch_runs':('state_read_batch_runs',('environment','session_id','batch_id','purpose','allowance')),
    'read_allocations':('state_read_allocations',('environment','session_id','reservation_key','batch_id','purpose')),
    'usage_violation_acknowledgments':('state_usage_acknowledgments',('environment','session_id','reservation_key','violation_hash','approval','created')),
}


def rows(state,db,sql,args=()):
    cursor=state.sql(db,sql,args)
    columns=[d[0] for d in cursor.description]
    return [dict(zip(columns,row)) for row in cursor.fetchall()]


def charged(row):
    value=json.loads(row['reserved'])
    actual=json.loads(row['actual']) if row['actual'] else {}
    if row['status']!='RESERVED' and type(actual.get('output_tokens')) is int:
        value['output_tokens']=actual['output_tokens']
    return value


def export_usage(connection,environment,policy,round_policy):
    """Read inside an operator-owned snapshot transaction; does not alter source.

    Columns are named explicitly. SQLite REAL timestamps stay REAL (IEEE754
    binary64), while all reservation counts remain exact integers in JSON.
    """
    tables={}
    for table,(_,columns) in TABLES.items():
        cursor=connection.execute('SELECT '+','.join(columns)+' FROM '+table+' WHERE environment=?',(environment,))
        tables[table]={'columns':list(columns),'rows':sorted([list(row) for row in cursor],key=encoded)}
    return {'version':'shared-usage-import-v1','environment':environment,'policy':policy,
            'round_policy':round_policy,'tables':tables}


def orphan_approval(source,approval):
    """Explicitly preserve, never settle, named historical reservations."""
    pending=[{'session_id':r[1],'reservation_key':r[2]} for r in source['tables']['adaptive_usage']['rows'] if r[7]=='RESERVED']
    if approval is None:
        if pending:raise StateConflict('USAGE_IMPORT_REQUIRES_DRAINED_WORKERS')
        return None
    fields(approval,['source_sha256','approved_by','approved_at','reason','drained_workers','reservations'])
    if approval['source_sha256']!=sha(source):raise StateConflict('ORPHAN_APPROVAL_SOURCE_HASH_DIFFERS')
    if approval['drained_workers']is not True:raise StateConflict('ORPHAN_APPROVAL_REQUIRES_DRAINED_WORKERS')
    for key in ('approved_by','approved_at','reason'):text(approval[key],2000)
    if not pending or sorted(approval['reservations'],key=encoded)!=sorted(pending,key=encoded):
        raise StateConflict('ORPHAN_APPROVAL_RESERVATIONS_DIFFER')
    return approval


def import_usage(state,identity,source,*,preserve_orphans=None):
    if set(source)!={'version','environment','policy','round_policy','tables'} or source['version']!='shared-usage-import-v1':
        raise ValueError('USAGE_IMPORT_SCHEMA_DIFFERS')
    environment=source['environment']
    if source['policy']['environment']!=environment or set(source['tables'])!=set(TABLES):
        raise ValueError('USAGE_IMPORT_SCOPE_DIFFERS')
    approval=orphan_approval(source,preserve_orphans)
    fingerprint=sha(source)
    with state.transaction() as db:
        prior=state.sql(db,'SELECT source_hash,verification FROM state_migrations WHERE identity=?',(identity,)).fetchone()
        if prior:
            if prior[0]!=fingerprint:raise StateConflict('MIGRATION_SOURCE_CHANGED')
            prior_proof=json.loads(prior[1])
            if prior_proof.get('preserved_orphan_approval')!=approval:raise StateConflict('MIGRATION_ORPHAN_APPROVAL_CHANGED')
            return prior_proof
        proof=[]
        for original,(target,columns) in TABLES.items():
            saved=source['tables'][original]
            if saved['columns']!=list(columns):raise ValueError('USAGE_IMPORT_COLUMNS_DIFFER')
            if state.sql(db,'SELECT 1 FROM '+target+' WHERE environment=?',(environment,)).fetchone():
                raise StateConflict('USAGE_TARGET_NOT_EMPTY')
            for row in saved['rows']:
                if len(row)!=len(columns) or row[0]!=environment:raise ValueError('USAGE_IMPORT_ROW_SCOPE_DIFFERS')
                if original=='adaptive_usage':
                    reservation=json.loads(row[5])
                    if set(reservation)!=set(KEYS) or any(type(v)is not int or v<0 for v in reservation.values()):
                        raise ValueError('USAGE_IMPORT_COUNTS_INVALID')
                insert_columns=columns+('owner',) if original=='adaptive_usage' else columns
                values=list(row)+['MIGRATED_ORPHAN' if row[7]=='RESERVED' else 'MIGRATED'] if original=='adaptive_usage' else row
                state.sql(db,'INSERT INTO '+target+'('+','.join(insert_columns)+') VALUES('+','.join('?' for _ in values)+')',values)
            actual=state.sql(db,'SELECT '+','.join(columns)+' FROM '+target+' WHERE environment=?',(environment,)).fetchall()
            actual=sorted([list(row) for row in actual],key=encoded)
            expected=sorted(saved['rows'],key=encoded)
            if actual!=expected:raise StateConflict('USAGE_MIGRATION_ROWS_DIFFER')
            proof.append({'table':original,'rows_before':len(expected),'rows_after':len(actual),
                          'sha256_before':sha(expected),'sha256_after':sha(actual),'matched':True})
        policy={'policy':source['policy'],'round_policy':source['round_policy']}
        state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',('usage_policy',environment,0,encoded(policy),sha(policy)))
        before=usage_totals(source)
        copied={'version':source['version'],'environment':environment,'policy':source['policy'],'round_policy':source['round_policy'],'tables':{}}
        for original,(target,columns) in TABLES.items():
            copied['tables'][original]={'columns':list(columns),'rows':[list(r) for r in state.sql(db,'SELECT '+','.join(columns)+' FROM '+target+' WHERE environment=?',(environment,)).fetchall()]}
        after=usage_totals(copied)
        if before!=after:raise StateConflict('USAGE_MIGRATION_TOTALS_DIFFER')
        verification={'source_sha256':fingerprint,'tables':proof,'policy':policy,'totals_before':before,'totals_after':after}
        if approval is not None:verification['preserved_orphan_approval']=approval
        state.sql(db,'INSERT INTO state_migrations VALUES(?,?,?)',(identity,fingerprint,encoded(verification)))
        return verification


def usage_totals(source):
    usage=[dict(zip(source['tables']['adaptive_usage']['columns'],r)) for r in source['tables']['adaptive_usage']['rows']]
    allocations=[dict(zip(source['tables']['read_allocations']['columns'],r)) for r in source['tables']['read_allocations']['rows']]
    by_key={(r['session_id'],r['reservation_key']):r for r in allocations}
    totals=dict.fromkeys(KEYS,0)
    for row in usage:
        for key,value in charged(row).items():totals[key]+=value
    result={'all_time_charged':totals,'row_count':len(usage),'round':None}
    policy=source['round_policy']
    if policy:
        reads=[r for r in usage if r['kind']=='cloud' and r['created']>=policy['starts_at_epoch']]
        restored=sum(by_key.get((r['session_id'],r['reservation_key']),{}).get('purpose')=='RESTORATION' for r in reads)
        result['round']={'physical_charged':len(reads),'ceiling':policy['physical_requests'],
                         'restoration_charged':restored,'restoration_remaining':max(0,policy['restoration_reserved']-restored)}
    return result


class SharedUsage:
    def __init__(self,governor,state,*,owner=None):
        self.governor=governor;self.state=state
        self.environment=governor.environment
        self.owner=owner or os.environ.get('INVESTIGATOR_WORKER_ID')
        if not self.owner:raise ValueError('SHARED_USAGE_WORKER_ID_REQUIRED')
        expected={'policy':governor.policy,'round_policy':governor.runtime.config.get('_estate',{}).get('round')}
        retained=state.get('usage_policy',self.environment)['body']
        from .build_phase import active
        # The retained round pin is history in build mode; the accounting
        # environment and imported policy still identify the same shared ledger.
        differs = retained.get('policy') != expected['policy'] if active(governor.runtime.config) else retained != expected
        if differs:
            raise StateConflict('SHARED_USAGE_POLICY_DIFFERS_FROM_APPROVED_IMPORT')
        self.policy_hash=sha(expected)

    def _check_policy(self):
        current={'policy':self.governor.policy,'round_policy':self.governor.runtime.config.get('_estate',{}).get('round')}
        if sha(current)!=self.policy_hash:
            raise StateConflict('SHARED_USAGE_POLICY_CHANGED_DURING_RUN')

    def _rows(self,db,table):
        return rows(self.state,db,'SELECT * FROM '+table+' WHERE environment=?',(self.environment,))

    def _day(self,now):
        return datetime.fromtimestamp(now,timezone.utc).date().isoformat()

    def mirror(self,local):
        """Refresh the job's read-only accounting view before tape checkpointing.

        The per-job catalog cannot be an attached live SQLite accounting file.
        Mirroring changes no source row or shared account; budget mutations are
        journalled normally so offline replay receives the same admission inputs.
        """
        if getattr(self,'reporting_mirror',True)is False:return
        if getattr(local,'shared_accounting',None):
            raise StateConflict('POSTGRES_MIRROR_MUST_BE_PRIVATE')
        retained=self.state._read_transaction(lambda db:{
            original:self.state.sql(db,'SELECT '+','.join(columns)+' FROM '+target+' WHERE environment=?',(self.environment,)).fetchall()
            for original,(target,columns) in TABLES.items()})
        for original,(_,columns) in TABLES.items():
            desired={tuple(row[:3] if 'reservation_key' in columns else row[:2]):tuple(row) for row in retained[original]}
            existing={tuple(row[:3] if 'reservation_key' in columns else row[:2]):tuple(row) for row in local.execute('SELECT '+','.join(columns)+' FROM '+original+' WHERE environment=?',(self.environment,))}
            # Append-only historical rows must never disappear or change identity.
            if set(existing)-set(desired):raise StateConflict('LOCAL_ACCOUNTING_MIRROR_HAS_UNOWNED_ROWS')
            for key,row in desired.items():
                prior=existing.get(key)
                if prior is None:
                    local.execute('INSERT INTO '+original+'('+','.join(columns)+') VALUES('+','.join('?' for _ in row)+')',row)
                elif prior!=row:
                    if original!='adaptive_usage' or any(prior[i]!=row[i] for i in range(len(row)) if columns[i] not in ('actual','status')):
                        raise StateConflict('LOCAL_ACCOUNTING_MIRROR_IMMUTABLE_ROW_DIFFERS')
                    local.execute('UPDATE adaptive_usage SET actual=?,status=? WHERE environment=? AND session_id=? AND reservation_key=?',(row[6],row[7],*key))

    def reserve(self,local,session,key,kind,characters=0,*,output_tokens=1500,purpose='INVESTIGATION'):
        from .usage_governance import UsageHold
        g=self.governor
        self._check_policy()
        if kind not in ('planner','cloud'):raise ValueError('Unknown usage kind')
        if kind=='planner' and purpose!='INVESTIGATION':raise ValueError('Restoration credits are read-only')
        if type(characters)is not int or characters<0:raise ValueError('Invalid input reservation')
        if type(output_tokens)is not int or not 500<=output_tokens<=MAX_OUTPUT_TOKENS:raise ValueError('Invalid output reservation')
        from . import build_phase
        monthly=build_phase.active(g.runtime.config)
        if purpose not in (build_phase.PURPOSES if monthly else ('INVESTIGATION','RESTORATION')):raise ValueError('Invalid read purpose')
        amount=dict.fromkeys(KEYS,0)
        if kind=='planner':amount.update(planner_calls=1,input_characters=characters,output_tokens=output_tokens)
        else:amount['cloud_calls']=1
        if monthly:
            category=build_phase.purpose(purpose) if purpose=='INVESTIGATION' else purpose
            return build_phase.shared_reserve(self,local,session,key,kind,amount,category)
        now=g.clock();today=self._day(now)
        with self.state.transaction() as db:
            usage=self._rows(db,'state_usage');allocations=self._rows(db,'state_read_allocations')
            alloc={(r['session_id'],r['reservation_key']):r for r in allocations}
            prior=next((r for r in usage if r['session_id']==session and r['reservation_key']==key),None)
            if prior:
                allocation=alloc.get((session,key))
                if (prior['owner']!=self.owner or prior['kind']!=kind or json.loads(prior['reserved'])!=amount
                        or allocation and allocation['purpose']!=purpose):
                    raise UsageHold('Shared reservation owner or request differs')
                return
            if kind=='planner' and sum(r['kind']=='planner' and r['status']=='RESERVED' for r in usage)>=g.policy['max_inflight_planners']:
                raise UsageHold('Planner concurrency limit')
            totals=dict.fromkeys(KEYS,0)
            for row in usage:
                if row['day']==today:
                    for k,v in charged(row).items():totals[k]+=v
            if any(amount[k] and totals[k]+amount[k]>g.policy['daily_limits'][k] for k in KEYS if k!='cloud_calls'):
                raise UsageHold('Daily usage limit')
            acknowledgments=self._rows(db,'state_usage_acknowledgments')
            for row in usage:
                original={k:row[k] for k in TABLES['adaptive_usage'][1]}
                if row['day']==today and row['status']=='VIOLATION' and purpose!='RESTORATION' and not any(
                    a['session_id']==row['session_id'] and a['reservation_key']==row['reservation_key'] and a['violation_hash']==digest(original)
                    for a in acknowledgments):raise UsageHold('Provider usage exceeded reservation')
            if kind=='cloud':
                round_policy=g.runtime.config.get('_estate',{}).get('round')
                if round_policy:
                    recent=[r for r in usage if r['kind']=='cloud' and r['created']>=round_policy['starts_at_epoch']]
                    restored=sum(alloc.get((r['session_id'],r['reservation_key']),{}).get('purpose')=='RESTORATION' for r in recent)
                    protected=0 if purpose=='RESTORATION' else max(0,round_policy['restoration_reserved']-restored)
                    if len(recent)+1+protected>round_policy['physical_requests']:
                        raise UsageHold('Estate manifest round physical allowance exhausted; restoration capacity reserved')
                batch_runs=self._rows(db,'state_read_batch_runs');batches=self._rows(db,'state_read_batches')
                run=next((r for r in batch_runs if r['session_id']==session),None)
                if run:
                    batch=next(b for b in batches if b['batch_id']==run['batch_id'])
                    if run['purpose']!=purpose:raise UsageHold('Batch run purpose differs')
                    if now>=batch['expires']:raise UsageHold('Batch credits expired')
                    if sum(r['session_id']==session for r in allocations)>=run['allowance']:raise UsageHold('Batch per-run read allowance exhausted')
                    batch_id=run['batch_id']
                else:
                    if purpose=='RESTORATION':raise UsageHold('Restoration needs earmarked batch credits')
                    ordinary=sum(json.loads(r['reserved'])['cloud_calls'] for r in usage if r['kind']=='cloud' and r['created']>now-WINDOW_SECONDS
                                 and alloc.get((r['session_id'],r['reservation_key']),{}).get('batch_id') is None)
                    if ordinary>=g.policy['daily_limits']['cloud_calls']:raise UsageHold('Rolling 24-hour read allowance exhausted')
                    batch_id=None
                self.state.sql(db,'INSERT INTO state_read_allocations VALUES(?,?,?,?,?)',(self.environment,session,key,batch_id,purpose))
            self.state.sql(db,'INSERT INTO state_usage VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                           (self.environment,session,key,today,kind,encoded(amount),None,'RESERVED',g.hash,now,self.owner))
        self.mirror(local)

    def settle(self,local,session,key,usage=None,uncertain=False):
        from .usage_governance import UsageHold
        with self.state.transaction() as db:
            found=rows(self.state,db,'SELECT * FROM state_usage WHERE environment=? AND session_id=? AND reservation_key=?',(self.environment,session,key))
            if not found:raise UsageHold('Missing usage reservation')
            row=found[0]
            if row['owner']=='MIGRATED_ORPHAN':raise UsageHold('Historical orphan reservation is immutable and conservatively charged')
            if row['owner']!=self.owner:raise UsageHold('Shared reservation owner differs')
            if row['status']=='RESERVED':
                actual={k:v for k,v in (usage if isinstance(usage,dict) else {}).items() if k in ('input_tokens','output_tokens','total_tokens') and type(v)is int and v>=0}
                status='UNCERTAIN' if uncertain else 'SETTLED'
                reserved=json.loads(row['reserved'])
                if actual.get('output_tokens',0)>reserved['output_tokens'] and reserved['planner_calls']:status='VIOLATION'
                self.state.sql(db,'UPDATE state_usage SET actual=?,status=? WHERE environment=? AND session_id=? AND reservation_key=?',
                               (encoded(actual),status,self.environment,session,key))
        self.mirror(local)

    def grant_batch(self,approval):
        fields(approval,['batch_id','environment','approved_by','approval_reference','expires_at','runs'])
        now=self.governor.clock();expiry=approval['expires_at']
        if approval['environment']!=self.environment:raise ValueError('Batch environment differs')
        for key in ('batch_id','approved_by','approval_reference'):text(approval[key],500)
        if type(expiry)not in (float,int) or not math.isfinite(expiry) or expiry<=now:raise ValueError('Batch must have a future finite expiry')
        entries=approval['runs']
        if not isinstance(entries,list) or not 1<=len(entries)<=100:raise ValueError('Invalid batch runs')
        seen=set()
        with self.state.transaction() as db:
            for run in entries:
                fields(run,['session_id','purpose','reads']);text(run['session_id'],200)
                if run['session_id']in seen:raise ValueError('Duplicate batch run')
                seen.add(run['session_id'])
                if run['purpose']not in ('INVESTIGATION','RESTORATION'):raise ValueError('Invalid read purpose')
                if type(run['reads'])is not int or not 1<=run['reads']<=10000:raise ValueError('Invalid run credits')
                if self.state.sql(db,'SELECT 1 FROM state_usage WHERE environment=? AND session_id=?',(self.environment,run['session_id'])).fetchone():
                    raise ValueError('Credits must be assigned before the run starts')
            if self.state.sql(db,'SELECT 1 FROM state_read_batches WHERE environment=? AND batch_id=?',(self.environment,approval['batch_id'])).fetchone():
                raise ValueError('Batch approval is immutable; already recorded')
            self.state.sql(db,'INSERT INTO state_read_batches VALUES(?,?,?,?,?)',(self.environment,approval['batch_id'],encoded(approval),now,expiry))
            for run in entries:
                self.state.sql(db,'INSERT INTO state_read_batch_runs VALUES(?,?,?,?,?)',(self.environment,run['session_id'],approval['batch_id'],run['purpose'],run['reads']))

    def acknowledge_violation(self,session,key,approval):
        fields(approval,['owner','approved_at','reason','corrected_output_tokens'])
        if any(not isinstance(approval[k],str) or not approval[k].strip() for k in ('owner','approved_at','reason')):
            raise ValueError('Dated owner approval required')
        if type(approval['corrected_output_tokens'])is not int or not 500<=approval['corrected_output_tokens']<=MAX_OUTPUT_TOKENS:
            raise ValueError('Invalid corrected output bound')
        with self.state.transaction() as db:
            found=rows(self.state,db,'SELECT * FROM state_usage WHERE environment=? AND session_id=? AND reservation_key=?',(self.environment,session,key))
            if not found or found[0]['status']!='VIOLATION':raise StateConflict('Named violation required')
            row=found[0]
            if approval['corrected_output_tokens']<json.loads(row['actual']).get('output_tokens',0):raise ValueError('Corrected bound does not cover retained usage')
            original={k:row[k] for k in TABLES['adaptive_usage'][1]}
            record={'violation_hash':digest(original),'approval':approval}
            prior=self.state.sql(db,'SELECT violation_hash,approval FROM state_usage_acknowledgments WHERE environment=? AND session_id=? AND reservation_key=?',(self.environment,session,key)).fetchone()
            if prior:
                if prior[0]!=record['violation_hash'] or json.loads(prior[1])!=approval:raise StateConflict('Acknowledgment is immutable')
                return record
            self.state.sql(db,'INSERT INTO state_usage_acknowledgments VALUES(?,?,?,?,?,?)',(self.environment,session,key,record['violation_hash'],encoded(approval),self.governor.clock()))
            return record

    def snapshot(self):
        """Read PG once, then use the existing presentation over a private mirror.

        No live admission consults the mirror. This retains the report contract
        and tape counters while avoiding an independent reporting algorithm.
        """
        import sqlite3
        from .read_allowance import snapshot as read_snapshot,initialize
        g=self.governor;now=g.clock();today=self._day(now)
        from .process_tape import ACTIVE
        tape=ACTIVE.get()
        if tape is not None and tape.bootstrap.get('state',{}).get('shared_usage_replay',{}).get('version')=='OWNED_SHARED_USAGE_V1':
            # Snapshot inputs can change before the first reservation. Capture
            # them with the same lossless external-delta contract as admission.
            from .budget_checkpoint import checkpoint
            with g.runtime.db() as local:
                self.mirror(local)
                checkpoint(tape,local,self.environment,getattr(tape,'budget_owned_sessions',set()))
                retained={original:local.execute('SELECT '+','.join(columns)+' FROM '+original+' WHERE environment=?',(self.environment,)).fetchall()
                          for original,(_,columns) in TABLES.items()}
        else:
            retained=self.state._read_transaction(lambda db:{
                original:self.state.sql(db,'SELECT '+','.join(columns)+' FROM '+target+' WHERE environment=?',(self.environment,)).fetchall()
                for original,(target,columns) in TABLES.items()})
        db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
        try:
            db.execute('CREATE TABLE adaptive_usage(environment,session_id,reservation_key,day,kind,reserved,actual,status,policy_hash,created)')
            initialize(db)
            for original,(_,columns) in TABLES.items():
                if original=='usage_violation_acknowledgments':continue
                db.executemany('INSERT INTO '+original+' VALUES('+','.join('?' for _ in columns)+')',retained[original])
            reads=read_snapshot(db,self.environment,now,g.policy['daily_limits']['cloud_calls'])
        finally:db.close()
        total=dict.fromkeys(KEYS,0);used=dict.fromkeys(KEYS,0);active=dict.fromkeys(KEYS,0);states={};unknown=0
        for values in retained['adaptive_usage']:
            row=dict(zip(TABLES['adaptive_usage'][1],values))
            if row['day']==today:
                for k,v in json.loads(row['reserved']).items():total[k]+=v
                for k,v in charged(row).items():used[k]+=v
                if row['status']=='RESERVED':
                    for k,v in json.loads(row['reserved']).items():active[k]+=v
                elif row['kind']=='planner' and 'output_tokens'not in json.loads(row['actual']or'{}'):unknown+=json.loads(row['reserved'])['output_tokens']
            states[row['status']]=states.get(row['status'],0)+1
        result = {'environment':self.environment,'day':today,'policy_hash':g.hash,'limits':g.policy['daily_limits'],
                'reserved_today':total,'charged_today':used,'active_reservations':active,'unknown_output_charged':unknown,
                'reservation_states':states,'read_allowance':reads,'billing_cap_verified':False,
                'limitation':'Planner reservations use UTC days; ordinary reads use rolling 24 hours, with separate expiring run credits. Initiated requests in this catalog only, not provider spend or SQL compute.'}
        from . import build_phase
        if build_phase.active(g.runtime.config):
            usage,allocations=self.state._read_transaction(lambda db:build_phase.shared_physical_rows(self.state,db,now))
            result['monthly']=build_phase.physical_status(usage,allocations,now)
            result['legacy_limits_informational']=True
            result['limitation']='Monthly UTC physical categories enforce admission; old daily, rolling and round counters are informational. Model dollars use their own monthly account.'
        return result

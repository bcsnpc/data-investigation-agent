"""Consumer-owned verdicts over ticket-local, immutable tool evidence.

Model prose and rankings never enter a support test. Missing evidence returns
not found; warnings never fabricate or suppress native evidence.
"""
import copy
from datetime import datetime,timedelta
from decimal import Decimal,InvalidOperation
from .estate_graph_contract import canonical,digest,timestamp

VERDICTS=('as designed','latency','waiting on job','failed job','refresh stale',
          'different question','access difference','source changed history','not found')


def quantity(value):
    state=value.get('state')
    if state=='BLANK' and value.get('value') is None:return ('BLANK',None)
    if state!='VALUE' or isinstance(value.get('value'),bool):raise ValueError('VALUE_OR_BLANK_REQUIRED')
    try:number=Decimal(str(value['value']))
    except (InvalidOperation,KeyError):raise ValueError('EXACT_VALUE_REQUIRED') from None
    if not number.is_finite():raise ValueError('EXACT_VALUE_REQUIRED')
    return ('VALUE',number)


class Evidence:
    def __init__(self,path,persist):self.path=frozenset(path);self._values={};self.persist=persist
    def add(self,kind,subjects,value):
        if not subjects or not set(subjects)<=self.path:raise ValueError('EVIDENCE_OUTSIDE_TICKET_PATH')
        record={'kind':kind,'subjects':sorted(set(subjects)),'value':copy.deepcopy(value)}
        from .planner_recording import _safe
        _safe(canonical(record).encode())
        identity='evidence:'+digest(record)
        if identity not in self._values:
            receipt=self.persist({'event':'INVESTIGATOR_EVIDENCE','id':identity,**record})
            if not isinstance(receipt,str) or not receipt:raise ValueError('EVIDENCE_PERSISTENCE_REQUIRED')
            self._values[identity]={**record,'receipt_id':receipt}
        return identity
    def get(self,identity):
        if identity not in self._values:raise ValueError('UNKNOWN_EVIDENCE_ID:'+str(identity))
        return copy.deepcopy(self._values[identity])
    def resolve(self,identities):
        if not isinstance(identities,list)or len(set(identities))!=len(identities):raise ValueError('EVIDENCE_ID_SET_REQUIRED')
        result={};pending=list(identities)
        while pending:
            identity=pending.pop()
            if identity in result:continue
            record=self.get(identity);result[identity]=record
            pending.extend(record['value'].get('support_ids',[]))
        return result


def check(verdict,ids,registry,*,now):
    if verdict not in VERDICTS:raise ValueError('UNKNOWN_VERDICT')
    records=registry.resolve(ids);entries=list(records.values());now=timestamp(now)
    if verdict=='not found':return {'verdict':verdict,'evidence_ids':list(records),'reason':'Evidence does not establish a cause within the admitted budget.'}
    reads={identity:r['value'] for identity,r in records.items() if r['kind']=='READ'}
    for read in reads.values():
        if read.get('route_admitted') is not True or read.get('read_only_verified') is not True or not read.get('receipt_id'):raise ValueError('READ_NOT_ADMITTED')
        quantity(read)
    comparisons=[r['value'] for r in entries if r['kind']=='COMPARISON']
    facts=[r['value'] for r in entries if r['kind']=='FACT' and r['value'].get('state') in ('OBSERVED','OBSERVED_NEGATIVE') and r['value'].get('freshness')=='CURRENT' and timestamp(r['value']['collected_at'])<=now and timestamp(r['value']['observed_at'])<=now]
    boundaries=[r['value'] for r in entries if r['kind']=='BOUNDARY']
    def pair(comparison):
        left=reads.get(comparison.get('left'));right=reads.get(comparison.get('right'))
        if left is None or right is None:raise ValueError('COMPARISON_READ_COVERAGE_MISSING')
        if left['key']!=right['key']:raise ValueError('COMPARISON_KEY_DIFFERS')
        return left,right
    divergent=[]
    for comparison in comparisons:
        left,right=pair(comparison)
        if canonical(left['context'])==canonical(right['context']) and quantity(left)!=quantity(right):divergent.append((left,right))
    def known(kind):return [f for f in facts if f['kind']==kind]
    def fact_time(value,field):
        raw=value['value'].get(field)
        return timestamp(raw) if raw else None
    if verdict in ('latency','waiting on job','failed job','refresh stale'):
        if not divergent:raise ValueError('FRESHNESS_REQUIRES_DIVERGENT_EQUIVALENT_CONTEXT_READS')
        for left,right in divergent:
            for boundary in boundaries:
                if (boundary.get('downstream'),boundary.get('upstream'))!=(left['subject'],right['subject']) or boundary.get('quantity_preserving') is not True:continue
                job=boundary.get('job');source=boundary.get('upstream');target=boundary.get('downstream')
                source_load=[f for f in known('TABLE_LOAD') if f['subject']==source and fact_time(f,'last_modified')]
                if not source_load:continue
                changed=fact_time(source_load[0],'last_modified')
                if changed>now:continue
                if verdict=='refresh stale':
                    refresh=[f for f in known('REFRESH_RUN') if f['subject']==job and f['value'].get('status')=='SUCCEEDED' and fact_time(f,'end')]
                    if boundary.get('kind')=='MODEL_REFRESH' and refresh and fact_time(refresh[0],'end')<changed:
                        return _supported(verdict,records,boundary,'The upstream load occurred after the last successful model refresh.')
                    continue
                runs=[f for f in known('JOB_RUN') if f['subject']==job]
                if verdict=='failed job':
                    failed=[f for f in runs if f['value'].get('status')=='FAILED' and f['value'].get('error') and fact_time(f,'start') and changed<=fact_time(f,'start')<=now and fact_time(f,'end') and fact_time(f,'end')<=now]
                    if failed:return _supported(verdict,records,boundary,'The linked quantity-preserving load failed after the source change: '+str(failed[0]['value']['error']))
                if verdict=='waiting on job':
                    queued=[f for f in runs if f['value'].get('status') in ('QUEUED','RUNNING') and fact_time(f,'start') and changed<=fact_time(f,'start')<=now]
                    overdue=[f for f in known('OVERDUE') if f['subject']==job and f['value'].get('overdue') is True and fact_time(f,'due_at') and changed<=fact_time(f,'due_at')<=now]
                    if queued or overdue:return _supported(verdict,records,boundary,'The linked load is queued/running or has not started by its declared due time.')
                if verdict=='latency':
                    completed=[f for f in runs if f['value'].get('status')=='SUCCEEDED' and fact_time(f,'end') and fact_time(f,'end')<changed]
                    schedules=[f for f in known('SCHEDULE') if f['subject']==job and fact_time(f,'next_due') and fact_time(f,'next_due')>=now]
                    durations=[f for f in known('TYPICAL_DURATION') if f['subject']==job and f['value'].get('sample_count',0)>0]
                    # A newer failed/running run prevents describing this as ordinary scheduled latency.
                    newer=[f for f in runs if fact_time(f,'start') and fact_time(f,'start')>=changed]
                    if completed and schedules and durations and not newer:
                        due=datetime.fromisoformat(fact_time(schedules[0],'next_due').replace('Z','+00:00'))
                        expected=due+timedelta(seconds=durations[0]['value']['median_seconds'])
                        return {**_supported(verdict,records,boundary,'The source changed after the completed load and the next declared load is not yet due.'),'expected_update_at':timestamp(expected.isoformat())}
        raise ValueError('FRESHNESS_CAUSAL_PATH_OR_CHRONOLOGY_MISSING')
    if verdict=='different question':
        for comparison in comparisons:
            a,b=pair(comparison)
            if (a.get('expression_hash') and a.get('expression_hash')==b.get('expression_hash') and a.get('execution_surface')==b.get('execution_surface') and canonical(a['context'])!=canonical(b['context']) and quantity(a)!=quantity(b)):
                return _supported(verdict,records,None,'The same expression on the same surface returns different values under the two explicitly declared contexts.')
        raise ValueError('CONTEXT_EFFECT_NOT_ESTABLISHED')
    witness_kind={'as designed':'DESIGN_CHECK','access difference':'ACCESS_CHECK','source changed history':'HISTORY_CHECK'}[verdict]
    witnesses=[r['value'] for r in entries if r['kind']==witness_kind]
    for witness in witnesses:
        if witness.get('checked') is not True or not witness.get('support_ids') or not witness.get('mechanism'):continue
        if not comparisons:continue
        if verdict=='as designed' and witness.get('business_correctness_claim') is not False:continue
        if verdict=='access difference' and (witness.get('impersonated') is not False or witness.get('same_query_and_context') is not True or witness.get('observed_access_difference') is not True):continue
        if verdict=='source changed history' and (witness.get('system_of_record') is not True or witness.get('row_history_verified') is not True):continue
        return _supported(verdict,records,None,witness['mechanism'])
    raise ValueError(witness_kind+'_CHECKED_WITNESS_REQUIRED')


def _supported(verdict,records,boundary,reason):
    return {'verdict':verdict,'evidence_ids':list(records),'boundary':copy.deepcopy(boundary),'reason':reason}

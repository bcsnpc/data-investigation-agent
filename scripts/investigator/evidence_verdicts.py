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
        if kind in ('READ','FACT') and set(subjects)!={value.get('subject')}:raise ValueError('EVIDENCE_SUBJECT_DIFFERS_FROM_RECORD')
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


def current_facts(entries,now):
    values=[r['value'] for r in entries if r['kind']=='FACT' and r['value'].get('state') in ('OBSERVED','OBSERVED_NEGATIVE') and r['value'].get('freshness')=='CURRENT' and timestamp(r['value']['collected_at'])<=now and timestamp(r['value']['observed_at'])<=now]
    histories={}
    for value in values:
        if value['kind']=='RUN_HISTORY':
            old=histories.get(value['subject'])
            if old is None or timestamp(old['collected_at'])<timestamp(value['collected_at']):histories[value['subject']]=value
    result=[]
    for value in values:
        if value['kind'] in ('JOB_RUN','REFRESH_RUN') and any(value['value'].get(field) and timestamp(value['value'][field])>now for field in ('start','end')):continue
        history=histories.get(value['subject'])
        if value['kind'] in ('JOB_RUN','REFRESH_RUN') and history and timestamp(history['collected_at'])>=timestamp(value['collected_at']):
            retained={run.get('run_id') for run in history['value'].get('runs',[])}
            if value['value'].get('run_id') not in retained:continue
        result.append(value)
    return result


def pending_comparison_status(verdict,records,reads,*,target,now):
    """A relevant current operational fact, explicitly not a numerical cause.

    This route requires the target's measured value and a declaration-backed
    directed path to the producer. It never manufactures a second quantity.
    """
    if verdict not in ('latency','waiting on job','failed job','refresh stale'):
        raise ValueError('PENDING_COMPARISON_OPERATIONAL_VERDICT_REQUIRED')
    if target is None or not any(read['subject']==target for read in reads.values()):
        raise ValueError('REQUESTED_TARGET_NOT_MEASURED')
    entries=list(records.values());paths=[entry['value'] for entry in entries if entry['kind']=='PATH']
    reachable={target};nodes={}
    for path in paths:
        nodes.update({node['id']:node for node in path.get('nodes',[])})
        edges=[edge for edge in path.get('edges',[]) if edge.get('kind') not in ('CONTAINS','INTERACTS_WITH')
            and edge.get('confidence') in ('DECLARED','VERIFIED','VALUE_VERIFIED')
            and edge.get('provenance',{}).get('source')!='MODEL_PROPOSAL'
            and edge.get('verification',{}).get('state')!='STALE']
        for _ in range(len(nodes)):
            expanded=reachable|{edge['target'] for edge in edges if edge['source'] in reachable}
            if expanded==reachable:break
            reachable=expanded
    facts=current_facts(entries,now)
    def time_of(fact,field):
        raw=fact['value'].get(field)
        return timestamp(raw) if raw else None
    def latest_runs(subject,kind):
        runs=[fact for fact in facts if fact['subject']==subject and fact['kind']==kind]
        if not runs:return []
        latest=max(time_of(fact,'start') or fact['observed_at'] for fact in runs)
        return [fact for fact in runs if (time_of(fact,'start') or fact['observed_at'])==latest]
    def supported(selected,reason,expected=None):
        result=_supported(verdict,records,None,reason+' The comparison has not been checked; no numerical cause has been established.')
        result.update(claim_scope='OPERATIONAL_STATUS_WITH_COMPARISON_PENDING',operational_fact=selected,comparison_checked=False)
        if expected:result['expected_update_at']=expected
        return result
    for subject in sorted(reachable):
        node=nodes.get(subject,{})
        if node.get('kind') not in ('PIPELINE','NOTEBOOK','COPY_ACTIVITY','MODEL'):continue
        kind='REFRESH_RUN' if node['kind']=='MODEL' else 'JOB_RUN'
        runs=latest_runs(subject,kind)
        # Conflicting simultaneous records cannot select the convenient status.
        states={fact['value'].get('status') for fact in runs}
        if len(states)>1:continue
        latest=runs[0] if runs else None
        if verdict=='failed job' and kind=='JOB_RUN' and latest and latest['value'].get('status')=='FAILED':
            return supported(latest,'The latest retained run of the declared path producer '+node.get('label',subject)+' failed.')
        if verdict=='waiting on job' and kind=='JOB_RUN':
            if latest and latest['value'].get('status') in ('QUEUED','RUNNING'):
                return supported(latest,'The latest retained run of the declared path producer '+node.get('label',subject)+' is '+latest['value']['status'].lower()+'.')
            overdue=next((fact for fact in facts if fact['subject']==subject and fact['kind']=='OVERDUE'
                and fact['value'].get('overdue')is True and time_of(fact,'due_at') and time_of(fact,'due_at')<=now
                and (latest is None or (time_of(latest,'start') or latest['observed_at'])<time_of(fact,'due_at'))),None)
            if overdue:return supported(overdue,'The declared path producer '+node.get('label',subject)+' has no observed start for its overdue scheduled run.')
        if verdict=='refresh stale' and node['kind']=='MODEL':
            stale=next((fact for fact in facts if fact['subject']==subject and fact['kind']=='REFRESH_STATE' and fact['value'].get('state',fact['value'].get('status'))=='STALE'),None)
            if stale:return supported(stale,'The retained refresh state for the declared path model '+node.get('label',subject)+' is stale.')
        if verdict=='latency' and latest and latest['value'].get('status')=='SUCCEEDED':
            boundaries=[entry['value'] for entry in entries if entry['kind']=='BOUNDARY' and entry['value'].get('job')==subject
                        and entry['value'].get('downstream') in reachable and entry['value'].get('upstream') in reachable]
            for boundary in boundaries:
                source=boundary['upstream']
                changed=next((time_of(fact,'last_modified') for fact in facts if fact['subject']==source and fact['kind']=='TABLE_LOAD' and time_of(fact,'last_modified')),None)
                schedules=[fact for fact in facts if fact['subject']==subject and fact['kind']=='SCHEDULE' and time_of(fact,'next_due') and time_of(fact,'next_due')>=now]
                durations=[fact for fact in facts if fact['subject']==subject and fact['kind']=='TYPICAL_DURATION' and fact['value'].get('sample_count',0)>0]
                if changed and time_of(latest,'end') and time_of(latest,'end')<changed<=now and schedules and durations:
                    due=datetime.fromisoformat(time_of(schedules[0],'next_due').replace('Z','+00:00'))
                    expected=timestamp((due+timedelta(seconds=durations[0]['value']['median_seconds'])).isoformat())
                    return supported(latest,'The declared source changed after this producer last completed; its next scheduled run is not yet due.',expected)
    raise ValueError('CURRENT_RELEVANT_OPERATIONAL_STATUS_REQUIRED')


def explicit_operational_fact(request,entries,now,ticket_text):
    """The latest status is a fact even when it establishes no incident verdict."""
    from .reported_figure import span
    import re
    if set(request)!={'kind','subject','question','source'} or request.get('kind')!='FACT' or request['question'] not in ('RUN_STATUS','REFRESH_STATUS'):
        raise ValueError('EXPLICIT_OPERATIONAL_QUESTION_REQUIRED')
    quote=span(request['source'],ticket_text)
    if ticket_text is None or not re.search(r'\b(did|has|was|is|what|when|show|latest|last)\b',quote,re.I) or not re.search(r'\b(job|pipeline|run|refresh|notebook|copy)\b',quote,re.I) or not re.search(r'\b(fail(?:ed)?|succeed(?:ed)?|status|finish(?:ed)?|complete(?:d)?|queued|running)\b',quote,re.I):
        raise ValueError('EXPLICIT_OPERATIONAL_QUESTION_REQUIRED')
    kinds={'JOB_RUN'} if request['question']=='RUN_STATUS' else {'REFRESH_RUN','REFRESH_STATE'}
    candidates=[entry['value'] for entry in entries if entry['kind']=='FACT' and entry['value'].get('subject')==request['subject'] and entry['value'].get('kind') in kinds
                and timestamp(entry['value']['collected_at'])<=now and timestamp(entry['value']['observed_at'])<=now]
    if not candidates:raise ValueError('CURRENT_OPERATIONAL_STATUS_REQUIRED')
    newest=max(timestamp(fact['collected_at']) for fact in candidates)
    batch=[fact for fact in candidates if timestamp(fact['collected_at'])==newest]
    # Unknown/unavailable newer observations do not resurrect older success.
    if any(fact.get('state') not in ('OBSERVED','OBSERVED_NEGATIVE') or fact.get('freshness')!='CURRENT' for fact in batch):
        raise ValueError('CURRENT_OPERATIONAL_STATUS_REQUIRED')
    current=current_facts(entries,now)
    batch=[fact for fact in batch if fact in current and fact.get('state')=='OBSERVED']
    if not batch:raise ValueError('CURRENT_OPERATIONAL_STATUS_REQUIRED')
    latest=max(timestamp(fact['value'].get('start') or fact['observed_at']) for fact in batch)
    selected=[fact for fact in batch if timestamp(fact['value'].get('start') or fact['observed_at'])==latest]
    statuses={fact['value'].get('status',fact['value'].get('state')) for fact in selected}
    if len(statuses)!=1 or not statuses<={'SUCCEEDED','COMPLETED','FAILED','QUEUED','RUNNING','STALE'}:
        raise ValueError('LATEST_OPERATIONAL_STATUS_UNKNOWN_OR_CONFLICTING')
    # Same time/status but different runs is not a uniquely established latest run.
    if len({fact['value'].get('run_id') for fact in selected})!=1:
        raise ValueError('LATEST_OPERATIONAL_RUN_AMBIGUOUS')
    return selected[0]


def check(verdict,ids,registry,*,now,request=None,ticket_text=None,target=None):
    if verdict not in VERDICTS:raise ValueError('UNKNOWN_VERDICT')
    records=registry.resolve(ids);entries=list(records.values());now=timestamp(now)
    request=request or {'kind':'COMPARE'}
    if verdict=='not found':
        result={'verdict':verdict,'evidence_ids':list(records),'reason':'Evidence does not establish a cause within the admitted budget.'}
        if request.get('kind')=='FACT':
            try:selected=explicit_operational_fact(request,entries,now,ticket_text)
            except ValueError:return result
            status=selected['value'].get('status',selected['value'].get('state'))
            if status in ('SUCCEEDED','COMPLETED'):
                result.update(claim_scope='OPERATIONAL_FACT_ONLY',operational_fact=selected,
                    reason='The latest retained '+request['question'].lower().replace('_',' ')+' is '+status+
                    ' (run '+str(selected['value'].get('run_id') or 'not recorded')+', observed '+selected['observed_at']+'). '+
                    'No failed, waiting or stale incident is established by this status. This answers only the explicit operational question; no numerical cause was established.')
        return result
    if request.get('kind') not in ('FACT','COMPARE','DEFINITION'):raise ValueError('REQUEST_KIND_REQUIRED')
    if request['kind']=='FACT':
        if request['subject'] not in registry.path:raise ValueError('EXPLICIT_OPERATIONAL_QUESTION_REQUIRED')
        selected=explicit_operational_fact(request,entries,now,ticket_text)
        states={'failed job':{'FAILED'},'waiting on job':{'QUEUED','RUNNING'},'refresh stale':{'STALE'}}.get(verdict,set())
        if selected['value'].get('status',selected['value'].get('state')) not in states:raise ValueError('CURRENT_OPERATIONAL_STATUS_REQUIRED')
        result=_supported(verdict,records,None,'The retained '+request['question'].lower().replace('_',' ')+' is '+selected['value'].get('status',selected['value'].get('state'))+'. This answers only the explicit operational question; no numerical cause was established.')
        result['claim_scope']='OPERATIONAL_FACT_ONLY';result['operational_fact']=selected
        return result
    if request['kind']=='DEFINITION':raise ValueError('DEFINITION_ROUTE_REQUIRES_RETAINED_EXPLANATION')
    reads={identity:r['value'] for identity,r in records.items() if r['kind']=='READ'}
    for read in reads.values():
        if read.get('route_admitted') is not True or read.get('read_only_verified') is not True or not read.get('receipt_id'):raise ValueError('READ_NOT_ADMITTED')
        quantity(read)
    if target is not None and not any(read['subject']==target for read in reads.values()):raise ValueError('REQUESTED_TARGET_NOT_MEASURED')
    if request.get('comparison_pending') is True:
        if any(entry['kind'] in ('COMPARISON','GIVEN_COMPARISON') for entry in entries):raise ValueError('PENDING_COMPARISON_CONTRACT_CONFLICT')
        return pending_comparison_status(verdict,records,reads,target=target,now=now)
    comparisons=[r['value'] for r in entries if r['kind']=='COMPARISON']
    facts=current_facts(entries,now)
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
            if target is not None and not any(read['subject']==target and canonical(read['context'])==canonical(left['context']) and quantity(read)==quantity(left) for read in reads.values()):continue
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
        if verdict=='as designed':
            from .native_verdict_support import validate_design
            mechanism=validate_design(witness,reads,comparisons)
            return _supported(verdict,records,None,mechanism+' This describes implemented technical logic, not a judgment of business correctness.')
        if verdict=='access difference':
            from .native_verdict_support import validate_access
            return _supported(verdict,records,None,validate_access(witness,reads,comparisons))
        if verdict=='source changed history':
            from .native_verdict_support import validate_history
            return _supported(verdict,records,None,validate_history(witness,reads,comparisons,entries,now))
        raise ValueError('VERDICT_WITNESS_NOT_VALIDATED')
    raise ValueError(witness_kind+'_CHECKED_WITNESS_REQUIRED')


def _supported(verdict,records,boundary,reason):
    return {'verdict':verdict,'evidence_ids':list(records),'boundary':copy.deepcopy(boundary),'reason':reason}

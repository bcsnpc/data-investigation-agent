"""Deterministic incremental collectors; platform calls live behind adapter/gateway.

The adapter's list_changes(subjects) returns a complete/incomplete marker listing
and evidence, never guesses missing items to be deleted. Each fetch is bound to
one listed subject. Request reservations are supplied by the shared SCAN budget;
adapters must also charge every physical request at their gateway boundary.
"""
from datetime import datetime, timedelta
from statistics import median
from .facts_ledger import fact
from .estate_graph_contract import timestamp
from .estate_graph_incremental import is_stop_condition


def observation(subject, kind, value, at, evidence, collector, *, state='OBSERVED', reason=None,
                observed_at=None, source='RUNTIME_OBSERVATION'):
    return fact({'subject':subject,'kind':kind,'value':value,'observed_at':observed_at or at,
                 'collected_at':at,'source':source,'state':state,'reason':reason,
                 'provenance':{'evidence_ids':evidence,'collector':collector,'locator':subject}})


def derived_runs(subject, runs, at, evidence, collector, schedule=None):
    """Derive duration/overdue only from observed run records + declared schedule."""
    values=[];durations=[]
    for run in runs:
        if run.get('start') and run.get('end'):
            start=datetime.fromisoformat(timestamp(run['start']).replace('Z','+00:00'))
            end=datetime.fromisoformat(timestamp(run['end']).replace('Z','+00:00'))
            seconds=(end-start).total_seconds()
            if seconds<0:raise ValueError('FACT_RUN_END_BEFORE_START')
            if run.get('status')=='SUCCEEDED':durations.append(seconds)
    if durations:
        values.append(observation(subject,'TYPICAL_DURATION',{'median_seconds':median(durations),'sample_count':len(durations)},at,evidence,collector,source='DERIVED_OBSERVATIONS'))
    if schedule is not None:
        due=timestamp(schedule['next_due'])
        now=timestamp(at)
        # A later successful/started run settles this due time. Failed runs are
        # not silently reclassified as absent work.
        since=[run for run in runs if run.get('start') and timestamp(run['start'])>=due]
        overdue=now>due and not since
        values.append(observation(subject,'OVERDUE',{'overdue':overdue,'due_at':due,
            'checked_run_count':len(runs)},at,evidence,collector,
            state='OBSERVED' if overdue else 'OBSERVED_NEGATIVE',source='DERIVED_OBSERVATIONS'))
    return values


class IncrementalFactCollector:
    def __init__(self, ledger, adapter, *, budget, key_tables=(), list_interval_seconds=1800):
        if type(list_interval_seconds) is not int or list_interval_seconds<1:raise ValueError('FACT_LIST_INTERVAL')
        self.ledger,self.adapter,self.budget=ledger,adapter,budget
        self.key_tables=frozenset(key_tables);self.interval=list_interval_seconds

    def run(self, estate, subjects, *, now, force=False):
        if not subjects or len(subjects)>200 or len(set(subjects))!=len(subjects):raise ValueError('FACT_PATH_BOUND')
        now=timestamp(now);identity=self.adapter.identity
        cursor=self.ledger.cursor(estate,identity,'__listing__:'+','.join(sorted(subjects)))
        if cursor and not force:
            elapsed=(datetime.fromisoformat(now.replace('Z','+00:00'))-datetime.fromisoformat(cursor.replace('Z','+00:00'))).total_seconds()
            if elapsed<self.interval:return {'status':'NOT_DUE','facts':[],'subjects':[]}
        if not self.budget.claim('LIST',subjects):return {'status':'BUDGET_EXHAUSTED','facts':[],'subjects':[],'coverage_gap':'Listing not refreshed: shared scan allowance unavailable.'}
        listing=self.adapter.list_changes(subjects)
        if set(listing)!={'items','complete','evidence_ids'} or type(listing['complete']) is not bool:raise ValueError('FACT_LIST_SHAPE')
        signals=listing['items']
        if not isinstance(signals,list) or len(signals)>200:raise ValueError('FACT_LIST_BOUND')
        if len({s['subject'] for s in signals})!=len(signals):raise ValueError('FACT_DUPLICATE_SUBJECT')
        if any(set(s)!={'subject','marker','load_marker'} or s['subject'] not in subjects or not isinstance(s['marker'],str) or not s['marker'] for s in signals):raise ValueError('FACT_SIGNAL_OUTSIDE_PATH')
        written=[];results=[]
        for signal in signals:
            subject=signal['subject'];old=self.ledger.cursor(estate,identity,subject)
            if old==signal['marker'] and not force:
                results.append({'subject':subject,'status':'UNCHANGED_MARKER'});continue
            if not self.budget.claim('FETCH',[subject]):
                results.append({'subject':subject,'status':'BUDGET_EXHAUSTED'});continue
            values=self.adapter.fetch(subject,now=now)
            values=[fact(value) for value in values]
            if any(value['subject']!=subject or value['collected_at']!=now for value in values):raise ValueError('FACT_FETCH_OUTSIDE_PATH_OR_TIME')
            if not values:raise ValueError('FACT_EMPTY_FETCH_REQUIRES_EXPLICIT_GAP')
            # Markers advance only after facts were durably appended; partial
            # failures stay retryable and cannot become successful negatives.
            written.extend(self.ledger.append(estate,values))
            if all(v['state']!='UNAVAILABLE' for v in values):self.ledger.advance(estate,identity,subject,signal['marker'],now)
            load=signal['load_marker']
            if subject in self.key_tables and load is not None:
                previous=self.ledger.cursor(estate,identity,subject+':profile')
                if previous!=load and self.budget.claim('PROFILE',[subject]):
                    profile=fact(self.adapter.profile(subject,load_marker=load,now=now))
                    if profile['subject']!=subject or profile['kind']!='TABLE_PROFILE' or profile['collected_at']!=now:raise ValueError('FACT_PROFILE_SCOPE')
                    if profile['state']!='UNAVAILABLE' and profile['value'].get('load_marker')!=load:raise ValueError('FACT_PROFILE_LOAD_MARKER')
                    written.extend(self.ledger.append(estate,[profile]))
                    if profile['state']!='UNAVAILABLE':self.ledger.advance(estate,identity,subject+':profile',load,now)
            results.append({'subject':subject,'status':'COLLECTED'})
        missing=set(subjects)-{s['subject'] for s in signals}
        for subject in sorted(missing):
            value=observation(subject,'COVERAGE',None,now,listing['evidence_ids'],identity,state='UNAVAILABLE',
                reason='Subject absent from '+('complete' if listing['complete'] else 'incomplete')+' listing; no negative runtime observation established.')
            written.extend(self.ledger.append(estate,[value]))
        self.ledger.advance(estate,identity,'__listing__:'+','.join(sorted(subjects)),now,now)
        return {'status':'COLLECTED','facts':written,'subjects':results,'listing_complete':listing['complete']}


def refresh_facts(ledger,estate,path,collector,*,now,max_age_seconds=3600,required_kinds=None):
    """Top up only stale/missing/unavailable facts on this explicitly admitted path."""
    before=ledger.read(estate,path,now=now,max_age_seconds=max_age_seconds)
    needed=set(before['missing_subjects'])
    for value in before['facts']:
        if value['freshness']=='STALE' or value['state']=='UNAVAILABLE':needed.add(value['subject'])
    if required_kinds:
        present={(v['subject'],v['kind']) for v in before['facts']}
        needed.update(node for node in path if any((node,kind) not in present for kind in required_kinds.get(node,())))
    result=collector.run(estate,sorted(needed),now=now,force=True) if needed else {'status':'CURRENT','facts':[],'subjects':[]}
    return {'refreshed_subjects':sorted(needed),'collection':result,
            **ledger.read(estate,path,now=now,max_age_seconds=max_age_seconds)}

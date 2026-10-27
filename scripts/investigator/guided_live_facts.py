"""Path-local triage over existing ledger/collector ports, without a new store."""
from copy import deepcopy
from datetime import datetime,timezone
from .path_triage import Triage
from .usage_governance import UsageHold


class ScanFactsUnavailable(ValueError):
    """The separate collector allocation is unavailable, not an INV allowance."""


def scan_refusal(error):
    # Do not swallow total/INV/REST refusals or a generic safety error.
    return isinstance(error,UsageHold) and str(error)=='MONTHLY_PHYSICAL_SCAN_EXHAUSTED'

KINDS={'MODEL_REFRESH':{'REFRESH_RUN','REFRESH_STATE','RUN_HISTORY'},
       'REFRESH_SCHEDULE':{'SCHEDULE'},'JOB_RUNS':{'JOB_RUN'},
       'LAYER_FRESHNESS':{'TABLE_LOAD','TABLE_PROFILE'},'SOURCE_CHANGES':{'TABLE_PROFILE'},
       'NEXT_LOAD':{'SCHEDULE'}}


class PathFacts:
    def __init__(self, *, ledger, estate, path, collector=None, save=lambda _:None, now=None):
        self.ledger,self.estate,self.path=ledger,estate,deepcopy(path)
        self.subjects=sorted({n['id'] for n in path['nodes']})
        self.collector,self.save=(collector if collector is None or callable(collector) else collector.run),save
        self.now=now or (lambda:datetime.now(timezone.utc).isoformat())
        self.snapshot=None;self.refreshed=False
        self.refresh_failure=None

    def read(self):
        if self.snapshot is None:
            self.snapshot=self.ledger.read(self.estate,self.subjects,now=self.now(),max_age_seconds=900)
        return self.snapshot

    def lookup(self,check,path):
        if check not in KINDS:return None
        rows=[f for f in self.read()['facts'] if f['kind'] in KINDS[check] and f['freshness']=='CURRENT'
              and f['state'] in ('OBSERVED','OBSERVED_NEGATIVE')]
        if check=='JOB_RUNS':
            now=datetime.fromisoformat(self.now().replace('Z','+00:00'))
            rows=[f for f in rows if 0<=(now-datetime.fromisoformat(f['collected_at'].replace('Z','+00:00'))).total_seconds()<=30]
        if check=='MODEL_REFRESH':
            model_ids={n['id'] for n in self.path['nodes'] if n['kind']=='MODEL'}
            rows=[f for f in rows if f['subject'] in model_ids or f['kind'] in ('REFRESH_RUN','REFRESH_STATE')]
        if not rows:return None
        return {'source':'facts-ledger','observed_at':min(f['collected_at'] for f in rows),
                'state':'OBSERVED' if any(f['state']=='OBSERVED' for f in rows) else 'OBSERVED_NEGATIVE',
                'value':deepcopy(rows)}

    def refresh(self,check,path):
        if check not in KINDS:raise ValueError('CHECK_HAS_NO_INSTALLED_NATIVE_FACT_PORT:'+check)
        if self.collector is None:raise ValueError('PATH_COLLECTOR_NOT_INSTALLED')
        if not self.refreshed:
            self.refreshed=True
            try:result=self.collector(self.estate,self.subjects,now=self.now(),force=True)
            except UsageHold as error:
                if not scan_refusal(error):raise
                self.refresh_failure=str(error)
                self.save({'event':'PATH_FACT_REFRESH_UNAVAILABLE','reason':self.refresh_failure,'purpose':'SCAN'})
                raise ScanFactsUnavailable(self.refresh_failure) from error
            self.save({'event':'PATH_FACT_REFRESH','result':result})
            self.snapshot=None
        result=self.lookup(check,path)
        if result is None:raise ScanFactsUnavailable(self.refresh_failure) if self.refresh_failure else ValueError('FRESH_PATH_FACT_NOT_AVAILABLE:'+check)
        return result

    def run(self):
        return Triage(path=self.subjects,lookup=self.lookup,refresh=self.refresh,save=self.save,now=self.now).run()

    def history(self,node,kinds):
        rows=self.ledger.read(self.estate,[node],now=self.now(),max_age_seconds=900)['facts']
        current=[f for f in rows if f['kind'] in kinds and f['freshness']=='CURRENT'
                 and f['state'] in ('OBSERVED','OBSERVED_NEGATIVE')]
        if not current and self.collector:
            try:self.collector(self.estate,[node],now=self.now(),force=True)
            except UsageHold as error:
                if not scan_refusal(error):raise
                return {'status':'UNAVAILABLE','reason':str(error),'purpose':'SCAN','retained':rows}
            rows=self.ledger.read(self.estate,[node],now=self.now(),max_age_seconds=900)['facts']
            current=[f for f in rows if f['kind'] in kinds and f['freshness']=='CURRENT'
                     and f['state'] in ('OBSERVED','OBSERVED_NEGATIVE')]
        if not current:return {'status':'UNAVAILABLE','reason':'No current readable native facts on this subject','retained':rows}
        return {'status':'OBSERVED','source':'facts-ledger','observed_at':min(f['collected_at'] for f in current),
                'facts':current}

"""Cheap, fixed ledger-first checks before AI investigation; target path only."""
from copy import deepcopy
from datetime import datetime,timezone
from .estate_graph_contract import timestamp
from .model_spend import SpendHold
from .usage_governance import UsageHold
from .live_gateway import GatewayDenied

CHECKS=('MODEL_REFRESH','REFRESH_SCHEDULE','AUTOMATIC_UPDATES','JOB_RUNS',
        'LAYER_FRESHNESS','SOURCE_CHANGES','NEXT_LOAD','CONNECTION_MODE',
        'SECURITY_PRESENCE','DEFINITION_CHANGES')


class Triage:
    def __init__(self,*,path,lookup,refresh,save,max_age_seconds=900,read_limit=10,now=None):
        if type(read_limit) is not int or not 0<=read_limit<=10:raise ValueError('TRIAGE_READ_BOUND')
        self.path=deepcopy(path);self.lookup,self.refresh,self.save=lookup,refresh,save
        self.max_age_seconds,self.read_limit=max_age_seconds,read_limit
        self.now=now or (lambda:datetime.now(timezone.utc).isoformat())

    def run(self):
        now=timestamp(self.now());now_dt=datetime.fromisoformat(now.replace('Z','+00:00'))
        facts=[];reads=0
        for check in CHECKS:
            value=self.lookup(check,deepcopy(self.path))
            current=False
            if isinstance(value,dict) and value.get('source') and value.get('observed_at'):
                try:
                    observed=datetime.fromisoformat(timestamp(value['observed_at']).replace('Z','+00:00'))
                    current=(value.get('state','OBSERVED') in ('OBSERVED','OBSERVED_NEGATIVE') and 'value' in value
                             and 0<=(now_dt-observed).total_seconds()<=self.max_age_seconds)
                except (ValueError,TypeError): current=False
            if current:
                fact={'check':check,'state':value.get('state','OBSERVED'),'source':value['source'],
                      'observed_at':value['observed_at'],'value':deepcopy(value['value']),'cached':True}
            elif reads<self.read_limit:
                reads+=1
                try:
                    refreshed=self.refresh(check,deepcopy(self.path))
                    if (not isinstance(refreshed,dict) or not refreshed.get('source') or not refreshed.get('observed_at')
                            or 'value' not in refreshed or refreshed.get('state','OBSERVED') not in ('OBSERVED','OBSERVED_NEGATIVE')):
                        raise ValueError('FRESH_FACT_NEEDS_SOURCE_AND_TIME')
                    observed=datetime.fromisoformat(timestamp(refreshed['observed_at']).replace('Z','+00:00'))
                    if not 0<=(now_dt-observed).total_seconds()<=self.max_age_seconds:
                        raise ValueError('REFRESH_RETURNED_STALE_FACT')
                    fact={'check':check,'state':refreshed.get('state','OBSERVED'),'source':refreshed['source'],
                          'observed_at':refreshed['observed_at'],'value':deepcopy(refreshed['value']),'cached':False}
                except (SpendHold,UsageHold,GatewayDenied):raise
                except Exception as error:
                    # Preserve known stale data separately; never re-date it.
                    fact={'check':check,'state':'UNAVAILABLE','source':None,'observed_at':None,
                          'reason':type(error).__name__,'previous':deepcopy(value)}
            else:
                fact={'check':check,'state':'UNAVAILABLE','source':None,'observed_at':None,
                      'reason':'TRIAGE_READ_LIMIT','previous':deepcopy(value)}
            self.save({'event':'TRIAGE_FACT','fact':deepcopy(fact)})
            facts.append(fact)
        return {'facts':facts,'refresh_operations':reads,'path':deepcopy(self.path)}

"""Scheduled facts collector entry point using existing shared SCAN authority.

No migrations, model calls, identities or estate writes. Operator applies schema
first. Unified-runner handlers can call execute(config) under their capture.
"""
from datetime import datetime, timezone
import json
import os
from investigator.shared_state import configured_state, sha
from investigator.facts_ledger import FactLedger
from investigator.facts_collectors import IncrementalFactCollector
from investigator.adapters.runtime_facts_microsoft import MicrosoftRuntimeFacts


class CollectorAllowance:
    def __init__(self,meter,limit):self.meter,self.limit=meter,limit
    def claim(self,operation,subjects):return self.meter.used<self.limit


class CollectorRequestAllowanceExhausted(ValueError):pass


def validate(config):
    required={'estate','authentication','storage','receipt_uri_prefix','budget','subjects','max_requests','approval'}
    optional={'sql_configs','list_interval_seconds','key_tables','max_subjects_per_wake'}
    if not isinstance(config,dict) or not required<=set(config)<=required|optional:raise ValueError('FACT_COLLECTOR_CONFIGURATION')
    if not isinstance(config['estate'],str) or not config['estate'] or not isinstance(config['approval'],str) or not config['approval']:raise ValueError('FACT_COLLECTOR_APPROVAL')
    if type(config['max_requests']) is not int or not 1<=config['max_requests']<=100:raise ValueError('FACT_REQUEST_ALLOWANCE')
    if not isinstance(config['subjects'],dict) or not 1<=len(config['subjects'])<=200:raise ValueError('FACT_SUBJECT_ALLOWLIST')
    if type(config.get('max_subjects_per_wake',10)) is not int or not 1<=config.get('max_subjects_per_wake',10)<=200:raise ValueError('FACT_WAKE_SUBJECT_BOUND')
    if not set(config.get('key_tables',[]))<=set(config['subjects']):raise ValueError('FACT_KEY_TABLE_OUTSIDE_SCOPE')
    return config


def execute(config):
    config=validate(config)
    from investigator.build_phase import active
    if not active():raise ValueError('FACT_COLLECTOR_REQUIRES_SHARED_MONTHLY_SCAN_POLICY')
    if os.environ.get('INVESTIGATOR_RECORDING_CLASS','EXACT')!='EXACT':raise ValueError('FACT_COLLECTOR_PROJECTED_CAPTURE_UNIMPLEMENTED')
    state=configured_state()
    if state is None or state.backend!='postgresql':raise ValueError('FACT_COLLECTOR_REQUIRES_SHARED_POSTGRESQL')
    return collect(config,state=state)


def collect(config,*,state,http=None,sql=None,retain=None,meter=None,clock=None):
    """Injection seams permit deterministic replay; production defaults are guarded."""
    config=validate(config)
    from scan_estate_graph import Meter
    from metadata_auth import MetadataHttp
    from investigator.adapters.blob_artifacts import recording_stores
    from investigator.graph_definitions import DefinitionSink
    from investigator.physical_reads import scope
    own_meter=meter is None
    if meter is None:meter=Meter(state,config['budget'],config['max_requests'])
    clock=clock or (lambda:datetime.now(timezone.utc).isoformat().replace('+00:00','Z'))
    at=clock();ledger=FactLedger(state)
    try:
        if http is None:
            mode=config['authentication'].get('mode')
            if mode=='federated_reader':from investigator.adapters.federated_reader import Tokens
            elif mode=='managed_identity':from investigator.adapters.managed_identity import Tokens
            else:raise ValueError('FACT_READONLY_READER_IDENTITY_REQUIRED')
            def physical(operation):
                if meter.used>=config['max_requests']:raise CollectorRequestAllowanceExhausted('FACT_PHYSICAL_ALLOWANCE_EXHAUSTED')
                return meter(operation)
            http=MetadataHttp(Tokens(config['authentication']),meter=physical)
        if retain is None:
            files,_=recording_stores(config['storage'])
            retain=DefinitionSink(files,config['receipt_uri_prefix'],recording_class='EXACT')
        if sql is None:
            from fabric_sql_surface import read
            def sql(route,request):
                settings=config.get('sql_configs',{}).get(route.get('reader'))
                if settings is None:raise ValueError('FACT_DECLARED_SQL_READER_ABSENT')
                reader=settings['fabric']['sql_reader']
                if reader.get('mode') not in ('federated_reader','managed_identity'):raise ValueError('FACT_READONLY_SQL_IDENTITY_REQUIRED')
                if reader['server']!=route['connection']:raise ValueError('FACT_SQL_DECLARED_CONNECTION_DIFFERS')
                def physical(kind,operation):
                    if meter.used>=config['max_requests']:raise CollectorRequestAllowanceExhausted('FACT_PHYSICAL_ALLOWANCE_EXHAUSTED')
                    return meter(operation)
                def operation():
                    with scope(physical):return read(settings,route['database'],request)
                if meter.used>=config['max_requests']:raise CollectorRequestAllowanceExhausted('FACT_PHYSICAL_ALLOWANCE_EXHAUSTED')
                return meter(operation)
        adapter=MicrosoftRuntimeFacts(config['subjects'],http=http,sql=sql,retain=retain)
        all_subjects=sorted(config['subjects']);batch_size=config.get('max_subjects_per_wake',10)
        dispatcher='__dispatcher__:'+sha(all_subjects)
        cursor=ledger.cursor(config['estate'],adapter.identity,dispatcher)
        offset=int(cursor) if cursor is not None else 0
        selected=(all_subjects+all_subjects)[offset:offset+min(batch_size,len(all_subjects))]
        # Validate only selected graph subjects before the first estate call.
        with state.transaction() as db:
            rows=state.sql(db,'SELECT identity FROM estate_graph_nodes WHERE estate=? AND identity IN ('+','.join('?' for _ in selected)+')',(config['estate'],*selected)).fetchall()
        if {row[0] for row in rows}!=set(selected):raise ValueError('FACT_CONFIGURED_GRAPH_SUBJECT_ABSENT')
        collector=IncrementalFactCollector(ledger,adapter,budget=CollectorAllowance(meter,config['max_requests']),
            key_tables=config.get('key_tables',[]),list_interval_seconds=config.get('list_interval_seconds',21600))
        result=collector.run(config['estate'],selected,now=at)
        ledger.advance(config['estate'],adapter.identity,dispatcher,str((offset+len(selected))%len(all_subjects)),at)
        output={'estate':config['estate'],'observed_at':at,'collector':adapter.identity,'collection':result,
                'selected_subjects':selected,'not_selected_subjects':sorted(set(all_subjects)-set(selected)),
                'physical_requests':meter.used,'purpose':'SCAN','config_hash':sha(config),'model_calls':0,
                'approval':config['approval'],'coverage':ledger.read(config['estate'],selected,now=at),
                'listing_interval_seconds':collector.interval,'continuous_30_minute_freshness_claim':False}
        state.put('facts_collector_run',getattr(meter,'owner','offline:'+sha(output)),output)
        return output
    finally:
        if own_meter:meter.close()


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True)
    args=parser.parse_args()
    with open(args.config,encoding='utf8') as stream:config=json.load(stream)
    print(json.dumps(execute(config),sort_keys=True))


if __name__=='__main__':main()

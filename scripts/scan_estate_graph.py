"""Scheduled, bounded live graph refresh. Default is a deployment plan, not reads."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from investigator.shared_state import sha


class Meter:
    def __init__(self, state, budget, limit, *, clock=None):
        import sqlite3
        import time
        from types import SimpleNamespace
        from investigator.shared_usage import SharedUsage, TABLES
        from investigator.onboarding import digest
        if not isinstance(budget, dict) or set(budget) != {'environment', 'policy_sha256', 'round_id', 'rolling_limit'}:
            raise ValueError('EXISTING_SHARED_USAGE_PINS_REQUIRED')
        if type(limit) is not int or not 1 <= limit <= 100: raise ValueError('GRAPH_PHYSICAL_REQUEST_BOUND')
        retained=state.get('usage_policy',budget['environment'])['body']
        if (sha(retained)!=budget['policy_sha256'] or retained['round_policy']['id']!=budget['round_id']
                or retained['policy']['daily_limits']['cloud_calls']!=budget['rolling_limit']):
            raise ValueError('GRAPH_SHARED_USAGE_APPROVAL_PIN_DIFFERS')
        self.state, self.limit, self.used = state, limit, 0
        self.owner = 'graph-scan:' + str(uuid4())
        governor=SimpleNamespace(environment=budget['environment'],policy=retained['policy'],hash=digest(retained['policy']),
            clock=clock or time.time,runtime=SimpleNamespace(config={'_estate':{'round':retained['round_policy']}}))
        self.usage=SharedUsage(governor,state,owner=self.owner)
        # The existing authority owns admission; memory is only its reporting
        # mirror. No new budget tables, limits, or durable local ledger exist.
        self.local=sqlite3.connect(':memory:')
        for table,(_,columns) in TABLES.items():
            self.local.execute('CREATE TABLE '+table+'('+','.join(columns)+')')
        self.before=self.usage.snapshot()
    def __call__(self, execute):
        if self.used >= self.limit: raise ValueError('GRAPH_PHYSICAL_REQUEST_CAP')
        key=str(uuid4())
        self.usage.reserve(self.local,self.owner,key,'cloud',purpose='INVESTIGATION')
        self.used += 1
        uncertain=True
        try:
            result=execute();uncertain=False;return result
        finally:
            self.usage.settle(self.local,self.owner,key,uncertain=uncertain)
    def close(self): self.local.close()


def validate(config):
    if isinstance(config,dict) and 'scans' in config:
        if set(config)!={'scans','budget','approval'}or not isinstance(config['scans'],list)or not 1<=len(config['scans'])<=2:
            raise ValueError('GRAPH_SCHEDULE_ESTATE_BOUND')
        if not isinstance(config['approval'],str)or not config['approval'].strip():raise ValueError('GRAPH_SCHEDULE_OWNER_APPROVAL_REQUIRED')
        for child in config['scans']:
            if 'scans' in child:raise ValueError('GRAPH_SCHEDULE_NESTING_FORBIDDEN')
            validate(child)
            if child['budget']!=config['budget']:raise ValueError('GRAPH_SCHEDULE_SHARED_BUDGET_PINS_DIFFER')
            if type(child['max_requests'])is not int or not 1<=child['max_requests']<=100:raise ValueError('GRAPH_PHYSICAL_REQUEST_BOUND')
        if len({child['estate']for child in config['scans']})!=len(config['scans']):raise ValueError('GRAPH_SCHEDULE_DUPLICATE_ESTATE')
        if sum(child['max_requests']for child in config['scans'])>100:raise ValueError('GRAPH_SCHEDULE_COMBINED_REQUEST_BOUND')
        return config
    required = {'estate', 'workspace', 'owners', 'authentication', 'storage', 'definition_uri_prefix',
                'budget', 'max_requests', 'approval'}
    if not isinstance(config, dict) or not required<=set(config)<=required|{'sql','container_schemas','dependency_models','admin_metadata'}: raise ValueError('GRAPH_SCHEDULE_CONFIGURATION')
    if not isinstance(config['approval'], str) or not config['approval'].strip():
        raise ValueError('GRAPH_SCHEDULE_OWNER_APPROVAL_REQUIRED')
    if not isinstance(config['authentication'],dict):raise ValueError('GRAPH_SCHEDULE_AUTHENTICATION_REQUIRED')
    if 'sql' in config and (not isinstance(config['sql'],list) or not 1<=len(config['sql'])<=10):
        raise ValueError('GRAPH_SQL_COLLECTOR_BOUND')
    for group in config.get('sql',[]):
        if not isinstance(group,dict)or set(group)!={'identity','config','objects'}:raise ValueError('GRAPH_SQL_COLLECTOR_SHAPE')
    if 'container_schemas' in config:
        groups=config['container_schemas']
        if not isinstance(groups,list)or not 1<=len(groups)<=10:raise ValueError('GRAPH_CONTAINER_GROUP_BOUND')
        for group in groups:
            if not isinstance(group,dict)or set(group)!={'identity','config','owners'}:raise ValueError('GRAPH_CONTAINER_GROUP_SHAPE')
            if not isinstance(group['owners'],dict)or not group['owners']:raise ValueError('GRAPH_CONTAINER_OWNER_BOUND')
            approved={'fabric://'+config['workspace']+'/'+key for key in config['owners']}
            if not set(group['owners'])<=approved:raise ValueError('GRAPH_CONTAINER_OWNER_SCOPE')
    if config.get('authentication',{}).get('mode')=='federated_scanner' and (config.get('sql')or config.get('container_schemas')):
        raise ValueError('SCANNER_SQL_CREDENTIAL_FORBIDDEN')
    if 'admin_metadata' in config and (type(config['admin_metadata'])is not bool or config['authentication'].get('mode')!='federated_scanner'):
        raise ValueError('SCANNER_ADMIN_METADATA_CONFIGURATION')
    if 'dependency_models' in config:
        from uuid import UUID
        models=config['dependency_models']
        if (config.get('authentication',{}).get('mode')!='federated_scanner'
                or not isinstance(models,list) or not 1<=len(models)<=100
                or len(set(models))!=len(models) or not set(models)<=set(config['owners'])
                or any(str(UUID(model))!=model for model in models)):
            raise ValueError('SCANNER_DEPENDENCY_MODEL_SCOPE_REQUIRED')
    if not isinstance(config['approval'], str) or not config['approval'].strip():
        raise ValueError('GRAPH_SCHEDULE_OWNER_APPROVAL_REQUIRED')
    return config


def definition_owner_ids(config):
    schemas={owner for group in config.get('container_schemas',[])for owner in group['owners']}
    return [key for key in config['owners']if 'fabric://'+config['workspace']+'/'+key not in schemas]


def execute(config):
    config=validate(config)
    if 'scans' not in config:return _execute_one(config)
    # Sequential scans share the same existing policy and counters. A failure
    # stops before the next estate; each started scan retains its own receipt.
    results=[]
    for child in config['scans']:results.append(_execute_one(child))
    return {'status':'COMPLETED','estates':results,'physical_requests':sum(r['physical_requests']for r in results),
        'config_hash':sha(config),'approval':config['approval'],'budget':config['budget']}


def scanner_dependencies(config,tokens,meter,sink):
    """Operator-selected models only; four fixed metadata queries, metered once."""
    validate(config)
    selected=frozenset(config.get('dependency_models',[]))
    if not selected:return None
    from investigator.adapters.scanner_identity import require_job
    from investigator.adapters.scanner_http import channel
    from investigator.adapters.graph_dax_http import DaxMetadataHttp
    from investigator.adapters.graph_dependencies import collect,FUNCTIONS
    from investigator.estate_graph_contract import canonical
    require_job(tokens.declaration,[config['workspace']])
    identity=channel(tokens.declaration)
    transport=DaxMetadataHttp(tokens,identity,lambda envelope:sink(canonical(envelope).encode())['sha256'])
    def dependencies(target):
        if target['workspace']!=config['workspace']:raise ValueError('SCANNER_DEPENDENCY_WORKSPACE_SCOPE_REQUIRED')
        if target['model'] not in selected:return []
        return [collect(kind=kind,target=target,identity=identity,gateway=None,
            meter=lambda descriptor,call:meter(call),transport=transport,route='EXECUTE_DAX_QUERIES',
            semantic_write_permission=True)for kind in FUNCTIONS]
    return dependencies


def _execute_one(config):
    if config['authentication'].get('mode')=='federated_scanner':
        from investigator.adapters.scanner_identity import job
        with job(config['authentication'],[config['workspace']],kind='CHANGE_DETECTION'):
            return _execute_one_scoped(config)
    return _execute_one_scoped(config)


def _execute_one_scoped(config):
    import os
    from investigator.privacy_capture import ACTIVE
    if ACTIVE.get() is not None or os.environ.get('INVESTIGATOR_RECORDING_CLASS', 'EXACT') != 'EXACT':
        raise ValueError('GRAPH_PROJECTED_DEFINITION_CAPTURE_NOT_IMPLEMENTED')
    from investigator.shared_state import configured_state
    from investigator.estate_graph_repository import GraphRepository
    from investigator.estate_graph_incremental import IncrementalScanner
    from investigator.adapters.graph_change_collector import FabricChanges
    from investigator.adapters.estate_graph_static import extract,extract_partitioned,asset_owners
    from investigator.adapters.blob_artifacts import recording_stores
    from investigator.graph_definitions import DefinitionSink
    from metadata_auth import MetadataHttp
    config = validate(config)
    state = configured_state()
    if state is None: raise ValueError('SHARED_GRAPH_STATE_REQUIRED')
    # Migrations are operator-owned; a scheduled reader must not create tables.
    repo = GraphRepository(state)
    meter = Meter(state, config['budget'], config['max_requests'])
    mode = config['authentication'].get('mode')
    if mode == 'federated_scanner':
        if config.get('sql')or config.get('container_schemas'):raise ValueError('SCANNER_SQL_CREDENTIAL_FORBIDDEN')
        from investigator.adapters.scanner_identity import Tokens
    elif mode == 'federated_reader':
        from investigator.adapters.federated_reader import Tokens
    elif mode == 'managed_identity':
        from investigator.adapters.managed_identity import Tokens
    else: raise ValueError('GRAPH_SCHEDULE_IDENTITY_MODE_UNSUPPORTED')
    if mode=='federated_scanner':
        from investigator.adapters.scanner_http import ScannerHttp
        tokens=Tokens(config['authentication'])
        http=ScannerHttp(tokens,meter=meter)
    else:http = MetadataHttp(Tokens(config['authentication']), meter=meter)
    files, _ = recording_stores(config['storage'])
    sink = DefinitionSink(files, config['definition_uri_prefix'], recording_class='EXACT')
    dependencies=scanner_dependencies(config,tokens,meter,sink) if mode=='federated_scanner' else None
    definition_owners=definition_owner_ids(config)
    collector = FabricChanges(config['workspace'],definition_owners,http,dependencies=dependencies) if definition_owners else None
    from investigator.graph_asset_catalog import AssetCatalog
    allowed={'fabric://'+config['workspace']+'/'+key for key in config['owners']}
    for group in config.get('sql',[]):allowed.update(group['objects'])
    catalog=AssetCatalog(repo,sink,extract_partitioned,asset_owners,allowed_owners=allowed)
    catalog.snapshot(config['estate'])  # Retained external symbols must exist before any estate call.
    clock=lambda:datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    scanner = IncrementalScanner(repo, collector, None,reconcile=catalog.refresh,observation_clock=clock) if collector else None
    at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    try:
        from investigator.adapters.scanner_admin import collect as admin_metadata
        admin_result=admin_metadata(config,http,sink)
        result = scanner.run(config['estate'], at) if scanner else {'estate':config['estate'],'observed_at':at,'owners':[],'definition_collection':'NOT_REQUESTED_SCHEMA_ONLY'}
        result['admin_metadata']=admin_result
        result['sql_collectors']=[]
        for group in config.get('sql',[]):
            from investigator.adapters.graph_sql_changes import FabricSqlChanges
            from investigator.physical_reads import scope
            from fabric_sql_surface import read
            def execute_sql(database,request):
                def operation():
                    with scope(lambda kind,call:meter(call)):
                        return read(group['config'],database,request)
                return meter(operation)
            sql=FabricSqlChanges(group['identity'],group['config'],group['objects'],execute_sql)
            reader=IncrementalScanner(repo,sql,None,reconcile=catalog.refresh,observation_clock=clock)
            result['sql_collectors'].append(reader.run(config['estate'],at))
        result['container_schema_collectors']=[]
        for group in config.get('container_schemas',[]):
            from investigator.adapters.graph_container_schema import SqlContainerChanges
            from investigator.physical_reads import scope
            from fabric_sql_surface import read
            def retained_owner(owner):
                _,assets,sources,_=catalog.snapshot(config['estate']);mapping=asset_owners(assets)
                values=[a for a in assets if mapping[a['id']]==owner]
                return {'assets':values,'source_asset_ids':[x for x in sources if mapping[x]==owner]}
            def execute_schema(database,request):
                def operation():
                    with scope(lambda kind,call:meter(call)):
                        return read(group['config'],database,request)
                return meter(operation)
            sql=SqlContainerChanges(group['identity'],group['config'],group['owners'],retained_owner,execute_schema)
            reader=IncrementalScanner(repo,sql,None,
                reconcile=lambda estate,owner,at,payload:sql.reconcile(catalog,estate,owner,at,payload),observation_clock=clock)
            result['container_schema_collectors'].append(reader.run(config['estate'],clock()))
        result['coverage_gaps']=[
            {'capability':'runtime_query_monitoring','status':'UNAVAILABLE','reason':'Scheduled runtime-query monitoring collector is not implemented; no monitoring permission or data is inferred.'},
            {'capability':'refresh_pipeline_delta_history','status':'UNAVAILABLE','reason':'Scheduled refresh, run and Delta-history collectors are not implemented. Item/SQL modify dates describe definitions, not data freshness.'}]
        result.update(physical_requests=meter.used, approval=config['approval'], config_hash=sha(config),
            usage_before=meter.before,usage_after=meter.usage.snapshot())
        state.put('graph_scan_run', meter.owner, result)
        return result
    except BaseException as error:
        from investigator.adapters.metadata_error import safe_failure
        state.put('graph_scan_run', meter.owner, {'estate': config['estate'], 'observed_at': at,
            'status': 'FAILED', 'error_type': type(error).__name__, 'failure':safe_failure(error),'physical_requests': meter.used,
            'approval': config['approval'], 'config_hash': sha(config)})
        raise
    finally: meter.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args(); config = validate(json.loads(args.config.read_text(encoding='utf-8-sig')))
    result = execute(config) if args.apply else {'status': 'PLAN_ONLY', 'config_hash': sha(config),
        'schedule': '0 */6 * * *', 'owners': sum(len(c['owners']) for c in config.get('scans',[config])), 'approval': config['approval'],
        'requirements': ['Existing Container Apps Job; no new resource', 'Existing shared request accounts and reserve',
                         'Exact gateway grants and reader permissions; no automatic elevation',
                         'Operator-migrated graph tables', 'Owner-approved deployment and controlled change/revert']}
    with args.receipt.open('x', encoding='utf8') as handle: json.dump(result, handle, indent=2)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__': main()

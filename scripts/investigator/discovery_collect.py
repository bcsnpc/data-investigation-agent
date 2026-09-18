"""Bounded metadata collection for an approved workspace and SQL database.

Discovery never executes business queries or changes remote assets. Each collection
surface reports its own coverage; failed definitions preserve successful listings.
"""
import copy
import hashlib
import json
import time
from urllib.parse import quote
from uuid import UUID

from metadata_inventory import expand_definition, collect_sql
from metadata_protocol import pages
from metadata_connectors import FabricMetadataConnector, PowerBIMetadataConnector
from .onboarding import digest


class BudgetExceeded(RuntimeError):
    pass


class Collector:
    def __init__(self, config, transport, sql_reader, *, max_calls=160,
                 max_assets=20000, max_bytes=32*1024*1024, seconds=600, clock=time.monotonic):
        self.config, self.transport, self.sql_reader = config, transport, sql_reader
        self.max_calls, self.max_assets, self.max_bytes = max_calls, max_assets, max_bytes
        self.clock, self.deadline = clock, clock()+seconds
        self.calls = self.bytes = self.asset_bytes = 0
        self.assets, self.coverage, self.observations = {}, {}, []
        self.scope = None

    def charge(self):
        if self.clock() >= self.deadline or self.calls >= self.max_calls:
            raise BudgetExceeded('Discovery budget exhausted')
        self.calls += 1

    def call(self, *args, **kwargs):
        self.charge()
        result = self.transport(*args, **kwargs)
        self.bytes += len(json.dumps(result).encode())
        if self.bytes > self.max_bytes: raise BudgetExceeded('Metadata byte limit')
        return result

    def asset(self, identity, kind, name, source, metadata, parent=None):
        if identity in self.assets: raise ValueError('Duplicate discovery identity')
        if len(self.assets) >= self.max_assets: raise BudgetExceeded('Asset limit')
        raw = json.dumps(metadata, sort_keys=True, ensure_ascii=False)
        self.asset_bytes += len(raw.encode())
        if self.asset_bytes > self.max_bytes:raise BudgetExceeded('Expanded metadata byte limit')
        self.assets[identity] = {'id': identity, 'parent_id': parent, 'kind': kind,
            'name': name, 'source': source, 'metadata': copy.deepcopy(metadata),
            'content_hash': hashlib.sha256(raw.encode()).hexdigest(), 'coverage_scope': self.scope,
            'provenance': 'DISCOVERED'}
        return identity

    def observe(self, asset, capability, status, source, detail):
        self.observations.append({'asset_id': asset, 'capability': capability,
                                  'status': status, 'source': source, 'detail': detail})

    def attempt(self, scope, collect):
        before = set(self.assets)
        self.scope = scope
        try:
            result = collect()
            self.coverage[scope] = {'status': 'COMPLETE'}
            return result
        except Exception as exc:
            # No partial definition or partial listing can imply complete membership.
            for identity in set(self.assets)-before: del self.assets[identity]
            self.coverage[scope] = {'status': 'UNAVAILABLE', 'error_type': type(exc).__name__}
            return None

    def run(self):
        config = self.config; workspace = config['fabric']['workspace_id']
        root = 'fabric://'+workspace
        # Enumerate accessible workspaces, but persist only the approved root.
        def workspaces():
            found = [w for w in pages('workspaces', self.call) if w.get('id') == workspace]
            if len(found) != 1: raise PermissionError('Approved workspace not visible')
            self.asset(root, 'Workspace', found[0]['displayName'], 'workspaces', found[0])
        self.attempt(root+'/workspace', workspaces)
        fabric = FabricMetadataConnector(workspace, self.call, None)
        powerbi = PowerBIMetadataConnector(fabric)
        def listing():
            items = fabric.discover_assets()
            for item in items:
                identity = str(UUID(item['id']))
                self.asset(root+'/'+identity, item['type'], item['displayName'],
                           f'workspaces/{workspace}/items', item, root)
            return items
        items = self.attempt(root+'/items', listing) or []
        # REST datasetId can bind a report even when PBIR definition access is denied.
        def report_bindings():
            rows=pages(f'groups/{workspace}/reports', self.call, audience='powerbi')
            return {root+'/'+str(UUID(r['id'])):root+'/'+str(UUID(r['datasetId'])) for r in rows if r.get('datasetId')}
        bindings = self.attempt(root+'/report_bindings',report_bindings)
        self.report_bindings = {}
        self.report_bindings.update(bindings or {})
        for item in items:
            aid = root+'/'+item['id']; kind = item['type']
            if kind in ('SemanticModel', 'Report', 'Notebook', 'DataPipeline', 'CopyJob'):
                def definition(item=item, aid=aid, kind=kind):
                    parts = (powerbi if kind in ('SemanticModel','Report') else fabric).get_definition(item)
                    expand_definition(self, aid, kind, parts, aid+'/getDefinition')
                self.attempt(aid+'/definition', definition)
            if kind == 'Lakehouse':
                def tables(item=item, aid=aid):
                    endpoint=f"workspaces/{workspace}/lakehouses/{item['id']}/tables"
                    try:found=pages(endpoint, self.call, key='data')
                    except RuntimeError:
                        from onelake_metadata import collect
                        base=f"delta/{workspace}/{item['id']}/api/2.1/unity-catalog/"
                        found=collect(workspace,item['id'],item['displayName']+'.Lakehouse',
                            get=lambda path:self.call(base+path,audience='onelake')['text'])['tables']
                    for table in found:
                        name=(table.get('schemaName',table.get('schema_name',''))+'.'+table['name']).lstrip('.')
                        tid=aid+'/table/'+quote(name,safe='')
                        self.asset(tid,'LakehouseTable',name,endpoint,table,aid)
                        for column in table.get('columns') or []:
                            self.asset(tid+'/column/'+quote(column['name'],safe=''), 'LakehouseColumn',
                                       column['name'],endpoint,column,tid)
                self.attempt(aid+'/tables', tables)
                self.observe(aid,'column_schema','UNKNOWN',aid,'REST table listing may omit columns')
            if kind == 'Warehouse':
                self.coverage[aid+'/tables']={'status':'UNSUPPORTED',
                    'reason':'Warehouse item discovered; approved SQL endpoint catalog connection required'}
            if kind in ('DataPipeline','CopyJob','Notebook'):
                history=self.attempt(aid+'/runs', lambda item=item: fabric.get_refresh_history(item))
                if history is not None:self.observe(aid,'run_history','AVAILABLE',aid,history)
            if kind == 'SemanticModel':
                history=self.attempt(aid+'/refreshes', lambda item=item: powerbi.get_refresh_history(item))
                if history is not None:self.observe(aid,'refresh_history','AVAILABLE',aid,history)
        sql=config['sql']; sqlroot='sql://'+sql['server']+'/'+sql['database']
        def sql_catalog():
            self.charge()
            snapshot=self.sql_reader(sql['server'],sql['database'],sql['visibility_schema'])
            if (snapshot['server'].removeprefix('tcp:').split(',')[0].lower()!=sql['server'].lower()
                    or snapshot['database']!=sql['database']):raise ValueError('SQL catalog target differs')
            snapshot=copy.deepcopy(snapshot)
            # The old reader enumerates all visible objects: constrain the projection.
            snapshot['objects']=[o for o in snapshot['objects'] if o['schema_name']==sql['visibility_schema']]
            collect_sql(self,snapshot)
            self.asset(sqlroot+'/schema/'+quote(sql['visibility_schema'],safe=''),'SqlSchema',
                       sql['visibility_schema'],'Azure SQL sys catalog',{'name':sql['visibility_schema']},sqlroot)
            if not snapshot['permissions'] or not snapshot['permissions'][0]['can_view_definition']:
                raise PermissionError('Complete schema visibility unavailable')
        self.attempt(sqlroot+'/catalog',sql_catalog)
        return {'assets':list(self.assets.values()),'coverage':self.coverage,
                'observations':self.observations,'report_bindings':self.report_bindings,
                'calls':self.calls,'bytes':self.bytes,'profile_hash':digest(config)}

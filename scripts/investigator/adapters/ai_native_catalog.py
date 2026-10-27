"""Native query routes from retained discovery and declared endpoint responses.

No measure compiler or ticket expectation participates. Schema top-ups use the
existing reader-only catalog control, for graph-known objects on opened layers.
"""
from copy import deepcopy
from collections import defaultdict
from ..estate_graph_contract import digest


class NativeCatalog:
    def __init__(self, *, assets, graph_nodes, configuration, endpoint, sql_read, record, source_read=None):
        self.assets={a['id']:deepcopy(a) for a in assets if a.get('availability')=='CURRENT'}
        self.config=deepcopy(configuration)
        self.endpoint,self.sql_read,self.record=endpoint,sql_read,record
        self.source_read=source_read
        self.nodes=defaultdict(list)
        for node in graph_nodes:
            asset=node.get('properties',{}).get('asset_id')
            if asset in self.assets:self.nodes[asset].append(node['id'])
        self.routes={};self.ready=set();self.opened=defaultdict(set)
        grouped=defaultdict(list)
        for asset in self.assets.values():
            if asset['id'] in self.nodes and asset['kind'] in ('SqlObject','LakehouseTable','WarehouseTable','SemanticTable'):
                grouped[asset['parent_id']].append(asset)
        for parent,objects in grouped.items():
            container=self.assets.get(parent,{})
            kind=container.get('kind')
            route={'path_nodes':sorted({i for a in objects for i in self.nodes[a['id']]}),
                   'label':container.get('name',parent),'config':deepcopy(self.config),
                   'asset_ids':[a['id'] for a in objects], 'objects':[],
                   'container':parent,'discovery':[{'id':a['id'],'content_hash':a['content_hash']} for a in objects]}
            if kind=='SemanticModel':
                ws,model=parent.removeprefix('fabric://').split('/')
                route.update(kind='DAX',dialect='DAX',workspace=ws,model=model)
                members=[a for a in self.assets.values() if a['parent_id']==parent or
                         a['parent_id'] in route['asset_ids']]
                route['objects']=[{'id':a['id'],'kind':a['kind'],'name':a['name'],
                                   'parent_id':a['parent_id'],'metadata':a['metadata']} for a in members
                                  if a['kind'] in ('SemanticTable','SemanticColumn','Measure')]
                route['asset_ids']=[a['id'] for a in route['objects']]
            elif kind=='SqlDatabase':
                expected='sql://'+self.config['sql']['server']+'/'+self.config['sql']['database']
                if parent!=expected:continue
                route.update(kind='SOURCE_SQL',dialect='T-SQL',database=self.config['sql']['database'])
                route['objects']=[{'id':a['id'],'metadata':deepcopy(a['metadata'])} for a in objects]
            elif kind in ('Lakehouse','Warehouse'):
                route.update(kind='FABRIC_SQL',dialect='T-SQL')
                for asset in objects:
                    meta=asset['metadata'];name=meta['name']
                    schema=meta.get('schema_name')
                    if schema is None and '.' in name:schema,name=name.split('.',1)
                    route['objects'].append({'id':asset['id'],'metadata':{
                        'name':name,'schema_name':schema or 'dbo','type_desc':'USER_TABLE','columns':[]}})
            else:continue
            identity='native:'+digest(parent)[:20]
            self.routes[identity]=route
            if route['kind']!='FABRIC_SQL':self.ready.add(identity)

    def prepare(self, identity, nodes=None):
        if identity not in self.routes:raise ValueError('NATIVE_LAYER_NOT_DECLARED')
        route=self.routes[identity]
        selected={a['id'] for a in route['objects'] if nodes is None or set(nodes).intersection(self.nodes[a['id']])}
        if route['kind']=='DAX':selected={a['id'] for a in route['objects']}
        self.opened[identity].update(selected)
        def projected():
            result=deepcopy(route)
            result['objects']=[a for a in result['objects'] if a['id'] in self.opened[identity]]
            return result
        if route['kind']=='DAX' or (route['kind']=='SOURCE_SQL' and self.source_read is None):return projected()
        pending=[a for a in route['objects'] if a['id'] in self.opened[identity] and
                 (not a['metadata']['columns'] or route['kind']=='SOURCE_SQL' and not a['metadata'].get('fresh_native_schema'))]
        if not pending:return projected()
        parent=route['container'];container=self.assets[parent]
        if route['kind']=='FABRIC_SQL':
            workspace,item=parent.removeprefix('fabric://').split('/')
            # Resolve the exact native parent, never a similarly named endpoint.
            observed=self.endpoint(container)
            if observed.get('id')!=item:raise ValueError('NATIVE_ENDPOINT_PARENT_DIFFERS')
            props=observed.get('properties',{})
            if container['kind']=='Lakehouse':props=props.get('sqlEndpointProperties',{})
            if props.get('connectionString')!=route['config']['fabric']['sql_reader']['server']:
                raise ValueError('NATIVE_ENDPOINT_LEAVES_INSTALLED_READER')
            endpoint_id=props.get('id') if container['kind']=='Lakehouse' else item
            endpoint=self.assets.get('fabric://'+workspace+'/'+str(endpoint_id))
            if not endpoint or endpoint['kind'] not in ('SQLEndpoint','Warehouse'):
                raise ValueError('NATIVE_ENDPOINT_ABSENT_FROM_DISCOVERY')
            route['database']=endpoint['name']
            route['endpoint_evidence']=deepcopy(observed)
        else:props={'connectionString':route['config']['sql']['server']}
        from .binding_catalog import read_many
        for offset in range(0,len(pending),8):
            batch=pending[offset:offset+8]
            requests=[{'asset_id':a['id'],'surface':route['kind'],'connection':props['connectionString'],
                       'database':route['database'],'catalog':a} for a in batch]
            def execute(db,q):
                if route['kind']=='FABRIC_SQL':return self.sql_read(route['config'],db,q)
                return self.source_read(route['config'],dict(q,response_mode='records',require_read_only=True))
            result=read_many(route['config'],requests,execute=execute,attestation_required=False,surface=route['kind'])
            for obj in batch:
                columns,proof=result[obj['id']]
                obj['metadata']['columns']=columns
                obj['metadata']['fresh_native_schema']=True
                self.record({'event':'NATIVE_QUERY_SCHEMA','asset_id':obj['id'],'proof':proof})
        self.ready.add(identity)
        return projected()

    def context(self, path, intake):
        ids={n['id'] for n in path['nodes']}
        assets={a for a,nodes in self.nodes.items() if ids.intersection(nodes)}
        containers={self.assets[a]['parent_id'] for a in assets}
        definitions=[{'id':a['id'],'kind':a['kind'],'name':a['name'],'metadata':deepcopy(a['metadata']),
                      'content_hash':a['content_hash'],'provenance':a.get('provenance')}
                     for a in self.assets.values() if a['id'] in assets or
                     a['parent_id'] in containers and a['kind'] in ('SemanticRelationship','SemanticTable','DefinitionPart')]
        terminal=self.config.get('system_of_record')
        declaration={'declared':False,'reachable':False}
        if terminal:
            matching=[i for i,r in self.routes.items() if terminal['asset_id'] in r['asset_ids']]
            declaration={'declared':True,'reachable':terminal.get('reachable') is True and len(matching)==1,
                         'asset_id':terminal['asset_id'],'layer':matching[0] if len(matching)==1 else None}
        return {'retained_native_definitions':definitions,'system_of_record':declaration,
                'warnings':['Native comparisons are observational snapshots; aligned query-bound versions are not established.']}

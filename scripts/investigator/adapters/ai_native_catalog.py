"""Native query routes from retained discovery and declared endpoint responses.

No measure compiler or ticket expectation participates. Schema top-ups use the
existing reader-only catalog control, for graph-known objects on opened layers.
"""
from copy import deepcopy
from collections import defaultdict
import json
import re
from ..estate_graph_contract import digest


class NativeCatalog:
    def __init__(self, *, assets, graph_nodes, configuration, endpoint, sql_read, record, source_read=None):
        self.assets={a['id']:deepcopy(a) for a in assets if a.get('availability')=='CURRENT'}
        self.config=deepcopy(configuration)
        self.endpoint,self.sql_read,self.record=endpoint,sql_read,record
        self.source_read=source_read
        self.graph_nodes={n['id']:deepcopy(n) for n in graph_nodes}
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
        if route['kind']=='DAX':
            tables={a['id'] for a in route['objects'] if a['kind']=='SemanticTable' and
                    (nodes is None or set(nodes).intersection(self.nodes[a['id']]))}
            names={a['name'] for a in route['objects'] if a['id'] in tables}
            # Schema relationships belong in the context; unrelated model
            # tables do not. This does not select the investigative next step.
            relationships=[a['metadata'] for a in self.assets.values() if a['kind']=='SemanticRelationship' and a['parent_id']==route['container']]
            for _ in range(len(relationships)+1):
                before=set(names)
                for relationship in relationships:
                    if names.intersection({relationship.get('fromTable'),relationship.get('toTable')}):
                        names.update(t for t in (relationship.get('fromTable'),relationship.get('toTable')) if t)
                if names==before:break
            tables.update(a['id'] for a in route['objects'] if a['kind']=='SemanticTable' and a['name'] in names)
            selected={a['id'] for a in route['objects'] if a['id'] in tables or a.get('parent_id') in tables}
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
            result=read_many(route['config'],requests,execute=execute,attestation_required=False,surface=route['kind'],include_views=True)
            for obj in batch:
                columns,proof=result[obj['id']]
                obj['metadata']['columns']=columns
                obj['metadata']['fresh_native_schema']=True
                self.record({'event':'NATIVE_QUERY_SCHEMA','asset_id':obj['id'],'proof':proof})
        self.ready.add(identity)
        return projected()

    def candidate_details(self, catalog):
        catalog=deepcopy(catalog)
        roles={r['asset_id']:r['role'] for r in self.config.get('layer_roles',[])}
        for node in catalog['nodes']:
            asset=self.assets.get(node.get('properties',{}).get('asset_id'))
            if not asset:continue
            parent=self.assets.get(asset['parent_id'],{})
            node.setdefault('properties',{})['native_location']={
                'asset_id':asset['id'],'container':asset['parent_id'],
                'container_name':parent.get('name'),'role':roles.get(asset['id'])}
        return catalog

    def declared_continuations(self,path):
        """Literal partition + retained native endpoint ownership, never a label match."""
        result=[]
        for node in path['nodes']:
            table=self.assets.get(node.get('properties',{}).get('asset_id'),{})
            if table.get('kind')!='SemanticTable':continue
            model=table['parent_id'];parts=table['metadata'].get('partitions',[])
            if len(parts)!=1 or parts[0].get('mode')!='directLake':continue
            source=parts[0].get('source',{})
            if source.get('type')!='entity' or not isinstance(source.get('schemaName'),str) or not isinstance(source.get('entityName'),str):continue
            definitions=[a for a in self.assets.values() if a.get('parent_id')==model and a['kind']=='DefinitionPart' and a['name']=='model.bim']
            if len(definitions)!=1:continue
            definition=definitions[0]
            try:document=json.loads(definition['metadata']['content'])['model']
            except (ValueError,KeyError,TypeError):continue
            expressions=[e['expression'] for e in document.get('expressions',[]) if e.get('name')==source.get('expressionSource')]
            if len(expressions)!=1:continue
            expression=expressions[0];expression='\n'.join(expression) if isinstance(expression,list) else expression
            match=re.fullmatch(r'\s*let\s+([A-Za-z][A-Za-z0-9_]*)\s*=\s*Sql\.Database\(\s*"([^"\r\n]+)"\s*,\s*"([^"\r\n]+)"\s*\)\s+in\s+\1\s*',expression or '')
            if not match or match[2]!=self.config['fabric']['sql_reader']['server']:continue
            workspace=model.rsplit('/',1)[0];endpoint=workspace+'/'+match[3];roots=[];witnesses=[]
            native_endpoint=self.assets.get(endpoint,{})
            if native_endpoint.get('kind')=='Warehouse':roots.append(endpoint)
            for witness in self.assets.values():
                if witness['kind']!='NativeItemRelationMetadata' or witness.get('parent_id')!=model:continue
                meta=witness['metadata'];relation=meta.get('relation',{});target=self.assets.get(relation.get('target'),{})
                if (relation.get('source')==endpoint and relation.get('relation')=='NATIVE_CASCADEDELETE' and relation.get('provenance')=='DISCOVERED'
                    and target.get('kind')=='Lakehouse' and target.get('parent_id')==workspace
                    and meta.get('endpoint_asset_hash')==native_endpoint.get('content_hash')
                    and meta.get('container_asset_hash')==target.get('content_hash')
                    and any(e.get('scope')==model and e.get('source_api')=='fabric_item_relations_beta' for e in relation.get('evidence',[]))):
                    roots.append(target['id']);witnesses.append({'asset_id':witness['id'],'metadata':deepcopy(meta)})
            if len(set(roots))!=1:continue
            root=roots[0];physical=[]
            for candidate in self.assets.values():
                if candidate.get('parent_id')!=root:continue
                meta=candidate.get('metadata',{});schema=meta.get('schema_name','dbo');name=meta.get('name',candidate.get('name',''))
                if '.' in name:schema,name=name.split('.',1)
                if candidate['kind'] in ('LakehouseTable','WarehouseTable') and schema==source['schemaName'] and name==source['entityName']:
                    physical.append(candidate)
            if len(physical)!=1:continue
            ids=self.nodes.get(physical[0]['id'],[])
            if not ids:continue
            result.append({'confidence':'DECLARED','semantic_table':table['id'],'physical_table':physical[0]['id'],
                'graph_nodes':list(ids),'definition_asset':definition['id'],'definition_hash':definition['content_hash'],
                'partition_source':deepcopy(source),'literal_expression':expression,'native_ownership':witnesses,
                'qualification':'Declared route only; value agreement and aligned snapshots are not implied.'})
        return result

    def context(self, path, intake):
        ids={n['id'] for n in path['nodes']}
        assets={a for a,nodes in self.nodes.items() if ids.intersection(nodes)}
        containers={self.assets[a]['parent_id'] for a in assets}
        definitions=[{'id':a['id'],'kind':a['kind'],'name':a['name'],'metadata':deepcopy(a['metadata']),
                      'content_hash':a['content_hash'],'provenance':a.get('provenance')}
                     for a in self.assets.values() if a['id'] in assets or
                     a['parent_id'] in containers and a['kind'] in ('SemanticRelationship','SemanticTable','DefinitionPart')]
        opened=set().union(*self.opened.values()) if self.opened else set()
        semantic_tables={self.assets[i]['name'] for i in opened if self.assets.get(i,{}).get('kind')=='SemanticTable'}
        definitions=[a for a in definitions if a['kind']!='SemanticTable' or a['id'] in opened]
        for definition in definitions:
            if definition['kind']!='DefinitionPart' or definition['name']!='model.bim' or not semantic_tables:continue
            raw=definition['metadata'].get('content')
            try:document=json.loads(raw)
            except (ValueError,TypeError):continue
            model=document.get('model')
            if not isinstance(model,dict):continue
            model['tables']=[t for t in model.get('tables',[]) if t['name'] in semantic_tables]
            definition['metadata']['content']=json.dumps(document,ensure_ascii=False)
            definition['projection']={'kind':'PATH_TABLES_WITH_RELATED_SCHEMA','tables':sorted(semantic_tables),
                                      'original_content_hash':definition['content_hash'],
                                      'original_retained_unchanged':True}
        text='\n'.join(str(a['metadata'].get('content','')) for a in definitions if a['kind']=='DefinitionPart')
        references=[{'id':a['id'],'kind':a['kind'],'name':a['name'],'metadata':deepcopy(a['metadata'])}
                    for a in self.assets.values() if a['kind'] in ('SQLEndpoint','Lakehouse','Warehouse','SourceConnection')
                    and a['id'].rsplit('/',1)[-1] in text]
        terminal=self.config.get('system_of_record')
        declaration={'declared':False,'reachable':False}
        if terminal:
            matching=[i for i,r in self.routes.items() if terminal['asset_id'] in r['asset_ids']]
            declaration={'declared':True,'reachable':terminal.get('reachable') is True and len(matching)==1,
                         'asset_id':terminal['asset_id'],'layer':matching[0] if len(matching)==1 else None}
        return {'retained_native_definitions':definitions,'system_of_record':declaration,'native_definition_references':references,
                'warnings':['Native comparisons are observational snapshots; aligned query-bound versions are not established.']}

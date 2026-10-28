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
    @classmethod
    def from_graph(cls,graph,**ports):
        return cls(graph_nodes=graph.native_index()['nodes'],**ports)

    def __init__(self, *, assets, graph_nodes, configuration, endpoint, sql_read, record, source_read=None):
        from .native_catalog_projection import project
        self.assets,self.catalog_warnings=project(assets,graph_nodes)
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
            route={'path_nodes':sorted({i for a in objects for i in self.object_nodes(a['id'])}),
                   'label':container.get('name',parent),'config':deepcopy(self.config),
                   'asset_ids':[a['id'] for a in objects], 'objects':[],
                   'container':parent,'discovery':[{'id':a['id'],'content_hash':a['content_hash'],
                       **({'content_hash_basis':a['content_hash_basis']} if a.get('content_hash_basis') else {})} for a in objects]}
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

    def object_nodes(self,identity):
        return set(self.nodes[identity])|{node for a in self.assets.values() if a.get('parent_id')==identity for node in self.nodes[a['id']]}

    def associated_nodes(self,path):
        """Literal native containment, not a same-name dependency inference.

        A stored-column visual need not traverse a calculated dependency to
        its table. The small intake index omits columns, so attach its known
        table/model ancestors using retained native parent identities.
        """
        reached={n.get('properties',{}).get('asset_id') for n in path['nodes']}
        pending=list(reached);ancestors=set()
        while pending:
            identity=pending.pop();asset=self.assets.get(identity,{})
            parent=asset.get('parent_id')
            if parent and parent not in reached and parent not in ancestors:
                # A measure home table is storage ownership, not an input.
                # Keep its model ancestor without inventing a data dependency.
                if asset.get('kind')!='Measure':ancestors.add(parent)
                pending.append(parent)
        present={n['id'] for n in path['nodes']}
        return [deepcopy(n) for n in self.graph_nodes.values() if n['id'] not in present
                and n.get('kind') in ('TABLE','VIEW','MODEL')
                and n.get('properties',{}).get('asset_id') in ancestors]

    def prepare(self, identity, nodes=None):
        if identity not in self.routes:raise ValueError('NATIVE_LAYER_NOT_DECLARED')
        route=self.routes[identity]
        selected={a['id'] for a in route['objects'] if nodes is None or set(nodes).intersection(self.object_nodes(a['id']))}
        if route['kind']=='DAX':
            tables={a['id'] for a in route['objects'] if a['kind']=='SemanticTable' and
                    (nodes is None or set(nodes).intersection(self.object_nodes(a['id'])))}
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
                 (not a['metadata'].get('columns') or route['kind']=='SOURCE_SQL' and not a['metadata'].get('fresh_native_schema'))]
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

    def definition(self,node_id):
        """Retained producer-native content, no DAX INFO or write-scoped API."""
        node=self.graph_nodes.get(node_id,{})
        asset=self.assets.get(node.get('properties',{}).get('asset_id'))
        if asset is None:asset=self.assets.get(node.get('properties',{}).get('definition_source_id'))
        if not asset:return None
        meta=asset['metadata'];fields={k:deepcopy(meta[k]) for k in ('expression','definitions','content','computed_definition') if meta.get(k)}
        if not fields:return None
        return {'node':node_id,'asset_id':asset['id'],'name':asset['name'],'kind':asset['kind'],
            'retained_native_definition':fields,'content':next(iter(fields.values())) if len(fields)==1 and isinstance(next(iter(fields.values())),str) else json.dumps(fields,ensure_ascii=False),
            'projection':'NATIVE_FIELDS_ONLY_ORIGINAL_METADATA_RETAINED','content_hash':asset['content_hash'],
            'provenance':deepcopy(asset.get('provenance')),
            'basis':'RETAINED_NATIVE_DEFINITION','current_native_fetch_performed':False,
            'qualification':'Retained producer content; no claim of current deployment freshness or aligned values.'}

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
            def digest_matches(expected,asset):
                # Missing collector digests are bookkeeping gaps, not missing
                # native identities. Keep the literal relation as DECLARED and
                # label it; a supplied contradictory digest is still distinct.
                return expected is None or asset.get('content_hash_basis')=='DERIVED_RETAINED_METADATA_CANONICAL_JSON' or expected==asset.get('content_hash')
            for witness in self.assets.values():
                if witness['kind']!='NativeItemRelationMetadata' or witness.get('parent_id')!=model:continue
                meta=witness['metadata'];relation=meta.get('relation',{});target=self.assets.get(relation.get('target'),{})
                if (relation.get('source')==endpoint and relation.get('relation')=='NATIVE_CASCADEDELETE' and relation.get('provenance')=='DISCOVERED'
                    and target.get('kind')=='Lakehouse' and target.get('parent_id')==workspace
                    and digest_matches(meta.get('endpoint_asset_hash'),native_endpoint)
                    and digest_matches(meta.get('container_asset_hash'),target)
                    and any(e.get('scope')==model and e.get('source_api')=='fabric_item_relations_beta' for e in relation.get('evidence',[]))):
                    roots.append(target['id']);witnesses.append({'asset_id':witness['id'],'metadata':deepcopy(meta),
                        'inventory_digest_qualification':('Unavailable inventory digest; retained literal identity relation only.'
                            if any(a.get('content_hash_basis')=='DERIVED_RETAINED_METADATA_CANONICAL_JSON' for a in (native_endpoint,target))
                            or meta.get('endpoint_asset_hash') is None or meta.get('container_asset_hash') is None else
                            'Retained inventory digests matched; this is not a current query-bound attestation.')})
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
            ids=list(ids)
            semantic_columns=[self.assets.get(n.get('properties',{}).get('asset_id'),{}) for n in path['nodes']]
            source_columns={a['metadata'].get('sourceColumn',a.get('name')) for a in semantic_columns
                            if a.get('kind')=='SemanticColumn' and a.get('parent_id')==table['id'] and not a['metadata'].get('expression')}
            for column in self.assets.values():
                if column.get('parent_id')==physical[0]['id'] and column['kind'] in ('LakehouseColumn','WarehouseColumn') and column['name'] in source_columns:
                    ids.extend(self.nodes.get(column['id'],[]))
            column_bindings=[]
            for semantic in self.assets.values():
                if semantic.get('parent_id')!=table['id']or semantic['kind']!='SemanticColumn':continue
                source_name=semantic['metadata'].get('sourceColumn')
                physical_columns=[a for a in self.assets.values()if a.get('parent_id')==physical[0]['id']and a['kind']in ('LakehouseColumn','WarehouseColumn')and a['name']==source_name]
                if source_name and len(physical_columns)==1:column_bindings.append({'semantic_column':semantic['id'],'physical_column':physical_columns[0]['id'],'basis':'EXACT_PARTITION_SOURCE_COLUMN'})
            result.append({'confidence':'DECLARED','semantic_table':table['id'],'physical_table':physical[0]['id'],
                'column_bindings':column_bindings,
                'graph_nodes':list(ids),'definition_asset':definition['id'],'definition_hash':definition['content_hash'],
                'partition_source':deepcopy(source),'literal_expression':expression,'native_ownership':witnesses,
                'qualification':'Declared route only; value agreement and aligned snapshots are not implied.'})
        return [*result,*self.manifest_continuations(path,result)]

    def manifest_continuations(self,path,bridges):
        """Carry literal installation declarations, without inferring a join.

        Only an already reached delivery can open its declared source. Audit
        declarations accompany the producer, never become quantity boundaries.
        """
        estate=self.config.get('_estate',{})
        layers={l['id']:l for l in estate.get('layers',[])}
        resources={r['id']:r for r in estate.get('resources',[])}
        reached={n.get('properties',{}).get('asset_id') for n in path['nodes']}
        reached.update(b['physical_table'] for b in bridges if 'physical_table' in b)
        pending=list(estate.get('lineage',{}).get('bindings',[]));result=[]
        while pending:
            progress=False
            for binding in pending[:]:
                source=layers.get(binding['from_layer'],{}).get('asset_id')
                target=layers.get(binding['to_layer'],{}).get('asset_id')
                if target not in reached or source not in self.assets or not self.nodes.get(source):continue
                producers=[p for p in estate.get('pipelines',[]) if p['from_layer']==binding['from_layer'] and p['to_layer']==binding['to_layer']]
                node_ids=list(self.nodes[source]);declarations=[]
                for producer in producers:
                    ids=self.nodes.get(producer['producer_asset_id'],[])
                    node_ids.extend(ids)
                    audit=producer.get('audit',{})
                    declarations.append({**deepcopy(producer),'audit_resource':deepcopy(resources.get(audit.get('resource')))})
                result.append({'confidence':'DECLARED','basis':'ESTATE_MANIFEST_BINDING',
                    'source_asset':source,'delivery_asset':target,'graph_nodes':sorted(set(node_ids)),
                    'binding':deepcopy(binding),'producers':declarations,
                    'qualification':'Declared mapping only; compare native values and retained load evidence to establish a cause.'})
                reached.add(source);pending.remove(binding);progress=True
            if not progress:break
        return result

    def context(self, path, intake):
        ids={n['id'] for n in path['nodes']}
        assets={a for a,nodes in self.nodes.items() if ids.intersection(nodes)}
        assets.update(n.get('provenance',{}).get('source_id') for n in path['nodes'] if n.get('provenance',{}).get('source_id') in self.assets)
        containers={self.assets[a]['parent_id'] for a in assets}
        definitions=[{'id':a['id'],'kind':a['kind'],'name':a['name'],'metadata':deepcopy(a['metadata']),
                      'content_hash':a['content_hash'],'provenance':a.get('provenance'),
                      **({'content_hash_basis':a['content_hash_basis']} if a.get('content_hash_basis') else {})}
                     for a in self.assets.values() if a['id'] in assets or
                     a['parent_id'] in containers and a['kind'] in ('SemanticRelationship','SemanticTable','DefinitionPart')]
        # PBIR sibling visuals are not on the ticket path. Keep the selected
        # visual, page/global filters and model binding, with an index of the
        # omitted siblings; original retained definitions are never modified.
        siblings=[a for a in definitions if a['kind']=='DefinitionPart' and '/visuals/' in a['name']
                  and a['id'] not in assets and self.assets.get(self.assets[a['id']]['parent_id'],{}).get('kind')=='Report']
        sibling_ids={a['id'] for a in siblings}
        definitions=[a for a in definitions if a['id'] not in sibling_ids]
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
                'off_path_visual_definition_index':[{'id':a['id'],'name':a['name'],'content_hash':a['content_hash']} for a in siblings],
                'warnings':['Native comparisons are observational snapshots; aligned query-bound versions are not established.',
                    *self.catalog_warnings]}

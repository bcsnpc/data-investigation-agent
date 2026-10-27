"""Conservative static graph extraction from retained Microsoft definitions only.

This adapter never queries an estate, executes code, parses DAX as dependency
proof, or treats a same-name candidate as a verified binding.
"""
import ast
import hashlib
import json
import re
from urllib.parse import unquote
from .. import estate_graph_contract as c

KINDS={'Report':'REPORT','ReportPage':'PAGE','ReportVisual':'VISUAL','SemanticModel':'MODEL',
 'SemanticTable':'TABLE','SemanticColumn':'COLUMN','Measure':'MEASURE','SemanticRelationship':'RELATIONSHIP',
 'SqlObject':'TABLE','SqlColumn':'COLUMN','SqlDatabase':'SOURCE','Lakehouse':'SOURCE','Warehouse':'SOURCE',
 'LakehouseTable':'TABLE','LakehouseColumn':'COLUMN','WarehouseTable':'TABLE','WarehouseColumn':'COLUMN',
 'RefreshSchedule':'REFRESH_SCHEDULE','Notebook':'NOTEBOOK','DataPipeline':'PIPELINE','CopyJob':'PIPELINE'}


def walk(value,path=''):
    yield path,value
    if isinstance(value,dict):
        for key,item in value.items():yield from walk(item,path+'/'+str(key).replace('~','~0').replace('/','~1'))
    elif isinstance(value,list):
        for index,item in enumerate(value):yield from walk(item,path+'/'+str(index))


class StaticGraph:
    def __init__(self,estate,owner,observed_at,assets,definition_sink,*,source_asset_ids=(),partitioned=False,source_observations=None):
        self.estate,self.owner,self.at=estate,owner,c.timestamp(observed_at)
        self.assets={a['id']:a for a in assets if a.get('availability','CURRENT')=='CURRENT'}
        if len(self.assets)!=len([a for a in assets if a.get('availability','CURRENT')=='CURRENT']):raise ValueError('GRAPH_DUPLICATE_ASSET')
        for asset in self.assets.values():
            if 'content_hash' in asset:
                raw=json.dumps(asset.get('metadata',{}),sort_keys=True,ensure_ascii=False).encode()
                compact=json.dumps(asset.get('metadata',{}),sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
                # Historical Collector.asset used spaced JSON, while enrichment
                # used onboarding.digest's compact JSON. Verify either exact
                # historical serialization; never rewrite the retained hash.
                if asset['content_hash'] not in (hashlib.sha256(raw).hexdigest(),hashlib.sha256(compact).hexdigest()):
                    raise ValueError('GRAPH_RETAINED_METADATA_HASH_DIFFERS')
        self.sink=definition_sink;self.definitions={};self.nodes={};self.edges={};self.by_asset={};self.proofs={}
        self.sources=set(source_asset_ids)
        self.partitioned=partitioned
        self.source_observations={key:c.timestamp(value) for key,value in (source_observations or {}).items()}
        if not self.source_observations.keys()<=self.assets.keys():raise ValueError('GRAPH_OBSERVATION_ASSET_NOT_RETAINED')
        if not self.sources<=self.assets.keys():raise ValueError('GRAPH_SOURCE_DECLARATION_NOT_COLLECTED')

    def retain(self,raw):
        raw=raw.encode('utf8') if isinstance(raw,str) else raw
        identity=hashlib.sha256(raw).hexdigest()
        if identity not in self.definitions:
            reference=self.sink(raw)
            if (not isinstance(reference,dict) or set(reference)!={'sha256','bytes','uri'} or reference['sha256']!=identity
                    or reference['bytes']!=len(raw) or not isinstance(reference['uri'],str) or not reference['uri']):
                raise ValueError('GRAPH_DURABLE_DEFINITION_REFERENCE_REQUIRED')
            self.definitions[identity]=reference
        return self.definitions[identity]

    def proof(self,asset,raw=None,path='',*,span=None):
        if raw is None:raw=json.dumps(asset.get('metadata',{}),sort_keys=True,ensure_ascii=False)
        reference=self.retain(raw)
        return {'source':'STATIC_DEFINITION','source_id':asset['id'],'definition_hash':reference['sha256'],
                'observed_at':self.source_observations.get(asset['id'],self.at),'span':span or {'kind':'JSON_POINTER','path':path}}

    def asset_proof(self,asset):
        # Prefer an exact retained native part over a re-serialized expanded
        # child. Equality is checked; a convenient same-name part is not proof.
        report=self.ancestor(asset['id'],'Report')
        if report and asset['kind'] in ('Report','ReportPage','ReportVisual'):
            from .legacy_report import location
            for part in self.assets.values():
                if (part['kind']=='DefinitionPart' and part.get('parent_id')==report and part['name']=='report.json'
                        and asset['kind'] in ('ReportPage','ReportVisual')):
                    raw=part['metadata']['content'];pointer=location(json.loads(raw),asset['id'],report,asset.get('metadata',{}))
                    if pointer is not None:return self.proof(part,raw,path=pointer)
            matches=[]
            suffix={'Report':'definition/report.json','ReportPage':'/page.json','ReportVisual':'/visual.json'}[asset['kind']]
            for part in self.assets.values():
                if part['kind']!='DefinitionPart' or part.get('parent_id')!=report or not part['name'].endswith(suffix):continue
                try:
                    raw=part['metadata']['content']
                    if json.loads(raw)==asset.get('metadata',{}):matches.append((part,raw))
                except (KeyError,ValueError,TypeError):continue
            if len(matches)==1:return self.proof(matches[0][0],matches[0][1])
        return self.proof(asset)

    def legacy(self,asset):
        report=self.ancestor(asset['id'],'Report')
        return any(p['kind']=='DefinitionPart' and p.get('parent_id')==report and p['name']=='report.json' for p in self.assets.values())

    def add(self,kind,label,locator,proof,properties=None,*,confidence='DECLARED',unknown=None,owner=None):
        owner=owner or (self.item_owner(proof['source_id']) if self.partitioned else self.owner)
        identity=c.identity(self.estate,owner,kind,locator)
        value=c.node(identity,owner,kind,str(label),proof,
            properties={**(properties or {}),'definition':self.definitions[proof['definition_hash']]},confidence=confidence,unknown=unknown)
        prior=self.nodes.get(identity)
        if prior is not None and prior!=value:raise ValueError('GRAPH_NODE_IDENTITY_COLLISION')
        self.nodes[identity]=value;return identity

    def link(self,kind,source,target,proof,*,properties=None,confidence='DECLARED',unknown=None):
        owner=self.nodes[source]['owner'] if self.partitioned else self.owner
        identity=c.identity(self.estate,owner,kind,[source,target,proof['source_id'],proof['span']])
        self.edges[identity]=c.edge(identity,owner,kind,source,target,proof,properties=properties,confidence=confidence,unknown=unknown)
        return identity

    def item_owner(self,asset_id):
        """Ownership follows retained parent IDs, never labels or GUID guessing."""
        if asset_id not in self.assets:raise ValueError('GRAPH_OWNER_ASSET_MISSING')
        seen=set();current=asset_id
        while True:
            if current in seen:raise ValueError('GRAPH_OWNER_PARENT_CYCLE')
            seen.add(current);parent=self.assets[current].get('parent_id')
            if parent not in self.assets or self.assets[parent]['kind'] in ('Workspace','SourceConnection'):
                return current
            current=parent

    def gap(self,origin,reason,remedy,proof,*,kind='COMPUTED_FROM'):
        unknown={'reason':reason[:2048],'remedy':remedy[:2048]}
        # Equal gap wording at different source locations is not one declaration.
        # Keep each location so repeated unresolved references cannot collide or
        # erase evidence. Deliberately omit observation time/content hash: the
        # same declaration location keeps its identity across later revisions.
        target=self.add('BOUNDARY',reason[:200],[origin,reason,proof['source_id'],proof['span']],
            proof,confidence='UNKNOWN',unknown=unknown)
        self.link(kind,origin,target,proof,confidence='UNKNOWN',unknown=unknown);return target

    def ancestor(self,asset_id,kind):
        seen=set()
        while asset_id in self.assets and asset_id not in seen:
            seen.add(asset_id);asset=self.assets[asset_id]
            if asset['kind']==kind:return asset_id
            asset_id=asset.get('parent_id')
        return None

    def field(self,model,table,name,kind):
        candidates=[]
        for aid,asset in self.assets.items():
            if asset['kind']!=kind or asset['name']!=name:continue
            parent=self.assets.get(asset.get('parent_id'),{})
            if parent.get('name')==table and self.ancestor(aid,'SemanticModel')==model:candidates.append(aid)
        return self.by_asset[candidates[0]] if len(candidates)==1 and candidates[0] in self.by_asset else None

    def model_for_report(self,report):
        from .native_catalog_projection import native_parent
        declarations=[]
        metadata=self.assets[report].get('metadata',{})
        if isinstance(metadata.get('datasetId'),str):declarations.append(metadata['datasetId'])
        for asset in self.assets.values():
            if asset['kind']=='DefinitionPart' and asset.get('parent_id')==report and asset['name']=='definition.pbir':
                try:
                    definition=json.loads(asset['metadata']['content']);ref=definition.get('datasetReference',{})
                    if 'byPath' in ref:continue
                    connection=ref.get('byConnection',{}).get('connectionString','')
                    declarations+=re.findall(r'(?:^|;)\s*semanticmodelid\s*=\s*([^;]+)',connection,re.I)
                except (KeyError,TypeError,ValueError):continue
        values=set(v.strip().casefold() for v in declarations)
        candidates=[a['id'] for a in self.assets.values() if a['kind']=='SemanticModel' and
            native_parent(a)==native_parent(self.assets[report]) and a['id'].split('/')[-1].casefold() in values]
        return candidates[0] if len(values)==1 and len(candidates)==1 else None

    def fields(self,origin,value,model,proof):
        found=0
        aliases={entry.get('Name'):entry.get('Entity') for entry in value.get('From',[]) if isinstance(entry,dict)} if isinstance(value,dict) else {}
        for path,item in walk(value):
            if not isinstance(item,dict):continue
            for native,kind in (('Measure','Measure'),('Column','SemanticColumn')):
                member=item.get(native)
                if not isinstance(member,dict):continue
                reference=member.get('Expression',{}).get('SourceRef',{})
                table=reference.get('Entity',aliases.get(reference.get('Source')));name=member.get('Property')
                if not isinstance(table,str) or not isinstance(name,str):continue
                found+=1;at={**proof,'span':{'kind':'JSON_POINTER','path':proof['span'].get('path','')+path+'/'+native}}
                target=self.field(model,table,name,kind) if model else None
                if target:self.link('COMPUTED_FROM',origin,target,at)
                else:self.gap(origin,'Unresolved '+native+' reference '+table+'['+name+']',
                    'Collect the explicit report-model binding and a unique member in that model; do not select a same-name object elsewhere.',at)
        return found

    def filters(self,origin,value,model,proof,*,scope):
        found=[]
        for path,item in walk(value):
            if not isinstance(item,dict):continue
            # Native filter payloads include their predicate. A field-only
            # declaration remains a filter node with predicate_present=False.
            if 'filter' in item and isinstance(item['filter'],dict):
                predicate=item['filter'];location=path+'/filter'
                if isinstance(predicate.get('filter'),dict):continue
            elif path.endswith('/filterConfig') and isinstance(item.get('filters'),list):
                for index,declaration in enumerate(item['filters']):
                    if isinstance(declaration,dict) and 'filter' not in declaration:
                        at={**proof,'span':{'kind':'JSON_POINTER','path':proof['span'].get('path','')+path+'/filters/'+str(index)}}
                        fid=self.add('FILTER',declaration.get('name','Field-only filter'),[origin,at['span']],at,
                            {'scope':scope,'predicate_present':False,'hidden':declaration.get('isHidden')})
                        self.link('FILTERED_BY',origin,fid,at);self.fields(fid,declaration,model,at);found.append(fid)
                continue
            else:continue
            at={**proof,'span':{'kind':'JSON_POINTER','path':proof['span'].get('path','')+location}}
            fid=self.add('FILTER',item.get('name','Declared filter'),[origin,at['span']],at,
                {'scope':scope,'predicate_present':bool(predicate.get('Where') or predicate.get('where')),
                 'hidden':item.get('isHidden'),'predicate':predicate,'condition':'STORED_ALTERNATIVE' if scope=='bookmark' else 'SAVED_DEFAULT'})
            self.link('FILTERED_BY',origin,fid,at);self.fields(fid,predicate,model,at);found.append(fid)
        return found

    def build(self):
        # Expanded catalog nodes retain their own metadata provenance. Native
        # definition parts are processed separately and never assumed equivalent.
        for aid,asset in sorted(self.assets.items()):
            native=asset['kind'];kind=KINDS.get(native)
            if kind is None:continue
            meta=asset.get('metadata',{});proof=self.asset_proof(asset)
            if native=='ReportVisual' and meta.get('visual',{}).get('visualType')=='slicer':kind='SLICER'
            legacy=self.legacy(asset) if native in ('Report','ReportPage','ReportVisual') else False
            if legacy and native=='ReportVisual':
                from .legacy_report import object_json
                if object_json(meta['config']).get('singleVisual',{}).get('visualType')=='slicer':kind='SLICER'
            if native in ('SqlObject','WarehouseTable'):kind={'V':'VIEW','SQL_STORED_PROCEDURE':'PROCEDURE','P':'PROCEDURE','VIEW':'VIEW'}.get(meta.get('type',meta.get('type_desc')),kind)
            if native=='SemanticColumn' and meta.get('type')=='calculated':kind='CALCULATED_COLUMN'
            props={'asset_id':aid,'native_kind':native,'hidden':meta.get('isHidden',meta.get('visibility'))}
            if legacy:props['native_format']='PBIR_LEGACY'
            if 'content_hash' in asset:
                spaced=hashlib.sha256(json.dumps(meta,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
                props['retained_metadata_hash_encoding']='SORTED_JSON_SPACED' if asset['content_hash']==spaced else 'SORTED_JSON_COMPACT_LEGACY'
            if aid in self.sources or any(parent in self.sources for parent in self._parents(aid)):props['system_of_record']=True
            for key in ('dataType','sourceColumn','isActive','crossFilteringBehavior','securityFilteringBehavior'):
                if key in meta:props[key]=meta[key]
            label=asset['name']
            if native=='ReportVisual' and not legacy:
                # Use the title visible in the report, not PBIR's opaque visual
                # name. Reuse the existing literal-title reader; dynamic titles
                # are not guessed or evaluated here.
                from .report_predicates import display_names
                title_context={'reports':[{'report_definitions':[{'id':aid,
                    'metadata':{'content':json.dumps(meta)}}]}]}
                label=display_names(title_context,[aid]).get(aid,label)
            node=self.add(kind,label,['asset',aid],proof,props);self.by_asset[aid]=node;self.proofs[aid]=proof
        engine_covered=self.engine_dependencies()
        for aid,node in list(self.by_asset.items()):
            asset=self.assets[aid];parent=asset.get('parent_id');proof=self.proofs[aid];meta=asset.get('metadata',{})
            if parent in self.by_asset:self.link('CONTAINS',self.by_asset[parent],node,proof)
            if asset['kind'] in ('Report','ReportPage','ReportVisual'):
                report=self.ancestor(aid,'Report');model=self.model_for_report(report) if report else None
                if self.legacy(asset):
                    self.gap(node,'PBIR-Legacy structure retained; embedded query, filter and interaction semantics are not interpreted.',
                        'Use a supported explicit legacy semantic reader; do not treat this structural graph as complete visual lineage.',proof)
                    continue
                self.filters(node,meta,model,proof,scope={'Report':'report','ReportPage':'page','ReportVisual':'visual'}[asset['kind']])
                if asset['kind']=='ReportVisual':
                    references=self.fields(node,meta.get('visual',{}).get('query',{}),model,proof)
                    if not model:self.gap(node,'Explicit report-to-model binding is missing or ambiguous.',
                        'Collect definition.pbir with a unique model identifier in the same workspace.',proof)
                    elif not references:
                        self.gap(node,'No supported explicit field reference was found in the retained visual query.','Collect the visual query or a permitted runtime visual-query observation.',proof)
                if asset['kind']=='ReportPage':self.interactions(aid,meta,proof)
            if asset['kind'] in ('Measure','SemanticColumn') and ('expression' in meta or asset['kind']=='Measure') and node not in engine_covered:
                self.gap(node,'Engine-resolved expression dependencies have not been collected.',
                    'CALCDEPENDENCY needs model write permission and is unavailable to this read-only investigator; retain UNKNOWN or use a separately approved metadata source.',proof)
            if asset['kind']=='SemanticRelationship':self.relationship(aid,meta,proof)
            if asset['kind'] in ('SqlObject','WarehouseTable'):
                for index,definition in enumerate(meta.get('definitions',[])):
                    text=definition.get('definition') if isinstance(definition,dict) else None
                    if isinstance(text,str):self.sql(aid,text,self.proof(asset,text,span={'kind':'TEXT','start':0,'end':max(1,len(text))}))
        for asset in sorted(self.assets.values(),key=lambda a:a['id']):
            if asset['kind']!='DefinitionPart':continue
            parent=asset.get('parent_id');content=asset.get('metadata',{}).get('content');path=asset['name']
            if parent not in self.by_asset or not isinstance(content,str):continue
            proof=self.proof(asset,content,span={'kind':'TEXT','start':0,'end':max(1,len(content))}) if path.endswith(('.py','.sql','.m','.tmdl')) else self.proof(asset,content)
            try:
                if path=='model.bim':self.model_parts(parent,json.loads(content).get('model',{}),proof)
                elif path.endswith('.tmdl'):self.tmdl(parent,content,proof)
                elif path.endswith('.py'):self.notebook(parent,content,proof)
                elif path.endswith('.ipynb'):
                    doc=json.loads(content)
                    for index,cell in enumerate(doc.get('cells',[])):
                        if cell.get('cell_type')=='code':self.notebook(parent,''.join(cell.get('source',[])),{**proof,'span':{'kind':'JSON_POINTER','path':'/cells/'+str(index)+'/source'}})
                elif path.endswith('.sql'):self.sql(parent,content,proof)
                elif 'bookmark' in path.lower():
                    doc=json.loads(content);step=self.add('QUERY_STEP','Saved bookmark',[asset['id'],'bookmark'],proof,{'conditional':True})
                    self.link('CONTAINS',self.by_asset[parent],step,proof);self.filters(step,doc,self.model_for_report(parent),proof,scope='bookmark')
                elif path.endswith('.json') and self.assets[parent]['kind'] in ('CopyJob','DataPipeline'):
                    self.pipeline(parent,json.loads(content),proof)
                elif path.endswith('.m'):self.power_query(parent,content,proof)
            except (ValueError,KeyError,TypeError,SyntaxError) as error:
                self.gap(self.by_asset[parent],'Definition cannot be statically read: '+path+' ('+type(error).__name__+').',
                    'Retain the original definition and use a bounded interpreter with exact code-span citations; verify any inferred links.',proof)
        self.inherited_filters()
        if self.partitioned:
            partitions=[]
            for owner in sorted({n['owner'] for n in self.nodes.values()}):
                nodes=[n for n in self.nodes.values() if n['owner']==owner]
                edges=[e for e in self.edges.values() if e['owner']==owner]
                # Content hash excludes collection time but includes resolved
                # external identities. Rebinding changes the owning item hash.
                records=[]
                for item in nodes+edges:
                    item=json.loads(c.canonical(item));item['provenance'].pop('observed_at')
                    records.append(item)
                partitions.append(c.snapshot({'estate':self.estate,'owner':owner,
                    'definition_hash':c.digest({'records':records,'source_assets':sorted(self.sources)}),
                    'observed_at':self.at,'nodes':nodes,'edges':edges}))
            return partitions
        return c.snapshot({'estate':self.estate,'owner':self.owner,'definition_hash':c.digest({'definitions':sorted(self.definitions),'source_assets':sorted(self.sources),
                'assets':[(a['id'],a.get('parent_id'),a['kind'],a['name'],c.digest(a.get('metadata',{}))) for a in sorted(self.assets.values(),key=lambda x:x['id'])]}),
            'observed_at':self.at,'nodes':list(self.nodes.values()),'edges':list(self.edges.values())})

    def engine_dependencies(self):
        """Join engine rows by exact model/table/member identity, never DAX text."""
        from .graph_dependencies import dependency_edges
        covered=set()
        for asset in sorted(self.assets.values(),key=lambda a:a['id']):
            if asset['kind']!='EngineDependencyMetadata':continue
            model=asset.get('parent_id');meta=asset.get('metadata',{});result=meta.get('result',{})
            if model not in self.by_asset or result.get('request',{}).get('kind')!='CALCULATIONS':continue
            proof=self.proof(asset)
            pins={hashlib.sha256(a['metadata']['content'].encode()).hexdigest() for a in self.assets.values()
                if a['kind']=='DefinitionPart' and a.get('parent_id')==model and a['name']=='model.bim'}
            request=result.get('request',{}).get('target',{})
            parts=model.split('/')
            if (pins!={meta.get('model_definition_hash')} or len(parts)!=4 or
                    request!={'workspace':parts[-2],'model':parts[-1]} or
                    meta.get('model_name')!=self.assets[model]['name']):
                self.gap(self.by_asset[model],'Engine dependency observation does not bind the retained model definition.',
                    'Collect dependency metadata and the exact model definition under one declared model identity.',proof);continue
            bindings={};expected=[]
            for aid,node in self.by_asset.items():
                item=self.assets[aid]
                if self.ancestor(aid,'SemanticModel')!=model:continue
                kind={'Measure':'MEASURE','SemanticColumn':'COLUMN','SemanticTable':'TABLE'}.get(item['kind'])
                if kind is None:continue
                table=self.assets.get(item.get('parent_id'),{}).get('name') if kind!='TABLE' else item['name']
                native=(kind,table,item['name'])
                if item['kind']=='SemanticColumn' and item.get('metadata',{}).get('expression'):
                    native=('CALC_COLUMN',table,item['name'])
                if native in bindings:raise ValueError('GRAPH_DEPENDENCY_MEMBER_AMBIGUOUS')
                bindings[native]=node
                if kind=='MEASURE' or native[0]=='CALC_COLUMN':expected.append(native)
            got=dependency_edges(result,estate=self.estate,owner=self.item_owner(model) if self.partitioned else self.owner,
                model=meta['model_name'],bindings=bindings,expected=expected,definition_hash=meta['model_definition_hash'],
                observed_at=self.source_observations.get(asset['id'],self.at),definition_sink=self.retain)
            for edge in got['edges']:self.edges[edge['id']]=edge
            for key in got['covered']:covered.add(bindings[tuple(key)])
            for gap in got['gaps']:self.gap(self.by_asset[model],gap['reason'],gap['remedy'],proof)
        return covered

    def _parents(self,aid):
        seen=set()
        while aid in self.assets:
            aid=self.assets[aid].get('parent_id')
            if aid in seen:break
            seen.add(aid);yield aid

    def inherited_filters(self):
        direct=list(self.edges.values())
        for aid,node in self.by_asset.items():
            if self.assets[aid]['kind']!='ReportVisual':continue
            for parent in self._parents(aid):
                ancestor=self.by_asset.get(parent)
                for edge in direct:
                    if edge['source']==ancestor and edge['kind']=='FILTERED_BY':
                        self.link('FILTERED_BY',node,edge['target'],edge['provenance'],properties={'inherited_from':ancestor})

    def interactions(self,page,metadata,proof):
        visuals={a.get('metadata',{}).get('name'):self.by_asset[aid] for aid,a in self.assets.items()
            if a.get('parent_id')==page and a['kind']=='ReportVisual' and aid in self.by_asset}
        for index,item in enumerate(metadata.get('visualInteractions',[])):
            at={**proof,'span':{'kind':'JSON_POINTER','path':'/visualInteractions/'+str(index)}}
            node=self.add('INTERACTION','Declared visual interaction',[page,index],at,{'type':item.get('type')})
            self.link('CONTAINS',self.by_asset[page],node,at)
            source,target=visuals.get(item.get('source')),visuals.get(item.get('target'))
            if source and target:self.link('INTERACTS_WITH',source,target,at,properties={'type':item.get('type'),'interaction':node})
            else:self.gap(node,'Interaction endpoint is missing or ambiguous.','Collect all visuals on this page with their native names.',at)

    def relationship(self,aid,value,proof):
        model=self.ancestor(aid,'SemanticModel');node=self.by_asset[aid]
        for prefix in ('from','to'):
            target=self.field(model,value.get(prefix+'Table'),value.get(prefix+'Column'),'SemanticColumn')
            if target:self.link('JOINED_VIA',node,target,proof,properties={'endpoint':prefix,'active':value.get('isActive'),'direction':value.get('crossFilteringBehavior')})
            else:self.gap(node,'Relationship '+prefix+' endpoint is unresolved.','Collect the exact referenced model table and column.',proof,kind='JOINED_VIA')

    def model_parts(self,model,value,proof):
        for index,role in enumerate(value.get('roles',[])):
            at={**proof,'span':{'kind':'JSON_POINTER','path':'/model/roles/'+str(index)}}
            node=self.add('SECURITY_ROLE',role.get('name','Unnamed role'),[model,'role',index],at,{'model_role':True})
            self.link('FILTERED_BY',self.by_asset[model],node,at)
            for number,permission in enumerate(role.get('tablePermissions',[])):
                expression=permission.get('filterExpression')
                if expression is not None:
                    fid=self.add('FILTER','Role table filter',[model,'role',index,number],at,
                        {'scope':'RLS','table':permission.get('name'),'expression':expression,'predicate_present':True,'runtime_identity_unknown':True})
                    self.link('FILTERED_BY',node,fid,at)
        for index,table in enumerate(value.get('tables',[])):
            if any(p.get('source',{}).get('type')=='entity' for p in table.get('partitions',[])):
                self.entity_partition(model,value,table,index,proof)
            for number,partition in enumerate(table.get('partitions',[])):
                source=partition.get('source',{});expression=source.get('expression')
                if isinstance(expression,list):expression='\n'.join(expression)
                if source.get('type')=='m' and isinstance(expression,str):
                    at={**proof,'span':{'kind':'JSON_POINTER','path':f'/model/tables/{index}/partitions/{number}/source/expression'}}
                    self.power_query(model,expression,at)
            if table.get('calculationGroup') is not None:
                at={**proof,'span':{'kind':'JSON_POINTER','path':f'/model/tables/{index}/calculationGroup'}}
                node=self.add('CALCULATION_GROUP',table['name'],[model,'calculationGroup',index],at)
                self.link('CONTAINS',self.by_asset[model],node,at)
                self.gap(node,'Calculation-group dependencies need engine resolution.','Collect INFO.CALCDEPENDENCY and the selected calculation item context.',at)
            for number,column in enumerate(table.get('columns',[])):
                if any(p.get('name')=='ParameterMetadata' for p in column.get('extendedProperties',[])):
                    at={**proof,'span':{'kind':'JSON_POINTER','path':f'/model/tables/{index}/columns/{number}'}}
                    node=self.add('FIELD_PARAMETER',column['name'],[model,'fieldParameter',index,number],at)
                    self.link('CONTAINS',self.by_asset[model],node,at)
                    self.gap(node,'Field-parameter selection is dynamic.','Resolve the selected field from retained/report context before traversing its dependency.',at)

    def entity_partition(self,model,value,table,index,proof):
        """Only literal DirectLake declarations bind; no same-label container search."""
        # field() resolves columns by their parent; tables need their model parent.
        matches=[aid for aid,a in self.assets.items() if a['kind']=='SemanticTable'
                 and a.get('parent_id')==model and a['name']==table.get('name')]
        origin=self.by_asset.get(matches[0]) if len(matches)==1 else None
        if origin is None:return
        at={**proof,'span':{'kind':'JSON_POINTER','path':f'/model/tables/{index}/partitions'}}
        def refuse(reason):
            self.gap(origin,'DirectLake bridge unresolved: '+reason,
                'Collect a unique literal expression source, exact container/endpoint binding and physical member catalog.',at)
        partitions=table.get('partitions',[])
        if len(partitions)!=1:return refuse('multiple partitions do not declare one physical source.')
        part=partitions[0];source=part.get('source',{})
        if part.get('mode')!='directLake' or source.get('type')!='entity':
            return refuse('entity partition is not DirectLake.')
        name=source.get('expressionSource')
        expressions=[(i,e) for i,e in enumerate(value.get('expressions',[])) if e.get('name')==name]
        if not isinstance(name,str) or len(expressions)!=1:return refuse('expressionSource is absent or ambiguous.')
        expression_index,expression=expressions[0];raw=expression.get('expression')
        if isinstance(raw,list):raw='\n'.join(raw)
        # Deliberately small M grammar. Aliases are captured, never interpreted.
        token=r'"((?:[^"]|"")*)"'
        pattern=r'\s*let\s+([A-Za-z_][A-Za-z_0-9]*)\s*=\s*Sql\.Database\(\s*'+token+r'\s*,\s*'+token+r'\s*\)\s+in\s+\1\s*'
        match=re.fullmatch(pattern,raw or '') if expression.get('kind')=='m' else None
        if not match:return refuse('expression is not a supported literal Sql.Database source.')
        server,catalog=(v.replace('""','"') for v in match.groups()[1:])
        import uuid
        try:catalog=str(uuid.UUID(catalog))
        except (ValueError,TypeError):return refuse('catalog is not an explicit container or endpoint identifier.')
        workspace=model.rsplit('/',1)[0]
        containers=[]
        # Reuse the legacy resolver's exact native endpoint->Lakehouse witness.
        # A display name is never a scope. These observations are independently
        # retained, hash-pinned item relations, not relationships proposed by a
        # model or inferred from equal container labels.
        endpoint_id=workspace+'/'+catalog
        endpoint_asset=self.assets.get(endpoint_id)
        native_relations=[]
        if endpoint_asset and endpoint_asset['kind']=='SQLEndpoint':
            for evidence in self.assets.values():
                if evidence['kind']!='NativeItemRelationMetadata' or evidence.get('parent_id')!=model:continue
                metadata=evidence.get('metadata',{});relation=metadata.get('relation',{})
                if relation.get('source')!=endpoint_id or relation.get('relation')!='NATIVE_CASCADEDELETE':continue
                if (relation.get('provenance')!='DISCOVERED' or not re.fullmatch('[a-f0-9]{64}',metadata.get('context_hash',''))
                        or not any(e.get('scope')==model and e.get('source_api')=='fabric_item_relations_beta'for e in relation.get('evidence',[]))):continue
                target=self.assets.get(relation.get('target'))
                if not target or target['kind']!='Lakehouse' or target.get('parent_id')!=workspace:continue
                native_endpoint=endpoint_asset.get('metadata',{})
                if (native_endpoint.get('id')!=catalog or native_endpoint.get('workspaceId')!=workspace.split('/')[-1]
                        or native_endpoint.get('type')!='SQLEndpoint'):continue
                for recorded,current in ((metadata.get('endpoint_asset_hash'),endpoint_asset.get('content_hash')),
                                         (metadata.get('container_asset_hash'),target.get('content_hash'))):
                    if recorded and current and recorded!=current:
                        return refuse('native item-relation asset hashes differ from the retained context.')
                if metadata.get('observed_at') and c.timestamp(metadata['observed_at'])>self.at:
                    return refuse('native item-relation observation is in the future.')
                native_relations.append((target['id'],self.proof(evidence)))
            if len({target for target,_ in native_relations})>1:
                return refuse('native endpoint ownership relations conflict.')
            containers.extend(native_relations)
        for aid,a in self.assets.items():
            if a['kind'] not in ('Warehouse','Lakehouse') or aid.rsplit('/',1)[0]!=workspace:continue
            meta=a.get('metadata',{})
            if a['kind']=='Warehouse' and aid.rsplit('/',1)[-1].lower()==catalog:
                containers.append((aid,self.asset_proof(a)))
            if a['kind']=='Lakehouse':
                observations=[]
                if meta.get('properties',{}).get('sqlEndpointProperties'):observations.append((meta,a))
                for observation in self.assets.values():
                    if observation['kind']!='LakehouseEndpointMetadata':continue
                    data=observation.get('metadata',{})
                    if data.get('request')=={'workspace':workspace.split('/')[-1],'lakehouse':aid.split('/')[-1]}:
                        observations.append((data.get('response',{}),observation))
                routes={(r.get('properties',{}).get('sqlEndpointProperties',{}).get('id'),
                         r.get('properties',{}).get('sqlEndpointProperties',{}).get('connectionString')) for r,_ in observations}
                if len(routes)>1:return refuse('retained endpoint declarations conflict for a container.')
                if any(aid==target for target,_ in native_relations) and routes and (catalog,server)not in routes:
                    return refuse('native item relation conflicts with retained endpoint server or identity.')
                for response,evidence in observations:
                    endpoint=response.get('properties',{}).get('sqlEndpointProperties',{})
                    if (response.get('id')==aid.split('/')[-1] and response.get('workspaceId')==workspace.split('/')[-1]
                            and response.get('type')=='Lakehouse' and endpoint.get('id')==catalog
                            and endpoint.get('connectionString')==server):
                        binding_proof=self.proof(evidence)
                        if evidence['kind']=='LakehouseEndpointMetadata' and evidence.get('metadata',{}).get('observed_at'):
                            binding_proof['observed_at']=c.timestamp(evidence['metadata']['observed_at'])
                            if binding_proof['observed_at']>self.at:return refuse('endpoint observation is in the future.')
                        containers.append((aid,binding_proof))
        identities={item[0] for item in containers}
        if len(identities)!=1:return refuse('exact container/endpoint binding is absent or ambiguous.')
        container=next(iter(identities));container_proof=next(p for aid,p in containers if aid==container)
        schema,entity=source.get('schemaName'),source.get('entityName')
        if not isinstance(schema,str) or not isinstance(entity,str):return refuse('schema or entityName is absent.')
        physical=[]
        for aid,a in self.assets.items():
            if a.get('parent_id')!=container:continue
            meta=a.get('metadata',{})
            if a['kind']=='WarehouseTable' and a['name']==schema+'.'+entity:physical.append(aid)
            if a['kind']=='LakehouseTable':
                # A retained OneLake URI binds the physical path and schema. A
                # legacy Tables/entity path exposes dbo; Tables/schema/entity
                # is schema-enabled. Neither uses the container display name.
                location=meta.get('location','')
                prefix='abfss://'+workspace.split('/')[-1]+'@onelake.dfs.fabric.microsoft.com/'+container.split('/')[-1]+'/Tables/'
                if location.startswith(prefix):
                    tail=unquote(location[len(prefix):]).strip('/').split('/')
                    expected=['dbo',tail[0]] if len(tail)==1 else tail
                    if expected==[schema,entity]:physical.append(aid)
        if len(physical)!=1:return refuse('physical schema/entity is absent or ambiguous in the bound container.')
        physical=physical[0]
        declaration={'server':server,'catalog_id':catalog,'schema':schema,'entity':entity,
            'expression_source':name,'expression_pointer':f'/model/expressions/{expression_index}',
            'container_asset_id':container,'container_binding':container_proof,
            'container_bindings':[p for aid,p in containers if aid==container],
            'physical_definition':self.asset_proof(self.assets[physical]),'binding_kind':'DIRECTLAKE_ENTITY'}
        self.link('COMPUTED_FROM',origin,self.by_asset[physical],at,properties=declaration)
        for number,column in enumerate(table.get('columns',[])):
            target=self.field(model,table['name'],column.get('name'),'SemanticColumn')
            if target is None or column.get('type')=='calculated' or column.get('expression') is not None:continue
            column_at={**proof,'span':{'kind':'JSON_POINTER','path':f'/model/tables/{index}/columns/{number}/sourceColumn'}}
            source_column=column.get('sourceColumn')
            candidates=[aid for aid,a in self.assets.items() if a.get('parent_id')==physical
                and a['kind'] in ('WarehouseColumn','LakehouseColumn') and a['name']==source_column]
            if not isinstance(source_column,str) or len(candidates)!=1:
                self.gap(target,'DirectLake sourceColumn is absent or ambiguous: '+str(source_column),
                    'Collect the exact physical column under the bound table; never match the semantic display name.',column_at)
            else:
                self.link('COMPUTED_FROM',target,self.by_asset[candidates[0]],column_at,
                    properties={**declaration,'source_column':source_column,
                        'physical_column_definition':self.asset_proof(self.assets[candidates[0]])})

    def tmdl(self,parent,content,proof):
        """Read declaration headers and retained spans, never interpret DAX."""
        table=None;found=0
        pattern=re.compile(r"(?m)^(\s*)(table|measure|column|relationship|role|calculationGroup)\s+('(?:''|[^'])*'|[^=\r\n]+?)(?:\s*=|\s*$)")
        for match in pattern.finditer(content):
            native=match.group(2);label=match.group(3).strip().strip("'").replace("''", "'")
            kind={'table':'TABLE','measure':'MEASURE','column':'COLUMN','relationship':'RELATIONSHIP','role':'SECURITY_ROLE','calculationGroup':'CALCULATION_GROUP'}[native]
            at={**proof,'span':{'kind':'TEXT','start':match.start(),'end':match.end()}}
            node=self.add(kind,label,[proof['source_id'],native,label],at,{'native_format':'TMDL','model_id':parent,'table_name':self.nodes.get(table,{}).get('label')})
            self.link('CONTAINS',table or self.by_asset[parent],node,at);found+=1
            if native=='table':table=node
            if native in ('measure','relationship','calculationGroup'):
                self.gap(node,'Engine-resolved TMDL dependencies have not been collected.','Collect INFO.CALCDEPENDENCY and INFO.VIEW.RELATIONSHIPS for this model.',at)
        if not found:self.gap(self.by_asset[parent],'No supported TMDL declarations were found.','Retain the full definition and add a parser for its declared form.',proof)

    def power_query(self,parent,content,proof):
        # Captures every syntactically named let step with its exact code span.
        # Dataflow/source resolution requires a proper M interpreter; assigning
        # every step to the previous one would invent dependencies on branches.
        matches=list(re.finditer(r'(?m)(?:^|[,\r\n])\s*(#"[^"]+"|[A-Za-z_][\w ]*)\s*=\s*',content))
        for index,match in enumerate(matches):
            end=matches[index+1].start() if index+1<len(matches) else len(content)
            expression=content[match.end():end].strip();label=match.group(1).strip()
            at={**proof,'span':{'kind':'TEXT','start':match.start(),'end':max(match.end(),end)}} if proof['span']['kind']=='TEXT' else proof
            node=self.add('QUERY_STEP',label,[proof['source_id'],proof['span'],'m',index],at,{'language':'M','expression':expression})
            self.link('CONTAINS',self.by_asset[parent],node,at)
            if re.match(r'Table\.SelectRows\s*\(',expression):
                fid=self.add('FILTER','Power Query row filter',[node,'filter'],at,{'scope':'transformation','predicate_present':True,'expression':expression})
                self.link('FILTERED_BY',node,fid,at)
            self.gap(node,'Power Query step source and expression semantics are not yet resolved.','Use a retained-definition interpreter with exact M spans; verify any proposed column mappings.',at)
        if not matches:self.gap(self.by_asset[parent],'Power Query declaration form is unsupported.','Retain and interpret the exact M expression; do not infer a source from its label.',proof)

    def sql(self,parent,content,proof):
        import sqlglot
        from sqlglot import exp
        statements=sqlglot.parse(content,read='tsql')
        if len(statements)!=1:
            self.gap(self.by_asset[parent],'SQL has multiple statements or procedural control flow.','Interpret its exact code spans and verify each proposed mapping; static SELECT lineage does not cover it.',proof);return
        tree=statements[0]
        if isinstance(tree,exp.Create):tree=tree.expression
        if not isinstance(tree,exp.Select) or tree.args.get('with_') or tree.find(exp.Star) or len(list(tree.find_all(exp.Select)))!=1:
            self.gap(self.by_asset[parent],'SQL is not a single explicit-column SELECT supported by the static reader.',
                'Retain procedural/CTE/star expansion semantics and propose exact column mappings with code-span evidence.',proof);return
        database=self.assets[parent].get('parent_id');tables={}
        for table in tree.find_all(exp.Table):
            qualified=(table.db+'.' if table.db else '')+table.name
            candidates=[aid for aid,a in self.assets.items() if a['kind'] in ('SqlObject','WarehouseTable') and a.get('parent_id')==database and a['name']==qualified]
            if table.catalog or len(candidates)!=1:
                self.gap(self.by_asset[parent],'SQL source is unresolved in its declared database: '+table.sql(dialect='tsql'),
                    'Collect that exact qualified object under the connection named by this definition.',proof);continue
            tables[table.alias_or_name]=candidates[0]
            self.link('COMPUTED_FROM',self.by_asset[parent],self.by_asset[candidates[0]],proof)
        def resolve(column):
            options=[tables[column.table]] if column.table in tables else list(tables.values()) if not column.table else []
            matches=[aid for aid,a in self.assets.items() if a['kind'] in ('SqlColumn','WarehouseColumn') and a.get('parent_id') in options and a['name']==column.name]
            return self.by_asset[matches[0]] if len(matches)==1 else None
        for index,projection in enumerate(tree.expressions):
            label=projection.alias_or_name
            if not label:
                self.gap(self.by_asset[parent],'SQL output expression has no stable column name.','Retain an explicit output-column declaration.',proof);continue
            matches=[aid for aid,a in self.assets.items() if a['kind'] in ('SqlColumn','WarehouseColumn') and a.get('parent_id')==parent and a['name']==label]
            target=self.by_asset[matches[0]] if len(matches)==1 else self.add('CALCULATED_COLUMN',label,[parent,'sql-output',label],proof)
            self.link('CONTAINS',self.by_asset[parent],target,proof)
            for column in projection.find_all(exp.Column):
                source=resolve(column)
                if source:self.link('COMPUTED_FROM',target,source,proof)
                else:self.gap(target,'SQL column reference is unresolved or ambiguous: '+column.sql(dialect='tsql'),
                    'Collect the referenced schema or qualify the column to its declared table.',proof)
        for index,clause in enumerate([*tree.find_all(exp.Where),*tree.find_all(exp.Join)]):
            join=isinstance(clause,exp.Join)
            node=self.add('QUERY_STEP' if join else 'FILTER','SQL join' if join else 'SQL row filter',[parent,'sql-clause',index],proof,
                {'expression':clause.sql(dialect='tsql'),'scope':'transformation','predicate_present':True})
            self.link('JOINED_VIA' if join else 'FILTERED_BY',self.by_asset[parent],node,proof)
            for column in clause.find_all(exp.Column):
                source=resolve(column)
                if source:self.link('COMPUTED_FROM',node,source,proof)
                else:self.gap(node,'SQL condition column is unresolved: '+column.sql(dialect='tsql'),
                    'Collect the exact condition-column metadata in this database.',proof)

    def notebook(self,parent,content,proof):
        from .graph_code_columns import attach_notebook
        from ..code_static import Unsupported
        try:attach_notebook(self,parent,content,proof)
        except (Unsupported,KeyError,TypeError,IndexError) as error:
            self.gap(self.by_asset[parent],'Bounded notebook column extraction stopped: '+str(error),
                'Retain the unresolved exact code span; use a bounded interpreter or collect the missing schema.',proof)
        tree=ast.parse(content);found=0;lines=content.splitlines(keepends=True)
        offsets=[0]
        for line in lines:offsets.append(offsets[-1]+len(line))
        for call in ast.walk(tree):
            if not isinstance(call,ast.Call) or not isinstance(call.func,ast.Attribute):continue
            method=call.func.attr
            if method not in ('sql','table','load','filter','where','join','saveAsTable','save'):continue
            found+=1;start=offsets[call.lineno-1]+call.col_offset;end=offsets[call.end_lineno-1]+call.end_col_offset
            at={**proof,'span':{'kind':'TEXT','start':start,'end':end}} if proof['span']['kind']=='TEXT' else proof
            step=self.add('QUERY_STEP',method,[proof['source_id'],proof['span'],start,end],at,{'language':'PYTHON','call':method})
            self.link('CONTAINS',self.by_asset[parent],step,at)
            if method in ('filter','where'):
                argument=ast.get_source_segment(content,call.args[0]) if call.args else None
                unknown={'reason':'The filter-call receiver has not been established as a tabular frame.','remedy':'Resolve the notebook dataflow and receiver type from retained code, then verify its effect.'}
                fid=self.add('FILTER','Notebook filter call',[step,'filter'],at,{'expression':argument,'predicate_present':argument is not None,'scope':'transformation'},confidence='UNKNOWN',unknown=unknown)
                self.link('FILTERED_BY',step,fid,at,confidence='UNKNOWN',unknown=unknown)
            self.gap(step,'Notebook call dataflow and bound object identity are not statically established.',
                'Use a bounded code interpreter with this exact span and declared source/destination identities; verify its inferred edges.',at)
        if not found:self.gap(self.by_asset[parent],'Notebook source has no supported static data operation.','Retain the code and interpret unsupported operations without executing it.',proof)

    def pipeline(self,parent,doc,proof):
        activities=doc.get('properties',{}).get('activities',doc.get('activities',[]))
        if self.assets[parent]['kind']=='CopyJob':activities=[{'name':self.assets[parent]['name'],'type':'Copy','typeProperties':doc.get('properties',{})}]
        if not activities:
            self.gap(self.by_asset[parent],'Pipeline activity definitions are missing.','Collect the complete pipeline definition through the reader metadata route.',proof);return
        for index,activity in enumerate(activities):
            if activity.get('type')=='Script':
                from .graph_script_sql import attach_scripts
                attach_scripts(self,parent,activity,index,proof)
            at={**proof,'span':{'kind':'JSON_POINTER','path':'/properties/activities/'+str(index)}}
            kind='COPY_ACTIVITY' if activity.get('type')=='Copy' else 'QUERY_STEP'
            node=self.add(kind,activity.get('name','Unnamed activity'),[parent,'activity',index],at,{'activity_type':activity.get('type')})
            self.link('CONTAINS',self.by_asset[parent],node,at)
            properties=activity.get('typeProperties',{});translator=properties.get('translator',{})
            mappings=translator.get('mappings',properties.get('columnMappings',[]))
            if isinstance(mappings,list):
                for number,mapping in enumerate(mappings):
                    step=self.add('QUERY_STEP','Explicit copy mapping',[node,'mapping',number],at,{'mapping':mapping})
                    self.link('DERIVED_IN_STEP',node,step,at)
            self.gap(node,'Activity source/destination connection and column identities are not resolved.',
                'Collect its exact connection metadata and dataset object definitions; explicit mapping text alone is not an object binding.',at)


def retained_lakehouse_endpoint_assets(raw,*,observed_at):
    """Convert an immutable native endpoint receipt to explicit evidence assets.

    No listing enrichment or guessed fields. Caller passes these observations to
    graph extraction alongside the unchanged retained catalog.
    """
    observed_at=c.timestamp(observed_at)
    if not isinstance(raw,bytes):raise ValueError('ENDPOINT_RECEIPT_BYTES_REQUIRED')
    rows=json.loads(raw);result=[];seen=set();receipt_hash=hashlib.sha256(raw).hexdigest()
    if not isinstance(rows,list):raise ValueError('ENDPOINT_RECEIPT_LIST_REQUIRED')
    import uuid
    for index,row in enumerate(rows):
        request=row.get('request',{});response=row.get('response',{})
        workspace=str(uuid.UUID(request['workspace']));lakehouse=str(uuid.UUID(request['lakehouse']))
        if response.get('id')!=lakehouse or response.get('workspaceId')!=workspace or response.get('type')!='Lakehouse':
            raise ValueError('ENDPOINT_RECEIPT_IDENTITY_DIFFERS')
        endpoint=response.get('properties',{}).get('sqlEndpointProperties',{})
        uuid.UUID(endpoint['id'])
        if not isinstance(endpoint.get('connectionString'),str) or not endpoint['connectionString']:
            raise ValueError('ENDPOINT_RECEIPT_SERVER_REQUIRED')
        identity='fabric://'+workspace+'/'+lakehouse+'/endpoint-metadata'
        if identity in seen:raise ValueError('ENDPOINT_RECEIPT_DUPLICATE')
        seen.add(identity)
        result.append({'id':identity,'parent_id':'fabric://'+workspace+'/'+lakehouse,
            'kind':'LakehouseEndpointMetadata','name':'Retained Lakehouse endpoint declaration',
            'metadata':{'request':request,'response':response,'receipt_sha256':receipt_hash,
                'receipt_pointer':'/'+str(index),'observed_at':observed_at}})
    return result


def retained_native_relation_assets(context,*,observed_at=None,model_ids=None):
    """Project exact retained native item-relation evidence, with its provenance.

    This is the legacy declared-source witness: an explicit endpoint ID from
    Sql.Database plus NATIVE_CASCADEDELETE to one discovered Lakehouse. No
    relation, endpoint or owner is synthesized by label. Callers can bound this
    projection to the admitted model IDs; no estate read or health update occurs.
    """
    observed_at=c.timestamp(observed_at) if observed_at else None
    if not isinstance(context,dict)or not isinstance(context.get('assets'),list):raise ValueError('RETAINED_RELATION_CONTEXT_REQUIRED')
    assets={a['id']:a for a in context['assets']}
    if len(assets)!=len(context['assets']):raise ValueError('RETAINED_RELATION_DUPLICATE_ASSET')
    selected=set(model_ids) if model_ids is not None else {a['id']for a in assets.values()if a['kind']=='SemanticModel'}
    if not selected or len(selected)>1000 or any(assets.get(i,{}).get('kind')!='SemanticModel'for i in selected):
        raise ValueError('RETAINED_RELATION_MODEL_SCOPE')
    context_hash=hashlib.sha256(c.canonical(context).encode()).hexdigest();result=[]
    for index,relation in enumerate(context.get('graph',{}).get('edges',[])):
        if relation.get('relation')!='NATIVE_CASCADEDELETE' or relation.get('provenance')!='DISCOVERED':continue
        endpoint=assets.get(relation.get('source'));lakehouse=assets.get(relation.get('target'))
        if (not endpoint or not lakehouse or endpoint.get('availability')not in(None,'CURRENT')or lakehouse.get('availability')not in(None,'CURRENT')
                or endpoint['kind']!='SQLEndpoint'or lakehouse['kind']!='Lakehouse'
                or endpoint.get('parent_id')!=lakehouse.get('parent_id')):continue
        for scope in sorted({e['scope']for e in relation.get('evidence',[])if e.get('source_api')=='fabric_item_relations_beta'and e.get('scope')in selected}):
            if assets[scope].get('parent_id')!=endpoint.get('parent_id'):continue
            metadata={'relation':relation,'context_hash':context_hash,'context_version':context.get('version'),
                      'relation_pointer':'/graph/edges/'+str(index),'observed_at':observed_at,
                      'endpoint_asset_id':endpoint['id'],'endpoint_asset_hash':endpoint.get('content_hash'),
                      'container_asset_id':lakehouse['id'],'container_asset_hash':lakehouse.get('content_hash')}
            if observed_at is None:
                metadata['warning']='Catalog observation timestamp unavailable; retained relation is not a fresh observation.'
            result.append({'id':scope+'/native-relation/'+hashlib.sha256(c.canonical(relation).encode()).hexdigest(),
                'parent_id':scope,'kind':'NativeItemRelationMetadata','name':'Retained native endpoint ownership relation',
                'metadata':metadata,'availability':'CURRENT'})
    return result


def extract(estate,assets,definition_sink,*,observed_at,owner='retained-catalog',source_asset_ids=(),source_observations=None):
    return StaticGraph(estate,owner,observed_at,assets,definition_sink,source_asset_ids=source_asset_ids,source_observations=source_observations).build()


def extract_partitioned(estate,assets,definition_sink,*,observed_at,source_asset_ids=(),source_observations=None):
    """Full retained symbol table, item-owned IDs and consumer-owned edges.

    Pass changed item definitions plus explicitly retained external assets for
    incremental extraction, then select the changed owner partitions. Absence
    of external symbols stays UNKNOWN; no catalog-name match is invented.
    """
    return StaticGraph(estate,'retained-catalog',observed_at,assets,definition_sink,
                       source_asset_ids=source_asset_ids,partitioned=True,source_observations=source_observations).build()


def asset_owners(assets):
    """Retained parent identity ownership shared by catalog and graph compiler."""
    graph=StaticGraph('catalog-ownership','retained-catalog','1970-01-01T00:00:00Z',assets,
        lambda raw: (_ for _ in ()).throw(ValueError('OWNERSHIP_MUST_NOT_CAPTURE')))
    return {identity:graph.item_owner(identity) for identity in graph.assets}

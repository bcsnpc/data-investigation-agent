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
        target=self.add('BOUNDARY',reason[:200],[origin,reason],proof,confidence='UNKNOWN',unknown=unknown)
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
            a.get('parent_id')==self.assets[report].get('parent_id') and a['id'].split('/')[-1].casefold() in values]
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
            if native in ('SqlObject','WarehouseTable'):kind={'V':'VIEW','SQL_STORED_PROCEDURE':'PROCEDURE','P':'PROCEDURE','VIEW':'VIEW'}.get(meta.get('type',meta.get('type_desc')),kind)
            if native=='SemanticColumn' and meta.get('type')=='calculated':kind='CALCULATED_COLUMN'
            props={'asset_id':aid,'native_kind':native,'hidden':meta.get('isHidden',meta.get('visibility'))}
            if 'content_hash' in asset:
                spaced=hashlib.sha256(json.dumps(meta,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
                props['retained_metadata_hash_encoding']='SORTED_JSON_SPACED' if asset['content_hash']==spaced else 'SORTED_JSON_COMPACT_LEGACY'
            if aid in self.sources or any(parent in self.sources for parent in self._parents(aid)):props['system_of_record']=True
            for key in ('dataType','sourceColumn','isActive','crossFilteringBehavior','securityFilteringBehavior'):
                if key in meta:props[key]=meta[key]
            node=self.add(kind,asset['name'],['asset',aid],proof,props);self.by_asset[aid]=node;self.proofs[aid]=proof
        for aid,node in list(self.by_asset.items()):
            asset=self.assets[aid];parent=asset.get('parent_id');proof=self.proofs[aid];meta=asset.get('metadata',{})
            if parent in self.by_asset:self.link('CONTAINS',self.by_asset[parent],node,proof)
            if asset['kind'] in ('Report','ReportPage','ReportVisual'):
                report=self.ancestor(aid,'Report');model=self.model_for_report(report) if report else None
                self.filters(node,meta,model,proof,scope={'Report':'report','ReportPage':'page','ReportVisual':'visual'}[asset['kind']])
                if asset['kind']=='ReportVisual':
                    references=self.fields(node,meta.get('visual',{}).get('query',{}),model,proof)
                    if not model:self.gap(node,'Explicit report-to-model binding is missing or ambiguous.',
                        'Collect definition.pbir with a unique model identifier in the same workspace.',proof)
                    elif not references:
                        self.gap(node,'No supported explicit field reference was found in the retained visual query.','Collect the visual query or a permitted runtime visual-query observation.',proof)
                if asset['kind']=='ReportPage':self.interactions(aid,meta,proof)
            if asset['kind'] in ('Measure','SemanticColumn') and ('expression' in meta or asset['kind']=='Measure'):
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
